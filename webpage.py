import os
from utils.db_tools import bad_page_contents, bad_list_page, \
    write_html,WWW_HOME, OVERVIEW_FOLDER, RESULTS_FOLDER, \
    SAMPLE_FOLDER, IMAGES_FOLDER, sidemenu_items, make_sidemenu,\
    field_products, overview, overview_path, get_level, sample_page, \
    sample_path, iterinfo, result_page, results_path, info_tupler, \
    TEMPLATE_FIELDS, db_loader, make_plot, get_item
from utils.misc import create_nonexistent_archive

xlmns = 'xmlns="http://www.w3.org/1999/xhtml"'
DB_PATH = 'edm_db.json'

create_nonexistent_archive(WWW_HOME)
create_nonexistent_archive(os.path.join(WWW_HOME, IMAGES_FOLDER))
create_nonexistent_archive(os.path.join(WWW_HOME, OVERVIEW_FOLDER))
create_nonexistent_archive(os.path.join(WWW_HOME, RESULTS_FOLDER))
create_nonexistent_archive(os.path.join(WWW_HOME, SAMPLE_FOLDER))
create_nonexistent_archive(os.path.join(WWW_HOME, IMAGES_FOLDER))


db = db_loader(DB_PATH)


# plots
for item in iterinfo(db, list(TEMPLATE_FIELDS)):
    make_plot(db, item)

# main.html
header_fields = ('branch', 'project', 'platform')
contents = bad_page_contents(db, header_fields)
path = os.path.join(WWW_HOME, 'main.html')
write_html(path, bad_list_page(contents))

# menu.html
fields = ['branch', 'project', 'platform']
menu_contents = sidemenu_items(db, fields)
path = os.path.join(WWW_HOME, 'menu.html')
write_html(path, make_sidemenu(menu_contents))

# overview, sample and results files
overview_fields = ['branch', 'project', 'platform']
for product in field_products(db, overview_fields):
    overview_tuple = tuple(zip(overview_fields, product))
    html = overview(db, overview_tuple)
    path = overview_path(product)
    write_html(path, html)
    
    level = dict(zip(overview_fields, product))
    for selected_sample in get_level(db, level):
        html = sample_page(db, level, selected_sample)
        sample_fields = list(product) + [selected_sample]
        path = sample_path(sample_fields)
        write_html(path, html)

for item_info in iterinfo(db, list(TEMPLATE_FIELDS)):
    html = result_page(db, item_info)
    fields = info_tupler(item_info)
    path = results_path(fields)
    write_html(path, html)
