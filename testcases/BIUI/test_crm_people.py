from testcases import requestbase
from utils import utils, requestlib
from config import config

import unittest
import json

from testdata.ApiJson import select_people_complex_search


class TestPeople(requestbase.RequestBase):
    crm_data = utils.load_yml("crm_people_library.yaml")
    resource = utils.load_yml("resources.yaml")
    desc_prefix = "autoTest"
    desc_complex_prefix = "autoTestComplex"

    @classmethod
    def setUpClass(cls):
        utils.log("==================================================================")
        utils.log("=                                                                =")
        utils.log("===============           TEST CLASS SETUP               =========")
        utils.log("==================================================================")
        utils.log("Set up test class...")
        cls.req = requestlib.RequestLib()
        cls.login_api(cls.req)
        cls.crm_db_conn = utils.get_db_connector(cls.resource['Mysql']['RiskDB']['db']['crm_db'])
        utils.log("==================================================================\n\n")

    @staticmethod
    def login_api(req):
        utils.log("call login crm api...")
        resp = req.post(config.QA_SERVER + TestPeople.crm_data['CRM']['login']['path'],
                        headers=TestPeople.crm_data['CRM']['header'],
                        json=TestPeople.crm_data['CRM']['login']['payload'])
        utils.log(resp.text)
        return resp

    def add_people_lib_task(self, people_lib_id):
        """
        设置人库开始结束时间， 添加定时任务
        """
        utils.log("1.提交后通知选人平台人库开始时间，结束时间")
        people_lib_query = self.crm_data['CRM']['peopleLibrary']['query'].format(
            # self.crm_data['CRM']['peopleLibrary']['people_lib_id'],
            people_lib_id,
            self.crm_data['CRM']['peopleLibrary']['start_time'],
            self.crm_data['CRM']['peopleLibrary']['end_time'],
            self.crm_data['CRM']['peopleLibrary']['cron'])
        people_lib_url = self.crm_data['CRM']['baseUrl'] + self.crm_data['CRM']['peopleLibrary']['path'] + people_lib_query
        headers = self.crm_data['CRM']['header']
        headers["Authorization"] = self.crm_data['CRM']['peopleLibrary']['authorization']
        people_lib_resp = self.req.post(people_lib_url, headers=headers)
        utils.log(people_lib_resp.text)

        utils.log("2.人库添加任务")
        people_lib_task_query = self.crm_data['CRM']['peopleLibraryTask']['query'].format(
            # self.crm_data['CRM']['peopleLibrary']['people_lib_id'],
            people_lib_id,
            self.crm_data['CRM']['peopleLibraryTask']['cron'])
        people_lib_task_url = self.crm_data['CRM']['baseUrl'] + self.crm_data['CRM']['peopleLibraryTask']['path'] + people_lib_task_query
        headers["Authorization"] = self.crm_data['CRM']['peopleLibraryTask']['authorization']
        people_lib_task_resp = self.req.post(people_lib_task_url, headers=headers)
        utils.log(people_lib_task_resp.text)

    def search_people_api(self, payload):
        utils.log("call search people api...")
        search_url = config.QA_SERVER + self.crm_data['CRM']['search']['path']
        headers = self.crm_data['CRM']['search']['header']

        label_payload = {'labelListJson': payload}

        search_resp = self.req.post(search_url, headers=headers, json=label_payload)

        self.assertMsg(search_resp)
        resp_dict = self.turn2dict(search_resp)
        utils.log(
            "dataCount:{}, selectCount:{}".format(resp_dict['data']['dataCount'], resp_dict['data']['selectCount']))
        return search_resp, resp_dict['data']['selectCount']

    def save_people_api(self, payload, control_group, select_count, is_complex=False):
        """
        save people api
        :param payload:
        :param control_group:
        :param select_count: the select count in search api
        :param is_complex: is select people complex
        :return:
        """
        utils.log("call create people library api...")
        # construct save payload
        if not isinstance(select_count, int):
            select_count = int(select_count)
        grp1_ratio = utils.get_random_numb(55, 100) + 0.23*utils.get_random_numb(1, 10)  # The sum of Radio should be 100
        grp2_ratio = 100 - grp1_ratio
        grp1_user_count = round(select_count * grp1_ratio * 0.01)  # 四舍五入取整
        grp2_user_count = round(select_count * grp2_ratio * 0.01)  # 四舍五入取整

        if is_complex:
            url = config.QA_SERVER + self.crm_data['CRM']['saveComplex']['path']
            header = self.crm_data['CRM']['saveComplex']['header']
            response_keyword = 'result'
            control_grp = json.loads(control_group % (grp1_ratio, grp1_user_count, grp2_ratio, grp2_user_count))
            control_grp_json = {"crmControlGroupReqList": control_grp}
            desc = self.desc_complex_prefix + utils.get_time_stamp()
        else:
            url = config.QA_SERVER + self.crm_data['CRM']['save']['path']
            header = self.crm_data['CRM']['save']['header']
            response_keyword = 'data'
            control_grp = control_group % (grp1_ratio, grp1_user_count, grp2_ratio, grp2_user_count)
            control_grp_json = {"controlGroupJson": control_grp}
            desc = self.desc_prefix + utils.get_time_stamp()

        people_library_desc = {'peopleLibraryDesc': desc}
        payload.update(people_library_desc)
        payload.update(control_grp_json)

        save_resp = self.req.post(url, headers=header, json=payload)
        self.assertMsg(save_resp)
        created_people_library_id = self.turn2dict(save_resp)[response_keyword]
        utils.log("Create Successfully, The ID of People Library is: {}".format(created_people_library_id))
        return save_resp, created_people_library_id

    def delete_people_library_api(self, people_library_id):
        """
        Not really delete in db, just set it's field [state] to 9, means delete
        :param people_library_id:
        """
        utils.log("delete people library for ID: {}".format(people_library_id))
        url = config.QA_SERVER + self.crm_data['CRM']['delete']['path'] + str(people_library_id)
        header = self.crm_data['CRM']['delete']['header']
        resp = self.req.put(url=url, headers=header)
        self.assertMsg(resp)

    @unittest.skip("")
    def test_select_save_people(self):
        """
        select people and save people library
        """
        utils.log("1. Call search people api.")
        utils.log("Select people: gender= Male, birthday<=2006-10-03, marita status in ('Single','Married'), "
                  "last application status not in (Failure, Rejected),last login date >current_date-20")

        # search_save_payload = self.crm_data['CRM']['search']['payload1']
        search_save_payload = self.crm_data['CRM']['search']['payload2']
        search_resp, select_count = self.search_people_api(search_save_payload)
        self.assertGreater(int(select_count), 0, "Select People Failed!!! The count less than 0")

        utils.log("2. Save searched people library.")
        save_resp, people_lib_id = self.save_people_api(
            {"labelListJson": search_save_payload},
            self.crm_data['CRM']['save']['controlGroupJson'],
            int(select_count))
        self.assertGreater(int(people_lib_id), 1, "Save People Library Failed!!!")

        utils.log("3. Verify new save people library exist in db.")
        self.verify_people_lib_id_in_db(people_lib_id, self.desc_prefix)

        utils.log("4. Add people library task.")
        self.add_people_lib_task(people_lib_id)

    def search_people_complex_api(self, payload):
        utils.log("call search people complex api...")
        search_complex_url = config.QA_SERVER + self.crm_data['CRM']['searchComplex']['path']
        headers = self.crm_data['CRM']['searchComplex']['header']

        search_resp = self.req.post(search_complex_url, headers=headers, json=payload)

        self.assertMsg(search_resp)
        resp_dict = self.turn2dict(search_resp)
        utils.log(
            "dataCount:{}, selectCount:{}".format(resp_dict['result']['dataCount'], resp_dict['result']['selectCount']))
        return search_resp, resp_dict['result']['selectCount']

    def verify_people_lib_id_in_db(self, people_lib_id, people_lib_desc):
        query_sql = "select * from crm_people_library where id in({})".format(people_lib_id)
        people_lib_record = self.crm_db_conn.fetchone(query_sql)
        utils.log("got people library record from db as below:\n{}".format(people_lib_record))
        self.assertTrue(people_lib_desc in people_lib_record['people_library_desc'], "Not find new saved people library in crm db!")

    def test_search_complex_save_people(self):
        utils.log("1. Call search complex people api.")
        search_complex_payload = select_people_complex_search.get_select_people_complex_payload(
            self.crm_data['CRM']['selectPeopleComplex'][config.COUNTRY],
            ['monthlyIncome', 'marryStatus', 'deviceOfFirstApply', 'lastLoginDate'],
            ['latestRiskScore', 'installDate'])
        search_resp, select_count = self.search_people_complex_api(search_complex_payload)
        utils.log("2. Save searched people library.")
        save_resp, people_lib_id = self.save_people_api(search_complex_payload, self.crm_data['CRM']['saveComplex']['controlGroupJson'], int(select_count), True)
        self.assertGreater(int(people_lib_id), 1, "Save People Library Failed!!!")
        utils.log("3. Verify new save people library exist in db.")
        self.verify_people_lib_id_in_db(people_lib_id, self.desc_complex_prefix)
        utils.log("4. Add people library task.")
        self.add_people_lib_task(people_lib_id)





