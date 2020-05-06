from utils import requestlib, utils
from logger import bi_logger
import unittest
import json


class RequestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        utils.log("==================================================================")
        utils.log("=                                                                =")
        utils.log("===============           TEST CLASS SETUP               =========")
        utils.log("==================================================================")
        utils.log("Set up test class...")
        cls.req = requestlib.RequestLib()
        utils.log("==================================================================\n\n")

    @classmethod
    def tearDownClass(cls):
        utils.log("==================================================================")
        utils.log("=                                                                =")
        utils.log("================           TEST CLASS CLEANUP           ==========")
        utils.log("==================================================================")
        if cls.req:
            cls.req.close_session()
        utils.log("==================================================================\n\n")

    def setUp(self):
        utils.log("******************************************************************")
        utils.log("*                                                                *")
        utils.log("****************           TEST START                 ************")
        utils.log("Testing Method:")
        utils.log(self.id())
        utils.log("******************************************************************")

    def tearDown(self):
        result = self.defaultTestResult()  # these 2 methods have no side effects
        self._feedErrorsToResult(result, self._outcome.errors)

        error = self.list2reason(result.errors)
        failure = self.list2reason(result.failures)
        ok = not error and not failure
        if not ok:
            utils.error("run fail or error\n{}".format(error))
        utils.log("******************************************************************")
        utils.log("****************           TEST END                   ************")
        utils.log("******************************************************************\n\n")

    def turn2dict(self, resp):
        return json.loads(resp.text)

    def assertMsg(self, resp):
        resp_dict = self.turn2dict(resp)
        self.assertEqual('success', resp_dict['msg'], "call api failed!")

    def list2reason(self, exc_list):
        if exc_list and exc_list[-1][0] is self:
            return exc_list[-1][1]

        


