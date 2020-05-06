import json
import time

from config import config, constants
from testcases import requestbase
from utils import utils, requestlib


class TestKycReason(requestbase.RequestBase):
    rule_data = utils.load_yml("rule_manager_data.yaml")
    resource = utils.load_yml("resources.yaml")

    @classmethod
    def setUpClass(cls):
        utils.log("==================================================================")
        utils.log("=                                                                =")
        utils.log("===============           TEST CLASS SETUP               =========")
        utils.log("==================================================================")
        utils.log("Set up test class...")
        cls.req = requestlib.RequestLib()
        cls.login_api(cls.rule_data['BaseUrl'] + cls.rule_data['FrontendPort'] + cls.rule_data['login']['path'],
                      cls.rule_data['login']['header'], cls.rule_data['login']['payload'])
        cls.risk_conn = utils.get_db_connector(cls.resource['Mysql']['RiskDB']['db'][config.COUNTRY]['risk_dev_tmp'])
        cls.tb_prefix = cls.resource['Mysql']['RiskDB']['db'][config.COUNTRY]['tbPrefix']
        utils.log("==================================================================\n\n")

    @classmethod
    def tearDownClass(cls):
        utils.log("==================================================================")
        utils.log("=                                                                =")
        utils.log("================           TEST CLASS CLEANUP           ==========")
        utils.log("==================================================================")
        if cls.req: cls.req.close_session()
        if cls.risk_conn: cls.risk_conn.close()
        utils.log("==================================================================\n\n")

    def test_search_kyc_reason_exist(self):
        """验证搜索存在的Flipping ids成功"""
        search_resp = self.search_kyc_with_params(self.rule_data['searchKyc']['validParams'][config.COUNTRY])
        kyc_reason_total = utils.query_json(json.loads(search_resp), 'data.total')
        utils.log('verify search kyc reason records success with exist Flipping ids')
        self.assertTrue(kyc_reason_total > 0, 'search kyc reason with exist Flipping ids failed!')

    def test_search_kyc_reason_not_exist(self):
        """验证搜索不存在的Flipping ids成功"""
        search_resp = self.search_kyc_with_params(self.rule_data['searchKyc']['invalidParams'])
        kyc_reason_total = utils.query_json(json.loads(search_resp), 'data.total')
        utils.log('verify search kyc reason records success with Not exist Flipping ids')
        self.assertEqual(kyc_reason_total, 0, 'search kyc reason with Not exist Flipping ids failed! should equal 0!')

    def test_update_publish_kyc_valid(self):
        """验证更新Kyc reason, snapshotversion等字段更新，设置isValid=1"""
        utils.log("Case. update rule and publish it, set rule_valid=1.")
        self.verify_kyc_update('payloadValid')

    def test_update_publish_kyc_invalid(self):
        """验证更新Kyc reason, snapshotversion等字段更新，设置isValid=0"""
        utils.log("Case. update rule and publish it, set rule_valid=0.")
        self.verify_kyc_update('payloadInValid')

    def test_reset_kyc_reason(self):
        """验证Reset Kyc reason成功"""
        update_payload = self.rule_data['update_kyc']['payloadInValid'][config.COUNTRY]
        update_payload.update({'topicType': 'autoRej' + utils.get_time_stamp()})
        url_host = self.rule_data['BaseUrl'] + self.rule_data['BackendPort'][config.COUNTRY]
        self.verify_update_kyc(url_host + self.rule_data['update_kyc']['path'], self.rule_data['update_kyc']['header'],
                               update_payload, update_payload['flippingId'])
        self.verify_reset_kyc(url_host + self.rule_data['reset_kyc']['path'].format(update_payload['flippingId']),
                              self.rule_data['reset_kyc']['header'], update_payload['flippingId'])

    def verify_kyc_update(self, test_payload):
        """
        1.验证update kyc，publish kyc
        2.验证kyc在table rule_kyc_reject_reason更新
        3.验证kyc在table rule_kyc_reject_reason_operation更新
        4.验证kyc在table rule_kyc_reject_reason_snapshot更新
        """
        if config.COUNTRY == constants.US:
            table_prefix = "usrisk"
        elif config.COUNTRY == constants.JP:
            table_prefix = "jprisk"
        elif config.COUNTRY == constants.CN:
            table_prefix = "cnrisk"
        else:
            table_prefix = ""

        update_payload = self.rule_data['update_kyc'][test_payload][config.COUNTRY]
        new_desc = 'autoRej' + utils.get_time_stamp()
        update_payload.update({'topicType': new_desc})
        update_flipping_id = update_payload['flippingId']
        update_header = self.rule_data['update_kyc']['header']
        self.verify_update_kyc(
            self.rule_data['BaseUrl'] + self.rule_data['BackendPort'][config.COUNTRY] + self.rule_data['update_kyc']['path'],
            update_header, update_payload, update_flipping_id)
        self.verify_publish_kyc(
            self.rule_data['BaseUrl'] + self.rule_data['FrontendPort'] + self.rule_data['publish_kyc']['path'],
            update_header, update_flipping_id)

        utils.log("1.verify flipping_id={} record [topic_type] updated in table {}_rule_kyc_reject_reason".format(update_flipping_id, table_prefix))
        query_kyc = "select * from {}_rule_kyc_reject_reason where flipping_id={}".format(table_prefix, update_flipping_id)
        kyc_record = self.risk_conn.fetchone(query_kyc)
        utils.log(kyc_record)
        self.assertEqual(new_desc, kyc_record['topic_type'], "kyc reason record not update value:{}! please check".format(new_desc))

        utils.log("2.verify flipping_id={} record,[snapshot_version] updated in table {}_rule_kyc_operation".format(update_flipping_id, table_prefix))
        query_kyc_operation = "select * from {}_rule_kyc_reject_reason_operation where flipping_id={} order by id desc".format(table_prefix, update_flipping_id)
        kyc_operation_record = self.risk_conn.fetchall(query_kyc_operation)[0]
        utils.log(kyc_operation_record)
        dt_now = utils.get_datetime_per_timezone()
        minutes_pass = utils.get_time_minus(dt_now, kyc_operation_record['updated_at'])
        utils.log('verify record update timestamp is latest, less than 2 min.')
        self.assertTrue(minutes_pass < 2, "rule not updated for rule_id={} in {}_rule_operation!".format(update_flipping_id, table_prefix))

        utils.log("3.verify flipping_id={} record [topic_type],[snapshot_version] updated in table {}_rule_kyc_reject_reason_snapshot".format(update_flipping_id, table_prefix))
        query_rule_snapshot = "select * from {}_rule_kyc_reject_reason_snapshot where flipping_id={} and snapshot_version='{}'".format(
            table_prefix, update_flipping_id, kyc_operation_record['snapshot_version'])
        kyc_snapshot_record = self.risk_conn.fetchall(query_rule_snapshot)
        utils.log(kyc_snapshot_record)
        self.assertTrue(len(kyc_snapshot_record) == 1, "there should only 1 record in table {}_rule_kyc_reject_reason_snapshot for this query!".format(table_prefix))
        self.assertEqual(new_desc, kyc_snapshot_record[0]['topic_type'], "kyc not update in {}_rule_kyc_reject_reason_snapshot!".format(table_prefix))
        self.assertTrue(kyc_record['is_valid'] == kyc_snapshot_record[0]['is_valid'] and
                        kyc_record['apply_amount_min'] == kyc_snapshot_record[0]['apply_amount_min'],
                        'field [is_valid] and [apply_amount_min] are same between {}_rule_kyc_reject_reason and {}_rule_kyc_reject_reason_snapshot'.format(table_prefix, table_prefix))

    def verify_update_kyc(self, url, header, payload, update_flipping_id):
        header.update({'Region': config.COUNTRY})
        update_resp = self.update_kyc_reason_api(url, header, payload)
        utils.log("verify update kyc reason successfully.")
        self.assertEqual(utils.query_json(json.loads(update_resp), 'msg'), 'success', 'update flipping_id={} kyc reason failed!'.format(update_flipping_id))

    def verify_publish_kyc(self, url, header, update_flipping_id):
        header.update({'Region': config.COUNTRY})
        publish_resp = self.publish_kyc_reason_api(url, header)
        utils.log("verify publish kyc reason successfully.")
        self.assertEqual(utils.query_json(json.loads(publish_resp), 'msg'), 'success', 'publish flipping_id={} kyc reason failed!'.format(update_flipping_id))

    def verify_reset_kyc(self, url, header, update_flipping_id):
        header.update({'Region': config.COUNTRY})
        reset_kyc_resp = self.reset_kyc_reason_api(url, header)
        utils.log('verify reset kyc reason for flipping_id={} successfully.'.format(update_flipping_id))
        self.assertEqual(json.loads(reset_kyc_resp.text)['msg'], 'success', 'call reset kyc reason api failed!')

    def search_kyc_with_params(self, params):
        url = self.rule_data['BaseUrl'] + self.rule_data['BackendPort'][config.COUNTRY] + self.rule_data['searchKyc']['path']
        return self.search_kyc_reason_api(url, self.rule_data['searchKyc']['header'], params)

    @classmethod
    def login_api(cls, url, header, payload):
        utils.log(">>login rule manager...")
        login_response = cls.req.post(url, headers=header, json=payload)
        utils.log("response is: {}".format(login_response.text))
        return login_response

    def search_kyc_reason_api(self, url, header, params):
        utils.log(">>search kyc reason records...")
        kyc_list_resp = self.req.get(url, headers=header, params=params)
        self.assertEqual(json.loads(kyc_list_resp.text)['msg'], 'success', 'call search kyc reason api failed!')
        return kyc_list_resp.text

    def update_kyc_reason_api(self, url, header, payload):
        utils.log(">>update kyc reason records...")
        save_resp = self.req.post(url, headers=header, json=payload)
        return save_resp.text

    def publish_kyc_reason_api(self, url, header):
        utils.log(">>publish kyc reason...")
        publish_result = self.req.post(url, headers=header)
        time.sleep(1)
        utils.debug(json.loads(publish_result.text)['data'])
        return publish_result.text

    def reset_kyc_reason_api(self, url, header):
        utils.log(">>reset kyc reason...")
        return self.req.get(url, headers=header)


