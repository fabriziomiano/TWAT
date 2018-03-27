from classes.EDM import EDM
"""
This example shows how to update a json file in such that 
it will contain the desired reference info for the EDM.
 
In particular, in this example the branch 21.0, together with 
the project Athena, built on the 2018-03-21T2154, was chosen 
to be the desired reference. 

"""

DB_PATH = 'archive_db.json'
TEMPLATE_FIELDS = [
    'branch', 'project', 'platform', 'sample', 'category'
]

edm = EDM(DB_PATH, TEMPLATE_FIELDS)

desired_fields = {'branch': '21.0', 'project': 'Athena'}
desired_date = '2018-03-21T2154'

mylevel = edm.get_level(desired_fields)
mygroup = TEMPLATE_FIELDS[len(desired_fields):]
for item in edm.item_infovalues(level=mylevel, group_names=mygroup):
    values = item.pop('values')
    item.update(desired_fields)
    ref = edm.most_recent(item)
    ref_size = values.get(desired_date)
    edm.add_ref(item, ref_size)

edm.save()
