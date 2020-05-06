from config import config, constants
from UIElements import genelements
from utils import *


class LoginPage(object):
    def __init__(self, driver):
        self.slb = seleniumLib.SeleniumLib(driver)

    def go_to_url(self, url=config.LOGIN_URL):
        utils.log("navigate to url: {}".format(config.LOGIN_URL))
        self.slb.open(url)
        if self.slb.get_title() != "QQ":
            raise Exception("This is not QQ Login page!")

    def input_name(self, username):
        utils.log('input user name...')
        self.slb.type(genelements.user_input, username)

    def input_pwd(self, pwd):
        utils.log('input password...')
        self.slb.type(genelements.pwd_input, pwd)

    def sign_in(self):
        utils.log('click sign in.')
        self.slb.click(genelements.login_btn)

    def login(self, username, pwd, check_login=False, url=config.LOGIN_URL):
        self.go_to_url(url)
        if check_login:
            self.log_out()
        utils.log("Login as user:[{}]".format(username))
        self.input_name(username)
        self.input_pwd(pwd)
        self.sign_in()

    def login_valid_usr(self, check_login=True):
        self.login(config.TEST_USR1, config.TEST_PWD1, check_login)

    def login_invalid_usr(self):
        self.login(config.TEST_USR1, config.DRIVER_TYPE, True)

    def is_usr_avatar_exist(self):
        return self.slb.is_element_exist(genelements.user_avatar)

    def log_out(self):
        if not self.is_usr_avatar_exist():  # Not login status
            return
        utils.log("try to log out account...")
        self.slb.click(genelements.account_detail_trigger)
        self.slb.sleep(1)
        utils.log("click log out.")
        self.slb.click(genelements.logout_btn)
        if not self.slb.is_element_exist(genelements.user_input):
            raise Exception("log out failed!")
        utils.log("log out successfully!")

    def is_invalid_pwd_show(self):
        return self.slb.is_element_exist(genelements.invalid_pwd)

    def close_invalid_dialog(self):
        utils.log("close invalid login dialog.")
        self.slb.click(genelements.invalid_ok_btn)
        self.slb.sleep(1)

    def switch_country(self, country):
        """
        switch to 
        :param country: the country name
        """
        utils.log("switch country to:[{}]".format(country))
        if self.get_country() == country:
            utils.log("current country is as expected, skip switch.")
            return
        self.slb.click(genelements.country_trigger)
        self.slb.sleep(1)
        country_el_list = self.slb.get_elements(genelements.country_li_list)
        for index, value in enumerate(constants.CountryList):
            if country == value:
                print("got target country element: {}".format(value))
                country_el_list[index].click()
                self.slb.sleep(1)
                break
        actual_country = self.get_country()
        if actual_country != country:
            raise Exception("failed switch country to:[{}], actual is:[{}]".format(country, actual_country))
        utils.log("switch country successfully!")

    def get_country(self):
        return self.slb.get_text(genelements.country_label)




