import time
import unittest
from datetime import datetime

from testcases import requestbase
from testcases.Risk.rule_engine_apis import RuleEngine
from utils import utils, requestlib, mysqlhelper,mongolib
from config import config


class TestRuleEngine(requestbase.RequestBase):
    rule_data = utils.load_yml("rule_engine_data.yaml")
    resource = utils.load_yml("resources.yaml")

    @classmethod
    def setUpClass(cls):
        utils.log("==================================================================")
        utils.log("=                                                                =")
        utils.log("===============           TEST CLASS SETUP               =========")
        utils.log("==================================================================")
        utils.log("Set up test class...")
        cls.req = requestlib.RequestLib()
        cls.trade_conn = mysqlhelper.MysqlConnector(cls.resource['TradeDB'][config.COUNTRY]['host'],
                                                    cls.resource['TradeDB']['user'],
                                                    cls.resource['TradeDB']['password'], cls.resource['TradeDB']['db'])
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

    def call_rule(self, test_data):
        params = self.rule_data['rule']['params']['general']
        params.update(test_data)
        result = RuleEngine.rule(self.req, params)
        utils.log('Step. verify call api borrow-apply successfully.')
        self.assertEqual(utils.query_json(result, 'msg'), 'success', 'call api rule failed!')
        time.sleep(3)
        utils.log(result)
        return result

    def verify_rule_result(self, data, rule_id, expected_result):
        id_account, id_borrow = data['idAccount'], data['idBorrow']
        rule_result_sql = self.rule_data['SQL']['query']['ruleResult'].format(id_account, rule_id)
        fetch_rule_result = self.risk_conn.fetchone(rule_result_sql)
        self.assertIsNotNone(fetch_rule_result, 'Not find rule #{} result for id_account:{} id_borrow:{}'.format(rule_id, id_account, id_borrow))
        utils.log("rule_result:\n{}".format(fetch_rule_result))
        rule_result = fetch_rule_result['rule_result']
        utils.log('Step. verify rule_id={} result is [{}] for id_account:{} id_borrow:{}'.format(rule_id, expected_result, id_account, id_borrow))
        self.assertEqual(expected_result, rule_result, 'rule result Not as expected! please check!')

    def insert_mongo_users(self, id_account):
        utils.log('insert mongo users if not exist for id_account: {}'.format(id_account))
        if not mongolib.MongoDAL.get_user(int(id_account)):
            mongolib.MongoDAL.upsert_user(int(id_account), self.rule_data['Mongo']['insert']['users'])
            time.sleep(1)

    def prepare_rule_99_100_data_verify_result(self, data_name, rule_id, expected_rule_result, set_score=False, total_score=None):
        test_data = self.rule_data['ruleTestData'][data_name]
        id_account, id_borrow = test_data['idAccount'], test_data['idBorrow']
        transaction_id = "RT{}{}{}".format(id_account, id_borrow, utils.get_random_numb(100, 200))
        test_data['transactionId'] = transaction_id
        utils.log('Step. make sure there are record in mongo users collection.')
        self.insert_mongo_users(id_account)
        utils.log('Step. make sure no model total score result via delete it in rule_model_total_score')
        delete_total_score_sql = self.rule_data['SQL']['delete']['modelTotalScore'].format(id_account)
        self.risk_conn.update(delete_total_score_sql)
        if set_score:
            utils.log('Step. insert a total score={} record in rule_model_total_score'.format(total_score))
            insert_total_score_sql = self.rule_data['SQL']['insert']['modelTotalScore'].format(id_account, id_borrow, total_score, transaction_id)
            self.risk_conn.update(insert_total_score_sql)
        self.call_rule(test_data)
        utils.log('Step. verify rule #{} result is {}'.format(rule_id, expected_rule_result))
        self.verify_rule_result(test_data, rule_id, expected_rule_result)

    def test_rule_99_has_apply_no_total_score(self):
        """验证VNKyc3.0.2 has user apply, no model total score,rule 99,loan_type='1'-> -2 not_null_but_null"""
        self.prepare_rule_99_100_data_verify_result('rule99', 99, -2)

    def test_rule_99_has_apply_total_score_null(self):
        """验证验证VNKyc3.0.2 has user apply, model total score is null,rule 99,loan_type='1'-> -2 not_null_but_null"""
        self.prepare_rule_99_100_data_verify_result('rule99', 99, -2, True, 'NULL')

    def test_rule_99_has_apply_total_score_less_560(self):
        """验证VNKyc3.0.2 has user apply, model total score<560,rule 99,loan_type='1'-> 1 bad guy"""
        self.prepare_rule_99_100_data_verify_result('rule99', 99, 1, True, 550)

    def test_rule_99_has_apply_total_score_more_560(self):
        """验证VNKyc3.0.2 has user apply, model total score>=560,rule 99,loan_type='1'-> 0 good guy"""
        self.prepare_rule_99_100_data_verify_result('rule99', 99, 0, True, 560)

    def test_rule_100_has_apply_no_total_score(self):
        """验证VNKyc3.0.2 has user apply, no model total score,rule 100,loan_type='2'-> -2 not_null_but_null"""
        self.prepare_rule_99_100_data_verify_result('rule100', 100, -2)

    def test_rule_100_has_apply_total_score_null(self):
        """验证验证VNKyc3.0.2 has user apply, model total score is null,rule 100,loan_type='2'-> -2 not_null_but_null"""
        self.prepare_rule_99_100_data_verify_result('rule100', 100, -2, True, 'NULL')

    def test_rule_100_has_apply_total_score_less_560(self):
        """验证VNKyc3.0.2 has user apply, model total score<560,rule 100,loan_type='2'-> 1 bad guy"""
        self.prepare_rule_99_100_data_verify_result('rule100', 100, 1, True, 550)

    def test_rule_100_has_apply_total_score_more_560(self):
        """验证VNKyc3.0.2 has user apply, model total score>=560,rule 100,loan_type='2'-> 0 good guy"""
        self.prepare_rule_99_100_data_verify_result('rule100', 100, 0, True, 560)

    def test_rule_101_relative_cnt_null_loan1(self):
        """验证VNKyc3.0.2联系人手机号关联账号次数 is null,rule 101,loan_type in (1,2)-> 0 good guy"""
        self.prepare_rule_101_data_verify_result('rule99', 101, 0, mobil_numb='852627326')

    def test_rule_101_relative_cnt_less_5_loan1(self):
        """验证VNKyc3.0.2 0<联系人手机号关联账号次数<5,rule 101,loan_type in (1,2)-> 0 good guy"""
        self.prepare_rule_101_data_verify_result('rule99', 101, 0, True, 3, '852627326')

    def test_rule_101_relative_cnt_eq_more_5_loan1(self):
        """验证VNKyc3.0.2联系人手机号关联账号次数>=5,rule 101,loan_type in (1,2)-> 1 bad guy"""
        self.prepare_rule_101_data_verify_result('rule99', 101, 1, True, 5, '852627326')

    def test_rule_101_relative_cnt_null_loan2(self):
        """验证VNKyc3.0.2联系人手机号关联账号次数 is null,rule 101,loan_type in (1,2)-> 0 good guy"""
        self.prepare_rule_101_data_verify_result('rule100', 101, 0, mobil_numb='852627638')

    def test_rule_101_relative_cnt_less_5_loan2(self):
        """验证VNKyc3.0.2 0<联系人手机号关联账号次数<5,rule 101,loan_type in (1,2)-> 0 good guy"""
        self.prepare_rule_101_data_verify_result('rule100', 101, 0, True, 3, '852627638')

    def test_rule_101_relative_cnt_eq_more_5_loan2(self):
        """验证VNKyc3.0.2联系人手机号关联账号次数>=5,rule 101,loan_type in (1,2)-> 1 bad guy"""
        self.prepare_rule_101_data_verify_result('rule100', 101, 1, True, 5, '852627638')

    def prepare_rule_101_data_verify_result(self, data_name, rule_id, expected_rule_result, set_contacts=False, relative_cnt=None, mobil_numb=None):
        test_data = self.rule_data['ruleTestData'][data_name]
        id_account, id_borrow = test_data['idAccount'], test_data['idBorrow']
        transaction_id = "RT{}{}{}".format(id_account, id_borrow, utils.get_random_numb(201, 300))
        test_data.update({'transactionId': transaction_id, 'roundId': '1'})   # roundId 更新为1
        utils.log('Step. make sure there are record in mongo users collection.')
        self.insert_mongo_users(id_account)
        utils.log('Step. make sure no relative_cnt via delete it in vnrisk_applied_contacts')
        delete_applied_contacts_sql = self.rule_data['SQL']['delete']['appliedContacts'].format(mobil_numb)
        self.risk_conn.update(delete_applied_contacts_sql)
        if set_contacts:
            utils.log('Step. insert a record in vnrisk_user_contacts for id_account:{} with mobil number:{}'.format(id_account, mobil_numb))
            query_user_contacts_cnt = self.rule_data['SQL']['query']['userContactsCnt'].format(id_account, mobil_numb)
            if self.risk_conn.fetchone(query_user_contacts_cnt)['cnt'] == 0:
                insert_user_contacts_sql = self.rule_data['SQL']['insert']['userContacts'].format(utils.get_random_numb(2999, 5555), id_account, mobil_numb)
                self.risk_conn.update(insert_user_contacts_sql)
            utils.log('Step. insert a record in vnrisk_applied_contacts for mobile={},set relative_cnt:{}'.format(mobil_numb, relative_cnt))
            query_applied_contacts_cnt = self.rule_data['SQL']['query']['applied_contacts_cnt'].format(mobil_numb)
            # if self.risk_conn.fetchone(query_applied_contacts_cnt)['cnt'] == 0:
            #     applied_contacts_sql = self.rule_data['SQL']['insert']['applied_contacts'].format(mobil_numb, id_account, relative_cnt)
            # else:
            #     applied_contacts_sql = self.rule_data['SQL']['update']['applied_contacts'].format(id_account, relative_cnt, mobil_numb)
            insert_applied_contacts = self.rule_data['SQL']['insert']['applied_contacts'].format(mobil_numb, id_account, relative_cnt)
            update_applied_contacts = self.rule_data['SQL']['update']['applied_contacts'].format(id_account, relative_cnt, mobil_numb)
            applied_contacts_sql = update_applied_contacts if self.risk_conn.fetchone(query_applied_contacts_cnt)['cnt'] else insert_applied_contacts
            self.risk_conn.update(applied_contacts_sql)
        self.call_rule(test_data)
        utils.log('Step. verify rule #{} result is {}'.format(rule_id, expected_rule_result))
        self.verify_rule_result(test_data, rule_id, expected_rule_result)

    def test_rule_102_no_history_device(self):
        """验证VNKyc3.0.2 三个月内historyDeviceCount=0,rule 102,loan_type in (1,2)-> -2 not_null_but_null"""
        self.prepare_rule_102_data_verify_result('rule99', 102, -2)

    def test_rule_102_history_device_more2_has_share_device(self):
        """验证VNKyc3.0.2 三个月内 historyDeviceCount>2且deviceShareCount> 0,rule 102,loan_type in (1,2)-> 1 bad guy"""
        self.prepare_rule_102_data_verify_result('rule99', 102, 1, True, True, True)

    def test_rule_102_history_device_less2_has_share_device(self):
        """验证VNKyc3.0.2 三个月内historyDeviceCount<=2但deviceShareCount>0,rule 102,loan_type in (1,2)-> 0 good guy"""
        self.prepare_rule_102_data_verify_result('rule99', 102, 0, True, False, True)

    def test_rule_102_history_device_more2_no_share_device(self):
        """验证VNKyc3.0.2 三个月内historyDeviceCount>2但无deviceShareCount,rule 102,loan_type in (1,2)-> 0 good guy"""
        self.prepare_rule_102_data_verify_result('rule99', 102, 0, True, True, False)

    def prepare_rule_102_data_verify_result(self, data_name, rule_id, expected_rule_result, set_device=False, two_more_device=False, share_device=False):
        test_data = self.rule_data['ruleTestData'][data_name]
        id_account, id_borrow = test_data['idAccount'], test_data['idBorrow']
        transaction_id = "RT{}{}{}".format(id_account, id_borrow, utils.get_random_numb(301, 400))
        test_data.update({'transactionId': transaction_id, 'roundId': '1'})  # roundId 更新为1
        utils.log('Step. make sure there are record in mongo users collection.')
        self.insert_mongo_users(id_account)
        utils.log('Step. make sure no test device_id info(in yml) via delete them in vnrpt_bhv_user_device_mapping.')
        delete_user_device_sql = self.rule_data['SQL']['delete']['userDeviceMapping']
        self.risk_conn.update(delete_user_device_sql)
        if set_device:
            update_ts = utils.get_previous_date(6)  # 6 days ago
            if two_more_device:
                utils.log('Step. insert 3 device info for account:{} within 3 months(historyDeviceCount > 2)'.format(id_account))  # vnrpt_bhv_user_device_mapping
                insert_device_in_3_month_sql = self.rule_data['SQL']['insert']['3devices'].format(id_account, update_ts, id_account, update_ts, id_account, update_ts)
            else:
                utils.log('Step. insert 2 device info for account:{} within 3 months(historyDeviceCount <= 2)'.format(id_account))
                insert_device_in_3_month_sql = self.rule_data['SQL']['insert']['2devices'].format(id_account, update_ts, id_account, update_ts)
            self.risk_conn.update(insert_device_in_3_month_sql)
        if share_device:
            utils.log('Step. insert a share device:[300728abda0ec6e7] record with account:10086 for account:{} (deviceShareCount>0)'.format(id_account))  # vnrpt_bhv_user_device_mapping
            insert_1_share_device_with_another_sql = self.rule_data['SQL']['insert']['sharedevice']
            self.risk_conn.update(insert_1_share_device_with_another_sql)
        time.sleep(2)
        self.call_rule(test_data)
        utils.log('Step. verify rule #{} result is {}'.format(rule_id, expected_rule_result))
        self.verify_rule_result(test_data, rule_id, expected_rule_result)
