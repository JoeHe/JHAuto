from utils import seleniumLib, utils
from UIElements import datagrid
from config import constants


class DataGridView:
    def __init__(self, driver):
        self.slb = seleniumLib.SeleniumLib(driver)

    def get_data_grid_rows(self):
        utils.debug("get data rows from data grid.")
        trs = self.slb.get_elements(datagrid.table_trs)
        if not trs:
            utils.warn("Not find any data gird data rows!")
        utils.debug("got total [{}] row data records".format(len(trs)))
        return trs

    def get_data_grid_headers(self):
        utils.debug("get headers from data grid.")
        headers = []
        headers_elements = self.slb.get_elements(datagrid.headers)
        for header in headers_elements:
            headers.append(self.slb.get_element_text(header))
        if not headers:
            utils.warn("not find any headers for this data grid!")
        utils.debug("got [{}] data gird headers.".format(len(headers)))
        return headers

    def get_data_grid_data(self):
        utils.debug("get the data grid data in view, save to a dict list.")
        data_dict_list = []
        trs = self.get_data_grid_rows()
        headers = self.get_data_grid_headers()
        for tr in trs:
            temp_row_dict = {}
            tds_in_tr = self.slb.get_elements_via_element(tr, datagrid.td)
            for column, td in zip(headers, tds_in_tr):
                temp_row_dict[column] = self.slb.get_element_text(td)
            data_dict_list.append(temp_row_dict)
        utils.debug("get data dict list as below:\n{}".format(data_dict_list))
        return data_dict_list

    def click_action_in_row(self, action_name, row_unique_key_name, row_unique_key):
        """
        Click Action [View], [Edit] etc. in the specific data row.
        :param action_name: which action button need to click
        :param row_unique_key_name: the unique key name for current row. eg:[Type], [Email Title], [Rule Id]
        :param row_unique_key: the unique key value.
        """
        action_btn_list = self.get_action_btn_list(row_unique_key_name, row_unique_key)

        for action_btn in action_btn_list:
            if self.slb.get_element_text(action_btn) == action_name:
                utils.log("click [{}] on row with [{}]={}".format(action_name, row_unique_key_name, row_unique_key))
                action_btn.click()
                return
        utils.warn("Not find record in data grid with [{}]={}, please check!".format(row_unique_key_name, row_unique_key))
        self.slb.sleep(2)

    def get_target_row(self, row_unique_key_name, row_unique_key):
        """
        get target row in data grid matched unique key value(eg: type, ruleId)
        """
        target_row, target_row_id, action_column_index = [], None, -1
        trs = self.get_data_grid_rows()
        headers = self.get_data_grid_headers()

        for index, header in enumerate(headers):
            if header == constants.ActionsColumnName or header == constants.ActionColumnName:
                action_column_index = index  # get the [Action] column index
                break
        for tr in trs:
            tds_in_tr = self.slb.get_elements_via_element(tr, datagrid.td)
            target_row_id = self.slb.get_element_text(tds_in_tr[0])  # first column value, help find row on ui
            for td in tds_in_tr:
                if self.slb.get_element_text(td) == row_unique_key:
                    utils.log("find the data record with {}={}".format(row_unique_key_name, row_unique_key))
                    target_row.append(tr)
                    break
            if target_row:
                break
        if not target_row:
            utils.warn("Not find any data record with {}={} !".format(row_unique_key_name, row_unique_key))
            return
        return target_row, target_row_id, action_column_index

    def get_action_btn_list(self, row_unique_key_name, row_unique_key):
        """
        get action button list from target row [Actions] column
        """
        target_row, target_row_id, action_column_index = self.get_target_row(row_unique_key_name, row_unique_key)
        tds_in_row = self.slb.get_elements_via_element(target_row[0], datagrid.td)
        if 'Rule' in row_unique_key_name:
            action_btn_list = self.slb.get_elements_via_element(
                tds_in_row[action_column_index],
                datagrid.action_button_rule_mgr)
        else:
            action_btn_list = self.slb.get_elements_via_element(
                tds_in_row[action_column_index],
                datagrid.action_button)
        return action_btn_list

    def is_action_in_row(self, row_unique_key_name, row_unique_key, action_name):
        """
        check is target action in target row.
        """
        found = False
        action_btn_list = self.get_action_btn_list(row_unique_key_name, row_unique_key)
        for action_btn in action_btn_list:
            if self.slb.get_element_text(action_btn) == action_name:
                found = True
        return found



