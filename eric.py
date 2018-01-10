#!/usr/bin/env/ python

"""
Selenium script that logs-in to Eric
Measures time taken my some actions.
"""

import time
import getpass

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

def fn_timer(fn, *args, **kwargs):
    """Measures execution time of function
    Args:
        fn - function to execute
        args - arbitary args, passed to fn
        kwargs - arbitary kwargs, passed to fn
    Returns:
        duration in seconds
    """
    t_start = time.time()
    fn(*args, **kwargs)
    t_end = time.time()
    return t_end - t_start

def fn_timer_decorator(fn):
    """
    Alternative to fn_timer
    Decorator that updates function to report its own
    execution time.
    Args:
        fn - function to be decorated
        args - arbitary args, passed to fn
        kwargs - arbitary kwargs, passed to fn
    Returns:
        decorated function
    """
    def temp(*args, **kwargs):
        t_start = time.time()
        fn(*args, **kwargs)
        t_end = time.time()
        return t_end - t_start
    return temp

class Eric(object):

    def __init__(self):
        #Text of link used to open application from Portal
        self.application_link = "Management Information (MI)"

    def check_page_blocked(self):
        """
        Check to see if page update is blocked by "Please Wait" message
        Return True if blocked, False if not blocked

        Relies on whether blockingDiv element is
        on display.
        """
        driver = self.driver
        blocker = driver.find_element_by_id("blockingDiv")
        return blocker.is_displayed()

    def login(self, username, password, url):
        """
        Login to Portal.
        Should work with both new and old Portals.
        Args:
            url: portal url
            username
            password

        Returns 0/1 success/failure code
            Success indicates portal login successful and MI link found
        """
        # Default fail return result
        result = 1
        # Create Webdriver instance
        self.driver = webdriver.Firefox()
        driver = self.driver
        # Open URL
        self.driver.get(url)
        # Wait for page
        WebDriverWait(driver, 10).until(lambda driver:
                                       driver.title == "LAA Online Portal"
                                       or "By logging in to this Portal"
                                       in driver.page_source)

        # Login to Portal - New or Old
        # New Portal
        if driver.title == "LAA Online Portal":
            # Username and password, if values supplied
            driver.find_element_by_name("username").send_keys(username)
            driver.find_element_by_name("password").send_keys(password)
            driver.find_element_by_class_name("button-start").click()
        # Old Portal
        else:
            driver.find_element_by_name("ssousername").send_keys(username)
            driver.find_element_by_name("password").send_keys(password)
            driver.find_element_by_name("submit").click()

        # Wait for response
        try:
            WebDriverWait(self.driver, 20).until(lambda driver:
                                                 ">Logged in as:" in driver.page_source
                                                 or "An incorrect Username or Password was specified" in driver.page_source
                                                 or "t be displayed" in driver.page_source  # Avoiding weird apostrophe! from "can't"
                                                 or "Secure Connection Failed" in driver.page_source)
        except TimeoutException:
            pass

        # Check if login was successful
        if ">Logged in as:" in driver.page_source:
            # Do we have MI link?
            links = [e.text for e in driver.find_elements_by_tag_name("a")]
            if self.application_link in links:
                result = 0

        return result

    def open_eric(self):
        """ Click Eric link in portal and wait for Eric app to open"""
        driver = self.driver
        # Click the Hyperlink
        driver.find_element_by_link_text(self.application_link).click()
        # Wait for the Eric Window to open, then switch to it.
        WebDriverWait(driver,20).until(lambda x: len(x.window_handles)==2,self.driver)
        newwindow = driver.window_handles[-1]
        driver.switch_to_window(newwindow)
        # Check expected page is present
        WebDriverWait(driver,20).until(lambda driver:"<p>4 reports found for" in driver.page_source)
        #Wait for "please wait" message to go
        WebDriverWait(driver,20).until(lambda driver: not self.check_page_blocked())

    def search(self, search_string):
        """Perform search
        Args:
            search_string - text typed into search field
        """
        driver = self.driver
        # Search field and search button lack convenient identifiers
        # Finding by looking for not-hidden input fields in containing div
        div = driver.find_element_by_class_name("tableBoxInd")
        fields = [e for e in div.find_elements_by_tag_name("input")
                  if e.get_attribute("type") != "hidden"]
        # Enter the search text
        fields[0].clear()
        fields[0].send_keys(search_string)
        # Click search button
        fields[1].click()
        # Wait for "please wait" to go
        WebDriverWait(driver,20).until(lambda driver: not self.check_page_blocked())

    def report_list(self):
        """Finds which reports are listed
        Should either be 0 or the 4 standard reports

        "Civil financial statement",
        "Criminal financial statement"
        "Family mediation financial statement"
        "Financial statement summary"

        """
        driver = self.driver
        # If report search successful, there's a div on the page
        # containing the results, otherwise it's abscent

        try:
            div = driver.find_element_by_class_name("tableBoxIndHalf2")
        except NoSuchElementException as e:
            pass
        else:
            reports = [e.text for e in div.find_elements_by_tag_name("a")]
            message = div.find_element_by_tag_name("p").text
            print reports
            print message
            print ""


    def select_report(self, report_no=0):
        """
        Select Report on Eric Main Screen by position (from 0 to 3)
        (only selects, does not open)
        Args:
            report_no - report position (0 to 3)
        """
        reports = ["Civil financial statement",
                   "Criminal financial statement",
                   "Family mediation financial statement",
                   "Financial statement summary"]
        driver = self.driver
        report = reports[report_no]
        driver.find_element_by_link_text(report).click()
        # Wait for "please wait" to go
        WebDriverWait(driver,20).until(lambda driver: not self.check_page_blocked())

    def view_report(self):
        """
        Click the "View Report" button
        Switch focus to new report window that appears.
        Wait for "Please Wait" message to dissapear.
        """
        driver = self.driver
        # Click "View Report" button
        # lacks a convenient identifier
        # Accessing via its parent form
        form = driver.find_element_by_id("ReportDetailsForm")
        # Contains multiple "input" fields, filter to get right one
        input_elements = [e for e in form.find_elements_by_tag_name("input")
                          if e.get_attribute("value")=="View Report"]
        button = input_elements[0]
        button.click()

        # Report is in a new window
        driver.switch_to_window(driver.window_handles[-1])
        # Wait for "Please Wait to go"
        WebDriverWait(driver,20).until(lambda driver: not self.check_page_blocked())


    def close_report(self):
        """
        Click close report button
        Return focus back to main Eric window.
        """
        driver = self.driver
        # Buttons lack convenient labels. Finding by tag name
        button_div = driver.find_element_by_id("buttons2")
        buttons = button_div.find_elements_by_tag_name("a")
        # Click the "Close Report" button
        buttons[-1].click()
        # Return Window focus
        driver.switch_to_window(driver.window_handles[-1])


    def log_out(self):
        """Click 'Log out' link in Eric"""
        self.driver.find_elements_by_link_text("Log out").click()


# Management Information (MI)
if __name__ == "__main__":
    print "Started"
    url = "https://syssso10.laadev.co.uk/"
    username = "pear-s"
    password = getpass.getpass(prompt="Password:")
    go = Eric()
    result = go.login(username, password, url)
    print result
    go.open_eric()
    for things in ["0G934M", "Mangle", "2N875V"]:
        go.search(things)
        go.report_list()
    """
    for report_no in [0, 1, 2, 3]:
        print fn_timer(go.select_report, report_no)

    go.view_report()
    go.close_report()
    """
    print "Finished"
