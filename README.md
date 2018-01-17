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

This is intended to be the main way of running the script.

- Drives eric.py using scenario data from specially formatted spreadsheet. 
- Results are saved to this spreadsheet too (in different tab).
- By default reads spreadsheet with filename eric_data.xlsx but can take an alternative filename as a command-line argument.
- Usernames and passwords can be optionally specified in the spreadsheet. Script will request user input if these items are not present.

### eric_data.xlsx
- Spreadsheet used by the above. 
- See Info tab in spreadsheet for information about how it is used.
- Usernames and passwords are not included in the Github version of the spreadsheet.

## Scheduler

### scheduler.py
- Above can be used to schedule automatic runs of spreadsheet_run.py (or any other python script).

- Automatically creates/adds to simple log file, scheduler_log.txt, but only tracks start-times (no response or completion time captured). 

- Can run any Python file and mutliple schedules can be setup.

- Relies on data recorded within spreadsheet_run.py between the test data start/end comments (lines 94 to 111).

*Example setup*
``` python
# Script to run 
script = "spreadsheet_run.py"

# Times of day to run as list of (hour, minute) tuples
run_times = [(15, 13), (15, 18)]
# Can use list comprehension to generate multiple values
## run_times = [(h, m) for h in (8, 9, 10, 11, 12, 13, 14, 15, 16) for m in (0,5,10,15,20,25,30,35,40,45,50,55)]

# Days on which to run from the present day, i.e. 0 for today, 1 for tomorrow, 2 for the day after that.
run_days = [0, 1, 2]

# Create events
create_events(script, run_times, run_days)

# Can repeat above mutliple times with different settings to schedule
# other runs within the same session.
# create_events is cumulative - can be called multiple times.
```
