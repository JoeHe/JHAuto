import unittest

from testcases import loginbase
from utils import utils
from pages import report_schedule
from config import config, constants


class TestReportSchedule(loginbase.LoginBase):

    data = utils.load_yml(config.TEST_DATA_DIR+"/report_schedule_data.yaml")
    new_biz_type_list = []

    def test_get_report_simple(self):
        """
        quick check there are data in Report View.
        """
        utils.log("Case. Test there are schedule reports in view.")
        self.reportSchedule.click_report_biz_list()
        schedule_reports = self.reportSchedule.get_data_grid_data()
        utils.log("verify schedule report is not empty.")
        self.assertIsNotNone(schedule_reports, "There are No schedule reports in view!")

    def test_add_schedule_excel(self):
        utils.log("Case. Test add a new excel report schedule and publish it.")
        self.add_publish_report('excel-report-2')

    def test_add_schedule_csv(self):
        utils.log("Case. Test add a new csv report schedule and publish it.")
        self.add_publish_report('csv-report-2')

    def test_add_schedule_table(self):
        utils.log("Case. Test add a new table report schedule and publish it.")
        self.add_publish_table_report('table-report-2')

    def add_schedule_report(self, test_data):
        self.reportSchedule.click_report_biz_list()
        suffix = utils.get_random_numb()
        biz_type = self.data[test_data]['BizType'] + str(suffix)
        TestReportSchedule.new_biz_type_list.append(biz_type)
        self.reportSchedule.click_add()
        self.reportSchedule.fill_add_report_config(
            biz_type,
            self.data[test_data]['EmailTitle'] + str(suffix),
            self.data[test_data]['ScheduleTimeCreate'],
            self.data[test_data]['Template'],
            description=self.data[test_data]['Description'],
            email_date_format=self.data[test_data]['EmailDateFormat'],
            mail_title_timezone=self.data[test_data]['EmailTitleTimezone'],
            backdate=self.data[test_data]['BackDate'])
        self.reportSchedule.click_confirm()
        utils.log("success create report schedule, biz type is: {}".format(biz_type))
        return biz_type

    def action_on_report(self, action, biz_type):
        self.reportSchedule.click_action_in_row(action, constants.BIZ_TYPE, biz_type)

    def view_edit_report(self, biz_type, test_data):
        """
        View Report, Add Report List, Email Recipients For excel, csv file type.
        """
        self.action_on_report(constants.ReportView, biz_type)
        self.reportSchedule.fill_view_report_config(
            self.data[test_data]['ExcelName'] + biz_type.split('_')[2],
            self.data[test_data]['SheetName'],
            self.data[test_data]['SheetOrder'],
            self.data[test_data]['AttachmentDateFormat'],
            self.data[test_data]['FileType'],
            self.data[test_data]['MailHtml'],
            self.data[test_data]['ExcelReportSql'],
            self.data[test_data]['EmailRecipients'],
            self.data[test_data]['AttachBackDate'],
            self.data[test_data]['EmailOrder'])

    def publish_report(self, biz_type):
        self.reportSchedule.click_report_biz_list()
        self.action_on_report(constants.ReportPublish, biz_type)
        self.reportSchedule.click_publish_in_confirm()

    def add_publish_report(self, test_data):
        """
        Add Report, View Report, Publish Report.
        """
        utils.log("1. Add new schedule report.")
        biz_type = self.add_schedule_report(test_data)
        target_rows, target_row_id, action_column_index = self.reportSchedule.get_target_row(constants.BIZ_TYPE, biz_type)
        self.assertTrue(len(target_rows) > 0, "create new report schedule, biz-type:[] failed!!!".format(biz_type))
        utils.log("2. View schedule, add 'Report List', 'Email Recipients' for it.")
        self.action_on_report(constants.ReportView, biz_type)
        self.view_edit_report(biz_type, test_data)
        utils.log("3. Publish report schedule.")
        self.publish_report(biz_type)
        publish_success = self.reportSchedule.is_action_in_row(constants.BIZ_TYPE, biz_type, constants.ReportPause)
        self.assertTrue(publish_success, "publish report failed! Not find 'Pause' in row Action column.")

    def add_publish_table_report(self, test_data):
        """
        Add Report, View Report, Publish  table Report.
        """
        utils.log("1. Add new schedule report.")
        biz_type = self.add_schedule_report(test_data)
        target_rows, target_row_id, action_column_index = self.reportSchedule.get_target_row(constants.BIZ_TYPE, biz_type)
        self.assertTrue(len(target_rows) > 0, "create new report schedule, biz-type:[] failed!!!".format(biz_type))
        utils.log("2. View schedule, add 'Report List', 'Email HTML', 'Email Recipients' for it.")
        self.view_edit_table_report(biz_type, test_data)
        utils.log("3. Publish report schedule.")
        self.publish_report(biz_type)
        publish_success = self.reportSchedule.is_action_in_row(constants.BIZ_TYPE, biz_type, constants.ReportPause)
        self.assertTrue(publish_success, "publish report failed! Not find 'Pause' in row Action column.")

    def view_edit_table_report(self, biz_type, test_data):
        """
        View Report, Add Report List, Email HTML, Email Recipients For table file type.
        """
        self.action_on_report(constants.ReportView, biz_type)
        self.reportSchedule.fill_view_report_config_table(
            self.data[test_data]['Title'] + biz_type.split('_')[2],
            self.data[test_data]['Type'],
            self.data[test_data]['Order'],
            self.data[test_data]['TableSQL'],
            self.data[test_data]['EmailHtmlHeader'],
            self.data[test_data]['EmailHtmlTail'],
            self.data[test_data]['EmailRecipients'])

