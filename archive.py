"""
Read ART result archive and 
create new archive within art_home like
ART/2018/2/1/21.0/Athena/21H53M/x86_64-slc6-gcc62-opt/test_mc_pp_v7_rdotoaod_grid 

"""
import os, glob, datetime, gzip
from itertools import product
from utils.misc import *
from settings.constants import *

today = datetime.datetime.now()
weekday = today.strftime("%w")

splash_screen(today, weekday)

dirs = []

for pattern_fields in product(*input_path_structure):    
    pattern = os.path.join(*pattern_fields)
    for file_toarchive in glob.glob(pattern):
        input_file = os.path.basename(file_toarchive)
        print
        print 'INFO :: Getting info from ART path = '
        print '%s ' % file_toarchive
        
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
            
print
print
if len(dirs) > 0:
    print '\t', len(dirs), 'files successfully archived. Done'
else:
    print '\tNo new files were added to the archive.'
print 
print