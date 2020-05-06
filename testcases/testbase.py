import unittest
from utils import getdriver
from config import config
from logger import bi_logger


class BaseTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        bi_logger.info("==================================================================")
        bi_logger.info("=                                                                =")
        bi_logger.info("===============           TEST CLASS SETUP               =========")
        bi_logger.info("==================================================================")
        bi_logger.info("Set up test class...")
        cls.driver = getdriver.getdriver(config.DRIVER_TYPE)
        bi_logger.info("==================================================================\n\n")

    @classmethod
    def tearDownClass(cls):
        bi_logger.info("==================================================================")
        bi_logger.info("=                                                                =")
        bi_logger.info("================           TEST CLASS CLEANUP           ==========")
        bi_logger.info("==================================================================")
        if cls.driver:
            bi_logger.info("Tear down test class, close web driver.")
            cls.driver.quit()
        bi_logger.info("==================================================================\n\n")

