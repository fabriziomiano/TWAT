input_home = ['/eos/atlas/atlascerngroupdisk/trig-daq/ART' ]
project_home = '/afs/cern.ch/user/f/fmiano/TWAT'
archive_home = ['/afs/cern.ch/user/f/fmiano/TWAT/archive']
summary_home = ['/afs/cern.ch/user/f/fmiano/TWAT/summary']
web_home = ['/afs/cern.ch/user/f/fmiano/TWAT/webpage']
plots_home = ['/afs/cern.ch/user/f/fmiano/TWAT/plots']
# Change to these values when the code will be on atrvshft@lxplus.cern.ch 
# project_home = '/eos/user/a/atrvshft/www/TriggerEDMSizeMonitoring' 
# archive_home = ['/eos/user/a/atrvshft/www/TriggerEDMSizeMonitoring/archive']
# summary_home = ['/eos/user/a/atrvshft/www/TriggerEDMSizeMonitoring/summary']
# web_home = ['/eos/user/a/atrvshft/www/TriggerEDMSizeMonitoring/webpage']
# plots_home = ['/eos/user/a/atrvshft/www/TriggerEDMSizeMonitoring/plots']

ART = ['ART']
branches = ['*'] 
projects = ['*']
platforms = ['*']
timestamps = ['20*-*-*T*']
year = ['*']
month = ['*']
day = ['*']
clock = ['*H*M']
samples = ['*']
test = ['TrigAnalysisTest']

triginfo_file = ['AOD.pool.root.checkFiletrigSize.txt']
additional_files = ['AOD.pool.root.checkFile',
                    'AOD.pool.root.checkFile0',
                    '*_script_log'
]

input_files = triginfo_file + additional_files 
archived_files = [input_file + '.gz' for input_file in input_files]

input_path_structure = (input_home, branches, projects, platforms,
       	       	        timestamps, test, samples, input_files)

archive_path_structure = (archive_home, ART, year, month, day,
                          branches, projects, clock, platforms,
                          samples, archived_files)

summary_file = ['trigger']

trig_categories = ['Total', 'Bjet', 'Bphys', 'Calo',\
                   'Combined', 'Cosmics', 'Egamma',\
                   'HeavyIon','Jet','L1','MET','MinBias',\
                   'Muon','Steer','Tau','Tracking']

summary_files = [f + category + '.txt' for f in summary_file for category in trig_categories]


summary_files_path_structure = (summary_home, ART, year, month, day,
                          branches, projects, clock, platforms,
                               samples, summary_files)


