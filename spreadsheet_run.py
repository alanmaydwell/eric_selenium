#!/usr/bin/env/ python

#More secure password input
import getpass
import time

# Command-line argument handling
import sys

#Used to read spreadsheet
import openpyxl

# Generic function timer
from eric import fn_timer
# import eric Webdriver handling
from eric import Eric



class ExcelRun(object):
    def __init__(self, filename=""):
        """
        Uses Selenium to carry out various CCR activities based on data
        data from specially formatted spredsheet.
        Args:
            filename - Excel file with test data
        """
        # Selenium runer
        self.eric = Eric()
        # Excel filename
        self.filename = filename
        # Row where columns headings are located
        self.heading_row = 5

    def run(self):
        """Run using data from spreadsheet"""
        #Try to open spreadsheet
        self.open_spreadsheet()

        #Check that required tabs are present and give up if any missing
        essential_tabs = ["Scenario", "Results"]
        missing_tabs = [tab for tab in essential_tabs if tab not in self.wb.sheetnames]
        if missing_tabs:
            print "Excel file:", self.filename
            print "Ending - required tab(s) missing: "+ ", ".join(missing_tabs)
            return "Missing tabs: "+", ".join(missing_tabs)

        # The scenario sheet
        ss = self.wb.get_sheet_by_name("Scenario")
        # The results sheet
        rs = self.wb.get_sheet_by_name("Results")

        # Get the starting row to write_results from
        # Read value recorded in spreadsheet but ensure
        # it is below the heading row
        results_start_row = rs["C3"].value
        if results_start_row <= self.heading_row:
            results_start_row = self.heading_row + 1

        # Seet starting results column
        results_start_column = 2

        # Iterate through the scenario rows
        scenario_row  = self.heading_row +1
        results_row = results_start_row
        results_column = results_start_column
        continue_run = True
        while continue_run:
            # Read scenario step
            action = ss.cell(row=scenario_row, column=1).value
            parameter = ss.cell(row=scenario_row, column=2).value
            # make lower-case str
            action = str(action).lower()
            parameter = str(parameter).lower()

            # Record run time to spreadsheet
            rs.cell(row=results_row, column=1).value = time.strftime("%d/%m/%Y - %H:%M:%S")

            # Take action based on step read
            if action == "login":
                rs.cell(row=results_row, column=results_column).value = parameter
                results_column += 1
                launch_time = self.check_login(parameter)
                rs.cell(row=results_row, column=results_column).value = launch_time
                results_column += 1
                #Give up if login was unsuccsessful
                if str(launch_time) == "Login Failed":
                    continue_run = False
            elif action == "search":
                rs.cell(row=results_row, column=results_column).value = parameter
                results_column += 1
                search_time = self.check_search(parameter)
                rs.cell(row=results_row, column=results_column).value = search_time
                results_column += 1
            elif action == "select":
                # Record parameter value
                rs.cell(row=results_row, column=results_column).value = parameter
                results_column +=1
                # Check there are reports available to view
                message, report_names = self.eric.report_list_items()
                # Get selection time if reports are present
                if report_names:
                    select_time = self.check_report_select(parameter)
                    rs.cell(row=results_row, column=results_column).value = search_time
                # Write message if reports absent
                else:
                    rs.cell(row=results_row, column=results_column).value = "No Reports Present"
                results_column += 1
            elif action == "view":
                report_name = self.eric.read_report_choice()
                rs.cell(row=results_row, column=results_column).value = report_name
                results_column +=1
                view_time = self.check_report_view()
                rs.cell(row=results_row, column=results_column).value = view_time
                results_column += 1
            elif action == "newline":
                """Start new results line"""
                results_row += 1
                results_column = results_start_column

            # Advance to next row
            scenario_row += 1

            # Quit if we're at end
            if scenario_row >30 or not action:
                continue_run = False

        # Final actions
        # Update the details of the row reached
        results_row += 1
        rs["C3"].value = results_row

        #Save at end
        self.wb.save(self.filename)

    def check_login(self, url):
        """Login to CCR"""
        username = raw_input("Username:")
        password = password = getpass.getpass(prompt="Password:")
        login_response = self.eric.login(username, password, url)
        if login_response == 0:
            launch_time =  fn_timer(self.eric.open_eric)
        else:
            launch_time = "Login Failed"
        return launch_time

    def check_search(self, account_no):
        search_time = fn_timer(self.eric.search, account_no)
        return search_time

    def check_report_select(self, report_id):
        report_no = int(report_id)-1
        if report_no in (0,1,2,3):
            select_time = fn_timer(self.eric.select_report, report_no)
        else:
            select_time = "Invalid report_id '{}'".format(report_id)
        return select_time

    def check_report_view(self):
        """Response time for report to appear after clicking view button"""
        view_time = fn_timer(self.eric.view_report)
        #Close the report after viewing (not timed currently)
        self.eric.close_report()
        return view_time

    def open_spreadsheet(self):
        try:
            self.wb = openpyxl.load_workbook(filename=self.filename)
        #Give up if fails
        except Exception as e:
            response = self.filename+" - Failed to read: " + e.__doc__
            print response
            print os.getcwd()
            #Give up if unsuccessful
            return response


if __name__ == "__main__":

    if len(sys.argv)>1:
        filename = sys.argv[1:]

    go = ExcelRun("eric_data.xlsx")
    go.run()
    print "Finished"