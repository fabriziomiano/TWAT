"""
Read ART result archive from input_home and:
 - create new archive like
input_home/ART/2018/2/1/21.0/Athena/21H53M/x86_64-slc6-gcc62-opt/test_mc_pp_v7_rdotoaod_grid/AOD.pool.root.checkFiletrigSize.txt

 - 

"""

import copy
import logging
import logging.handlers
import time as time_module
import os
import glob
import datetime
from itertools import product
from classes.BufferingSMTPHandler import BufferingSMTPHandler
from classes.EDM import EDM
from utils.misc import utils_log
from utils.misc import get_logger, set_consecutive, create_nonexistent_archive, \
    set_archive_path, extract_path_info, copy_file, get_trigsize, \
    datetime_to_timestamp, splash_screen
from settings.constants import TODAY, WEEKDAY, LOG_DIRECTORY, LOG_FILE_NAME, \
    INPUT_PATH_STRUCT, INPUT_HOME
from settings.config import MAILHOST, FROM, TO, SUBJECT

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


TEMPLATE_FIELDS = [
    'branch', 'project', 'platform', 'sample', 'category'
]
DB_PATH = 'archive_db.json'


edm = EDM(DB_PATH, TEMPLATE_FIELDS)

for pattern_fields in product(*INPUT_PATH_STRUCT):
    pattern = os.path.join(*pattern_fields)
    for file_toarchive in glob.glob(pattern):
        logger.info('Getting info from ART path = %s \n',
                    file_toarchive)
        input_file = os.path.basename(file_toarchive)
        input_info = extract_path_info(file_toarchive, INPUT_HOME[0])

        archive_path = set_archive_path(input_info)

        create_nonexistent_archive(archive_path)
        destination_file = os.path.join(archive_path, input_file)
        if not os.path.exists(destination_file):
            # copy_and_compress(file_toarchive, archive_path)
            copy_file(file_toarchive, archive_path)
            dirs += [file_toarchive]

        trigger_categories, total_size, total_aod_size = get_trigsize(
            destination_file)
        timestamp = input_info.pop("datetime")
        prefix = 'trigger'
        for trigger_category in trigger_categories:
            category = trigger_category[0]
            if category.startswith(prefix):
                category = category[len(prefix):]
            new_item = copy.deepcopy(input_info)
            new_item.update({'category': category})
            value = {datetime_to_timestamp(timestamp): trigger_category[1]}
            edm.add_test(new_item, value)

        new_item.update({'category': 'Total'})
        value = {datetime_to_timestamp(timestamp): total_size}
        edm.add_test(new_item, value)
        new_item.update({'category': 'TotalAOD'})
        value = {datetime_to_timestamp(timestamp): total_aod_size}
        edm.add_test(new_item, value)

edm.save()

if len(dirs) > 0:
    logger.info('%s files successfully archived. Done \n',
                len(dirs))
else:
    logger.info('\t No new files were added to the archive\n')
