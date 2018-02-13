"""
Read created archive from a path like
ART/2018/2/1/21.0/Athena/21H53M/x86_64-slc6-gcc62-opt/test_mc_pp_v7_rdotoaod_grid 
and write out summary files for dedicated trigger categories

"""
import time as time_module
from classes.BufferingSMTPHandler import BufferingSMTPHandler
from utils.misc import utils_log
import os, glob, datetime, gzip
from itertools import product
from utils.misc import *
from settings.constants import *

dirs = []

MAILHOST = 'localhost'
FROM = 'fmiano@lxplus.cern.ch'
TO = ['giosue.ruscica@gmail.com']
SUBJECT = 'TWAT test'

LOG_DIRECTORY = "logs"
LOG_FILE_NAME = os.path.join(
    LOG_DIRECTORY,
    "summary_" + time_module.strftime('%Y-%m-%d') + ".out")

# Set logger and its handlers
create_nonexistent_archive(LOG_DIRECTORY)
log_file = set_consecutive(LOG_FILE_NAME)
logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(log_file, mode='w')
email_handler = BufferingSMTPHandler(MAILHOST, FROM, TO, SUBJECT, 100)
file_handler.setLevel(logging.INFO)
email_handler.setLevel(logging.ERROR)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(email_handler)
utils_log.addHandler(file_handler)
utils_log.addHandler(email_handler)

for pattern_fields in product(*archive_path_structure):
    pattern = os.path.join(*pattern_fields)
    for archived_file in glob.glob(pattern):
        input_file = os.path.basename(archived_file)
        if input_file.strip('.gz') not in triginfo_file: continue
        
        logger.info("Getting info from archived file = %s\n",
                    archived_file)
        
        summary_path = set_summary_path(archived_file)
        create_nonexistent_archive(summary_path)
        
        trigger_categories, total_size = get_trigsize(archived_file)
        write_triginfo_to_file(
            summary_path, trigger_categories, total_size)
        
