"""
Read ART result archive and 
create new archive within art_home like
ART/2018/2/1/21.0/Athena/21H53M/x86_64-slc6-gcc62-opt/test_mc_pp_v7_rdotoaod_grid 

"""
import logging, logging.handlers
from classes.BufferingSMTPHandler import BufferingSMTPHandler
from utils.misc import utils_log
import time as time_module
import os, glob, datetime, gzip
from itertools import product
from utils.misc import *
from settings.constants import *


MAILHOST = 'localhost'
FROM = 'fmiano@lxplus.cern.ch'
TO = ['fabriziomiano@gmail.com']
SUBJECT = 'TWAT test'

LOG_DIRECTORY = "logs"
LOG_FILE_NAME = os.path.join(
    LOG_DIRECTORY,
    "archive_" + time_module.strftime('%Y-%m-%d') + ".out")
today = datetime.datetime.now()
weekday = today.strftime("%w")

splash_screen(today, weekday)

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

for pattern_fields in product(*input_path_structure):
    pattern = os.path.join(*pattern_fields)
    for file_toarchive in glob.glob(pattern):
        logger.info('Getting info from ART path = %s \n',
                    file_toarchive)
        input_file = os.path.basename(file_toarchive)        
        input_info = extract_path_info(file_toarchive, input_home[0])
        archive_path = os.path.join(archive_home[0], 'ART', \
                                    str(input_info["datetime"].year), \
                                    str(input_info["datetime"].month), \
                                    str(input_info["datetime"].day), \
                                    str(input_info["branch"]), \
                                    str(input_info["project"]), \
                                    str(input_info["datetime"].hour) + 'H' + \
                                    str(input_info["datetime"].minute) + 'M', \
                                    str(input_info["platform"]), \
                                    str(input_info["sample"])
        )
        create_nonexistent_archive(archive_path)
        destination_file = os.path.join(archive_path, input_file + '.gz')
        if not os.path.exists(destination_file):
            copy_and_compress(file_toarchive, archive_path)
            dirs+=[file_toarchive]
            
if len(dirs) > 0:
    logger.info('%s files successfully archived. Done \n',
                len(dirs))
else:
    logger.info('\t No new files were added to the archive\n')

# file_handler.close()
# logger.removeHandler(file_handler)
