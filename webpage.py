import os
from utils.webpage_tools import make_plot, WWW_HOME, OVERVIEW_FOLDER, \
    RESULTS_FOLDER, SAMPLE_FOLDER, IMAGES_FOLDER, bad_page_contents, write_html, \
    bad_list_page, sidemenu_items, make_sidemenu, overview, overview_path, \
    sample_path, image_path, results_path, result_page, sample_page
from utils.misc import create_nonexistent_archive
from classes.EDM import EDM


xlmns = 'xmlns="http://www.w3.org/1999/xhtml"'
DB_PATH = 'edm_db.json'
TEMPLATE_FIELDS = [
    'branch', 'project', 'platform', 'sample', 'category'
]

create_nonexistent_archive(WWW_HOME)
create_nonexistent_archive(os.path.join(WWW_HOME, IMAGES_FOLDER))
create_nonexistent_archive(os.path.join(WWW_HOME, OVERVIEW_FOLDER))
create_nonexistent_archive(os.path.join(WWW_HOME, RESULTS_FOLDER))
create_nonexistent_archive(os.path.join(WWW_HOME, SAMPLE_FOLDER))
create_nonexistent_archive(os.path.join(WWW_HOME, IMAGES_FOLDER))


# db = db_loader(DB_PATH)
edm = EDM(DB_PATH,TEMPLATE_FIELDS)

# plots
for i, item_info in enumerate(edm.item_infos()):
    make_plot(edm, item_info)

# main.html
header_fields = ('branch', 'project', 'platform')
contents = bad_page_contents(edm, header_fields)
path = os.path.join(WWW_HOME, 'main.html')
write_html(path, bad_list_page(contents))

# menu.html
fields = ['branch', 'project', 'platform']
menu_contents = sidemenu_items(edm, fields)
path = os.path.join(WWW_HOME, 'menu.html')
write_html(path, make_sidemenu(menu_contents))

# overview, sample and results files
overview_fields = ['branch', 'project', 'platform']
for product in edm.field_products(overview_fields):
    overview_tuple = tuple(zip(overview_fields, product))
    html = overview(edm, overview_tuple)
    path = overview_path(product)
    write_html(path, html)
    
    level = dict(zip(overview_fields, product))
    for selected_sample in edm.get_level(level):
        html = sample_page(edm, level, selected_sample)
        sample_fields = list(product) + [selected_sample]
        path = sample_path(sample_fields)
        write_html(path, html)

for item_info in edm.item_infos():
    html = result_page(edm, item_info)
    fields = edm.info_tupler(item_info)
    path = results_path(fields)
    write_html(path, html)
