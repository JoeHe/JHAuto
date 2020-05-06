report_toggle = "//*[text()='Report Schedule']/parent::div//i"
report_schedule_link = "//a[@href='#/reportSchedule/reportBizList']"
report_menu_item_li = "//*[text()='Report Schedule']/parent::div/.."

add_btn = "//*[@class='app-container']//*[text()='Add']/parent::Button"

report_table = "div.el-table table.el-table__body"
report_table_trs = report_table+" tr"

#  Edit Report View
biz_type_input = "//*[text()='Biz Type']/following-sibling::div//input"
email_title_input = "//*[text()='Email Title']/following-sibling::div//input"
mail_title_timezone_input = "//*[text()='Mail Title Timezone']/following-sibling::div//input"
email_date_format_input = "//*[text()='Email Date Format']/following-sibling::div//input"
back_date_input = "//*[text()='Back Date']/following-sibling::div//input"
schedule_time_input = "//*[text()='Schedule Time']/following-sibling::div//input"
template_input = "//*[text()='Template']/following-sibling::div//input"

return_btn = "//*[text()='Return']/parent::button"
confirm_btn = "//*[text()='Confirm']/parent::button"


#  Add Report View
add_biz_type_input = "//*[text()='Biz Type']/following-sibling::div//input"
add_description_area = "//*[text()='Description']/following-sibling::div//textarea"
add_email_title_input = email_title_input
add_email_date_format_input = email_date_format_input
add_schedule_time_input = schedule_time_input
add_template_input = template_input
add_mail_title_timezone_input = mail_title_timezone_input
cancel_btn = "//*[text()='Cancel']/parent::button"

# drop_down_trigger = "//*[text()='Template']/parent::div//i"
drop_down_trigger = "//*[text()='{}']/parent::div//i"

# drop down list items
drop_ul_li = "//div[contains(@class, 'el-select-dropdown el-popper') and not(contains(@style, 'display: none;'))]//li"
span = "//span"


# View Report page
view_logs_history = "//*[@class='app-container']//*[text()='Logs History']/parent::Button"
view_send_test_email = "//*[@class='app-container']//*[text()='Send Test Email']/parent::Button"
# View Report->[Add] for Report List
# view_add_report_list = "//*[text()='Report List']/../following-sibling::div/button"
view_add_report_list = "//*[text()='Send Test Email']/../following-sibling::button"
view_report_row = "//*[text()='Report List']/../../following-sibling::div//tr[@class='el-table__row']"
# View Report->[Add] for Email Recipients
# view_add_email_recipients = "//*[text()='Email Recipients']/../following-sibling::div//button"
view_add_email_recipients = "//*[text()='Email Recipients']/../../following-sibling::div//button"
# View Report->[Add] in Report list details items
view_input = "//*[text()='{}']/parent::div//input"
view_mail_html = "//*[text()='Mail Html']/following-sibling::div//textarea"
view_excel_report_sql = "//*[text()='Excel Report Sql']/following-sibling::div//textarea"
view_text_area = "//*[text()='{}']/following-sibling::div//textarea"
view_html_text_area = "//*[contains(@class, 'table_module_container')]//*[text()='{}']/following-sibling::div//textarea"

view_add_table_report_list = "//*[text()='Send Test Email']/../following-sibling::button"

view_button = "//*[text()='{}']/parent::button"

view_email_html_edit = "//*[text()='Email HTML']/../../following-sibling::div//span[text()='Edit']"
view_email_html_submit = "//*[text()='Email HTML']/../../following-sibling::div//span[text()='Submit']"

view_email_input = "//*[contains(@class, 'el-dialog')]//*[text()='{}']/following-sibling::div//input"

view_add_email_recipt_confirm = "//*[contains(@class, 'el-dialog__footer')]//*[text()='Confirm']/parent::button"


# pop up box after click publish
confirm_publish_btn = "//button[normalize-space()='Cancle']/following-sibling::button"










