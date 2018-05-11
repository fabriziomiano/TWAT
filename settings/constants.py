import os
import datetime
import time as time_module

INPUT_HOME = ['/eos/atlas/atlascerngroupdisk/trig-daq/ART']
PROJECT_HOME = '/eos/user/a/atrvshft/www/TriggerEDMSizeMonitoring'
ARCHIVE_HOME = ['/eos/user/a/atrvshft/www/TriggerEDMSizeMonitoring/archive']
WWW_HOME = '/eos/user/a/atrvshft/www/TriggerEDMSizeMonitoring/webpage'

LOG_DIRECTORY = "logs"
LOG_FILE_NAME = os.path.join(
    LOG_DIRECTORY,
    "archive_" + time_module.strftime('%Y-%m-%d') + ".out")

TODAY = datetime.datetime.now()
WEEKDAY = TODAY.strftime("%w")

ART = ['ART']
BRANCHES = ['*']
PROJECTS = ['*']
PLATFORMS = ['*']
TIMESTAMPS = ['20*-*-*T*']
YEARS = ['*']
MONTHS = ['*']
DAYS = ['*']
CLOCK = ['*H*M']
SAMPLES = ['*']
TEST = ['TrigAnalysisTest']

TRIGINFO_FILE = ['AOD.pool.root.checkFiletrigSize.txt']
ADDITIONAL_FILES = ['AOD.pool.root.checkFile',
                    'AOD.pool.root.checkFile0',
                    '*_script_log'
                    ]
INPUT_FILES = TRIGINFO_FILE + ADDITIONAL_FILES
INPUT_PATH_STRUCT = (INPUT_HOME, BRANCHES, PROJECTS, PLATFORMS,
                     TIMESTAMPS, TEST, SAMPLES, INPUT_FILES)

ARCHIVED_FILES = [input_file for input_file in INPUT_FILES]
ARCHIVE_PATH_STRUCT = (ARCHIVE_HOME, ART, YEARS, MONTHS, DAYS,
                       BRANCHES, PROJECTS, CLOCK, PLATFORMS,
                       SAMPLES, ARCHIVED_FILES)
