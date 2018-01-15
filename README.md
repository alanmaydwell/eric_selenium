# eric_selenium
Webdriver script for Eric

Requires

- Python 2.7
- Webdriver for Python
- Geckodriver

## Files

### eric.py
Carries out simple transaction time measurement in Eric

- Eric class - uses webdriver to perform actions in Eric
- fn_timer - function that measures execution time of function/method passed to it
- "```__main__```" block at end includes simple executatble example

### spreadsheet_run.py
Drives eric.py using scenario data from specially formatted spreadsheet. Results are saved to this spreadsheet too (in different tab).
### eric_data.xlsx
Spreadsheet used by the above
