"""
Read ART result archive from input_home and:
 - create new archive like
input_home/ART/2018/2/1/21.0/Athena/21H53M/x86_64-slc6-gcc62-opt/test_mc_pp_v7_rdotoaod_grid/AOD.pool.root.checkFiletrigSize.txt.gz

 - create new summary writing out summary files for dedicated trigger categories like
summary_home/ART/21.0/Athena/x86_64-slc6-gcc62-opt/test_mc_pp_v7_rdotoaod_grid/triggerMET.txt

"""

import logging, logging.handlers
import time as time_module
import os, glob, datetime, gzip
from itertools import product
from utils.misc import *
from settings.constants import *
from classes.BufferingSMTPHandler import BufferingSMTPHandler
from utils.misc import utils_log

splash_screen(TODAY, WEEKDAY)

dirs = []

# Create logger
logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)
# Add  file handler
# TODO: try to use RotatingFileHandler and doRollover
# instead of 'set_consecutive'
create_nonexistent_archive(LOG_DIRECTORY)
log_file = set_consecutive(LOG_FILE_NAME)
file_handler = logging.FileHandler(log_file, mode='w')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
# Add email handler
email_handler = BufferingSMTPHandler(MAILHOST, FROM, TO, SUBJECT, 100)
email_handler.setLevel(logging.ERROR)
logger.addHandler(email_handler)
# Add handlers to utils_log
utils_log.addHandler(file_handler)
utils_log.addHandler(email_handler)


for pattern_fields in product(*INPUT_PATH_STRUCT):
    pattern = os.path.join(*pattern_fields)
    for file_toarchive in glob.glob(pattern):
        logger.info('Getting info from ART path = %s \n',
                    file_toarchive)
        input_file = os.path.basename(file_toarchive)        
        input_info = extract_path_info(file_toarchive, INPUT_HOME[0])

        archive_path = set_archive_path(input_info)
        summary_path = set_summary_path(input_info)

        create_nonexistent_archive(archive_path)
        destination_file = os.path.join(archive_path, input_file + '.gz')
        if not os.path.exists(destination_file):
            copy_and_compress(file_toarchive, archive_path)
            dirs+=[file_toarchive]

        create_nonexistent_archive(summary_path)
            
        trigger_categories, total_size = get_trigsize(destination_file)
        write_triginfo_to_file(input_info, summary_path,
                               trigger_categories, total_size)

            
if len(dirs) > 0:
    logger.info('%s files successfully archived. Done \n',
                len(dirs))
else:
    logger.info('\t No new files were added to the archive\n')
