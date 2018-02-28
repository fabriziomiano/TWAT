"""
Create, if doesn't exist, or update a json file
containing the references information for the EDM 

"""
import os, glob, datetime, gzip
import json
from itertools import product
from collections import defaultdict
from settings.constants import *

RANGE_ACCEPTED = 0.05
REFS_PATH = os.path.join(project_home, 'edm.json')
nested_dict = lambda: defaultdict(nested_dict)


def fill_updatable(edm, updatable_edm):
    for k, v in edm.iteritems():
        if isinstance(v, dict):
            updatable_edm[k] = defaultdict(dict, v)
            fill_updatable(v, updatable_edm[k])
        else:
            updatable_edm[k] = v
    return updatable_edm


def edm_loader(path):    
    if os.path.isfile(path):
        f = open(path, 'r')
        edm = json.load(f)
        updatable_edm = nested_dict()
        edm = fill_updatable(edm, updatable_edm)
    else:
        edm = nested_dict()
    return edm


def edm_inserter(edm, path):
    f = open(path, 'w')
    loader = json.dump(edm, f, indent=4, separators=(',', ': '))
    f.close()


def add_ref(info, edm):
    fields, value = info
    
    nested_fields = edm
    for field in fields:
        if field not in nested_fields:
            nested_fields[field] = {}
        else:
            pass
        nested_fields = nested_fields[field]
    nested_fields['nominal'] = value
    nested_fields['range'] = value * RANGE_ACCEPTED
    return edm


def update_refs(info, path):
    edm = edm_loader(path)
    updated_edm = add_ref(info, edm)
    edm_inserter(updated_edm, path)

    
for pattern_fields in product(*summary_files_path_structure):
    pattern = os.path.join(*pattern_fields)
    for summary_file in glob.glob(pattern):
        
        f = open(summary_file,'r')
        size = -1
        for line in f:
            parts = line.strip().split()
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            branch = parts[3]
            project = parts[4]
            clock = parts[5]
            platform = parts[6]
            sample = parts[7]
            size = float(parts[8])
            category = os.path.basename(summary_file)[len('trigger'):-len('.txt')]

            info = ([branch, project, platform, sample, category], size)

            update_refs(info, REFS_PATH)
