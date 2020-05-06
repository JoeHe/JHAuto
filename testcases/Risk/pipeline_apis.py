import json

from config import config
from utils import utils


class Pipeline:

    model_data = utils.load_yml("rule_model_data.yaml")

    @staticmethod
    def borrow_apply(req, data):
        utils.log('call api [borrow-apply] for [{}]'.format(config.COUNTRY))
        url = Pipeline.model_data['Host'][config.COUNTRY] + Pipeline.model_data['CeleryPort'][config.COUNTRY] + Pipeline.model_data['BorrowApply']['path']
        header = Pipeline.model_data['BorrowApply']['header']
        result = json.loads(req.post(url, headers=header, json=data).text)
        return result

    @staticmethod
    def kyc_switch(req, data):
        utils.log('call api [kyc-switch] for [{}]'.format(config.COUNTRY))
        pass

    @staticmethod
    def process_post_kyc(req, data):
        utils.log('call api [process-post-kyc] for [{}]'.format(config.COUNTRY))
        pass
