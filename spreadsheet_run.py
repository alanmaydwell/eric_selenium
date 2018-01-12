#More secure password input
import getpass
import time

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

    def run(self, endrow=20):
        """Run using data from spreadsheet
        Args:
            endrow (int) - maximum row number when reading scenarios from
                           run tab. Optional - defaults to 20
        """
        #Try to open spreadsheet
        self.open_spreadsheet()

        #Check that required tabs are present and give up if any missing
        essential_tabs = ["Scenario", "Results"]
        missing_tabs = [tab for tab in essential_tabs if tab not in self.wb.sheetnames]
        if missing_tabs:
            print "Excel file:", self.filename
            print "Ending - required tab(s) missing: "+ ", ".join(missing_tabs)
            return "Missing tabs: "+", ".join(missing_tabs)

        #Find positions of each expected column heading
        r_columns = self.excel_column_positions("Results",
                                               heading_row=self.heading_row,
                                               leftcol=1,
                                               maxcol=14)

        # The scenario sheet
        ss = self.wb.get_sheet_by_name("Scenario")
        # The Results tab
        rs = self.wb.get_sheet_by_name("Results")

        # Get the starting row to write_results from
        # Read value recorded in spreadsheet but ensure
        # it is below the heading row
        results_start_row = rs["C3"].value
        if results_start_row <= self.heading_row:
            results_start_row = self.heading_row + 1

        # Iterate through the scenario rows
        scenario_row  = self.heading_row +1
        results_row = results_start_row
        continue_run = True
        while continue_run:
            # Read scenario step
            action = ss.cell(row=scenario_row, column=1).value
            parameter = ss.cell(row=scenario_row, column=2).value
            # make lower-case str
            action = str(action).lower()
            parameter = str(parameter).lower()

            # Record run time to spreadsheet
            rs.cell(row=results_row, column=r_columns["date/time"]).value = time.strftime("%d/%m/%Y - %H:%M:%S")

            # Take action based on step read
            if action == "login":
                launch_time = self.check_login(parameter)
                rs.cell(row=results_row, column=r_columns["url"]).value = parameter
                rs.cell(row=results_row, column=r_columns["launch"]).value = launch_time
            elif action == "search":
                rs.cell(row=results_row, column=r_columns["account"]).value = parameter
                search_time = self.check_search(parameter)
                rs.cell(row=results_row, column=r_columns["search"]).value = search_time
            elif action == "view":
                pass

            # Advance to next row
            scenario_row += 1
            results_row += 1
            #rs["C3"].value += 1
            # Quit if we're at end
            if scenario_row >10 or not action:
                continue_run = False

        ##for current_row in range(results_start_row, results_start_row+10):
            ##rs.cell(row=current_row, column=r_columns["message"]).value = current_row

        #Save at end
        self.wb.save("A"+self.filename)

    def check_login(self, url):
        """Login to CCR"""
        username = raw_input("Username:")
        password = password = getpass.getpass(prompt="Password:")
        self.eric.login(username, password, url)
        launch_time =  fn_timer(self.eric.open_eric)
        return launch_time

    def check_search(self, account_no):
        search_time = fn_timer(self.eric.search, account_no)
        return search_time

    def check_report(self, report_id):
        pass

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

    def excel_column_positions(self, tab, heading_row=6, leftcol=1, maxcol=20):
        """Finds the positions of columns in spreadsheet bases on unique
        text labels in a heading row.

        Args:
            tab - Name of tab on which to look
            heading_row - row number in which to look
            leftcol - first column to examine (as number)
            maxcol - last column to examine (as number)

        Returns:
            dirctionary with text labels as keys and column numbers as values
            e.g. {"Name":1, "Date":2, "ID":3 }
        """
        #Select tab
        ws = self.wb.get_sheet_by_name(tab)
        #Read headings (will be used as dictionary keys)
        #and map to its column number to make reading easier
        heading_columns = {}
        for column in range(leftcol, maxcol+1):
            val = ws.cell(row=heading_row, column=column).value
            if val:
                val = str(val).lower()#ensure lower-case
                heading_columns[val] = column
        return heading_columns


go = ExcelRun("eric_data.xlsx")
go.run()