# eric_selenium
Webdriver script for Eric that captures simple transaction times.

Requires

- Python 2.7
- Webdriver for Python
- Geckodriver

## Files

### eric.py
Carries out simple transaction time measurement in Eric. Mainly intended to be a module but can also be run directly.

- Eric class - uses webdriver to perform actions in Eric
- fn_timer - function that measures execution time of function/method passed to it
- "```__main__```" block at end includes simple executatble example

### spreadsheet_run.py
Drives eric.py using scenario data from specially formatted spreadsheet. Results are saved to this spreadsheet too (in different tab). By default reads filename eric_data.xlsx but can take an alternative filename as a command-line argument.

Usernames and passwords can be optionally specified in the spreadsheet. Script will request user input if these items are not present.

### eric_data.xlsx
Spreadsheet used by the above. Info tab in spreadsheet contains some information about how it is used. Usernames and passwords are not included in the Github version of the spreadsheet.
