# coding=utf-8
import time
import os
import unittest
import sys
from optparse import OptionParser

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))
from running import HTML_test_runner
from config import config


class TestRunner(object):
    " Run test "
    def __init__(self, cases=config.UI_TestCase_DIR, title="Test Report", description="Test case execution"):
        self.cases = cases
        self.title = title
        self.des = description

    def run(self):
        self.title = "UI Test Report"
        now = time.strftime("%Y%m%d_%H%M%S")
        fp = open(config.REPORT_DIR + "/BIUI_" + now + "_result.html", 'wb')
        tests = unittest.defaultTestLoader.discover(self.cases, pattern='test*.py', top_level_dir=None)
        runner = HTML_test_runner.HTMLTestRunner(stream=fp, title=self.title, description=self.des)
        runner.run(tests)
        fp.close()

    def debug(self):
        tests = unittest.defaultTestLoader.discover(self.cases, pattern='test*.py', top_level_dir=None)
        runner = unittest.TextTestRunner(verbosity=2)
        print("test start:")
        runner.run(tests)
        print("test end!!!")


def main():
    """
     python test_runner.py -r 'debug' -d  "add new feature ***"
    """
    parser = OptionParser()
    parser.add_option("-r", "--RunType", dest="run_type", help="run or debug")
    parser.add_option("-d", "--Description", dest="description", help="description of this run, like build number...")
    parser.add_option("-c", "--CaseDir", dest="case_dir", help="test cases folder, folder name under ./testcases")
    (options, args) = parser.parse_args()
    run_type = options.run_type
    description = options.description
    case_dir = None
    if options.case_dir:
        case_dir = config.BASE_PATH + '/testcases/' + options.case_dir
    if description and case_dir:
        test = TestRunner(cases=case_dir, description=description)
    elif case_dir:
        test = TestRunner(cases=case_dir)
    elif description:
        test = TestRunner(description=description)
    else:
        test = TestRunner()

    if run_type:
        if run_type.lower() == "debug":
            return test.debug()
    test.run()


if __name__ == '__main__':
    main()
