from settings.constants import *
import json, os

def getCategoryNominalSize(branch, project, platform, sample, category):

path = os.path.join(project_home, 'edm.json')
if os.path.isfile(path):
    f = open(path, 'r')
    edm = json.load(f)
    return \
        edm[branch][project][platform][sample][category]['nominal'],\
        edm[branch][project][platform][sample][category]['range'], 

