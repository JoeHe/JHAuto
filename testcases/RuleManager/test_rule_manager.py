import json
import time
import unittest

from testcases import requestbase
from utils import utils, requestlib
from pages import datagridview, login
from utils import getdriver
from config import config, constants
from pages.RuleManage import rule_manage_home


class TestRuleManager(requestbase.RequestBase):
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
        cls.login_api(cls.rule_data['BaseUrl'] + cls.rule_data['FrontendPort'] + cls.rule_data['login']['path'], cls.rule_data['login']['header'], cls.rule_data['login']['payload'])
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

    def test_update_publish_rule_valid(self):
        """验证更新Rule, snapshotversion等字段更新，设置rule_valid=1"""
        utils.log("Case. update rule and publish it, set rule_valid=1.")
        self.verify_rule_update('payloadValid')

    def test_update_publish_rule_invalid(self):
        """验证更新Rule, snapshotversion等字段更新，设置rule_valid=0"""
        utils.log("Case. update rule and publish it, set rule_valid=0.")
        self.verify_rule_update('payloadInValid')

    def test_search_rule_group1_correct(self):
        """验证页面按规则组1搜索结果总数应与DB查询结果一致。"""
        self.verify_search_rule_group_consistence_web_db(self.rule_data['search']['searchGroupPara'][config.COUNTRY][0])

    def test_search_rule_group3_correct(self):
        """验证页面按规则组3搜索结果总数应与DB查询结果一致。"""
        self.verify_search_rule_group_consistence_web_db(self.rule_data['search']['searchGroupPara'][config.COUNTRY][1])

    def test_search_rule_grp_rule_id_valid_correct(self):
        """验证按RuleGroup及有效RuleID查询结果正确"""
        params = self.rule_data['search']['searchGroupPara'][config.COUNTRY][2]
        response = self.verify_search_rule_api_and_check(params, True)
        self.verify_search_rule_id_consistence_web_db(params, response)

    def test_search_rule_grp_rule_id_invalid_correct(self):
        """验证按RuleGroup及无效RuleID查询结果正确"""
        params = self.rule_data['search']['searchGroupPara'][config.COUNTRY][3]
        response = self.verify_search_rule_api_and_check(params, True)
        self.verify_search_rule_id_consistence_web_db(params, response)

    def test_rule_groups_list_item_correct(self):
        """验证页面规则组下拉框数据与db一致"""
        rule_manage = rule_manage_home.RuleManageHome(getdriver.getdriver(config.DRIVER_TYPE))
        utils.log('1.get rule group list items in web page.')
        rule_groups_page = set(rule_manage.login_get_rule_group_item(self.rule_data))
        utils.log('2.get rule group list from db')
        sql_groups = 'select id, group_name as name from {}risk_rule_group;'.format(self.tb_prefix)
        # sql_groups = 'select id, group_name as name from {}risk_rule_group where is_valid=1;'.format(self.tb_prefix)
        rule_groups_db = {'{}-{}'.format(grp.get('id'), grp.get('name')) for grp in self.risk_conn.fetchall(sql_groups)}
        utils.log("3.verify rule groups items in page and db are consistence")
        utils.log('Rule Groups data \nin Page:{} \nin db:{}'.format(rule_groups_page, rule_groups_db))
        self.assertEqual(rule_groups_page, rule_groups_db, 'Rule Group in page and db Not consistence!')

    def verify_rule_update(self, test_payload):
        """
        1.验证update rule，publish rule执行正确
        2.验证rule在table rule更新
        3.验证rule在table rule_operation更新
        4.验证rule在table rule_snapshot更新
        """
        if config.COUNTRY == constants.US: table_prefix = "usrisk"
        elif config.COUNTRY == constants.JP: table_prefix = "jprisk"
        elif config.COUNTRY == constants.CN: table_prefix = "cnrisk"
        else: table_prefix = ""

        update_payload = self.rule_data['update_rule'][test_payload]
        new_desc = 'auto test' + utils.get_time_stamp()
        update_payload.update({'ruleDescription': new_desc})
        update_rule_id = update_payload['ruleId']
        update_header = self.rule_data['update_rule']['header']
        self.verify_update_rule(
            self.rule_data['BaseUrl'] + self.rule_data['BackendPort'][config.COUNTRY] + self.rule_data['update_rule']['path'],
            update_header, [update_payload], update_rule_id)
        self.verify_publish_rule(
            self.rule_data['BaseUrl'] + self.rule_data['FrontendPort'] + self.rule_data['publish_rule']['path'],
            update_header, update_rule_id)

        utils.log("1.verify rule_id={} record [rule_description] updated in table {}_rule".format(update_rule_id, table_prefix))
        query_rule = "select * from {}_rule where rule_id={}".format(table_prefix, update_rule_id)

        rule_record = self.risk_conn.fetchone(query_rule)
        utils.log(rule_record)
        self.assertEqual(new_desc, rule_record['rule_description'], "rule record not update value:{}! please check".format(new_desc))

        utils.log("2.verify rule_id={} record [rule_description],[snapshot_version] updated in table {}_rule_operation".format(update_rule_id, table_prefix))
        query_rule_operation = "select * from {}_rule_operation where rule_description='{}'".format(table_prefix, new_desc)
        rule_operation_record = self.risk_conn.fetchone(query_rule_operation)
        utils.log(rule_operation_record)
        self.assertEqual(update_rule_id, rule_operation_record['rule_id'],
                         "rule not updated for rule_id={} in {}_rule_operation!".format(update_rule_id, table_prefix))

        utils.log("3.verify rule_id={} record [rule_description],[snapshot_version] updated in table {}_rule_snapshot".format(update_rule_id, table_prefix))
        query_rule_snapshot = "select * from {}_rule_snapshot where rule_id={} and snapshot_version='{}'".format(table_prefix, update_rule_id, rule_operation_record['snapshot_version'])
        rule_snapshot_record = self.risk_conn.fetchall(query_rule_snapshot)
        utils.log(rule_snapshot_record)
        self.assertTrue(len(rule_snapshot_record) == 1,
                        "there should only 1 record in table {}_rule_snapshot for this query!".format(table_prefix))
        self.assertEqual(new_desc, rule_snapshot_record[0]['rule_description'],
                         "rule not update in {}_rule_snapshot!".format(table_prefix))
        self.assertTrue(rule_record['rule_valid'] == rule_snapshot_record[0]['rule_valid'] and
                        rule_record['api_service'] == rule_snapshot_record[0]['api_service'],
                        'field [rule_valid] and [api_service] are same between {}_rule and {}_rule_snapshot'.format(table_prefix, table_prefix))

    def verify_update_rule(self, url, header, payload, update_rule_id):
        header.update({'Region': config.COUNTRY})
        update_resp = self.update_rule_api(url, header, payload)
        utils.log("verify update rule successfully.")
        self.assertEqual(utils.query_json(json.loads(update_resp.text), 'msg'),
                         'success', 'update rule_id={} rule failed!'.format(update_rule_id))

    def verify_publish_rule(self, url, header, update_rule_id):
        header.update({'Region': config.COUNTRY})
        publish_resp = self.publish_rule_api(url, header)
        utils.log("verify publish rule successfully.")
        self.assertEqual(utils.query_json(json.loads(publish_resp.text), 'msg'), 'success',
                         'publish rule_id={} rule failed!'.format(update_rule_id))

    def verify_search_rule_api_and_check(self, group_params, check_count=False):
        headers = self.rule_data['search']['header']
        headers.update({'Region': config.COUNTRY})
        search_resp = self.rule_search_api(
            self.rule_data['BaseUrl'] + self.rule_data['BackendPort'][config.COUNTRY] + self.rule_data['search']['path'],
            headers,
            group_params)
        search_resp_result = json.loads(search_resp.text)
        utils.log('1.verify call rule manage search RuleGroup api success.')
        self.assertEqual(utils.query_json(search_resp_result, 'msg'), 'success', 'rule manage search rule failed!')
        web_search_total = utils.query_json(search_resp_result, 'data.total')
        if check_count:
            utils.log('verify search RuleGroup:[{}] and RuleId:[{}] success. got rule count:[{}]'.format(group_params.get('groups'), group_params.get('ruleId'), web_search_total))
            self.assertTrue(web_search_total == 1 or web_search_total == 0, 'search rule via given RuleGroup and RuleId failed!')
        return search_resp_result

    def verify_search_rule_group_consistence_web_db(self, group_params):
        search_resp_result = self.verify_search_rule_api_and_check(group_params)
        web_search_total = utils.query_json(search_resp_result, 'data.total')

        sql_query_cnt_in_grp = "select count(rule_id) as count from {}risk_rule_group_relation where group_id in ({});" \
            .format(self.tb_prefix, group_params['groups'])
        db_search_grp_count = self.risk_conn.fetchone(sql_query_cnt_in_grp).get('count')
        utils.log('2.verify search RuleGroup count in db >= Rule Manage search api get count. '
                  'there maybe still exist invalid rule  in RuleGroup, and api will filter those item.')
        if db_search_grp_count > web_search_total:
            utils.log('search rules count via RuleGroup in db:[{}] bigger than web api:[{}], check extra rules invalid in risk_rule.'.format(db_search_grp_count, web_search_total))
            web_rule_list = utils.query_json(search_resp_result, 'data.list')
            utils.log('get ruleId list from search RuleGroup response.')
            web_rule_set = {rule.get('ruleId') for rule in web_rule_list}
            sql_query_rules_in_grp = "select rule_id from {}risk_rule_group_relation where group_id in ({});".format(
                self.tb_prefix, group_params['groups'])
            db_search_all = self.risk_conn.fetchall(sql_query_rules_in_grp)
            db_rules_set = {rule.get('rule_id') for rule in db_search_all}
            extra_rule = db_rules_set - web_rule_set  # db里比页面规则组查询额外多出的rules，应该是无效的，即已在rule表删除
            # self.risk_conn.connection.string_literal(tuple(extra_rule))
            if len(extra_rule) == 0: return utils.log('the extra rules in db is duplicate. ignore them.')
            sql_rule_not_exist = "select count(1) as count from {}risk_rule where rule_id in ({});".format(
                self.tb_prefix, ','.join(str(x) for x in extra_rule))
            utils.log('verify those extra rules:{} are invalid, Not exist in risk_rule table.'.format(extra_rule))
            self.assertEqual(self.risk_conn.fetchone(sql_rule_not_exist).get('count'), 0, 'rules:{} still exist in rule table!'.format(extra_rule))
        else:
            utils.log('verify db search rule count:[{}] and web search rule count:[{}] via RuleGroup should equal.'.format(db_search_grp_count, web_search_total))
            self.assertTrue(db_search_grp_count == web_search_total,
                            'RuleGroup searched rule count mismatch between database and rule manage search api!')

    def verify_search_rule_id_consistence_web_db(self, group_params, resp_result):
        web_search_total = utils.query_json(resp_result, 'data.total')
        sql = "select count(1) as cnt from {}risk_rule_group_relation where group_id={} and rule_id={};".format(
            self.tb_prefix, group_params.get('groups'), group_params.get('ruleId'))
        db_count = self.risk_conn.fetchone(sql).get('cnt')
        utils.log('2.verify rule count is consistence between search RuleGroup,RuleID api:[{}] and db:[{}]'.format(web_search_total, db_count))
        self.assertEqual(web_search_total, db_count, 'rule count is diff search via RuleGroup,RuleID api and db!')

    @unittest.skip("test")
    def test_rule_ui(self):
        self.driver = getdriver.getdriver(config.DRIVER_TYPE)
        self.driver.maximize_window()
        self.loginPage = login.LoginPage(self.driver)
        rule_mgr_url = "http://52.80.187.221:30367/#/"
        self.loginPage.login(config.TEST_USR1, config.TEST_PWD1, url=rule_mgr_url)
        self.loginPage.switch_country(constants.US)

        self.dgv = datagridview.DataGridView(self.driver)
        self.dgv.click_action_in_row(constants.VIEW, constants.RulId, "-3")
        utils.log("done")

    @classmethod
    def login_api(cls, url, header, payload):
        utils.log(">>login rule manager...")
        login_response = cls.req.post(url, headers=header, json=payload)
        utils.log("response is: {}".format(login_response.text))
        return login_response

    def rule_search_api(self, url, header, params):
        utils.log(">>search rule...")
        rule_list_resp = self.req.get(url, headers=header, params=params)
        utils.log(json.loads(rule_list_resp.text)['msg'])
        return rule_list_resp

    def get_rule_api(self, url, header):
        utils.log(">>get rule...")
        get_update_rule_info = self.req.get(url, headers=header)
        update_rule_info = json.loads(get_update_rule_info.text)['data']
        utils.log(update_rule_info)

    def update_rule_api(self, url, header, payload: list):
        utils.log(">>update rule...")
        update_rule_result = self.req.post(url, headers=header, json=payload)
        utils.debug(update_rule_result.text)
        return update_rule_result

    def publish_rule_api(self, url, header):
        utils.log(">>publish rule...")
        publish_result = self.req.post(url, headers=header)
        time.sleep(0.5)
        utils.debug(json.loads(publish_result.text)['data'])
        return publish_result
