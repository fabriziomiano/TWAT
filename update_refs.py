import argparse, sys, shutil
from classes.EDM import EDM
"""
This tool allows to update the file archive_db.json
previously created with main.py. 

Run 'python update_refs.py -h' to see the helper

First, it creates a backup of the current json file

It needs to be given three arguments of type string:
e.g. 'python update_refs.py 21.0 Athena 2018-05-02T2156' 

"""
args=sys.argv

parser = argparse.ArgumentParser(description=\
                                 """Tool to update the references \
                                 using the desired branch, project, \
                                 and nightly production timestamp \
                                 e.g. python update_refs.py 21.0 Athena 2018-05-02T2156""")

parser.add_argument('desired_branch', type=str, help='Specify the desired branch (e.g. 21.0, 21.1, 21.1-dev, etc.) you want to produce reference for')
parser.add_argument('desired_project', type=str, help='Specify the desired project (e.g. Athena, AthenaP1, etc.) you want to use as a reference for the specified branch')
parser.add_argument('desired_date', type=str, help='Specify the timestamp (e.g. 2018-05-20T2141) of the nightly that you want to use as a reference')

args = parser.parse_args()


DB_PATH = 'archive_db.json'
BKPDB_PATH = 'archive_db.json.bkp'
shutil.copy(DB_PATH, BKPDB_PATH)
TEMPLATE_FIELDS = [
    'branch', 'project', 'platform', 'sample', 'category'
]

edm = EDM(DB_PATH, TEMPLATE_FIELDS)

desired_fields = {'branch': args.desired_branch, 'project': args.desired_project}
#desired_date = '2018-03-02T2225' #old
#desired_date = '2018-05-02T2156'  #new 

mylevel = edm.get_level(desired_fields)
mygroup = TEMPLATE_FIELDS[len(desired_fields):]
for item in edm.item_infovalues(level=mylevel, group_names=mygroup):
    values = item.pop('values')
    item.update(desired_fields)
    #ref_size = values.get(desired_date)
    ref_size = values.get(args.desired_date)
    if ref_size is not None: 
        edm.add_ref(item, ref_size)

edm.save()
