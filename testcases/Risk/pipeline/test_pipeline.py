import json
import time
import unittest
from datetime import datetime

from testcases import requestbase
from testcases.Risk.pipeline_apis import Pipeline
from utils import utils, requestlib, mysqlhelper,mongolib
from config import config


class TestPipeline(requestbase.RequestBase):
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

    def clean_borrow_case_if_exist(self, id_account, id_borrow):
        utils.log('check whether borrow case with id_account:{}, id_borrow:{} already exist, delete it if exist.'.format(id_account, id_borrow))
        query_sql = "select * from {}risk_borrow_case where id_account={} and id_borrow={}".format(self.prefix, id_account, id_borrow)
        query_result = self.risk_conn.fetchone(query_sql)
        if query_result:
            utils.log('delete current borrow case record')
            delete_sql = "delete from {}risk_borrow_case where id_account={} and id_borrow={}".format(self.prefix, id_account, id_borrow)
            update_result = self.risk_conn.update(delete_sql)
            self.assertTrue(update_result == 1, 'delete current borrow case record failed!')

    def call_borrow_apply_verify_kyc_call_type(self, data, call_type):
        self.call_borrow_apply(data)
        self.verify_kyc_result(data, call_type)

    def call_borrow_apply(self, data, clean_borrow_case=True):
        id_account, id_borrow = data['id_account'], data['id_borrow']
        if clean_borrow_case:
            self.clean_borrow_case_if_exist(id_account, id_borrow)
        transaction_id = "RT{}{}{}".format(id_account, id_borrow, utils.get_random_numb(1001, 9999))
        data.update({"transaction_id": transaction_id})
        result = Pipeline.borrow_apply(self.req, data)
        utils.log('2.verify call api borrow-apply successfully.')
        self.assertEqual(utils.query_json(result, 'success'), 'true', 'call api borrow-apply failed!')
        time.sleep(6)
        return result, transaction_id

    def verify_kyc_result(self, data, call_type):
        id_account, id_borrow = data['id_account'], data['id_borrow']
        kyc_result_sql = "select id,id_account,id_borrow,transaction_id,kyc_type_res,updated_at from vnrisk_rule_kyc_type_result where id_account={} order by id desc limit 1;"
        kyc_result = self.risk_conn.fetchone(kyc_result_sql.format(id_account))
        self.assertIsNotNone(kyc_result, 'Not find kyc type result for id_account:{} id_borrow:{}'.format(id_account, id_borrow))
        utils.log("kyc_type_result:\n{}".format(kyc_result))
        kyc_result_dict = json.loads(kyc_result['kyc_type_res'])
        self_call_type, family_call_type = kyc_result_dict[0]['call_type'], kyc_result_dict[1]['call_type']
        utils.log('3.verify kyc call type is [{}] for id_account:{} id_borrow:{}'.format(call_type, id_account, id_borrow))
        self.assertTrue(self_call_type == call_type and family_call_type == call_type, 'KYC call type is Not As expected!')

    def insert_kyc_score_result(self, id_account, sql):
        utils.log('1.insert a kyc approve record in vnrisk_rule_kyc_score_result for id_account:{}'.format(id_account))
        query_kyc_score_cnt_sql = "select count(*) as cnt from vnrisk_rule_kyc_score_result where id_account={};"
        kyc_score_result_cnt = self.risk_conn.fetchone(query_kyc_score_cnt_sql.format(id_account)).get('cnt')
        if kyc_score_result_cnt > 0:
            delete_kyc_score_sql = "delete from vnrisk_rule_kyc_score_result where id_account={};".format(id_account)
            self.risk_conn.execute(delete_kyc_score_sql)
        return self.risk_conn.execute(sql)

    def add_account_to_black_list(self, id_account):
        utils.log('1.add id_account to black user list.')
        query_black_account_cnt_sql = "select count(*) as cnt from vnrisk_black_user_id where black_id_account={};".format(id_account)
        black_account_cnt = self.risk_conn.fetchone(query_black_account_cnt_sql.format(id_account)).get('cnt')
        if black_account_cnt > 0:
            return utils.log('id_account:{} already in vnrisk_black_user_id.'.format(id_account))
        sql = self.model_data['SQL']['insertBlackUser'].format(id_account)
        return self.risk_conn.execute(sql)

    def verify_rule_resfinally_reject_result(self, id_account, id_borrow, result='reject', status='new'):
        query_rule_resfin = "select * from vnrisk_rule_resfinally where id_account={} and id_borrow={} order by id desc limit 1;".format(id_account, id_borrow)
        time.sleep(2)
        resfinally_result = self.risk_conn.fetchone(query_rule_resfin)
        utils.log("rule_resfinally result:\n{}".format(resfinally_result))
        actual_result, actual_status, blocking_day = resfinally_result['result'], resfinally_result['status'], resfinally_result['blocking_day']
        self.assertTrue(actual_result == result and actual_status == status and blocking_day >= 3, 'rule result Not correct! please check.')

    def update_mongo_loans_repaid_at(self, id_account, previous_day):
        utils.log('update mongo loans')
        action = 'update' if mongolib.MongoDAL.get_loans(id_account) else 'insert'
        doc_json = self.model_data['Mongo'][action]['loans_repaid_at']
        set_repaid_at = {'id_account': id_account, 'repaid_at': utils.get_previous_date(previous_day)}
        if action == 'insert': set_repaid_at['loan_id'] = utils.get_random_numb(10001, 99999)
        doc_json.update(set_repaid_at)
        mongolib.MongoDAL.upsert_user_loans([doc_json])
        time.sleep(1)

    def test_kyc_manual_no_approve_no_repaid(self):
        """验证KYC3.0 call type manual, no kyc approve in 90 days, no repaid in 30 days"""
        data = self.model_data['BorrowApply']['payloadnew'][config.COUNTRY][0]
        self.call_borrow_apply_verify_kyc_call_type(data, "manual")

    def test_kyc_skip_in_90_approve(self):
        """验证KYC3.0 call type skip, has kyc approve in 90 days"""
        data = self.model_data['BorrowApply']['payloadnew'][config.COUNTRY][1]
        id_account, id_borrow = data['id_account'], data['id_borrow']
        insert_kyc_score_result_sql = self.model_data['SQL']['insertKycScoreNow'].format(id_account)
        self.insert_kyc_score_result(id_account, insert_kyc_score_result_sql)
        self.call_borrow_apply_verify_kyc_call_type(data, "skip")

    def test_kyc_manual_in_180_approve_no_repaid(self):
        """验证KYC3.0 call type manual, has kyc approve 90<date<180 days, no repaid in 30 days"""
        data = self.model_data['BorrowApply']['payloadnew'][config.COUNTRY][2]
        id_account, id_borrow = data['id_account'], data['id_borrow']
        insert_sql = self.model_data['SQL']['insertKycScoreDayGap'].format(id_account, utils.get_previous_date(145)) # set created_at to 145 days ago
        self.insert_kyc_score_result(id_account, insert_sql)
        self.call_borrow_apply_verify_kyc_call_type(data, "manual")

    def test_kyc_skip_in_180_approve_has_repaid(self):
        """验证KYC3.0 call type skip, has kyc approve 90<date<180 days, has repaid in 30 days"""
        data = self.model_data['BorrowApply']['payloadnew'][config.COUNTRY][5]
        id_account, id_borrow = data['id_account'], data['id_borrow']
        insert_sql = self.model_data['SQL']['insertKycScoreDayGap'].format(id_account, utils.get_previous_date(160))
        self.insert_kyc_score_result(id_account, insert_sql)
        self.update_mongo_loans_repaid_at(id_account, 23)  # insert a repaid record in 30 days in loans
        self.call_borrow_apply_verify_kyc_call_type(data, "skip")

    def test_new_reject_and_block_day(self):
        """验证new轮黑名单->reject, blocking day>=3"""
        data = self.model_data['BorrowApply']['payloadnew'][config.COUNTRY][3]
        id_account, id_borrow = data['id_account'], data['id_borrow']
        self.add_account_to_black_list(id_account)
        utils.log('2.fire new borrow-apply')
        self.call_borrow_apply(data)
        utils.log('3.verify rule result is reject, status is [new] and blocking day>=3, cause blockingDay + 3')
        self.verify_rule_resfinally_reject_result(id_account, id_borrow)

    def test_adjust_reject_and_block_day(self):
        """验证adjust轮黑名单->reject, blocking day>=3"""
        data = self.model_data['BorrowApply']['payloadnew'][config.COUNTRY][4]
        id_account, id_borrow = data['id_account'], data['id_borrow']
        utils.log('1.fire new borrow-apply')
        delete_from_black_list_sql = "delete from vnrisk_black_user_id where black_id_account={}".format(id_account)
        self.risk_conn.update(delete_from_black_list_sql)
        result, transaction_id = self.call_borrow_apply(data)
        utils.log('2.fire adjust borrow-apply')
        self.add_account_to_black_list(id_account)
        data.update({"is_review": 'true', "transaction_id": transaction_id})  # keep same transaction_id with new round
        self.call_borrow_apply(data, False)  # adjust round(more info)
        utils.log('3.verify rule result is reject, status is [adjust] and blocking day>=3, cause blockingDay + 3')
        self.verify_rule_resfinally_reject_result(id_account, id_borrow, status='adjust')

