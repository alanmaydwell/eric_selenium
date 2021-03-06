#!/usr/bin/env/ python

"""
Selenium script that logs-in to Eric
Measures time taken my some actions.

Mainly intended to be a module used by other scripts.
However, can be run directly
"""

import time
import getpass

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

# Needed to set particular Firefox profile in Selenium (e.g. for Modify Headers)
from selenium.webdriver.firefox.webdriver import FirefoxProfile

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


def table_extract(table):
    """Extract content from an html table.
    Args:
        Webdriver element associated with the html table. Ideally the table
        itself but container such as div should work too.
    Returns:
        list of lists (rows, columns) containing <th> and <td> text
    """
    table_content = []
    rows = table.find_elements_by_tag_name("tr")
    for row in rows:
        for tag in ("th", "td"):
            row_text = [e.text for e in row.find_elements_by_tag_name(tag)]
            if row_text:
                table_content.append(row_text)
    return table_content


class Eric(object):
    """Uses Webdriver to interact with Eric"""
    def __init__(self):
        # Text of link used to open application from Portal
        self.application_link = "Management Information (MI)"
        # When True, Browser window is placed at x-coordinate -3000 to hide it.
        self.offscreen = False

    def check_page_blocked(self):
        """
        Check to see if page update is blocked by "Please Wait" message
        Return True if blocked, False if not blocked
        """
        blocker = self.driver.find_element_by_id("blockingDiv")
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
        #Move window off edge of screen (effecivtely hides it) if flag set
        if self.offscreen:
            driver.set_window_position(3000, 0) # driver.set_window_position(0, 0) to get it bac

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
                                                 or "Authentication failed. Please try again" in driver.page_source
                                                 or "t be displayed" in driver.page_source # Avoiding weird apostrophe! from "can't"
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

    def login_direct(self,
                     url="http://ds01za003:7813/lscapps/eric-emi-murali/AutoLoginServlet",
                     profile_path="" ):
        """Alternative login that uses firefox profile with Modify Headers
        to access Eric without using the portal (doesn't work in every
        Eric instance but does with DEV10).

        Args:
            url - "auto login" url
            profile_path - path to Firefox profile with apporpriate Modify
                Headers details.
        """
        ffp_object = FirefoxProfile(profile_path)
        # Use Webdriver to open Firefox using chosen profile
        self.driver = webdriver.Firefox(ffp_object)
        # Open the URL
        self.driver.get(url)
        # Check expected page is present
        WebDriverWait(self.driver, 20).until(lambda driver:
                                        "reports found for" in driver.page_source
                                        or "0 report(s) found for user" in driver.page_source)
        # Wait for "please wait" message to go
        WebDriverWait(self.driver, 20).until(lambda driver: not self.check_page_blocked())

    def open_eric(self):
        """ Click Eric link in portal and wait for Eric app to open"""
        driver = self.driver
        # Click the Hyperlink
        driver.find_element_by_link_text(self.application_link).click()
        # Wait for the Eric Window to open, then switch to it.
        WebDriverWait(driver, 20).until(lambda x: len(x.window_handles) == 2, self.driver)
        newwindow = driver.window_handles[-1]
        driver.switch_to_window(newwindow)
        # Check expected page is present
        WebDriverWait(driver, 20).until(lambda driver:
                                        "reports found for" in driver.page_source
                                        or "0 report(s) found for user" in driver.page_source)
        # Wait for "please wait" message to go
        WebDriverWait(driver, 20).until(lambda driver: not self.check_page_blocked())

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
        WebDriverWait(driver, 20).until(lambda driver: not self.check_page_blocked())

    def report_list_items(self):
        """Finds which reports are listed
        Should either be 0 or the 4/6 standard reports

        "Civil financial statement",
        "Criminal financial statement"
        "Family mediation financial statement"
        "Financial statement summary"

        Returns search result message, list of report names,
        eg. "4 reports found for 2N875V", [u'Civil financial statement', u'Criminal financial statement',
        u'Family mediation financial statement', u'Financial statement summary']

        """
        driver = self.driver

        # No convenient locators for these items. Also response message
        # in different location if search unsuccessful
        # If report search successful, there's a div on the page
        # If search was successful there's a "tableBoxIndHalf2" div

        results_div = driver.find_elements_by_class_name("tableBoxIndHalf2")
        # Search result has reports
        if results_div:
            div = results_div[0]
            report_names = [e.text for e in div.find_elements_by_tag_name("a")]
            message = div.find_element_by_tag_name("p").text
        # Search result has no reports
        else:
            report_names = []
            message = driver.find_element_by_tag_name("ul").text

        return message, report_names

    def select_report(self, report=0):
        """
        Select Report on Eric Main Screen by position (from 0)
        or by name.
        Only selects, does not open.
        Args:
            report - either (int) report position (0 to 5)
                     or (str) the full report name
        """
        #reports = ["Civil financial statement",
        #           "Criminal financial statement",
        #           "Family mediation financial statement",
        #           "Financial statement summary"]

        # Find the report name present on screen

        driver = self.driver
        # If position provided, find the associated report name
        if type(report) is int:
            _, reports = self.report_list_items()
            report_text = reports[report]
        # Otherwise just use the supplied value
        else:
            report_text = report

        driver.find_element_by_link_text(report_text).click()
        # Wait for "please wait" to go
        WebDriverWait(driver, 20).until(lambda driver: not self.check_page_blocked())

    def read_report_choice(self):
        """Returns the name of the report currently selected"""
        driver = self.driver
        # No convenient identifier.
        # Also not always present
        # Also report text is in the 2nd h3 tag
        h3_texts = [e.text for e in driver.find_elements_by_tag_name("h3")]
        report_name = ""
        if len(h3_texts) == 2:
            report_name = h3_texts[-1]
        return report_name

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
                          if e.get_attribute("value") == "View Report"]
        button = input_elements[0]
        button.click()
        # Report is in a new window - switch to it
        driver.switch_to_window(driver.window_handles[-1])
        # Wait for "Please Wait to go"
        WebDriverWait(driver, 20).until(lambda driver: not self.check_page_blocked())

    def get_report_details(self, get_source=True, get_cells=False):
        """Extract details from already open report.
        Args:
            get_source (bool) - When True, get page source and return
            as "source" element of content dictionary
            get_cells (bool) - When True, get contents of each HTML table cell in
                3-level list - table, row, column. Returned as cells element
                of content dictionary. n.b. can be slow (>25 seconds)
        Returns:
                Report details indictionary
        """
        driver = self.driver

        #Holds report content - three layers: table, row, column
        content = {"source":"", "cells":[]}
        #Add report title to cells
        content["cells"].append([[driver.find_element_by_tag_name("h3").text]])

        # Report is in an iframe
        report_frame = driver.find_element_by_id("reportContent")
        driver.switch_to_frame(report_frame)

        if "Empty Report" in driver.page_source:
            content["cells"]=([["Empty Report"]])

        # Just get the whole source
        if get_source:
            content["source"] = driver.page_source.encode('utf-8')
        # Extract each table individually
        if get_cells:
            # Results are in four tables within (Summary, Detail, Additional, Payments)
            tables = driver.find_elements_by_tag_name("table")
            #Extract details from each table individually
            for ti, table in enumerate(tables):
                ##table_details = table.get_attribute('outerHTML')
                ## table_details = table_details.encode('utf-8')

                # Extract rows and columns as list of lists
                # using table_extract function
                table_details = table_extract(table)
                content["cells"].append(table_details)

        # Leave the iframe
        driver.switch_to_default_content()
        return content

    def close_report(self):
        """
        Click close report button
        Return focus back to main Eric window.
        """
        driver = self.driver
        # Buttons lack convenient labels. Finding by tag name
        button_div = driver.find_element_by_id("buttons2")
        buttons = button_div.find_elements_by_tag_name("a")
        # Click the "Close Report" button (assuming its the last one)
        buttons[-1].click()
        # Return Window focus
        driver.switch_to_window(driver.window_handles[-1])

    def log_out(self):
        """Log out from Eric and the Portal (if present)
        Note if accessed using Modify Headers, Portal logout not possible.
        """
        driver = self.driver
        window_count = len(driver.window_handles)
        # Click Eric logout link
        driver.find_element_by_link_text("Log out").click()

        # Follow-up Portal logout
        if window_count ==2:
            # Wait for the Eric window to close
            WebDriverWait(driver, 20).until(lambda x: len(x.window_handles) == 1, self.driver)
            # Ensure focus is on the portal window
            driver.switch_to_window(driver.window_handles[0])
            # Click the portqal log out link
            driver.find_element_by_link_text("Log Out").click()
            # Wait for confirmation message
            WebDriverWait(driver, 20).until(lambda driver: '<h1 class="heading-xlarge">Logged Out</h1>' in driver.page_source)
        # Non portal
        else:
            WebDriverWait(driver, 20).until(lambda driver: "You have successfully logged out of EMI application" in driver.page_source)

    def close(self):
        """Shutdown webdriver"""
        self.driver.close()

# Management Information
if __name__ == "__main__":
    print "Started"
    url = "https://syssso10.laadev.co.uk/"
    username = "pear-s"
    password = getpass.getpass(prompt="Password:")
    test = Eric()

    # Login to Portal (not timed)
    login_result = test.login(username, password, url)
    print "\nPortal login result:", login_result

    # Open CCR from Portal Link
    launch_time = fn_timer(test.open_eric)
    print url
    print "CCR launch time:", launch_time

    # Perform Search in CCR
    search_time = fn_timer(test.search, "0G934M")
    print "Search time:", search_time

    # Show which reports were found (not timed)
    message, report_list = test.report_list_items()
    print message

    # Select each report in turn and view it
    for report_no in [0, 1, 2, 3]:
        print "\nTimings for report:", report_no
        # Select the report
        print "Select:", fn_timer(test.select_report, report_no)
        print "Found:", test.read_report_choice()
        # View the selected report
        print "View:", fn_timer(test.view_report)
        # Examine report details - not complete
        ##test.examine_report_details()
        # Close the report (not timed)
        test.close_report()

    print "Finished"
