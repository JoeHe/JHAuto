import json

from config import config
from utils import utils


class RuleEngine:

    rule_data = utils.load_yml("rule_engine_data.yaml")

    @staticmethod
    def rule(req, params):
        utils.log('call api rule engine [rule] for [{}]'.format(config.COUNTRY))
        url = RuleEngine.rule_data['Host'][config.COUNTRY] + RuleEngine.rule_data['RuleEnginePort'][config.COUNTRY] + RuleEngine.rule_data['rule']['path']
        header = RuleEngine.rule_data['rule']['header']
        result = json.loads(req.get(url, headers=header, params=params).text)
        return result
