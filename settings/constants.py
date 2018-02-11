input_home = ['/eos/atlas/atlascerngroupdisk/trig-daq/ART' ]
project_home = '/eos/user/a/atrvshft/www/TriggerEDMSizeMonitoring' 
archive_home = ['/eos/user/a/atrvshft/www/TriggerEDMSizeMonitoring/archive']
summary_home = ['/eos/user/a/atrvshft/www/TriggerEDMSizeMonitoring/summary']
web_home = ['/eos/user/a/atrvshft/www/TriggerEDMSizeMonitoring/webpage']

ART = ['ART']
branches = ['*'] 
projects = ['*']
platforms = ['*']
timestamps = ['20*-*-*T*']
year = ['*']
month = ['*']
day = ['*']
time = ['*H*M']
samples = ['*']
test = ['TrigAnalysisTest']

triginfo_file = ['AOD.pool.root.checkFiletrigSize.txt']
additional_files = ['AOD.pool.root.checkFile',
                    'AOD.pool.root.checkFile0',
                    '*_script_log'
]

input_files = triginfo_file + additional_files 

# input_files = ['AOD.pool.root.checkFiletrigSize.txt',
#                'AOD.pool.root.checkFile',
#                'AOD.pool.root.checkFile0',
#                '*_script_log'
# ]
archived_files = [input_file + '.gz' for input_file in input_files]

input_path_structure = (input_home, branches, projects, platforms,
       	       	        timestamps, test, samples, input_files)

archive_path_structure = (archive_home, ART, year, month, day,
                          branches, projects, time, platforms,
                          samples, archived_files)


# The following needs revision:
# if active adds one extra line like this one 
#
# 2018 2 1 21.0 Athena 21H53M x86_64-slc6-gcc62-opt test_mc_pp_v7_rdotoaod_grid 0
#
# in the summary files triggerTotal.txt.
# Temporarily solved by using
# a single-element input_files

