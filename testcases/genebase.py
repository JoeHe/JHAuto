import os
import time

from testcases import testbase
from config import config
from utils import seleniumLib, utils
from logger import bi_logger


class GeneralBase(testbase.BaseTest):

    def setUp(self):
        bi_logger.info("******************************************************************")
        bi_logger.info("*                                                                *")
        bi_logger.info("****************           TEST START                 ************")
        bi_logger.info("Testing Method:")
        bi_logger.info(self.id())
        bi_logger.info("******************************************************************")

    def tearDown(self):
        result = self.defaultTestResult()  # these 2 methods have no side effects
        self._feedErrorsToResult(result, self._outcome.errors)

        error = self.list2reason(result.errors)
        failure = self.list2reason(result.failures)
        ok = not error and not failure

        if not ok:
            self.slb = seleniumLib.SeleniumLib(self.driver)
            if not os.path.isdir(config.SCREENSHOT_DIR):
                os.mkdir(config.SCREENSHOT_DIR)
            file_path = config.SCREENSHOT_DIR + "/{}{}.png".format(self.id(), time.strftime("%H%M%S"))
            # utils.error("run fail or error, take snapshot at:\n{}".format(file_path))
            utils.error("run fail or error, take snapshot at:\n{}\n{}".format(file_path, error))
            self.slb.get_screenshot(file_path)

        bi_logger.info("******************************************************************")
        bi_logger.info("****************           TEST END                   ************")
        bi_logger.info("******************************************************************\n\n")

    def list2reason(self, exc_list):
        if exc_list and exc_list[-1][0] is self:
            return exc_list[-1][1]
