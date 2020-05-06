from datetime import datetime
import json
import time
import unittest

from testcases import requestbase
from utils import utils, requestlib, mysqlhelper
from config import config, constants


class TestRuleModel(requestbase.RequestBase):
    model_data = utils.load_yml("rule_model_data.yaml")
    resource = utils.load_yml("resources.yaml")
    query_count = model_data['QueryCount']

    @classmethod
    def setUpClass(cls):
        utils.log("==================================================================")
        utils.log("=                                                                =")
        utils.log("===============           TEST CLASS SETUP               =========")
        utils.log("==================================================================")
        utils.log("Set up test class...")
        cls.req = requestlib.RequestLib()
        cls.trade_conn = mysqlhelper.MysqlConnector(cls.resource['TradeDB'][config.COUNTRY]['host'], cls.resource['TradeDB']['user'], cls.resource['TradeDB']['password'], cls.resource['TradeDB']['db'])
        cls.risk_conn = mysqlhelper.MysqlConnector(cls.resource['StagingRiskDB'][config.COUNTRY]['host'],
                                                   cls.resource['StagingRiskDB']['user'],
                                                   cls.resource['StagingRiskDB']['password'],
                                                   cls.resource['StagingRiskDB']['db'],
                                                   cls.resource['StagingRiskDB'][config.COUNTRY]['port'])
        cls.prefix = cls.resource['StagingRiskDB'][config.COUNTRY]['tbPrefix']
        cls.time_now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        utils.log("==================================================================\n\n")

    @classmethod
    def tearDownClass(cls):
        utils.log("==================================================================")
        utils.log("=                                                                =")
        utils.log("================           TEST CLASS CLEANUP           ==========")
        utils.log("==================================================================")
        if cls.req: cls.req.close_session()
        if cls.trade_conn: cls.trade_conn.close()
        if cls.risk_conn: cls.risk_conn.close()
        utils.log("==================================================================\n\n")

    def call_borrow_apply(self, data):
        utils.log('call api [borrow-apply] for [{}]'.format(config.COUNTRY))
        url = self.model_data['Host'][config.COUNTRY] + self.model_data['CeleryPort'][config.COUNTRY] + self.model_data['BorrowApply']['path']
        header = self.model_data['BorrowApply']['header']
        model_result = json.loads(self.req.post(url, headers=header, json=data).text)
        utils.log('1.verify call RiskMQ-app API borrow-apply successfully.')
        self.assertEqual(utils.query_json(model_result, 'success'), 'true', 'call api borrow-apply failed!')

    def get_borrow_order_from_trade(self):
        utils.log('pick latest borrow orders from trade db.')
        sql = 'select * from BorrowOrders order by id desc limit 30'
        return self.trade_conn.fetchall(sql)

    def update_trade_person(self, home_own_code, stay_length, person_property, occupation, occupation_code, id_account):
        utils.log("update [trade][Persons], set homeOwnershipCode={}, stayLength='{}' , property='{}', occupation='{}'"
                  ", occupationCode={} for accountId={}".format(home_own_code, stay_length, person_property, occupation, occupation_code, id_account))
        sql = """
        update Persons
        set homeOwnershipCode='{}', stayLength='{}', property='{}', occupation='{}', occupationCode='{}'
        where accountId={}
        """.format(home_own_code, stay_length, person_property, occupation, occupation_code, id_account)
        result = self.trade_conn.update(sql)
        time.sleep(1)
        # self.assertTrue(result == 1, 'update Persons failed!')

    def get_vn_cash_model_test_data(self):
        """#1 model"""
        utils.log('get records from user_apply match cash model: loan_success=0 and loan_type in (1,2)')
        sql = 'select * from vnrisk_user_apply where loan_success=0 and loan_type in (1,2) order by id desc limit ' + str(self.query_count)
        picked_apply_orders = self.risk_conn.fetchall(sql)
        self.assertTrue(len(picked_apply_orders) > 0, 'there is no qualify records in table user_apply!')
        return picked_apply_orders

    def pre_check_order_exist_in_trade(self, id_borrow, id_account):
        utils.log('verify record with id={} and accountId={} exist in origin [trade] db [BorrowOrders] table.'.format(
            id_borrow, id_account))
        trade_sql = 'select * from BorrowOrders where id={} and accountId={}'.format(id_borrow, id_account)
        origin_record = self.trade_conn.fetchone(trade_sql)
        self.assertIsNotNone(origin_record, 'Not find any record with given id_borrow and id_account! please pick another one')

    def clean_borrow_case_if_exist(self, id_account, id_borrow):
        utils.log('check whether borrow case with id_account:{}, id_borrow:{} already exist, delete it if exist.'.format(id_account, id_borrow))
        query_sql = "select * from {}risk_borrow_case where id_account={} and id_borrow={}".format(self.prefix, id_account, id_borrow)
        query_result = self.risk_conn.fetchone(query_sql)
        if query_result:
            utils.log('delete current borrow case record')
            delete_sql = "delete from {}risk_borrow_case where id_account={} and id_borrow={}".format(self.prefix, id_account, id_borrow)
            update_result = self.risk_conn.update(delete_sql)
            self.assertTrue(update_result == 1, 'delete current borrow case record failed!')

    def get_test_id_borrow_id_account(self, picked_apply_orders, index):
        borrow_order = picked_apply_orders[index]
        id_borrow, id_account = borrow_order['id_borrow'], borrow_order['id_account']
        return id_borrow, id_account

    def verify_borrow_case_status(self, id_account, id_borrow):
        """验证borrow_case表case_status字段更新正确"""
        utils.log('verify filed [case_status] in [borrow_case] updated with correct status(success, postkyc_success)')
        sql = "select * from {}risk_borrow_case where id_account={} and id_borrow={}".format(self.prefix, id_account, id_borrow)
        time.sleep(15)  # need time to process
        result = self.risk_conn.fetchone(sql)
        utils.log('result in borrow case:\n{}'.format(result))
        case_status, update_at = result['case_status'], result['updated_at']
        total_seconds = (datetime.now()-update_at).total_seconds()
        minutes = abs(int(total_seconds / 60))  # 数据库时间比local快几分钟，取绝对值查看相差分钟数，小于10分钟
        self.assertTrue(case_status in ('success', 'postkyc_success') and minutes < 10, 'borrow case status Not In correct status')

    def prepare_model_data(self, picked_apply_orders, random=False):
        id_borrow, id_account = self.get_test_id_borrow_id_account(picked_apply_orders, 0)  # get last one
        if random:
            id_borrow, id_account = self.get_test_id_borrow_id_account(picked_apply_orders, utils.get_random_numb(0, len(picked_apply_orders)-1))
        self.pre_check_order_exist_in_trade(id_borrow, id_account)
        self.clean_borrow_case_if_exist(id_account, id_borrow)
        data = self.model_data['BorrowApply']['payload']['General']
        data.update({'id_account': id_account, 'id_borrow': id_borrow})
        return id_borrow, id_account, data

    def verify_model_workflow_pass(self, picked_apply_orders, random=False):
        id_borrow, id_account, data = self.prepare_model_data(picked_apply_orders, random)
        self.call_borrow_apply(data)
        self.verify_borrow_case_status(id_account, id_borrow)

    def verify_model_feature(self, id_borrow, id_account, expect_feature_json):
        utils.log('verify filed [feature] in [model_feature] updated correct')
        sql = "select * from {}risk_model_feature where id_account={} and id_borrow={}".format(self.prefix, id_account, id_borrow)
        result = self.risk_conn.fetchone(sql)
        feature_json = json.loads(result['feature'])
        # TestRuleModel.update_None_str_2_None(expect_feature_json)
        utils.update_none_str_2_none(expect_feature_json)
        utils.log('verify expected feature generated in table model_feature')
        utils.log('expected feature:{}\nactual feature:{}'.format(expect_feature_json, feature_json))
        self.assertTrue(set(expect_feature_json.items()).issubset(set(feature_json.items())),
                        'expected feature value Not write to db model_feature!')

    def verify_model_total_score(self, id_borrow, id_account):
        utils.log('verify filed [total_score] in [model_total_score] updated correct')
        sql = "select * from {}risk_rule_model_total_score where id_account={} and id_borrow={}".format(self.prefix, id_account, id_borrow)
        result = self.risk_conn.fetchone(sql)
        self.assertIsNotNone(result, 'there is No total_score found in [model_total_score] for this id_borrow.')
        total_score = result['total_score']
        utils.log('got total_score={}'.format(str(total_score)))

    def verify_riskcontrol_resfin(self, id_borrow, id_account):
        utils.log('verify filed [res],[status] in [riskcontrol_resfin] updated correct')
        sql = "select * from {}risk_riskcontrol_resfin where id_account={} and id_borrow={} and updated_at>'{}'".format(self.prefix, id_account, id_borrow, self.time_now_str)
        result_list = self.risk_conn.fetchall(sql)
        self.assertTrue(len(result_list) > 1,
                        'there should more than 1 resfin record for one (id_account, id_borrow) pair!')
        res_set, status_set = set(), set()
        for result in result_list:
            res_set.add(result['res'])
            status_set.add(result['status'])
        expected_res = ('approve', 'success', 'reject')
        expected_status = ('new', 'new-score', 'post-kyc')

    @unittest.skipUnless(config.COUNTRY == constants.CN, 'only for CN')
    def test_cash_model_workflow_pass(self):
        """验证VN #1 model流程是通的"""
        self.verify_model_workflow_pass(self.get_vn_cash_model_test_data())

    @unittest.skipUnless(config.COUNTRY == constants.CN, 'only for CN')
    def test_CN_cash_model(self):
        utils.log('test borrow orders with condition: loan_type in (1,2) and loan_success=0 to hit CN cash model.')
        id_borrow, id_account, data = self.prepare_model_data(self.get_vn_cash_model_test_data(), True)  # random data
        # id_borrow, id_account, data = self.prepare_model_data(self.get_vn_cash_model_test_data())  # last one
        test_scenario = 2  # rule_model_data VNCashModel
        self.update_trade_person(self.model_data['VNCashModel']['SetField'][test_scenario]['homeOwnershipCode'],
                                 self.model_data['VNCashModel']['SetField'][test_scenario]['stayLength'],
                                 self.model_data['VNCashModel']['SetField'][test_scenario]['property'],
                                 self.model_data['VNCashModel']['SetField'][test_scenario]['occupation'],
                                 self.model_data['VNCashModel']['SetField'][test_scenario]['occupationCode'],
                                 id_account)
        self.call_borrow_apply(data)
        self.verify_borrow_case_status(id_account, id_borrow)
        self.verify_model_feature(id_borrow, id_account, self.model_data['VNCashModel']['expectFeature'][test_scenario])
        self.verify_model_total_score(id_borrow, id_account)
        # self.verify_riskcontrol_resfin(id_borrow, id_account)


