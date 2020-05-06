from testcases import genebase
from pages import *
from utils import getdriver, seleniumLib
from config import config
from logger import bi_logger
import time
import os


class LoginBase(genebase.GeneralBase):
    @classmethod
    def setUpClass(cls):
        bi_logger.info("==================================================================")
        bi_logger.info("=                                                                =")
        bi_logger.info("===============           TEST CLASS SETUP               =========")
        bi_logger.info("==================================================================")
        bi_logger.info("Set up test class...")
        try:
            cls.driver = getdriver.getdriver(config.DRIVER_TYPE)
            cls.driver.maximize_window()
            cls.loginPage = login.LoginPage(cls.driver)
            cls.loginPage.login_valid_usr(check_login=False)
            cls.loginPage.switch_country(config.COUNTRY)
        except Exception as e:
            if not os.path.isdir(config.SCREENSHOT_DIR):
                os.mkdir(config.SCREENSHOT_DIR)
            file_path = config.SCREENSHOT_DIR + "/FailLogin_{}.png".format(time.strftime("%H%M%S"))
            slb = seleniumLib.SeleniumLib(cls.driver)
            slb.get_screenshot(file_path)
            slb.close()
            bi_logger.error("run fail or error, take snapshot at:\n{}".format(file_path), exc_info=1)
            raise e

        cls.statisticsOverview = statistics_overview.StatisticsOverview(cls.driver)
        cls.reportSchedule = report_schedule.ReportSchedule(cls.driver)
        bi_logger.info("==================================================================\n\n")

    def setUp(self):
        bi_logger.info("******************************************************************")
        bi_logger.info("*                                                                *")
        bi_logger.info("****************           TEST START                 ************")
        bi_logger.info("Testing Method:")
        bi_logger.info(self.id())
        bi_logger.info("******************************************************************")
        # self.statisticsOverview.click_statistics_overview()


