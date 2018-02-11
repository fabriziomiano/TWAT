import datetime as dt
import os, errno, gzip, shutil
from settings.constants import *

def timestamp_to_datetime(timestamp):
    """ 
    %Y-%m-%dT%H%M -> datetime.datetime() 
    e.g. 2018-02-03T2135 -> datetime.datetime(2018, 2, 3, 21, 35)

    """
    return dt.datetime.strptime(timestamp, "%Y-%m-%dT%H%M")


def set_summary_path(archived_file):
    """
    substitute the word 'archive' from 
    a given archive_path with 'summary'
    """ 
    archive_dir = os.path.split(archived_file)[0]
    summary_dir = archive_dir.replace('archive', 'summary')
    return summary_dir
        
        
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


def create_nonexistent_archive(path):
    """
    Create directory from given path
    Return True if created, False if it exists

    """
    try:
        os.makedirs(path)
	print("------> Created directory with path:")
        print path
        return path
    except OSError as e:
        if e.errno != errno.EEXIST:
            print('ERROR :: An error occurred, could not ' +
		  'create directory with path: ',
		  path)
            raise
        return None
    

def delete_empty_archive(path):
    """
    Try to remove a directory at a given path
    Return True if created, otherwise raise error 

    """
    try:
        os.rmdir(path)
        print("WARNING :: Removed empty archive with path: %s " % path)
        return True
    except OSError as e:
        if e.errno != errno.ENOTEMPTY:
            print("ERROR :: Unknown Error occurred")
            raise
        print("WARNING :: Archive is not empty and was not removed")

        
def copy_and_compress(filein_path, destination_path):
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
        print '------> File\t' + filein.split('/')[-1] + '\t archived at: '
        print fileout_path
    except IOError as e:
        delete_empty_archive(destination_path)
        print '------> ERROR :: Failed to copy file. Please run script again.'
        raise
    finally:
        f_out.close()
        f_in.close()
    

def get_trigsize(input_file):
    """
    For a given txt file it returns a tuple 
    with all the trigger categories and 
    their sizes, plus the total size 

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
        return (trigger_categories, total_size);
    except IOError as e:
        print '------> ERROR :: Could not read from file. Please run script again.'
        raise
    finally:
        f.close()

        

def write_triginfo_to_file(summary_path, trigger_categories, total_size):
    """
    For each trigger category it creates a .txt file 
    named after that category. The file created will 
    contain all the summary information
    of that specific category 

    """
    parts = summary_path[len(summary_home[0]):].split('/')
    year = parts[2]
    month = parts[3]
    day = parts[4]
    branch = parts[5]
    project = parts[6]
    time = parts[7]
    platform = parts[8]
    sample = parts[9]

    for trigger in trigger_categories:
        fileout_path = os.path.join(summary_path,trigger[0]+".txt")        
        info_line = "%s %s %s %s %s %s %s %s %s" %\
        (year, month, day, branch, project, time, platform, sample, trigger[1])

        if not os.path.exists(fileout_path):
            print "------> Creating summary file for %s" % trigger[0]
        else:
            print "------> Opening summary file for %s" % trigger[0]

        f = open(fileout_path, "a+")
        f.seek(0)
        found = False
        for line in f:
            if line.strip() == info_line:
                found = True
                break
        if not found:
            print "------> Entering info into summary file : %s = %s" %\
                (trigger[0], trigger[1])
            f.write(info_line+"\n")
        else:
            print "------> Info already in summary file"




    fileout_path = os.path.join(summary_path, "triggerTotal.txt")
    info_line = "%s %s %s %s %s %s %s %s %s" %\
    (year, month, day, branch, project, time, platform, sample, total_size)

    if not os.path.exists(fileout_path):
        print "------> Creating summary file for %s" % "triggerTotal.txt"
    else:
        print "------> Opening summary file for %s" % "triggerTotal.txt"

    f = open(fileout_path, "a+")	
    f.seek(0)
    found = False
    for line in f:
        if line.strip() == info_line:
            found = True
            break
    if not found and total_size != 0:
        print "------> Entering info into summary file : %s = %s" %\
            ("triggerTotal", total_size)
        f.write(info_line+"\n")
    elif found and total_size != 0:
        print "------> Info already in summary file"
    elif total_size == 0:
        print "------> Skipping this file : %s = %s" %\
            ("triggerTotal is ", total_size)
                    
                







##############################################################

def splash_screen(today, weekday):
    print
    print
    print "\t-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
    print
    print "\t ----  Trigger-size Web-display for ART Tests ---- "
    print
    print " Author : Fabrizio Miano" 
    print
    print "\t Run Date : %s" % today.strftime("%A %b %d %Y %H:%M") 
    print
    print
    print "\t ART home directory     : %s" % input_home
    print "\t Archive home directory  : %s" % archive_home
    print "\t Summary home directory  : %s" % summary_home
    print "\t Webpage home directory  : %s" % web_home
    print
    print "\t-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
    print

##############################################################
