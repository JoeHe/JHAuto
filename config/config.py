import os
import time
import logging

from config import constants

BASE_PATH = os.path.dirname(os.path.dirname(__file__))
REPORT_DIR = BASE_PATH+'/report'
SCREENSHOT_BASEDIR = BASE_PATH+'/screenshots/'
SCREENSHOT_DIR = SCREENSHOT_BASEDIR+time.strftime("%Y%m%d")

if not os.path.isdir(REPORT_DIR):
    os.mkdir(REPORT_DIR)

if not os.path.isdir(SCREENSHOT_BASEDIR):
    os.mkdir(SCREENSHOT_BASEDIR)

COUNTRY = constants.CN

# is product user_tag_storage
IS_PROD_STORAGE = True

# test case folder
UI_TestCase_DIR = BASE_PATH+'/testcases/BIUI'

# test site
QA_SERVER = 'http://10.10.10.111:8080'
LOGIN_URL = QA_SERVER+'/#/'

# test credential
TEST_USR1 = 'mike.jordan@qq.com'
TEST_PWD1 = 'pwd01'

# driver folder
DRIVER_DIR = BASE_PATH+'/tools/drivers'
CHROME_DRIVER = DRIVER_DIR+'/chromedriver'


# firefox, chrome, ie
DRIVER_TYPE = 'chrome'

# log
LOG_DIR = BASE_PATH+'/logs'
LOG_LEVEL = logging.INFO
LOG_FILE = None

TEST_DATA_DIR = BASE_PATH+'/testdata'

# Redash
API_KEY = 'Zodsp12lkjedsdf1111sdfdfkO0'
REDASH_HOST = 'http://redash.qq.com'
POLL_JOB = 'api/jobs'
QUERY_RESULT = 'api/query_results'




