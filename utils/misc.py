import logging
import datetime as dt
import os
import errno
import gzip
import shutil
from dateutil.parser import parse
from collections import OrderedDict, defaultdict
from settings.constants import *

DATE_FMT = "%Y-%m-%dT%H%M"


def nested_dict(): return defaultdict(nested_dict)


def get_logger(name):
    """ 
    Add a StreamHandler to a logger if still not added and
    return the logger

    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.propagate = 1  # propagate to parent
        console = logging.StreamHandler()
        logger.addHandler(console)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console.setFormatter(formatter)
    return logger


# logger for utils functions
utils_log = get_logger(__name__)
utils_log.setLevel(logging.INFO)


def timestamp_to_datetime(timestamp):
    """ 
    %Y-%m-%dT%H%M -> datetime.datetime() 
    e.g. 2018-02-03T2135 -> datetime.datetime(2018, 2, 3, 21, 35)

    """
    return dt.datetime.strptime(timestamp, DATE_FMT)


def datetime_to_timestamp(datetime):
    return datetime.strftime(DATE_FMT)


def is_date(string):
    try:
        parse(string)
        return True
    except ValueError:
        return False


def set_archive_path(input_info):
    """
    Return archive-path-like string from 
    a dictionary containing all the relevant
    info read from input_home

    """
    archive_path = os.path.join(ARCHIVE_HOME[0], 'ART',
                                str(input_info["datetime"].year),
                                str(input_info["datetime"].month),
                                str(input_info["datetime"].day),
                                str(input_info["branch"]),
                                str(input_info["project"]),
                                str(input_info["datetime"].hour) + 'H' +
                                str(input_info["datetime"].minute) + 'M',
                                str(input_info["platform"]),
                                str(input_info["sample"])
                                )
    return archive_path


def extract_path_info(path, source_home):
    """
    Read info from a given path and
    return dictionary with all the relevant info 

    """
    full_info = path[len(source_home):].split('/')
    relevant_info = {
        "branch": full_info[1],
        "project": full_info[2],
        "platform": full_info[3],
        "sample": full_info[6],
        "datetime": timestamp_to_datetime(full_info[4])
    }
    return relevant_info


def create_nonexistent_archive(path, exc_raise=False):
    """
    Create directory from given path
    Return True if created, False if it exists

    """
    try:
        os.makedirs(path)
        utils_log.info("Created directory with path: %s\n", path)
        return path
    except OSError as e:
        if e.errno != errno.EEXIST:
            utils_log.exception(
                "Could not create directory with path: %s\n", path)
            if exc_raise:
                raise
        return None


def delete_empty_archive(path, exc_raise=False):
    """
    Try to remove a directory at a given path
    Return True if created, otherwise raise error 

    """
    try:
        os.rmdir(path)
        utils_log.warn('Removed empty archive with path: %s\n', path)
        return True
    except OSError as e:
        if e.errno != errno.ENOTEMPTY:
            utils_log.exception("Could not remove path: %s\n", path)
            if exc_raise:
                raise
        utils_log.warn(
            "Directory %s is not empty and was not removed\n", path)


def copy_and_compress(filein_path, destination_path, exc_raise=False):
    """ 
    Copy and compress given input file 
    to a given destination destination directory  
    Raise an error if not possible

    """
    try:
        filein = os.path.basename(filein_path)
        fileout = filein + '.gz'
        fileout_path = os.path.join(destination_path, fileout)
        f_in = open(filein_path, 'rb')
        f_out = gzip.open(fileout_path, 'wb')
        shutil.copyfileobj(f_in, f_out)
        os.system('chmod 644 ' + fileout_path)
        utils_log.info("File\t%s\t archived at: %s\n",
                       filein, fileout_path)
    except IOError as e:
        delete_empty_archive(destination_path)
        utils_log.exception("Failed to copy file from %s\n",
                            filein_path)
        if exc_raise:
            raise
    finally:
        f_out.close()
        f_in.close()


def get_trigsize(input_file, exc_raise=False):
    """
    For a given txt file it returns a tuple 
    with all the trigger categories and 
    their sizes, plus the total size

    Args:
    input_file <string> -- a checkfiletrigsize containing lines such as 
    'Trigger<category> <size>' (e.g. TriggerJet 2.1)
    Returns:
    tuple(trigger_categories, total_size) -- 
    trigger_categories <list(list())> -- a list whose elements are lists
    such as ['TriggerBjet', '2.2']
    total_size <string> -- the sum of all the trigger category sizes

    """
    try:
        trigger_categories = []
        total_size = 0
        f = gzip.open(input_file, "rb")
        for line in f:
            if line.count('from checkFile'):
                total_size = (line.split()[-1]).strip()
            if line.startswith('trigger'):
                trigger_categories += [(line.strip()).split()]
        return (trigger_categories, total_size)
    except IOError as e:
        utils_log.exception("Could not read file: %s\n", input_file)
        if exc_raise:
            raise
    finally:
        f.close()


def write_triginfo_to_file(input_info, summary_path, trigger_categories, total_size):
    """
    For each trigger category it creates a .txt file 
    named after that category. The file created will 
    contain all the summary information
    of that specific category 

    """
    year = str(input_info["datetime"].year)
    month = str(input_info["datetime"].month)
    day = str(input_info["datetime"].day)
    branch = str(input_info["branch"])
    project = str(input_info["project"])
    clock = str(input_info["datetime"].hour) + 'H' +\
        str(input_info["datetime"].minute) + 'M'
    platform = str(input_info["platform"])
    sample = str(input_info["sample"])

    for trigger in trigger_categories:
        fileout_path = os.path.join(summary_path, trigger[0]+".txt")
        info_line = "%s %s %s %s %s %s %s %s %s" %\
            (year, month, day, branch, project,
             clock, platform, sample, trigger[1])

        if not os.path.exists(fileout_path):
            utils_log.info("Creating summary file for %s\n", trigger[0])
        else:
            utils_log.info("Opening summary file for %s\n", trigger[0])

        f = open(fileout_path, "a+")
        f.seek(0)
        found = False
        for line in f:
            if line.strip() == info_line:
                found = True
                break
        if not found:
            utils_log.info("Entering info into summary file: %s = %s\n",
                           trigger[0], trigger[1])
            f.write(info_line+"\n")
        else:
            utils_log.info("Info already in summary file\n")

    fileout_path = os.path.join(summary_path, "triggerTotal.txt")
    info_line = "%s %s %s %s %s %s %s %s %s" %\
        (year, month, day, branch, project, clock, platform, sample, total_size)

    if not os.path.exists(fileout_path):
        utils_log.info(
            "Creating summary file for %s" % "triggerTotal.txt")
    else:
        utils_log.info(
            "Opening summary file for %s" % "triggerTotal.txt")

    f = open(fileout_path, "a+")
    f.seek(0)
    found = False
    for line in f:
        if line.strip() == info_line:
            found = True
            break
    if not found and total_size != 0:
        utils_log.info("Entering info into summary file: %s = %s\n"
                       % ("triggerTotal", total_size))
        f.write(info_line+"\n")
    elif found and total_size != 0:
        utils_log.info("Info already in summary file")
    elif total_size == 0:
        utils_log.info("Skipping this file: %s = %s"
                       % ("triggerTotal is ", total_size))


def set_consecutive(file_path):
    """ 
    Return a string with consecutive id number if file_path exists, 
    else return file_path

    """
    new_path = file_path
    last_id = 0
    while os.path.isfile(new_path):
        last_id += 1
        new_path = file_path + '.' + str(last_id)
    return new_path


##############################################################

def splash_screen(today, weekday):
    print
    print
    print "\t-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
    print
    print "\t ----  Trigger-size Web-display for ART Tests ---- "
    print
    print "\t Author : Fabrizio Miano"
    print "\t Special Thanks to Giosue Ruscica for his support"
    print
    print "\t Run Date : %s" % today.strftime("%A %b %d %Y %H:%M")
    print
    print
    print "\t ART home directory      : %s" % INPUT_HOME
    print "\t Archive home directory  : %s" % ARCHIVE_HOME
    print "\t Webpage home directory  : %s" % WWW_HOME
    print
    print "\t-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
    print

##############################################################
