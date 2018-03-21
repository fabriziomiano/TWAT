from dateutil.parser import parse
from itertools import product
from collections import OrderedDict, defaultdict
import json
import os
import textwrap
import copy
import errno
import datetime as dt
from utils.misc import timestamp_to_datetime, set_archive_path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import dates
from matplotlib.ticker import FormatStrFormatter

# TODO: transiction to deepcopy where pop is used

WWW_HOME = 'webpage'
IMAGES_FOLDER = 'images'
RESULTS_FOLDER = 'results_html'
OVERVIEW_FOLDER = 'overview_html'
SAMPLE_FOLDER = 'sample_html'
RANGE_ACCEPTED = 0.05
TEMPLATE_FIELDS = [
    'branch', 'project', 'platform', 'sample', 'category'
]
DATE_FMT = "%Y-%m-%dT%H%M"
HTML_DOCTYPE = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 ' +\
    'Transitional//EN" ' + \
    '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'


def nested_dict(): return defaultdict(nested_dict)


def datetime_to_timestamp(datetime):
    return datetime.strftime(DATE_FMT)


def db_loader(path):
    """ Return the dict database from given json-file path """

    if os.path.isfile(path):
        f = open(path, 'r')
        db = json.load(f)
    else:
        db = {}
    return db


def add_item(db, item_info, value):
    nested_fields = db
    info = dict(item_info)
    for template_field in TEMPLATE_FIELDS:
        field = info.pop(template_field)
        if field not in nested_fields:
            nested_fields[field] = {}
        nested_fields = nested_fields[field]
    nested_fields.update(value)
    return db


def get_item(db, info):
    selected_item = db
    for template_field in TEMPLATE_FIELDS:
        field = info[template_field]
        try:
            selected_item = selected_item[field]
        except KeyError:
            msg = "key " + field + " does not exist"
            print(msg)
            return template_field.index(field)  # per fare come Rodger
    return selected_item


def get_level(db, level):
    depth = len(level.keys())
    selected_fields = TEMPLATE_FIELDS[:depth]
    selected_level = db
    for selected_field in selected_fields:
        field = str(level[selected_field])
        try:
            selected_level = selected_level[field]
        except KeyError:
            msg = "key " + str(field) + " does not exist"
            print(msg)
            # return template_field.index(field)  # per fare come Rodger
    return selected_level


def level_keys(db, level):
    return list(get_level(db, level).keys())


def get_runs(db, item_info):
    item = dict(get_item(db, item_info))
    reference = item.pop('reference', None)
    return item


def last_to_first(db, item_info):
    unordered = get_runs(db, item_info)
    ordered_dates = sorted(unordered, reverse=True)
    ordered_runs = OrderedDict([(date, unordered[date])
                                for date in ordered_dates])
    return ordered_runs


def most_recent_nonzero(db, item_info):
    ordered_runs = last_to_first(db, item_info)
    for date in ordered_runs:
        size = ordered_runs[date]
        if size > 0:
            return size


def update_db(info, value, path):
    edm_db = db_loader(path)
    updated_db = add_item(edm_db, info, value)
    edm_inserter(updated_db, path)
    return db


def is_goodtest(db, item_info, size):
    item = get_item(db, item_info)
    nominal = item.get('reference')
    if size > 0 and nominal:
        tolerance = nominal*RANGE_ACCEPTED
        min, max = nominal - tolerance, nominal + tolerance
        if (size > max) or (size < min):
            return False
    return True


def most_recent(item):
    import copy

    item_copy = copy.deepcopy(item)
    reference = item.pop("reference", None)
    last_update = max(item.keys())
    return {last_update: item[last_update]}


def flatten(data, group_names):
    try:
        group, group_names = group_names[0], group_names[1:]
    except IndexError:
        # No more key to extract, we just reached
        # the most nested dictionnary
        yield data.copy()  # dont modify data in place
        return  # Nothing more to do, it is already considered flattened

    try:
        for key, value in data.iteritems():
            # value can contain nested dictionaries
            # so flatten it and iterate over the result
            for flattened in flatten(value, group_names):
                flattened.update({group: key})
                yield flattened
    except AttributeError:
        yield {group: data}


def is_date(string):
    try:
        parse(string)
        return True
    except ValueError:
        return False


def itertests(db, group_names):
    for flattened in flatten(db, group_names):
        item = {}
        item['tests'] = {}
        for key in flattened:
            if is_date(key) or key == 'reference':
                item['tests'][key] = flattened[key]
            else:
                item[key] = flattened[key]
        yield item


def iterinfo(db, group_names):
    for test in itertests(db, group_names):
        item_info = test.copy()
        item_info.pop('tests')
        yield item_info


def item_string(level, separator='_'):
    depth = len(level)
    fields = list(TEMPLATE_FIELDS[:depth])
    return separator.join([str(level[field]) for field in fields])


def date_in_keys(item):
    """ Return first encountered date found in item keys """
    for key in item:
        if is_date(key):
            return key
    return None


def to_info(info_plus_smth):
    info = dict((field, info_plus_smth[field])
                for field in TEMPLATE_FIELDS)
    return info


def info_tupler(item_info):
    """
    From item_info dict return a tuple of all field names in 
    their depth order (i.e. following TEMPLATE_FIELDS)

    Note that this works also if item_info is not complete, i.e.
    is a level dict (see get_level() for infos), but tuple
    will be shorter than TEMPLATE_FIELDS

    """
    infos = tuple(item_info[field] for field in TEMPLATE_FIELDS
                  if item_info.get(field) is not None)
    return infos


def depth_field(level):
    depth = len(level)
    return TEMPLATE_FIELDS[depth]


def field_products(db, fields):
    """
    Same as combine() but can select fields to combine.

    Args:
    fields (iterable) -- fields to get info of(e.g.['branch', 'sample'])

    """
    products = []
    for info in iterinfo(db, list(TEMPLATE_FIELDS)):
        comb = []
        for field in fields:
            comb.append(info.get(field))
        if comb not in products:
            products.append(comb)
    return products


def field_products(db, fields):
    """
    Same as combine() but can select fields to combine.

    Args:
    fields (iterable) -- fields to get info of(e.g.['branch', 'sample'])

    """
    products = []
    for info in iterinfo(db, list(TEMPLATE_FIELDS)):
        comb = []
        for field in fields:
            comb.append(info.get(field))
        if comb not in products:
            products.append(comb)
    return products


def is_red_item(db, item_info):
    """
    Return True if most recent non zero size for a given item info
    is out of range, i.e. is not a good test

    """
    item = get_item(db, item_info)
    size_to_check = most_recent_nonzero(db, item_info)
    if is_goodtest(db, item_info, size_to_check):
        return False
    return True


def test_to_archive(item_info, timestamp):
    item_datetime = timestamp_to_datetime(timestamp)
    test = dict(item_info)
    test["datetime"] = item_datetime

    return set_archive_path(test)


def write_html(path, html_lines):
    f = open(path, 'w')
    for line in html_lines:
        f.write(line)
    f.close()


def bad_list(db):
    """
    Return a list of all items with most recent test out of range

    Single list element is a item_info dictionary 
    of the corresponding out-of-range tes plus its {date: size}

    """
    bad_list = []
    for item in itertests(db, list(TEMPLATE_FIELDS)):
        tests = item['tests']
        last_test = most_recent(tests)
        last_size = next(iter(last_test.values()))
        item_info = item.copy()
        item_info.pop('tests')
        if not is_goodtest(db, item_info, last_size):
            item_info.update(last_test)
            bad_list.append(item_info)
    return bad_list


def bad_page_contents(db, header_fields, levels_from_page=0):
    """
    Return contents for the main page, which should display all 
    items with most recent test out-of-range (bad list)

    Returns:
    container (dict of dicts) -- 
    first-level keys (tuple): combinations of given 
    header_fields present in db
    second-level keys (string): categories with bad items
    values (list(tuple()): list of (date, link to 
    specific sample_link()) of every out-of-range sample

    """
    container = nested_dict()
    for bad in bad_list(db):
        header = tuple((field, bad[field]) for field in header_fields)
        date = date_in_keys(bad)
        link = sample_link(bad, levels_from_page)
        category = TEMPLATE_FIELDS[-1]
        items_inlist = container[header].get(bad[category])
        if not items_inlist:
            container[header][bad[category]] = [(date, link)]
        else:
            container[header][bad[category]].append((date, link))
    return container


def sidemenu_items(db, fields):
    """ List of (link, alias) tuples to insert in the menu

    Args:
    fields -- see field_products() arguments
    """
    items = []
    for product in field_products(db, fields):
        overview_string = '_'.join([field for field in product])
        overview_file = 'overview_' + overview_string + '.html'
        link = os.path.join(OVERVIEW_FOLDER, overview_file)
        alias = ' '.join([field for field in product])
        items.append((link, alias))
    return items

def sample_link(item_info, levels_from_page=0):
    """
    From given item_info return a html link to corresponding 
    sample file and # to the category present in item
    E.g: 
    ../sample_html/sample_branch_project_platform_sample.html#category

    """
    relative = ''.join(['../' for _ in range(levels_from_page)])
    info_copy = item_info.copy()
    category = info_copy.pop('category')
    sample_string = '_'.join([info_copy[field]
    for field in TEMPLATE_FIELDS if info_copy.get(field) is not None])
    ref = relative + 'sample_html/sample_' + \
        sample_string + '.html' + '#' + category 
    alias = info_copy['sample']
    return make_link(ref, alias)        


def html_table(*columns):
    """
    Return html text of a table filled with given columns

    Args:
    columns (tuple) -- columns of the table. A single column must have:
    column[0] (string) -- the title of the column
    column[1] (list) -- a list of all cell contents of the column,
    from the first (top) to the last (bottom)

    """
    data = OrderedDict()
    for column in columns:
        title, content = column
        data[title] = content
    rows = [tuple(data.keys())] + list(zip(*data.values()))
    headers = rows.pop(0)

    html = textwrap.dedent(
        """
        <style>
        table, th, td{border:1px}
        </style>
        <table>
        """
    )
    html += '  <tr>\n'
    for header in headers:
        html += '    <th>' + header + '</th>\n'
    html += '  </tr>\n'

    for row in rows:
        html += '  <tr>\n'
        for element in row:
            content, color = element
            html += ('    <td style="background-color:' +
                     color + '">' + str(content) + '</td>\n')
        html += '  </tr>\n'

    html += '</table>\n'
    return html


def make_link(ref, alias, color=''):
    link = (
        '&nbsp;&nbsp; <a style="color:' + color + ';"' +
        'href="' + ref + '">' +
        alias + '</a>&nbsp;&nbsp;'
    )
    return link


def table_content(db, item_info,
                  redirect=True, max_entries=float("inf")):
    """
    Return contents to fill a table using html_table function

    Args:
    item_info (dict) -- a dict of all infos to display results of

    redirect (bool) -- if True a ('Link', list(links)) is returned
    among with dates and sizes

    max_entries (int or float) -- max number of entries to append to 
    data list

    Returns:
    [('Date', dates), ('Size', sizes)] (and links if redirect=True)
    dates and sizes (list) -- all dates and sizes of given item_info
    associated with a color.
    If it's a bad item first non zero element of 
    dates, sizes and links will be red

    e.g.
    dates = [('2018-03-03T1212', 'red'), ('2018-03-04T1345', '')]
    sizes = [(2.3, 'red'), (0.45, '')]
    Note that if colors are removed from the lists, then
    dict(zip(dates, sizes)) will be equivalent 
    to get_runs(db, item_info)

    TODO: change links when moving to lxplus
    """
    dates, sizes, links = [], [], []
    ordered = last_to_first(db, item_info)
    entries = 0
    out_of_range_colour = 'red' \
        if is_red_item(db, item_info) else ''
    for date in ordered:
        if entries < max_entries:
            dates.append((date, out_of_range_colour))
            sizes.append((ordered[date], out_of_range_colour))
            ref = test_to_archive(item_info, date)  # glob in future
            alias = os.path.basename(ref)  # to change with glob.glob()
            links.append((make_link(ref, alias), out_of_range_colour))
            out_of_range_colour = ''
    dates = ('Date', dates)
    sizes = ('Size', sizes)
    links = ('Link', links)
    if redirect:
        return [dates, sizes, links]
    elif not redirect:
        return [dates, sizes]


def result_page(db, item_info):
    title = '_'.join([item_info[key] for key in TEMPLATE_FIELDS
                      if item_info.get(key) is not None])
    html = make_head(title)
    html += '<body>\n'
    header_rows = [key.title() + ': ' + item_info[key]
                   for key in TEMPLATE_FIELDS]
    header_rows.append('Nominal Size: ' +
                       str(get_item(db, item_info).get('reference')))
    html += make_header(*header_rows)
    html += '<div id="container"' + \
        'style="font-size:20px; line-height:35px">\n'
    html += plot_link(item_info, plot_width='800',
                      levels_from_page=2, from_home=True)
    html += '</div><!--container-->\n'
    html += '<div id="container">\n'
    # html += '</td></tr></table>\n'
    # html += '<p>\n'
    columns = table_content(db, item_info)
    html += html_table(*columns)
    html += '</div><!--container-->\n'
    html += '</body>\n'
    html += '</html>\n'
    return html


def overview(db, overview_tuple):
    level = dict((field[0], field[1]) for field in overview_tuple)
    title = '_'.join([level[key] for key in TEMPLATE_FIELDS
                      if level.get(key) is not None])
    html = make_head(title, style_path='../css/def.css')
    # header: title and drop menu
    html += '<body>\n'
    header_rows = [key.title() + ': ' + level[key] for key in level]
    html += make_header(*header_rows)
    # html += '<body>\n'
    html += make_dropdown(db, level)
    contents = bad_page_contents(
        db, header_fields, levels_from_page=1)
    bad_categories = contents.get(overview_tuple)
    if bad_categories is not None:
        for category in bad_categories:
            html += badlist_category(category,
                                     bad_categories[category])
    html += '</body>\n'
    html += '</html>\n'
    return html


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


def badlist_category(category, contents):
    """
    Return html text showing all out-of-range samples for a given
    category (branch, project, platform should be previously fixed)

    Args:
    category (string) -- the category to show data of
    contents (iterable) -- rows of words to display for every category.
    every row should contain a date and the link to sample file

    """
    html = '<div id="container">\n'
    html += 'Category - ' + category + '</br>\n'
    html += '<p class="tab">\n'
    for item in contents:
        for i, word in enumerate(item):
            html += word if i < len(item)-1 else word + '\n'
        html += '      </p>\n'
    html += '</div><!--container-->\n'
    return html


def badlist_box(header, contents):
    """
    Return html text diplaying bad items for the given header

    Args:
    header (tuple) -- tuple containing bad items infos
    e.g. (branch, project, platform)
    to diplay bad items of
    contents (dict) --
    keys: categories with bad items
    values (list(tuple)) -- see returns of bad_page_contents() 

    """
    html = ''
    html += textwrap.dedent(
        '''
    <div id="container">
    <font size="4">  
    '''
    )
    for i, word in enumerate(header):
        field, name = word
        title = field.title() + ': ' + name
        html += title + '; ' if i < len(header)-1 else title
    html += textwrap.dedent(
        '''
    </font>
    </p>
    '''
    )
    for category in contents:
        html += badlist_category(category, contents[category])
    html += '    </div><!--container-->\n'
    return html


def bad_list_page(contents):
    """
    Return html text of the main page, showing all bad items

    Args:
    contents (dict of dicts) -- see returns of bad_page_contents

    """
    html = textwrap.dedent(
        '''
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html>
          <head>
            <title>Main</title>
            <link rel="stylesheet"type="text/css" href="css/def.css">
            <style type="text/css">
              body,table{font-family:sans-serif}
              .tab{margin-left:40px;}
            </style>
          </head>
          <body>
          <div id="container";align="center">
          <font size="6">          
          ATLAS EDM Trigger Size Monitoring by Trigne
          </font>
          </p>
          </div>
          <p> 
          </br>
          The following is a list of the most recent EDM size tests that
          fall outside the nominal range. Click on the links to go to a
          summary of the results.
          </p>
          </div><!--container-->
        <hr/>
        '''
    )
    for header in contents:
        html += badlist_box(header, contents[header])

    html += textwrap.dedent(
        '''    
      </body>
    </html>
    '''
    )
    return html


def plot_link(item_info, plot_width='400', levels_from_page=0,
              from_home=False):
    """
    Return html text of link to the plot corresponding to given 
    item_info

    """

    fields = info_tupler(item_info)
    relative = ''.join(['../' for _ in range(levels_from_page)])
    path = relative + image_path(fields, from_home)
    link = '<a href="' + path + '"> <img src="' + \
        path + '" width="' + plot_width + '" /> </a>\n'
    return link


def category_box(db, item_info):
    """
    Return html text of a table and plot specific of given item_info

    html parts:
    table -- shows most recent tests of given item_info. If most recent
    is out of range it is diplayed in red

    plot -- a plot of DatesVsSize for given item_info

    """
    html = textwrap.dedent(
        '''
    <div id="container">
    <div id="left">
    '''
    )
    html += '<a name="' + item_info['category'] + '"></a>\n'
    html += '<table width="90%"><tr><td>\n'
    html += '  <p>\n'
    html += item_info['category']
    ref = '../results_html/results_' + item_string(item_info) + '.html'
    alias = 'full results'
    reference = get_item(db, item_info).get('reference')
    html += '( <a href="' + ref + '" target="_blank"> <b>' + \
        alias + '</b></a> )</br>\n'
    html += '<font size="3">Nominal = ' + str(reference) + '</font>\n'
    html += '<br></br>\n'

    columns = table_content(db, item_info, redirect=False)
    html += html_table(*columns)
    html += textwrap.dedent(
        '''
    </p>
    </td></tr></table>
    <p><br></p>
    </div><!-- left -->
    <div id="right">
    '''
    )
    html += plot_link(item_info, levels_from_page=2)
    html += textwrap.dedent(
        '''
    </div><!-- right -->      
    <div class="clear"></div>
    </div><!-- container -->
    '''
    )
    return html


def make_head(title, html_type='',
              style_path='css/def.css', base_target=''):
    """ Return html text of a sample (and not only)file head """

    html = HTML_DOCTYPE
    html += '<html ' + html_type + '>\n'
    html += '<head>\n'
    html += '<title>' + title + '</title>\n'
    html += '<link rel="stylesheet" type="text/css" href="' + \
        style_path + '">'
    html += '<base target="' + base_target + '">\n'
    html += textwrap.dedent(
        '''
    <style type="text/css">
      body {font-family: sans-serif}
      table {font-family: sans-serif}
    </style>
    <script type="text/javascript">
    </script>
    </head>
    '''
    )
    return html


def make_header(*rows):
    """
    From given rows return a html text that can be used as header
    for sample files and possibly others

    """
    html = textwrap.dedent(
        '''
        <div id="container">
        <div style="font-size:20px; line-height:35px">
    '''
    )
    html += ''.join([row + '</br>\n' for row in rows])
    html += textwrap.dedent(
        '''
        <div style="line-height:10px"></br></div>
        </div>
    '''
    )
    return html


def make_dropdown(db, level,
                  selected_menu='Please select a trigger sample'):
    """
    Return html text of a dropdown menu

    Args:
    level (dict) -- a dict of selected fields we want to consider
    e.g. {'branch': '21.0', 'project': 'Athena'}

    selected_menu (string) -- a specific element of the keys present
    in the very sub level dict of given level that will act as 
    selected item of the dropdown menu
    e.g. 'x86_64-slc6-gcc62-opt' is a platform key present in the
    sub level of the level example

    """
    html = textwrap.dedent(
        '''
    <script type="text/javascript">
        function goToPage(url)
        {
            if (url != "")
            {
                //this.open(url)
                location = url
            }
        }
    </script>
    <form>
    '''
    )
    overview_string = item_string(level)
    overview_file = 'overview_' + overview_string + '.html'
    field = depth_field(level)
    html += '<label>' + field.title() + ': </label>\n'
    html += '<select onchange="goToPage(this.options[this.selectedIndex].value)">\n'
    html += '<option selected>' + selected_menu + '</option>\n'
    html += '<option value="../overview_html/' + overview_file + \
        '">Overview</option>\n'
    for key in get_level(db, level):
        sample_string = overview_string + '_' + key + '.html'
        sample_file = '../sample_html/sample_' + sample_string
        html += '<option value="' + sample_file + \
            '">' + key + '</option>\n'
    html += textwrap.dedent(
        '''
    </select>
    </form>
    '''
    )
    return html


def make_category_links(db, super_level):
    """
    Return html text of links to categories present in given 
    super_level. Links to bad item are dislayed in red

    Args:
    super_level (dict) -- see level in make_dropdown or get_level()
    super_level should contain categories as its keys

    """
    html = textwrap.dedent(
        '''
    <br>
    Click on links below to jump to results section on this page
    (red links indicate problems)
    </br>
    '''
    )
    super_category = get_level(db, super_level)
    for category in super_category:
        category_key = depth_field(super_level)
        item_info = dict(super_level)
        item_info.update({category_key: category})
        link_color = 'red' if is_red_item(db, item_info) else ''
        ref = '#' + category
        alias = category
        html += make_link(ref, alias, color=link_color)
    html += '</div><!-- container -->\n'
    return html


def html_sample_header(db, level, selected_menu,
                       style_path='../css/def.css'):
    """
    Return html text of the upper part of a html sample file

    (i.e. header with considered fields, dropdown_menu to select
    samples and links to categories present in selected sample)

    """
    title = '_'.join([level[key] for key in TEMPLATE_FIELDS
                      if level.get(key) is not None])
    html = make_head(title, style_path=style_path)
    # header: title and drop menu
    html += '<body>\n'
    header_rows = [key.title() + ': ' + level[key] for key in level]
    html += make_header(*header_rows)
    html += '<body>\n'
    html += make_dropdown(db, level, selected_menu)
    # header: links to categories
    sample_level = dict(level)
    sample_key = depth_field(level)
    sample_level.update({sample_key: selected_menu})
    html += make_category_links(db, sample_level)
    return html


def sample_page(db, level, selected_menu):
    """
    Return html text of a sample file

    It's composed of sample_header and a category_box (table and plot)
    for every category present in the selected sample of the considered
    branch, project, platform

    """
    html = html_sample_header(db, level, selected_menu)
    sample_key = depth_field(level)
    samples = dict(level)
    samples.update({sample_key: selected_menu})
    categories = get_level(db, samples)
    for category in categories:
        item_info = dict(samples)
        item_info.update({'category': category})
        html += category_box(db, item_info)
    return html


def make_sidemenu(menu_items,
                  html_type='xmlns="http://www.w3.org/1999/xhtml"'):
    """
    Return html text of a menu made of a home button and a list of 
    links to navigate over results

    Args:
    menu_items (list(tuple)) -- a list of (link, alias) to display
    html_type (string) -- to check what it is

    """
    html = HTML_DOCTYPE
    title = 'Menu'
    html += make_head(title, base_target='Right')
    html += textwrap.dedent(
        '''
        <body bgcolor="black">
        <center>
        <nav>
        <ul>
        <li><a target="main" href="main.html">Home</a></li>
        </ul>
        </nav>
        <nav>
        <ul>
    '''
    )
    for item in menu_items:
        ref, alias = item
        html += '<li><a target="main" href="' + ref + '">'
        html += '<br/>'.join([word for word in alias.split()])
        html += '</a></li>\n'
    html += textwrap.dedent(
        '''
        </ul>
        </nav>
        </center>
        </body>
        </html>
    '''
    )
    return html


def result_page(db, item_info):
    title = '_'.join([item_info[key] for key in TEMPLATE_FIELDS
                      if item_info.get(key) is not None])
    html = make_head(title)
    html += '<body>\n'
    header_rows = [key.title() + ': ' + item_info[key]
                   for key in TEMPLATE_FIELDS]
    header_rows.append('Nominal Size: ' +
                       str(get_item(db, item_info).get('reference')))
    html += make_header(*header_rows)
    html += '<div id="container"' + \
        'style="font-size:20px; line-height:35px">\n'
    html += plot_link(item_info, plot_width='800', levels_from_page=2)
    html += '</div><!--container-->\n'
    html += '<div id="container">\n'
    # html += '</td></tr></table>\n'
    # html += '<p>\n'
    columns = table_content(db, item_info)
    html += html_table(*columns)
    html += '</div><!--container-->\n'
    html += '</body>\n'
    html += '</html>\n'
    return html


def overview(db, overview_tuple):
    level = dict((field[0], field[1]) for field in overview_tuple)
    title = '_'.join([level[key] for key in TEMPLATE_FIELDS
                      if level.get(key) is not None])
    html = make_head(title, style_path='../css/def.css')
    # header: title and drop menu
    html += '<body>\n'
    header_rows = [key.title() + ': ' + level[key] for key in level]
    html += make_header(*header_rows)
    # html += '<body>\n'
    html += make_dropdown(db, level)
    fields = [field[0] for field in overview_tuple]
    contents = bad_page_contents(
        db, fields, levels_from_page=1)
    bad_categories = contents.get(overview_tuple)
    if bad_categories is not None:
        for category in bad_categories:
            html += badlist_category(category,
                                     bad_categories[category])
    html += '</body>\n'
    html += '</html>\n'
    return html


def make_plot(db, item_info, from_home=False):
    """
    Given item info, create and save a plot where: 
    X axis -- dates of tests of selected item
    Y axis -- sizes of tests

    """
    ordered = last_to_first(db, item_info)
    Xdate = [key for key in ordered if ordered[key] > 0]
    Ysize = [float(ordered[key]) for key in ordered if ordered[key] > 0]
    if len(Ysize) > 0:
        item = get_item(db, item_info)
        plottitle = item_string(item_info, separator='/')
        imagesHome = os.path.join(WWW_HOME, IMAGES_FOLDER)
        plotfile = os.path.join(imagesHome,
                                item_string(item_info) + '.png')
        # xfmt = dates.DateFormatter('%Y %b %d')
        fig = plt.figure()
        ax = fig.add_subplot(111)
        # ax.xaxis.set_major_formatter(xfmt)
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))

        plt.plot_date(Xdate, Ysize, 'bo-')
        plt.title(plottitle, fontsize=10)
        plt.xlim(Xdate[0], Xdate[-1])
        #plt.xlim(Xdate[0]-datetime.timedelta(days=1), Xdate[-1]+datetime.timedelta(days=1))
        plt.ylim(0, max(Ysize)*1.1)
        plt.xticks(rotation='vertical')
        plt.xlabel('Date')
        plt.ylabel('Size/Evt (kb)')
        plt.gcf().subplots_adjust(bottom=0.25)

        plt.savefig(plotfile)


def image_path(fields, from_home=False):
    image_file = '_'.join([field for field in fields]) + '.png'
    path = os.path.join(IMAGES_FOLDER, image_file)\
        if from_home \
        else os.path.join(WWW_HOME, IMAGES_FOLDER, image_file)
    return path


def results_path(fields, from_home=False):
    results_file = 'results_' + \
        '_'.join([field for field in fields]) + '.html'
    path = os.path.join(RESULTS_FOLDER, results_file)\
        if from_home \
        else os.path.join(WWW_HOME, RESULTS_FOLDER, results_file)
    return path


def overview_path(fields, from_home=False):
    overview_file = 'overview_' + \
        '_'.join([field for field in fields]) + '.html'
    path = os.path.join(OVERVIEW_FOLDER, overview_file)\
        if from_home \
        else os.path.join(WWW_HOME, OVERVIEW_FOLDER, overview_file)
    return path


def sample_path(fields, from_home=False):
    sample_file = 'sample_' + \
        '_'.join([field for field in fields]) + '.html'
    path = os.path.join(SAMPLE_FOLDER, sample_file)\
        if from_home \
        else os.path.join(WWW_HOME, SAMPLE_FOLDER, sample_file)
    return path
