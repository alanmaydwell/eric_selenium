import sched
import time
import datetime
import subprocess
import os

"""
Scheduler that runs specified Python script at chosen intervals
defined by time(s)of day and days to run.
Relies on sched module to schedule events and
subprocess module to run external scripts.

v0.1 - initial version
v0.2 -
    (i) added create_events() function.
    (ii) Scripts no longer have to be in same folder as present script.
    Full path can now be specified
    (iii) Also more than one script can be scheduled in the same run.
    (iv) Days to run now a list, run_days, rather than integer.
    (iii) Optional log file kept. Uses log_print() function
"""

def run_script(script):
    """Runs chosen python script (in own separate interpreter instance).
    When full path supplied, working directory for
    the script set to the path's location. This is to help it find files
    that share its directory.
    Args:
        script (str) - name of script to run, e.g. test1.py
        If in same folder as present scirpt can just be filename (e.g. "test1.py")
        otherwise specify full path (r"E:\scripts\test1.py")
    """
    #get script's directory, used to set cwd argument.
    path = os.path.dirname(script)
    #Don't use cwd when supplied path is "". Done by setting to None
    if path=="":
        path=None
    log_print(time.strftime("%d-%m-%Y %H:%M:%S")+" - triggered "+os.path.basename(script))
    subprocess.call(["python"]+[script], cwd=path)


def create_events(script, run_times , run_days=[0]):
    """
    Creates events that call specified script at specified times
    throughout day range.
    Args:
        script - filename of script to be run. Can just be filename if in same directory, otherwise full path.
        e.g. "one.py" or r"E:\scripts\test1.py"
        run_times - times of day to run as list of tuple (hour,minute) pairs e.g. [(1,0),(2,45),(3,15)]
        run_days (list of ints) - days on which to run, starting from today. e.g. [0,1,2] for today,tomorrow and day after.
    """
    #Get current date
    today = datetime.date.today()
    #Create daily interval - used for date arithmatic
    day_interval = datetime.timedelta(days=1)

    #Generate event for each run time
    for day_number in run_days:
        run_date = today + day_interval*day_number
        for run_time in run_times:
            schedule_time = datetime.time(*run_time)#*time because need to separate the tuple into 2 args
            schedule_date_time = datetime.datetime.combine(run_date, schedule_time)
            log_print(schedule_date_time.strftime("%d-%m-%Y %H:%M:%S")+" - "+os.path.basename(script))
            #Create the scheduled event which calls run_script()function
            scheduler.enterabs(time.mktime(schedule_date_time.timetuple()), 1, run_script, (script,))


def log_print(text):
    """Prints text like print statement but also optionally writes to log file
    too if global LOGFILE value set
    Args:
        text (str) - text to be printed/logged
    """
    print text
    if LOGFILE:
        with open(LOGFILE,"a") as log:
            log.write(text+"\n")


#Create scheduler object
scheduler = sched.scheduler(time.time, time.sleep)

#Set logfile name, set to "" for no logging
LOGFILE = "scheduler_log.txt"

#Record/show initial info
log_print("*** Python Script Run Scheduler - New Run "+time.strftime("(%d-%m-%Y %H:%M:%S)")+" ***\n")
log_print("Creating Scheduled Events")

# ********************************************
# * Test Data - define scheduled events here *
# ********************************************

#Script 1
#Script to run - this one in same folder as present script
script = "spreadsheet_run.py"
#Times of day to run. List of (hour,minute) tuples
run_times = [(13,56),(12,15),(12,16)]
#Days on which to run from the present day, i.e. 0 for today, 1 for tommorrow, 2 for the day after that, e.g. [0,2,4].
run_days = [0,2,4]
#Create events
create_events(script, run_times, run_days)

# ********************
# * End of Test Data *
# ********************

#Run the scheduler
log_print("\nStarting Scheduler "+time.strftime("(%d-%m-%Y %H:%M:%S)"))
scheduler.run()
log_print("Schedule Completed "+time.strftime("(%d-%m-%Y %H:%M:%S)\n"))
