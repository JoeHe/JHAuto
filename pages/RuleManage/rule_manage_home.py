from config import config
from pages import datagridview, login
from utils import utils
from UIElements import rule_manage


class RuleManageHome(datagridview.DataGridView):

    def click_rule_manage(self):
        utils.log('"click [Rule Manager] tab in Left MenuBar."')
        self.slb.move_to_click(rule_manage.rule_manager_tab)
        self.get_rule_manage_rows()

    def click_rule_group_trigger(self):
        self.slb.click(rule_manage.rule_group_trigger)
        self.slb.sleep(1)

    def get_rule_manage_rows(self):
        rule_rows = self.slb.get_elements(rule_manage.rule_tbody_rows)
        return rule_rows

    def get_rule_group_items(self):
        utils.log('get [Rule Groups] DropDown list items')
        self.click_rule_group_trigger()
        rule_grp_items = self.slb.get_elements_text_list(rule_manage.rule_groups_list_items)
        return rule_grp_items

    def login_get_rule_group_item(self, rule_data):
        self.login(rule_data)
        self.click_rule_manage()
        return self.get_rule_group_items()

    def login(self, rule_data):
        self.slb.driver.maximize_window()
        loginPage = login.LoginPage(self.slb.driver)
        url = rule_data['BaseUrl'] + rule_data['FrontendPort']
        loginPage.login(config.TEST_USR1, config.TEST_PWD1, url=url)
        loginPage.switch_country(config.COUNTRY)

