import os,datetime
import time as time_module

# Change to these values when the code will be on atrvshft@lxplus.cern.ch 
# PROJECT_HOME = '/eos/user/a/atrvshft/www/TriggerEDMSizeMonitoring' 
# ARCHIVE_HOME = ['/eos/user/a/atrvshft/www/TriggerEDMSizeMonitoring/archive']
# SUMMARY_HOME = ['/eos/user/a/atrvshft/www/TriggerEDMSizeMonitoring/summary']
# WEB_HOME = ['/eos/user/a/atrvshft/www/TriggerEDMSizeMonitoring/webpage']
# PLOTS_HOME = ['/eos/user/a/atrvshft/www/TriggerEDMSizeMonitoring/plots']
INPUT_HOME = ['/eos/atlas/atlascerngroupdisk/trig-daq/ART' ]
PROJECT_HOME = '/afs/cern.ch/user/f/fmiano/TWAT'
ARCHIVE_HOME = ['/afs/cern.ch/user/f/fmiano/TWAT/archive']
SUMMARY_HOME = ['/afs/cern.ch/user/f/fmiano/TWAT/summary']
WEB_HOME = ['/afs/cern.ch/user/f/fmiano/TWAT/webpage']
PLOTS_HOME = ['/afs/cern.ch/user/f/fmiano/TWAT/plots']


MAILHOST = 'localhost'
FROM = 'atrvshft@lxplus.cern.ch'
TO = ['fabriziomiano@gmail.com']
SUBJECT = 'TWAT test'

LOG_DIRECTORY = "logs"
LOG_FILE_NAME = os.path.join(
    LOG_DIRECTORY,
    "archive_" + time_module.strftime('%Y-%m-%d') + ".out")

RANGE_ACCEPTED = 0.05
REFS_PATH = os.path.join(PROJECT_HOME, 'edm.json')

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

ARCHIVED_FILES = [input_file + '.gz' for input_file in INPUT_FILES]
ARCHIVE_PATH_STRUCT = (ARCHIVE_HOME, ART, YEARS, MONTHS, DAYS,
                          BRANCHES, PROJECTS, CLOCK, PLATFORMS,
                          SAMPLES, ARCHIVED_FILES)

SUMMARY_FILE = ['trigger']
TRIG_CATEGORIES = ['Total', 'Bjet', 'Bphys', 'Calo',\
                   'Combined', 'Cosmics', 'Egamma',\
                   'HeavyIon','Jet','L1','MET','MinBias',\
                   'Muon','Steer','Tau','Tracking']
SUMMARY_FILES = [f + category + '.txt' for f in SUMMARY_FILE\
                 for category in TRIG_CATEGORIES]
SUMMARY_PATH_STRUCT = (SUMMARY_HOME, ART, BRANCHES, PROJECTS,
                                PLATFORMS, SAMPLES, SUMMARY_FILES)
