from config import constants, config
from testcases import requestbase
from utils import utils, requestlib, redashlib

import unittest
import json


class TestCRMTag(requestbase.RequestBase):
    crm_data = utils.load_yml("crm_people_library.yaml")
    resource = utils.load_yml("resources.yaml")

    partition_0 = utils.get_time_stamp('%Y%m%d')

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
    def get_es_url(cls, region, query_type='_search'):
        """
        get ElasticSearch url via region and type.
        :param region: US, JP, CN
        :param query_type: eg: _search, _stats
        :return: ES url
        """
        utils.log('get [{}] ElasticSearch [{}] url.'.format(region, query_type))
        if region == constants.US:
            url = cls.crm_data['ElasticSearch']['host'] + cls.crm_data['ElasticSearch']['ph'+query_type]  # Philippine
        elif region == constants.JP:
            url = cls.crm_data['ElasticSearch']['host'] + cls.crm_data['ElasticSearch']['id'+query_type]  # Indonesia
        else:
            url = cls.crm_data['ElasticSearch']['host'] + cls.crm_data['ElasticSearch']['vn'+query_type]  # Vietnam
        utils.log('es search url:{}'.format(url))
        return url

    @classmethod
    def es_search(cls, es_query):
        utils.log('es query:\n{}'.format(es_query))
        return cls.req.post(
            cls.get_es_url(config.COUNTRY),
            headers=cls.crm_data['ElasticSearch']['headers'],
            data=es_query.encode('utf-8'))

    @classmethod
    def get_indices_count(cls, region):
        resp = cls.req.get(cls.get_es_url(region, query_type='_stats'), headers=cls.crm_data['ElasticSearch']['headers'])
        count = json.loads(resp.text)['_all']['primaries']['docs']['count']
        utils.log("indices total count is: {}".format(count))
        return count

    def verify_tag_in_es(self, tag_name, query):
        """
        快速验证Tag在ES里按条件查询出来的records数量在正常范围，即0<count<整个indices size。
        等于0或等于整个indices size，大概率数据异常。
        """
        utils.log("Test tag [{}] from ElasticSearch. Make sure there are records matched.".format(tag_name))
        resp = self.es_search(query)
        hit_total = json.loads(resp.text)['hits']['total']
        utils.log("got hits total:{}".format(hit_total))
        utils.log("Verify get records count, 0<count<{}(total indices count)".format(self.indices_size))
        self.assertTrue(0 < hit_total < self.indices_size,
                        "Not find any records or equal indices count in ES for current query, please check!")

    def verify_wide_es_equal(self, tag, wide_sql, es_query):
        """
        compare user_tag_wide and ES data count should equal for tag.
        """
        redash_count = self.reds.get_query_results_count(wide_sql)
        resp = self.es_search(es_query)
        es_count = json.loads(resp.text)['hits']['total']
        utils.log('verify Redash and ES query count for tag [{}] should equal.'.format(tag))
        utils.log("got redash count:{}, es count:{}".format(redash_count, es_count))
        self.assertEqual(redash_count, es_count, 'The Redash and ES query count Not Equal!')

    def verify_src_bigger_than_ext(self, src_table, backup_table, partition_0=partition_0, diff_size=2000, extra=None):
        sql1 = 'select count(*) from {}'.format(src_table)
        if extra:
            sql2 = 'select count(*) from {} where partition_0={} {}'.format(backup_table, partition_0, extra)
        else:
            sql2 = 'select count(*) from {} where partition_0={}'.format(backup_table, partition_0)
        src_result = self.reds.query_results(sql1)[0].get('count')
        back_result = self.reds.query_results(sql2)[0].get('count')
        utils.log("verify src table [{}] record count bigger than backup ext table [{}] and the count is close.".format(
            src_table, backup_table))
        utils.log("src count:{}, backup ext count:{}".format(src_result, back_result))
        self.assertTrue(
            0 <= src_result - back_result < diff_size,
            "source table count should bigger than backup ext table count! And their count should be close!")

    def verify_storage_wide_consistent(self, tag, storage_sql, wide_sql):
        if config.IS_PROD_STORAGE:
            storage_sql = storage_sql.replace("crmtest_ext", "crm_ext")
        storage_result = self.reds.get_query_results_count(storage_sql)
        wide_result = self.reds.get_query_results_count(wide_sql)
        utils.log('verify for tag:[{}], user_tag_storage and user_tag_wide Not Null count should Equal.'.format(tag))
        self.assertEqual(storage_result, wide_result,
                         'user_tag_storage and user_tag_wide for tag:[{}] not null count Not Equal!'.format(tag))

    @unittest.skipUnless(config.COUNTRY == constants.CN, 'case only for Vietnam')
    def test_vn_storage_wide_total_consistent(self):
        """验证窄表与宽表数据总量一致"""
        utils.log("verify user_tag_storage and user_tag_wide total count equals")
        self.verify_storage_wide_consistent(
            '',
            "select count(1) from vncrmtest_ext.user_tag_storage where tag_id='accountname'",
            "select count(1) from vncrmtest_ext.user_tag_wide")

    @unittest.skipUnless(config.COUNTRY == constants.CN, 'case only for Vietnam')
    def test_vn_storage_wide_consistent(self):
        """验证窄表和宽表各个Tag的Not Null数据一致."""
        storage_query_list = self.crm_data['StorageWideQuery']['Storage'][constants.CN]
        wide_query_list = self.crm_data['StorageWideQuery']['Wide'][constants.CN]
        for sq, wq in zip(storage_query_list, wide_query_list):
            with self.subTest(storage_query=sq, wide_query=wq):
                self.verify_storage_wide_consistent(next(iter(sq.keys())), next(iter(sq.values())),
                                                    next(iter(wq.values())))

    @unittest.skipUnless(config.COUNTRY == constants.CN, 'case only for Vietnam')
    def test_vn_wide_es_total_count_equal(self):
        """验证宽表和ES Indices:vn_crm_user_profile_alias数据总量相同"""
        utils.log('verify vncrmtest_ext.user_tag_wide and es indices:vn_crm_user_profile_alias total count equal.')
        wide_total = self.reds.get_query_results_count('select count(1) from vncrmtest_ext.user_tag_wide')
        self.assertEqual(wide_total, self.indices_size, 'user_tag_wide and es total count Not equal!')

    @unittest.skipUnless(config.COUNTRY == constants.CN, 'case only for Vietnam')
    def test_vietnam_wide_es_consistent(self):
        """验证宽表和ES里各个Tag数据一致"""
        wide_sql = self.crm_data['UserTagWide'][constants.CN]
        es_query = self.crm_data['ESQuery'][constants.CN]
        for wq, eq in zip(wide_sql, es_query):
            with self.subTest(wide_query=wq, es_query=eq):
                self.verify_wide_es_equal(next(iter(wq.keys())), next(iter(wq.values())), next(iter(eq.values())))

    def test_tag_in_es(self):
        """验证tag在ES里按条件查询出的数量是正常的(0<count<total_count)"""
        tag_query_list, skip_list = self.crm_data['ESQuery'][config.COUNTRY], self.crm_data['ESQuerySkip'][config.COUNTRY]
        final_query_list = [item for item in tag_query_list if next(iter(item.keys())) not in skip_list]
        for query in final_query_list:
            with self.subTest(query=query):
                self.verify_tag_in_es(next(iter(query.keys())), next(iter(query.values())))

    @unittest.skipUnless(config.COUNTRY == constants.CN, 'case only for Vietnam')
    def test_vnods_persons_and_ext(self):
        """验证原始表和它的备份表ext，备份表数据总量应小于原始表，且相差不大(默认相差阀值：2000)"""
        extra_condition = "and createdat !='' and updatedat !='' and mobile is not null and residentialdistrictaddress is not null"
        self.verify_src_bigger_than_ext('vnods.persons', 'vnods_ext.persons', extra=extra_condition)

    def get_es_data_details_list(self, query):
        """get es data details record data list"""
        detail_result_list = []
        resp = self.es_search(query)
        hits_list = json.loads(resp.text)['hits']['hits']
        for hit in hits_list:
            detail_result_list.append(hit['_source'])
        return detail_result_list

    def verify_es_details_with_src(self, es_check_list, src_check_list, es_data_list, src_query, partition_0=None):
        if len(es_check_list) != len(src_check_list):
            return utils.warn("please make sure the src and es compare fields number equal!")
        es_data = es_data_list if len(es_data_list) <= 3 else es_data_list[0:3]
        for num, es in enumerate(es_data, start=1):
            es_actual, src_expect = [], []
            utils.log("check record #{}".format(num))
            if partition_0:
                src = self.reds.query_results(src_query.format(es['accountid'], partition_0))[0]
            else:
                src = self.reds.query_results(src_query.format(es['accountid']))[0]
            for es_col, src_col in zip(es_check_list, src_check_list):
                es_actual.append(str(es[es_col]) if es[es_col] is not None else es[es_col])
                src_expect.append(str(src[src_col]) if src[src_col] is not None else src[src_col])
            utils.log("verify es and src [{}] data matched for below fields.\n{}".format(src_query.split(' ')[3], es_check_list))
            self.assertListEqual(src_expect, es_actual, 'Not Match between es and src data!')

    @unittest.skipUnless(config.COUNTRY == constants.CN, 'case only for Vietnam')
    def test_vn_es_data_consistence_with_account(self):
        """验证ES数据内容与源表account一致"""
        utils.log("verify es details data is consistence with source account.")
        self.verify_es_details_with_src(self.crm_data['ESSrcDetail']['Check'][constants.CN]['es_account'],
                                        self.crm_data['ESSrcDetail']['Check'][constants.CN]['account'],
                                        self.get_es_data_details_list(self.crm_data['ESSrcDetail']['ES'][constants.CN]['query']),
                                        self.crm_data['ESSrcDetail']['Src'][constants.CN]['account'])

    @unittest.skipUnless(config.COUNTRY == constants.CN, 'case only for Vietnam')
    def test_vn_es_data_consistence_with_person(self):
        """验证ES数据内容与源表person一致"""
        utils.log("verify es details data is consistence with source person.")
        self.verify_es_details_with_src(self.crm_data['ESSrcDetail']['Check'][constants.CN]['person'],
                                        self.crm_data['ESSrcDetail']['Check'][constants.CN]['person'],
                                        self.get_es_data_details_list(self.crm_data['ESSrcDetail']['ES'][constants.CN]['query']),
                                        self.crm_data['ESSrcDetail']['Src'][constants.CN]['person'])

    @unittest.skipUnless(config.COUNTRY == constants.CN, 'case only for Vietnam')
    def test_vn_es_data_consistence_with_work(self):
        """验证ES数据内容与源表work一致"""
        utils.log("verify es details data is consistence with source work.")
        self.verify_es_details_with_src(self.crm_data['ESSrcDetail']['Check'][constants.CN]['es_work'],
                                        self.crm_data['ESSrcDetail']['Check'][constants.CN]['work'],
                                        self.get_es_data_details_list(self.crm_data['ESSrcDetail']['ES'][constants.CN]['workQuery']),
                                        self.crm_data['ESSrcDetail']['Src'][constants.CN]['work'])

    def verify_es_location_with_src(self, es_data_list, src_query):
        es_data = es_data_list if len(es_data_list) <= 3 else es_data_list[0:3]
        for num, es in enumerate(es_data, start=1):
            utils.log("check record #{}".format(num))
            src = self.reds.query_results(src_query.format(es['accountid'], self.partition_0))[0]
            src_location = ','.join(str(i) for i in [src['residential_latitude'], src['residential_longitude']])
            utils.log("verify es [location] data is matched src construct str 'residential_latitude,residential_longitude'.")
            self.assertEqual(src_location, es['location'], 'Not Match between es and src data!')

    @unittest.skipUnless(config.COUNTRY == constants.US, 'case only for US')
    def test_ph_es_geo_consistence_with_user_addr_gps(self):
        """验证ES经纬度与源表crm_ext.user_addr_gps一致"""
        utils.log("verify es residential_latitude, residential_longitude data is consistence with source user_addr_gps")
        self.verify_es_details_with_src(self.crm_data['ESSrcDetail']['Check'][constants.US]['geo'],
                                        self.crm_data['ESSrcDetail']['Check'][constants.US]['geo'],
                                        self.get_es_data_details_list(
                                            self.crm_data['ESSrcDetail']['ES'][constants.US]['query']),
                                        self.crm_data['ESSrcDetail']['Src'][constants.US]['gps'], self.partition_0)

    @unittest.skipUnless(config.COUNTRY == constants.US, 'case only for US')
    def test_ph_es_location_consistence_with_user_addr_gps(self):
        """验证ES location与源表crm_ext.user_addr_gps数据一致"""
        self.verify_es_location_with_src(
            self.get_es_data_details_list(self.crm_data['ESSrcDetail']['ES'][constants.US]['query']),
            self.crm_data['ESSrcDetail']['Src'][constants.US]['gps'])

    @unittest.skipUnless(config.COUNTRY == constants.US, 'case only for US')
    def test_ph_storage_wide_total_consistent(self):
        """验证窄表与宽表数据总量一致"""
        utils.log("verify US user_tag_storage and user_tag_wide total count equals")
        self.verify_storage_wide_consistent(
            '',
            "select count(1) from crmtest_ext.user_tag_storage where tag_id='accountname'",
            "select count(1) from crmtest_ext.user_tag_wide")

    @unittest.skipUnless(config.COUNTRY == constants.US, 'case only for US')
    def test_ph_storage_wide_consistent(self):
        """验证窄表和宽表各个Tag的Not Null数据一致."""
        storage_query_list = self.crm_data['StorageWideQuery']['Storage'][constants.US]
        wide_query_list = self.crm_data['StorageWideQuery']['Wide'][constants.US]
        for sq, wq in zip(storage_query_list, wide_query_list):
            with self.subTest(storage_query=sq, wide_query=wq):
                self.verify_storage_wide_consistent(next(iter(sq.keys())), next(iter(sq.values())),
                                                    next(iter(wq.values())))

    @unittest.skipUnless(config.COUNTRY == constants.US, 'case only for US')
    def test_ph_wide_es_total_count_equal(self):
        """验证宽表和ES Indices:crm_user_profile_alias数据总量相同"""
        utils.log('verify crmtest_ext.user_tag_wide and es indices:crm_user_profile_alias total count equal.')
        wide_total = self.reds.get_query_results_count('select count(1) from crmtest_ext.user_tag_wide')
        self.assertEqual(wide_total, self.indices_size, 'user_tag_wide and es total count Not equal!')

    @unittest.skip('')
    def test_update_increment_new_tb_consistence_with_src(self):
        """验证tag数据增量更新,new表数据与源表一致"""
        utils.log('Test tables use incremental update works.')
        origin_query_list = self.crm_data['IncrementalUpdate']['originTb'][config.COUNTRY]
        new_query_list = self.crm_data['IncrementalUpdate']['newTb'][config.COUNTRY]
        ignore_items = self.crm_data['IncrementalUpdate']['ignoreItems'][0]
        for o, n in zip(origin_query_list, new_query_list):
            with self.subTest(origin_tb_query=o, new_tb_query=n):
                self.verify_incremental_update(next(iter(o.keys())), next(iter(n.keys())), next(iter(o.values())),
                                               next(iter(n.values())), ignore_items)

    def verify_incremental_update(self, origin_tb, new_tb, origin_query, new_query, ignore_items):
        is_diff = False
        added_list, modified_list = [], []
        for origin_record, new_record in zip(self.reds.query_results(origin_query), self.reds.query_results(new_query)):
            for ignore in ignore_items:
                origin_record.pop(ignore)
                new_record.pop(ignore)
            new_record.pop('updatedat')  # new add col in new table, ignore it
            added, modified = utils.dict_compare(origin_record, new_record)
            if added: added_list.append(added)
            if modified: modified_list.append(modified)
            if origin_record != new_record: is_diff = True
        utils.log('verify {} and {} data details is consistence.'.format(origin_tb, new_tb))
        if added_list: utils.log('new columns item found in {}:{}'.format(new_tb, added_list))
        if modified_list: utils.log('diff items details in two table:{}'.format(modified_list))
        self.assertFalse(is_diff, 'There are records diff between {} and {}!'.format(origin_tb, new_tb))

    def test_wide_tag_all_type_sum_equal_total(self):
        """验证宽表总量=tag value(not null+null+'')count之和"""
        wide_total = self.reds.get_query_results_count(self.crm_data['WideTotalQuery'][config.COUNTRY]['query'])
        not_null_query_list = self.crm_data['StorageWideQuery']['Wide'][config.COUNTRY]
        null_query_list = self.crm_data['WideNullEmpty'][config.COUNTRY]
        for notnq, nq in zip(not_null_query_list, null_query_list):
            with self.subTest(wide_not_null_query=notnq, wide_null_query=nq):
                not_null_count = self.reds.get_query_results_count(next(iter(notnq.values())))
                null_empty_count = self.reds.get_query_results_count(next(iter(nq.values())))
                utils.log("verify tag:[{}], it's value with (not null+null+'') count sum should equal wide total count".
                          format(next(iter(notnq.keys()))))
                utils.log("got tag {}, not null count:[{}], null+'' count:[{}], and wide total:[{}]".format(
                    next(iter(notnq.keys())), not_null_count, null_empty_count, wide_total))
                self.assertEqual(wide_total, (not_null_count+null_empty_count),
                                 "wide total count Not Equal tag value(not null+null+'') sum!")

    @unittest.skipUnless(config.COUNTRY == constants.US, 'case only for US')
    def test_ph_wide_es_consistent(self):
        """验证宽表和ES里各个Tag数据一致"""
        wide_sql = self.crm_data['UserTagWide'][constants.US]
        es_query = self.crm_data['ESQuery'][constants.US]
        for wq, eq in zip(wide_sql, es_query):
            with self.subTest(wide_query=wq, es_query=eq):
                self.verify_wide_es_equal(next(iter(wq.keys())), next(iter(wq.values())), next(iter(eq.values())))

    @unittest.skipUnless(config.COUNTRY == constants.JP, 'case only for JP')
    def test_id_storage_wide_consistent(self):
        """验证窄表和宽表各个Tag的Not Null数据一致."""
        storage_query_list = self.crm_data['StorageWideQuery']['Storage'][constants.JP]
        wide_query_list = self.crm_data['StorageWideQuery']['Wide'][constants.JP]
        for sq, wq in zip(storage_query_list, wide_query_list):
            with self.subTest(storage_query=sq, wide_query=wq):
                self.verify_storage_wide_consistent(next(iter(sq.keys())), next(iter(sq.values())),
                                                    next(iter(wq.values())))

    @unittest.skipUnless(config.COUNTRY == constants.JP, 'case only for JP')
    def test_id_wide_es_total_count_equal(self):
        """验证宽表和ES Indices:id_crm_user_profile_alias"""
        utils.log('verify crmtest_ext.user_tag_wide and es indices:id_crm_user_profile_alias total count equal.')
        wide_total = self.reds.get_query_results_count('select count(1) from idcrmtest_ext.user_tag_wide')
        self.assertEqual(wide_total, self.indices_size, 'user_tag_wide and es total count Not equal!')

    @unittest.skipUnless(config.COUNTRY == constants.JP, 'case only for JP')
    def test_id_wide_es_consistent(self):
        """验证宽表和ES里各个Tag数据一致"""
        wide_sql = self.crm_data['UserTagWide'][constants.JP]
        es_query = self.crm_data['ESQuery'][constants.JP]
        for wq, eq in zip(wide_sql, es_query):
            with self.subTest(wide_query=wq, es_query=eq):
                self.verify_wide_es_equal(next(iter(wq.keys())), next(iter(wq.values())), next(iter(eq.values())))

    @unittest.skipUnless(config.COUNTRY == constants.JP, 'case only for JP')
    def test_id_es_risk_score_consistence_with_src(self):
        """验证ES数据latest_risk_score与源表account_credits一致"""
        utils.log("verify es data latest_risk_score data is consistence with source account_credits.")
        self.verify_es_details_with_src(self.crm_data['ESSrcDetail']['Check'][constants.JP]['es_latest_risk_score'],
                                        self.crm_data['ESSrcDetail']['Check'][constants.JP]['score'],
                                        self.get_es_data_details_list(
                                            self.crm_data['ESSrcDetail']['ES'][constants.JP]['query']),
                                        self.crm_data['ESSrcDetail']['Src'][constants.JP]['account_credits'],
                                        self.partition_0)

    @unittest.skipUnless(config.COUNTRY == constants.JP, 'case only for JP')
    def test_id_es_salary_consistence_with_src(self):
        """验证ES数据monthly_income与源表account_credits一致"""
        utils.log("verify es data monthly_income data is consistence with source works.")
        self.verify_es_details_with_src(self.crm_data['ESSrcDetail']['Check'][constants.JP]['es_work'],
                                        self.crm_data['ESSrcDetail']['Check'][constants.JP]['work'],
                                        self.get_es_data_details_list(
                                            self.crm_data['ESSrcDetail']['ES'][constants.JP]['query']),
                                        self.crm_data['ESSrcDetail']['Src'][constants.JP]['work'])

    @unittest.skipUnless(config.COUNTRY == constants.JP, 'case only for JP')
    def test_id_storage_wide_total_consistent(self):
        """验证窄表与宽表数据总量一致"""
        utils.log("verify JP user_tag_storage and user_tag_wide total count equals")
        self.verify_storage_wide_consistent(
            '',
            "select count(1) from idcrmtest_ext.user_tag_storage where tag_id='accountname'",
            "select count(1) from idcrmtest_ext.user_tag_wide")

    def test_wide_union_query_sum_same_with_total(self):
        """验证宽表标签组合查询之和与总数一致"""
        wide_total_list = self.crm_data['WideUnionSeparate']['Total']
        wide_sep_sql1_list = self.crm_data['WideUnionSeparate']['Separate1']
        wide_sep_sql2_list = self.crm_data['WideUnionSeparate']['Separate2']
        for wtq, wsq1, wsq2 in zip(wide_total_list, wide_sep_sql1_list, wide_sep_sql2_list):
            with self.subTest(wide_total_query=wtq, wide_sep_query1=wsq1, wide_sep_query2=wsq2):
                self.verify_wide_union_query_sum_equal_total(next(iter(wtq.keys())), next(iter(wtq.values())),
                                                             next(iter(wsq1.values())), next(iter(wsq2.values())))

    def verify_wide_union_query_sum_equal_total(self, tag, wide_total, wide_sep_sql1, wide_sep_sql2):
        prefix = self.get_prefix()
        wide_total, wide_sep_sql1, wide_sep_sql2 = wide_total.format(prefix), wide_sep_sql1.format(prefix), wide_sep_sql2.format(prefix)
        wide_total_result = self.reds.get_query_results_count(wide_total)
        wide_sep1_result = self.reds.get_query_results_count(wide_sep_sql1)
        wide_sep2_result = self.reds.get_query_results_count(wide_sep_sql2)
        utils.log('verify for tag:[{}], user_tag_wide union query count sum should Equal total count.'.format(tag))
        self.assertEqual(wide_sep1_result+wide_sep2_result, wide_total_result,
                         'user_tag_wide union query count sum for tag:[{}] Not Equal with total count!'.format(tag))

    def test_wide_not_null_with_storage_null_2_zero(self):
        """验证窄表中把null值转为0的标签，宽表Not null=窄表null+not null"""
        wide_not_null_list = self.crm_data['WideStorageNullToZero']['WideNotNull']
        storage_not_null_list = self.crm_data['WideStorageNullToZero']['StorageNotNull']
        storage_null_list = self.crm_data['WideStorageNullToZero']['StorageNull']
        for wq, sq1, sq2 in zip(wide_not_null_list, storage_not_null_list, storage_null_list):
            with self.subTest(wide_not_null_query=wq, storage_not_null_query=sq1, storage_null_query=sq2):
                self.verify_wide_storage_null_to_0_consistent(next(iter(wq.keys())), next(iter(wq.values())),
                                                              next(iter(sq1.values())), next(iter(sq2.values())))

    def verify_wide_storage_null_to_0_consistent(self, tag, wide_not_null_sql, storage_not_null_sql, storage_null_sql):
        """窄表中把null值转为0， 宽表Not null=窄表null+not null"""
        prefix = self.get_prefix()
        wide_not_null_sql, storage_not_null_sql, storage_null_sql = wide_not_null_sql.format(prefix), storage_not_null_sql.format(prefix), storage_null_sql.format(prefix)
        if config.IS_PROD_STORAGE:
            storage_not_null_sql = storage_not_null_sql.replace("crmtest_ext", "crm_ext")
            storage_null_sql = storage_null_sql.replace("crmtest_ext", "crm_ext")
        wide_not_null_result = self.reds.get_query_results_count(wide_not_null_sql)
        storage_not_null_result = self.reds.get_query_results_count(storage_not_null_sql)
        storage_null_result = self.reds.get_query_results_count(storage_null_sql)
        utils.log('verify for tag:[{}], user_tag_wide not null count should Equal (storage not null + null) count.'.format(tag))
        self.assertEqual(wide_not_null_result, storage_not_null_result+storage_null_result,
                         'user_tag_wide tag[{}] not null count Not Equal (storage not null + null) count!'.format(tag))

    def get_prefix(self):
        prefix = ''
        if config.COUNTRY == constants.JP:
            prefix = 'id'
        elif config.COUNTRY == constants.CN:
            prefix = 'vn'
        return prefix
