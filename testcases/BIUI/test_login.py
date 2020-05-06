import unittest

from testcases import genebase
from pages import login, statistics_overview
from utils import getdriver, utils
from config import config


@unittest.skip("skip")
class TestQQLogin(genebase.GeneralBase):

    expect_cards = ['Downloads', 'Registered Users', 'Applications', 'Approved Application', 'Total Borrowers',
                    'Repeat Borrowers111']

    @classmethod
    def setUpClass(cls):
        utils.log("==================================================================")
        utils.log("=                                                                =")
        utils.log("===============           TEST CLASS SETUP               =========")
        utils.log("==================================================================")
        utils.log("Set up test class...")
        cls.driver = getdriver.getdriver(config.DRIVER_TYPE)
        cls.driver.maximize_window()
        cls.loginPage = login.LoginPage(cls.driver)
        cls.statics_overview = statistics_overview.StatisticsOverview(cls.driver)
        utils.log("==================================================================\n\n")

    def test_login_success(self):
        utils.log("Test login [QQ One] with valid credential.")
        self.loginPage.login_valid_usr()
        utils.log("verify login success.")
        self.assertTrue(self.loginPage.is_usr_avatar_exist(), "Login Should success!")
        actual_cards = self.statics_overview.get_cards_text()
        utils.log("verify statics overview card text is correct.")
        self.assertListEqual(actual_cards, TestQQLogin.expect_cards, "The card text is Not as expected!")

    # @unittest.skip("skip test")
    def test_login_failed(self):
        utils.log("Test login [QQ One] with Invalid credential.")
        self.loginPage.login_invalid_usr()
        utils.log("verify login failed.")
        self.assertTrue(self.loginPage.is_invalid_pwd_show(), "Login Should failed!")
        self.loginPage.close_invalid_dialog()



