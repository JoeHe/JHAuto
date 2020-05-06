from utils import utils
from UIElements import report_schedule
from pages import datagridview


class ReportSchedule(datagridview.DataGridView):

    def click_report_biz_list(self):
        utils.log("click [Report Biz List] tab.")
        if not self.is_report_menu_expanded():
            utils.debug("expand menu [Report Schedule]")
            self.slb.click(report_schedule.report_toggle)
        self.slb.move_to_click(report_schedule.report_schedule_link)
        self.slb.sleep(1)

    def click_add(self):
        utils.log("click [Add] at [Report Biz List] view.")
        self.slb.click(report_schedule.add_btn)

    def is_report_menu_expanded(self):
        utils.debug("check whether menu [Report Schedule] expanded.")
        report_menu_class = self.slb.get_attribute(report_schedule.report_menu_item_li, 'class')
        if "is-opened" in report_menu_class:
            return True
        return False

    def set_add_biz_type(self, biz_type):
        utils.log("input Type: [{}] in new create report dialog.".format(biz_type))
        self.slb.type(report_schedule.add_biz_type_input, biz_type)

    def set_add_description(self, description):
        utils.log("input Description: [{}] in new create report dialog.".format(description))
        self.slb.type(report_schedule.add_description_area, description)

    def set_add_email_title(self, email_title):
        utils.log("input Email title: [{}] in new create report dialog.".format(email_title))
        self.slb.type(report_schedule.add_email_title_input, email_title)

    def set_add_email_date_format(self, email_date_format):
        utils.log("set Email Date Format: [{}] in new create report dialog.".format(email_date_format))
        self.select_drop_down_list("Email Date Format", email_date_format)

    def set_add_schedule_time(self, schedule_time):
        utils.log("input Schedule Time: [{}] in new create report dialog.".format(schedule_time))
        self.slb.type(report_schedule.add_schedule_time_input, schedule_time)

    def set_add_template(self, template):
        utils.log("set Template: [{}] in new create report dialog.".format(template))
        self.select_drop_down_list("Template", template)

    def set_add_mail_title_timezone(self, mail_title_timezone):
        utils.log("set Mail Title Timezone: [{}] in new create report dialog.".format(mail_title_timezone))
        self.select_drop_down_list("Mail Title Timezone", mail_title_timezone)

    def set_backdate(self, backdate):
        """
        set backdate for View and Edit
        """
        utils.log("input Back Date: [{}] in report dialog.".format(backdate))
        self.slb.type(report_schedule.back_date_input, backdate)

    def fill_add_report_config(self, biz_type, email_title, schedule_time, template,
                               description=None, email_date_format=None, mail_title_timezone=None, backdate=None):
        utils.log("input information for new add report...")
        self.set_add_biz_type(biz_type)
        self.set_add_email_title(email_title)
        self.set_add_schedule_time(schedule_time)
        self.set_add_template(template)
        if description:
            self.set_add_description(description)
        if email_date_format:
            self.set_add_email_date_format(email_date_format)
        if mail_title_timezone:
            self.set_add_mail_title_timezone(mail_title_timezone)
        if backdate:
            self.set_backdate(backdate)

    def click_cancel(self):
        utils.log("click [Cancel] in new create report dialog.")
        self.slb.click(report_schedule.cancel_btn)

    def click_confirm(self):
        utils.log("click [Confirm] in report dialog.")
        self.slb.click(report_schedule.confirm_btn)
        self.slb.sleep(1)

    def select_drop_down_list(self, drop_down_label_name, value):
        """
        select the value for drop down list
        """
        utils.log("select value:[{}] for Drop Down Box:[{}]".format(value, drop_down_label_name))
        self.slb.click(report_schedule.drop_down_trigger.format(drop_down_label_name))
        li_list = self.slb.get_elements(report_schedule.drop_ul_li)
        for li in li_list:
            self.slb.sleep(0.5)
            if self.slb.get_element_text(li) == value:
                li.click()
                self.slb.sleep(0.5)
                return
        utils.error("failed to select! Not found item [{}] in Drop Down List:[{}]. Please check!".format(
            value, drop_down_label_name))

    # remove it after server issue fixed
    def dismiss_server_error(self):
        svr_error_ok_btn = "div.el-message-box__wrapper:not([style*='display: none;']) .el-message-box__btns button"
        while self.slb.is_element_exist(svr_error_ok_btn):
            utils.log("click warning dialog [OK] btn")
            self.slb.click(svr_error_ok_btn)
            self.slb.sleep(1)

    def click_view_add_report_list(self):
        utils.log("click [Add] for [Report List] in View report dialog.")
        self.slb.click(report_schedule.view_add_report_list)

    def click_view_add_email_recipient(self):
        utils.log("click [Add] for [Email Recipients] in View report dialog.")
        self.slb.click(report_schedule.view_add_email_recipients)

    def set_view_excel_file_name(self, excel_name):
        utils.log("input Excel File Name: [{}] in [View] report dialog.".format(excel_name))
        self.slb.type(report_schedule.view_input.format("Excel File Name"), excel_name)

    def set_view_sheet_name(self, name):
        utils.log("input Sheet Name: [{}] in [View] report dialog.".format(name))
        self.slb.type(report_schedule.view_input.format("Sheet Name"), name)

    def set_view_sheet_order(self, order_number):
        utils.log("input Sheet Order: [{}] in [View] report dialog.".format(order_number))
        self.slb.type(report_schedule.view_input.format("Sheet Order"), order_number)

    def set_view_attachment_date_format(self, attachment_date_format):
        utils.log("set Attachment Data Formate: [{}] in [View] report dialog.".format(attachment_date_format))
        self.select_drop_down("Attachment Data Formate", attachment_date_format)

    def set_view_file_type(self, excel_type):
        utils.log("set File Type: [{}] in [View] report dialog.".format(excel_type))
        self.select_drop_down("File Type", excel_type)

    def set_view_mail_html(self, report_html):
        utils.log("input Mail Html in [View] report dialog. html as below\n{}".format(report_html))
        self.slb.type(report_schedule.view_mail_html, report_html)

    def set_view_excel_report_sql(self, report_sql):
        utils.log("input Excel Report Sql in [View] report dialog. sql as below\n{}".format(report_sql))
        self.slb.type(report_schedule.view_excel_report_sql, report_sql)

    def select_drop_down(self, drop_down_label_name, value):
        """
        select the value for drop down list
        """
        utils.log("select value:[{}] for Drop Down Box:[{}]".format(value, drop_down_label_name))
        self.slb.select_drop_down_list(
            report_schedule.drop_down_trigger.format(drop_down_label_name),
            report_schedule.drop_ul_li,
            value)

    def fill_view_report_config(self, excel_name, sheet_name, sheet_order, date_format,
                                file_type, report_html, report_sql, email_recipient, backdate, email_order=None):
        utils.log("input information for view report...")
        self.view_add_report(excel_name, sheet_name, sheet_order, date_format, file_type, report_html, report_sql, backdate)
        self.view_add_multiple_mail_recipient(email_recipient)

    def view_add_report(self, excel_name, sheet_name, sheet_order, date_format, file_type, report_html, report_sql, backdate):
        utils.log("Add [Report List] in [View] and fill configs...")
        is_append_sheet = self.is_exist_report_in_list()
        self.click_view_add_report_list()
        if not is_append_sheet:  # if already added report, can't set excel name again
            self.set_view_excel_file_name(excel_name)
        self.set_view_sheet_name(sheet_name)
        self.set_view_sheet_order(sheet_order)
        self.set_view_attachment_date_format(date_format)
        self.set_view_file_type(file_type)
        self.set_view_mail_html(report_html)
        self.set_view_excel_report_sql(report_sql)
        self.set_backdate(backdate)
        self.click_confirm()

    def view_add_email_recipient(self, email_recipient):
        utils.log("input Email Recipient:{} in [View] report dialog.".format(email_recipient))
        self.slb.type(report_schedule.view_email_input.format("Email"), email_recipient)

    def view_set_email_order(self, email_order):
        utils.log("input Email Order:{} in [View] report dialog.".format(email_order))
        self.slb.type(report_schedule.view_email_input.format("Email Order"), email_order)

    def view_add_mail_recipient(self, email_recipient, email_order=None):
        utils.log("Add [Email Recipients] in View and")
        self.click_view_add_email_recipient()
        self.view_add_email_recipient(email_recipient)
        if email_order:
            self.view_set_email_order(email_order)
        # self.click_confirm()
        self.click_view_add_mail_recip_confirm_btn()

    def view_add_multiple_mail_recipient(self, mail_recip_list):
        utils.log("Add multiple mail recipient: {}".format(mail_recip_list))
        if not mail_recip_list:
            utils.warn("There is No item in EmailRecipients, please check your configuration!!!")
            return
        for index, item in enumerate(mail_recip_list):
            self.view_add_mail_recipient(item, index)

    def is_exist_report_in_list(self):
        return self.slb.is_element_exist(report_schedule.view_report_row)

    def click_publish_in_confirm(self):
        utils.log("Click [Publish] in confirm dialog.")
        self.slb.move_to_click(report_schedule.confirm_publish_btn)
        self.slb.sleep(1)

    def fill_view_report_config_table(self, title, types, order, table_sql, email_header, email_tail, email_recipient):
        """For table type"""
        utils.log("input information for view report...")
        self.view_add_report_table(title, types, order, table_sql)
        self.view_add_report_table_email_html(email_header, email_tail)
        self.view_add_multiple_mail_recipient(email_recipient)

    def view_add_report_table(self, title, types, order, table_sql):
        utils.log("Add [Report List] in Table [View] and fill configs...")
        self.click_view_add_tbl_report_list()
        self.set_view_table_title(title)
        self.set_view_table_type(types)
        self.set_view_table_order(order)
        self.set_view_table_report_sql(table_sql)
        self.click_confirm()

    def click_view_add_tbl_report_list(self):
        utils.log("click [Add] for type Table [Report List] in View report dialog.")
        self.slb.click(report_schedule.view_add_table_report_list)

    def set_view_table_title(self, title):
        utils.log("input Report Title: [{}] in [View] add report dialog.".format(title))
        self.slb.type(report_schedule.view_input.format("Title"), title)

    def set_view_table_type(self, types):
        utils.log("input Report Type: [{}] in [View] add report dialog.".format(types))
        self.slb.type(report_schedule.view_input.format("Type"), types)

    def set_view_table_order(self, order_number):
        utils.log("input Report Order: [{}] in [View] report dialog.".format(order_number))
        self.slb.type(report_schedule.view_input.format("Order"), order_number)

    def set_view_table_report_sql(self, report_sql):
        utils.log("input Table Report Sql in [View] report dialog. sql as below\n{}".format(report_sql))
        self.slb.type(report_schedule.view_text_area.format('Table SQL'), report_sql)

    def click_view_table_edit_email_html(self):
        """click [Edit] in table view 'Email HTML'"""
        # self.slb.click(report_schedule.view_button.format('Edit'))
        self.slb.click(report_schedule.view_email_html_edit)

    def click_view_table_submit_email_html(self):
        """click [Submit] in table view Edit 'Email HTML'"""
        # self.slb.click(report_schedule.view_button.format('Submit'))
        self.slb.click(report_schedule.view_email_html_submit)

    def set_view_table_email_header(self, email_header):
        utils.log("input Table Report Email Header in [View] report dialog. as below\n{}".format(email_header))
        self.slb.type(report_schedule.view_html_text_area.format('Email Header'), email_header)

    def set_view_table_email_tail(self, email_tail):
        utils.log("input Table Report Email Tail in [View] report dialog. as below\n{}".format(email_tail))
        self.slb.type(report_schedule.view_html_text_area.format('Email Tail'), email_tail)

    def view_add_report_table_email_html(self, email_header, email_tail):
        utils.log("Edit [Email HTML] in Table [View]...")
        self.click_view_table_edit_email_html()
        self.set_view_table_email_header(email_header)
        self.set_view_table_email_tail(email_tail)
        self.click_view_table_submit_email_html()

    def click_view_add_mail_recip_confirm_btn(self):
        utils.log("click [Confirm] in [View] Add 'Email Recipients' dialog.")
        self.slb.click(report_schedule.view_add_email_recipt_confirm)
        self.slb.sleep(1)


