from config import constants, config
from testcases import requestbase
from utils import utils, requestlib, redashlib

import unittest
import json

@unittest.skip('')
class TestProdTags(requestbase.RequestBase):
    crm_data = utils.load_yml("crm_people_library_prod.yaml")

    @classmethod
    def setUpClass(cls):
        utils.log("==================================================================")
        utils.log("=                                                                =")
        utils.log("===============           TEST CLASS SETUP               =========")
        utils.log("==================================================================")
        utils.log("Set up test class...")
        cls.req = requestlib.RequestLib(silence=True)
        cls.indices_size = cls.get_indices_count(config.COUNTRY)
        cls.reds = redashlib.Redash()
        utils.log("==================================================================\n\n")

    @classmethod
    def get_kibana_url(cls, region, query_type='_search'):
        """
        get kibana url via region and type.
        :param region: PH, US, CN
        :param query_type: eg: _search, _stats
        :return: kibana url
        """
        utils.log('get [{}] kibana [{}] url.'.format(region, query_type))
        if region == constants.US:
            url = cls.crm_data['ElasticSearch']['prod_host'] + cls.crm_data['ElasticSearch']['prod_ph'+query_type]
        elif region == constants.JP:
            url = cls.crm_data['ElasticSearch']['prod_host'] + cls.crm_data['ElasticSearch']['prod_id'+query_type]
        else:
            url = cls.crm_data['ElasticSearch']['prod_host'] + cls.crm_data['ElasticSearch']['prod_vn'+query_type]
        utils.log('kibana search url:{}'.format(url))
        return url

    @classmethod
    def kibana_search(cls, es_query):
        utils.log('kibana query:\n{}'.format(es_query))
        return cls.req.post(cls.get_kibana_url(config.COUNTRY), headers=cls.crm_data['ElasticSearch']['prod_headers'], json=es_query)

    @classmethod
    def get_indices_count(cls, region):
        resp = cls.req.post(cls.get_kibana_url(region, query_type='_stats'), headers=cls.crm_data['ElasticSearch']['prod_headers'])
        count = json.loads(resp.text)['_all']['primaries']['docs']['count']
        utils.log("kibana indices total count is: {}".format(count))
        return count

    def verify_prod_wide_es_equal_for_specify_value(self, field_name, check_value):
        wide_sql = self.crm_data['TagValuesUpdate']['wide'][constants.US][field_name].format(check_value)
        es_query = self.crm_data['TagValuesUpdate']['kibana'][constants.US][field_name] % check_value
        wide_count = self.reds.get_query_results_count(wide_sql)
        resp = self.kibana_search(json.loads(es_query))
        kibana_count = json.loads(resp.text)['hits']['total']
        utils.log("verify field [{}]=[{}] count equals between wide and Kibana for product env.".format(field_name, check_value))
        utils.log("wide count: {}, kibana count: {}".format(wide_count, kibana_count))
        self.assertEqual(wide_count, kibana_count, "field [{}] value [{}] count in wide not consistance with kibana!".format(field_name, check_value))

    def verify_tag_value_updates(self, field):
        values_list = self.crm_data['TagValuesUpdate']['checkValues'][constants.US][field]
        for value in values_list:
            with self.subTest(check_tag_value=value):
                self.verify_prod_wide_es_equal_for_specify_value(field, value)

    def test_wide_kibana_total_equals(self):
        """验证宽表和Kibana Indices数据总量相同"""
        utils.log('verify user_tag_wide and kibana indices total count equal.')
        prod_wide_total = self.reds.get_query_results_count(self.crm_data['Wide'][config.COUNTRY]['totalSize'])
        utils.log("Total count for user_tag_wide:{}, kibana:{}".format(prod_wide_total, self.indices_size))
        self.assertEqual(prod_wide_total, self.indices_size, 'user_tag_wide and kibana total count Not equal!')

    @unittest.skipUnless(config.COUNTRY == constants.US, 'only for US')
    def test_first_application_loantype_update(self):
        """验证标签first_application_loantype值更新正确,wide及Kibana数据一致"""
        self.verify_tag_value_updates('first_application_loantype')

    @unittest.skipUnless(config.COUNTRY == constants.US, 'only for US')
    def test_second_approved_loantype_update(self):
        """验证标签second_approved_loantype值更新正确,wide及Kibana数据一致"""
        self.verify_tag_value_updates('second_approved_loantype')

    @unittest.skipUnless(config.COUNTRY == constants.US, 'only for US')
    def test_first_approved_loantype_update(self):
        """验证标签first_approved_loantype值更新正确,wide及Kibana数据一致"""
        self.verify_tag_value_updates('first_approved_loantype')

