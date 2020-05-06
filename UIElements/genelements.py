# *********** Login View ********
user_input = "//*[@id='pane-loginByEmailPwd']//*[@placeholder='Email']"
pwd_input = "//*[@id='pane-loginByEmailPwd']//*[@placeholder='Password']"
# login_btn = "//*[@id='pane-loginByEmailPwd']//*[normalize-space(text())='SIGN IN']"
login_btn = "div#pane-loginByEmailPwd button.loginBnt"
invalid_pwd = "//*[text()='Invalid password!']"
invalid_ok_btn = "//*[normalize-space(text())='OK']"


# *********** Account ********
user_avatar = "//img[contains(@class,'user-avatar')]"
account_detail_trigger = "//img[contains(@class,'user-avatar')]/following-sibling::i"
logout_btn = "//span[text()='Logout']"

# *********** Country | Account Dropdown active list ********
header_dropdown_list = "//*[contains(@class, 'el-dropdown-menu--medium') and not(contains(@style,'display: none;'))]"

# *********** Country ********
country_trigger = ".el-menu--horizontal .right-menu span.el-dropdown-selfdefine  .el-icon-caret-bottom"
country_label = ".el-menu--horizontal .right-menu span.el-dropdown-selfdefine"
country_li_list = "//*[contains(@class, 'el-dropdown-menu--medium') and not(contains(@style,'display: none;'))]/li"





