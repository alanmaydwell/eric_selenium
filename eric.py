#!/usr/bin/env/ python
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


class Eric(object):

    def __init__(self):
        a=1

    def login(self, username, password, url):
        """
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

        # Was login successful?
        if ">Logged in as:" in driver.page_source:
            # Do we have MI link?
            links = [e.text for e in driver.find_elements_by_tag_name("a")]

            if "Management Information (MI)" in links:
                result = 0

        return result

        def open_eric(self):
            """ Click eric link in portal and wait for Eric app to open"""
            driver = self.driver
            

# Management Information (MI)
if __name__ == "__main__":
    print "Started"
    url = "https://syssso10.laadev.co.uk/"
    username = "pear-s"
    password = "welcome01"
    go = Eric()
    result = go.login(username, password, url)
    print result
    print "Finished"
