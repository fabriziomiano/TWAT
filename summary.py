"""
Read created archive from a path like
ART/2018/2/1/21.0/Athena/21H53M/x86_64-slc6-gcc62-opt/test_mc_pp_v7_rdotoaod_grid 
and write out summary files for dedicated trigger categories

"""
import os, glob, datetime, gzip
from itertools import product
from utils.misc import *
from settings.constants import *

dirs = []

for pattern_fields in product(*archive_path_structure):
    pattern = os.path.join(*pattern_fields)
    for archived_file in glob.glob(pattern):
        input_file = os.path.basename(archived_file)
        if input_file.strip('.gz') not in triginfo_file: continue
        print
        print 'INFO :: Getting info from archived file = '
        print '%s ' % archived_file
        
        summary_path = set_summary_path(archived_file)
        create_nonexistent_archive(summary_path)
        
        trigger_categories, total_size = get_trigsize(archived_file)
        write_triginfo_to_file(summary_path, trigger_categories, total_size)
        
