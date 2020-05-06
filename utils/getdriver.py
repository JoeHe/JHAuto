from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from logger import bi_logger


def getdriver(browser="ff"):
    """
    Run class initialization method, the default is proper
    to drive the Firefox browser. Of course, you can also
    pass parameter for other browser, Chrome browser for the "Chrome",
    the Internet Explorer browser for "internet explorer" or "ie".
    """
    if browser == "firefox" or browser == "ff":
        bi_logger.info("Initialize Firefox Driver")
        return webdriver.Firefox()
    elif browser == "chrome":
        bi_logger.info("Initialize Chrome Driver")
        return webdriver.Chrome(executable_path=config.CHROME_DRIVER)
    elif browser == "internet explorer" or browser == "ie":
        bi_logger.info("Initialize IE Driver")
        return webdriver.Ie()
    elif browser == "opera":
        bi_logger.info("Initialize Opera Driver")
        return webdriver.Opera()
    elif browser == "chrome_headless":
        bi_logger.info("Initialize Chrome Headless Driver")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        return webdriver.Chrome(chrome_options=chrome_options)
    elif browser == 'edge':
        bi_logger.info("Initialize Edge Driver")
        return webdriver.Edge()
    else:
        raise NameError(
                "Not found %s browser,You can enter 'ie', 'ff', 'opera', 'edge', 'chrome' or 'chrome_headless'." % browser)