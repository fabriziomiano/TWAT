from settings.constants import *
import json, os

REF_PATH = os.path.join(project_home, 'edm.json')

def getCategoryNominalSize(info, path):
    f = open(path, 'r')
    edm = json.load(f)
    f.close()
    fields = rel_info
    selected_trig = edm    
    for field in fields:
        try:
            selected_trig = selected_trig[field]
        except KeyError:
            msg = "key " +  field + " does not exist"
            print(msg)
            return fields.index(field)  # per fare come Rodger
    return selected_trig['nominal'], selected_trig['range']
