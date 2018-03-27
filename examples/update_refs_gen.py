import os
from aclasses.EDM import EDM
"""
This exampls shows how to manually add a 'reference' entry 
to the json file for a specific branch, project, sample, platform
using the EDM method add_ref(). 
In this example a size of 12 is added to the muon category 
of the branch 21.0, project Athena, sample test_physics_pp_v7_rdotoesdaod_grid,
and platform x86_64-slc6-gcc62-opt

"""
DB_PATH = os.path.join(PROJECT_HOME, 'archive_db.json')
TEMPLATE_FIELDS = [
    'branch', 'project', 'platform', 'sample', 'category'
]

edm = EDM(DB_PATH, TEMPLATE_FIELDS)

desired_fields = {'branch': '21.0', 'project': 'Athena',
                  'sample': 'test_physics_pp_v7_rdotoesdaod_grid',
                  'platform': 'x86_64-slc6-gcc62-opt'}
desired_date = '2018-03-21T2154'

myref_info = {
    'branch': '21.0',
    'project': 'Athena',
    'sample': 'test_physics_pp_v7_rdotoesdaod_grid',
    'platform': 'x86_64-slc6-gcc62-opt',
    'category': 'Muon'
}
myref_size = 12  # as an example of Muon-category size
edm.add_ref(myref_info, myref_size)
edm.save()
