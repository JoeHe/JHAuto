import time
import os
import pandas as pd

from utils import requestlib, utils
from config import config


class Redash:

    pd.set_option('display.max_rows', 4096)
    pd.set_option('display.max_columns', 4096)
    pd.set_option('display.width', 4096)

    def __init__(self, url=config.REDASH_HOST):
        utils.log("init redash client for host: {}".format(url))
        self.url = url
        self.header = {'Authorization': 'Key {}'.format(config.API_KEY)}
        self.req = requestlib.RequestLib(silence=True)

    def poll_job(self, job):
        utils.debug("redash poll job:[{}]".format(job))
        counter = 0
        while True:
            response = self.req.get(os.path.join(self.url, config.POLL_JOB, str(job['id'])), headers=self.header)
            if response.json()['job']['status'] in (3, 4):
                break
            elif counter > 80:
                break
            else:
                counter += 1
                time.sleep(2)
        if response.json()['job']['status'] == 3:
            return response.json()['job']['query_result_id']
        else:
            raise Exception(response.json()['job']['error'])

    def query_results(self, sql, ro_risk_idrisk=11, max_age=0):
        utils.log("redash query:\n{}".format(sql))
        payload = {'query': sql, 'data_source_id': ro_risk_idrisk, 'max_age': max_age}
        response = self.req.post(os.path.join(self.url, config.QUERY_RESULT), headers=self.header, json=payload)
        if response.status_code != 200:
            raise Exception(response.text)
        result_id = self.poll_job(response.json()['job'])
        if result_id:
            response = self.req.get(os.path.join(self.url, config.QUERY_RESULT, str(result_id)), headers=self.header)
            if response.status_code != 200:
                raise Exception('Failed getting results.')
        else:
            raise Exception('Query execution failed.')
        return response.json()['query_result']['data']['rows']

    def get_query_results_count(self, sql):
        resp = self.query_results(sql)
        return resp[0].get('count')

    @staticmethod
    def pandas_show(response):
        data_frame = pd.DataFrame(response)
        utils.log('pandas show results as below:\n{}'.format(data_frame.head()))

    def query_result_pandas_show(self, sql):
        res = self.query_results(sql)
        self.pandas_show(res)


