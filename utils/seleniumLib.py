# coding=utf-8
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import *

import time


class SeleniumLib(object):

    original_window = None

    def __init__(self, driver, timeout=5):
        self.driver = driver
        self.timeout = timeout

    def wait_element(self, el):
        """
        Waiting for an element to display.
        """
        try:
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located(el)
            )
        except TimeoutException:
            return False
        except NoSuchElementException:
            return False
        else:
            return True

    def get_element(self, css, silence=False):
        by, value = SeleniumLib.__handle_css(css)
        time_out_error = "定位元素超时, 请尝试其他定位方式.\n定位path: {}".format(css)
        if by == "id":
            req = self.wait_element((By.ID, value))
            if req is True:
                element = self.driver.find_element_by_id(value)
            else:
                if silence:
                    return None
                raise TimeoutException(time_out_error)
        elif by == "name":
            req = self.wait_element((By.NAME, value))
            if req is True:
                element = self.driver.find_element_by_name(value)
            else:
                if silence:
                    return None
                raise TimeoutException(time_out_error)
        elif by == "class":
            req = self.wait_element((By.CLASS_NAME, value))
            if req is True:
                element = self.driver.find_element_by_class_name(value)
            else:
                if silence:
                    return None
                raise TimeoutException(time_out_error)
        elif by == "link_text":
            req = self.wait_element((By.LINK_TEXT, value))
            if req is True:
                element = self.driver.find_element_by_link_text(value)
            else:
                if silence:
                    return None
                raise TimeoutException(time_out_error)
        elif by == "xpath":
            req = self.wait_element((By.XPATH, value))
            if req is True:
                element = self.driver.find_element_by_xpath(value)
            else:
                if silence:
                    return None
                raise TimeoutException(time_out_error)
        elif by == "css":
            req = self.wait_element((By.CSS_SELECTOR, value))
            if req is True:
                element = self.driver.find_element_by_css_selector(value)
            else:
                if silence:
                    return None
                raise TimeoutException(time_out_error)
        else:
            raise NameError(
                "Please enter the correct targeting elements,'id','name','class','link_text','xpath','css'.")
        return element

    def open(self, url):
        """
        open url.
        Usage:
        driver.open("https://www.google.com")
        """
        self.driver.get(url)

    def max_window(self):
        """
        Set browser window maximized.
        Usage:
        driver.max_window()
        """
        self.driver.maximize_window()

    def set_window(self, wide, high):
        """
        Set browser window wide and high.
        Usage:
        driver.set_window(wide,high)
        """
        self.driver.set_window_size(wide, high)

    def type(self, css, text):
        """
        Operation input box.
        Usage:
        driver.type("css=>#el","selenium")
        """
        el = self.get_element(css)
        if self.get_value(el) is not '':
            self.clear_by_sendkey(el)
        el.send_keys(text)

    def clear(self, css):
        """
        Clear the contents of the input box.
        Usage:
        driver.clear("css=>#el")
        """
        el = self.get_element(css)
        el.clear()

    def click(self, css):
        """
        It can click any text / image can be clicked
        Connection, check box, radio buttons, and even drop-down box etc..
        Usage:
        driver.click("css=>#el")
        """
        el = self.get_element(css)
        el.click()

    def right_click(self, css):
        """
        Right click element.
        Usage:
        driver.right_click("css=>#el")
        """
        el = self.get_element(css)
        ActionChains(self.driver).context_click(el).perform()

    def move_to_element(self, css):
        """
        Mouse over the element.
        Usage:
        driver.move_to_element("css=>#el")
        """
        el = self.get_element(css)
        ActionChains(self.driver).move_to_element(el).perform()

    def double_click(self, css):
        """
        Double click element.
        Usage:
        driver.double_click("css=>#el")
        """
        el = self.get_element(css)
        ActionChains(self.driver).double_click(el).perform()

    def drag_and_drop(self, el_css, ta_css):
        """
        Drags an element a certain distance and then drops it.
        Usage:
        driver.drag_and_drop("css=>#el","css=>#ta")
        """
        element = self.get_element(el_css)
        target = self.get_element(ta_css)
        ActionChains(self.driver).drag_and_drop(element, target).perform()

    def click_text(self, text):
        """
        Click the element by the link text
        Usage:
        driver.click_text("新闻")
        """
        self.driver.find_element_by_partial_link_text(text).click()

    def close(self):
        """
        Simulates the user clicking the "close" button in the titlebar of a popup
        window or tab.
        Usage:
        driver.close()
        """
        self.driver.close()

    def quit(self):
        """
        Quit the driver and close all the windows.
        Usage:
        driver.quit()
        """
        self.driver.quit()

    def submit(self, css):
        """
        Submit the specified form.
        Usage:
        driver.submit("css=>#el")
        """
        el = self.get_element(css)
        el.submit()

    def F5(self):
        """
        Refresh the current page.
        Usage:
        driver.F5()
        """
        self.driver.refresh()

    def js(self, script):
        """
        Execute JavaScript scripts.
        Usage:
        driver.js("window.scrollTo(200,1000);")
        """
        self.driver.execute_script(script)

    def get_attribute(self, css, attribute):
        """
        Gets the value of an element attribute.
        Usage:
        driver.get_attribute("css=>#el","type")
        """
        el = self.get_element(css)
        return el.get_attribute(attribute)

    def get_text(self, css):
        """
        Get element text information.
        Usage:
        driver.get_text("css=>#el")
        """
        el = self.get_element(css)
        return el.text

    def get_display(self, css):
        """
        Gets the element to display,The return result is true or false.
        Usage:
        driver.get_display("css=>#el")
        """
        el = self.get_element(css)
        return el.is_displayed()

    def get_title(self):
        """
        Get window title.
        Usage:
        driver.get_title()
        """
        return self.driver.title

    def get_url(self):
        """
        Get the URL address of the current page.
        Usage:
        driver.get_url()
        """
        return self.driver.current_url

    def get_alert_text(self):
        """
        Gets the text of the Alert.
        Usage:
        driver.get_alert_text()
        """
        return self.driver.switch_to.alert.text

    def wait(self, secs):
        """
        Implicitly wait.All elements on the page.
        Usage:
        driver.wait(10)
        """
        self.driver.implicitly_wait(secs)

    def accept_alert(self):
        """
        Accept warning box.
        Usage:
        driver.accept_alert()
        """
        self.driver.switch_to.alert.accept()

    def dismiss_alert(self):
        """
        Dismisses the alert available.
        Usage:
        driver.dismiss_alert()
        """
        self.driver.switch_to.alert.dismiss()

    def switch_to_frame(self, css):
        """
        Switch to the specified frame.
        Usage:
        driver.switch_to_frame("css=>#el")
        """
        iframe_el = self.get_element(css)
        self.driver.switch_to.frame(iframe_el)

    def switch_to_frame_out(self):
        """
        Returns the current form machine form at the next higher level.
        Corresponding relationship with switch_to_frame () method.
        Usage:
        driver.switch_to_frame_out()
        """
        self.driver.switch_to.default_content()

    def open_new_window(self, css):
        """
        Open the new window and switch the handle to the newly opened window.
        Usage:
        driver.open_new_window("link_text=>注册")
        """
        original_window = self.driver.current_window_handle
        el = self.get_element(css)
        el.click()
        all_handles = self.driver.window_handles
        for handle in all_handles:
            if handle != original_window:
                self.driver.switch_to.window(handle)

    def get_screenshot(self, file_path):
        """
        Saves a screenshot of the current window to a PNG image file.
        Usage:
        driver.get_screenshot('/Screenshots/foo.png')
        """
        self.driver.get_screenshot_as_file(file_path)

    def select(self, css, value):
        """
        Constructor. A check is made that the given element is, indeed, a SELECT tag. If it is not,
        then an UnexpectedTagNameException is thrown.
        :Args:
         - css - element SELECT element to wrap
         - value - The value to match against
        Usage:
            <select name="NR" id="nr">
                <option value="10" selected="">每页显示10条</option>
                <option value="20">每页显示20条</option>
                <option value="50">每页显示50条</option>
            </select>
            driver.select("#nr", '20')
            driver.select("xpath=>//[@name='NR']", '20')
        """
        el = self.get_element(css)
        Select(el).select_by_value(value)

    def sleep(self, sec):
        """
        sleep(seconds)
        """
        time.sleep(sec)

    def is_element_exist(self, css):
        return self.get_element(css, True) is not None

    def get_element_attribute(self, el, attribute):
        """
        get element attribute
        """
        return el.get_attribute(attribute)

    def get_value(self, el=None, css=None):
        """
        get element value via element or find path
        :param el: given element
        :param css: given find path, css, xpath...
        :return: control text
        """
        if css:
            return self.get_attribute(css, 'value')
        if el:
            return self.get_element_attribute(el, 'value')
        return None

    def get_element_text(self, el):
        return el.text

    def clear_by_sendkey(self, el):
        while self.get_value(el) is not '':
            el.send_keys(Keys.BACKSPACE)

    def get_elements(self, css, silence=False):
        by, value = SeleniumLib.__handle_css(css)
        time_out_error = "定位元素超时, 请尝试其他定位方式.\n定位path: {}".format(css)
        if by == "id":
            req = self.wait_element((By.ID, value))
            if req is True:
                element = self.driver.find_elements_by_id(value)
            else:
                if silence:
                    return None
                raise TimeoutException(time_out_error)
        elif by == "name":
            req = self.wait_element((By.NAME, value))
            if req is True:
                element = self.driver.find_elements_by_name(value)
            else:
                if silence:
                    return None
                raise TimeoutException(time_out_error)
        elif by == "class":
            req = self.wait_element((By.CLASS_NAME, value))
            if req is True:
                element = self.driver.find_elements_by_class_name(value)
            else:
                if silence:
                    return None
                raise TimeoutException(time_out_error)
        elif by == "link_text":
            req = self.wait_element((By.LINK_TEXT, value))
            if req is True:
                element = self.driver.find_elements_by_link_text(value)
            else:
                if silence:
                    return None
                raise TimeoutException(time_out_error)
        elif by == "xpath":
            req = self.wait_element((By.XPATH, value))
            if req is True:
                element = self.driver.find_elements_by_xpath(value)
            else:
                if silence:
                    return None
                raise TimeoutException(time_out_error)
        elif by == "css":
            req = self.wait_element((By.CSS_SELECTOR, value))
            if req is True:
                element = self.driver.find_elements_by_css_selector(value)
            else:
                if silence:
                    return None
                raise TimeoutException(time_out_error)
        else:
            raise NameError(
                "Please enter the correct targeting elements,'id','name','class','link_text','xpath','css'.")
        return element

    def get_elements_value_list(self, css):
        """
        get elements attribute [value]
        :param css:
        :return:
        """
        el_text_list = []
        elements = self.get_elements(css)
        for el in elements:
            el_text_list.append(self.get_value(el))
        return el_text_list

    def get_elements_text_list(self, css):
        """
        get elements text list
        :param css:
        :return:
        """
        el_text_list = []
        elements = self.get_elements(css)
        for el in elements:
            el_text_list.append(el.text)
        return el_text_list

    @staticmethod
    def __handle_css(css):
        """
        Judge element positioning way, and returns the elements.
        """
        if "=>" not in css:
            if css.startswith("//"):
                by = "xpath"
                value = css
            else:
                by = "css"
                value = css
        else:
            by = css.split("=>")[0]
            value = css.split("=>")[1]
            if by == "" or value == "":
                raise NameError(
                    "Grammatical errors, please add prefix 'method=>' except via css, xpath. reference: id=>username'.")
        return by, value

    def move_to_click(self, css):
        """
        move to element and click
        """
        el = self.get_element(css)
        ActionChains(self.driver).move_to_element(el).perform()
        el.click()

    def get_elements_via_element(self, el, css, silence=False):
        by, value = SeleniumLib.__handle_css(css)
        time_out_error = "定位元素超时, 请尝试其他定位方式.\n定位path: {}".format(css)
        if by == "xpath":
            elements = el.find_elements_by_xpath(value)
            if elements:
                return elements
            if silence:
                return None
            raise TimeoutException(time_out_error)
        elif by == "css":
            elements = el.find_elements_by_css_selector(value)
            if elements:
                return elements
            if silence:
                return None
            raise TimeoutException(time_out_error)
        else:
            raise NameError(
                "Please enter the correct elements locator, only support 'xpath','css'.")

    def get_element_via_element(self, el, css, silence=False):
        by, value = SeleniumLib.__handle_css(css)
        time_out_error = "定位元素超时, 请尝试其他定位方式.\n定位path: {}".format(css)
        if by == "xpath":
            element = el.find_element_by_xpath(value)
            if not element:
                if silence:
                    return None
                raise TimeoutException(time_out_error)
        elif by == "css":
            element = el.find_element_by_css_selector(value)
            if not element:
                if silence:
                    return None
                raise TimeoutException(time_out_error)
        else:
            raise NameError(
                "Please enter the correct targeting element locator, only support 'xpath','css'.")
        return element

    def select_drop_down_list(self, drop_down_trigger, drop_ul_li, value):
        """
        select item for drop down box.
        :param drop_down_trigger: target drop down box trigger
        :param drop_ul_li: active li
        :param value: the value need to select
        """
        self.click(drop_down_trigger)
        li_list = self.get_elements(drop_ul_li)
        for li in li_list:
            self.sleep(0.5)
            if self.get_element_text(li) == value:
                li.click()
                self.sleep(0.5)
                return
        raise NoSuchElementException("failed to select! Not found [{}] in Drop Down List. Please check!".format(value))


