import os
import glob
import textwrap
from collections import OrderedDict
from classes.EDM import EDM
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import dates
from matplotlib.ticker import FormatStrFormatter
from utils.misc import timestamp_to_datetime, set_archive_path, is_date, nested_dict

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


def date_in_keys(item):
    """ Return first encountered date found in item keys """
    for key in item:
        if is_date(key):
            return key
    return None


def bad_page_contents(edm, header_fields, levels_from_page=0):
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
    bad_list = edm.bad_list()
    for bad in bad_list:
        header = tuple((field, bad[field]) for field in header_fields)
        date = date_in_keys(bad)
        link = sample_link(edm, bad, levels_from_page)
        category = TEMPLATE_FIELDS[-1]
        items_inlist = container[header].get(bad[category])
        if not items_inlist:
            container[header][bad[category]] = [(date, link)]
        else:
            container[header][bad[category]].append((date, link))
    return container


def sidemenu_items(edm, fields):
    """ List of (link, alias) tuples to insert in the menu

    Args:
    fields -- see field_products() arguments
    """
    items = []
    for product in edm.field_products(fields):
        overview_string = '_'.join([field for field in product])
        overview_file = 'overview_' + overview_string + '.html'
        link = os.path.join(OVERVIEW_FOLDER, overview_file)
        alias = ' '.join([field for field in product])
        items.append((link, alias))
    return items


def sample_link(edm, item_info, levels_from_page=0):
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
                              for field in edm.template if info_copy.get(field) is not None])
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

    html = textwrap.dedent('''
        <table border="3">
    '''
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
                     color + '" align="center">' + str(content) + '</td>\n')
        html += '  </tr>\n'

    html += '</table>\n'
    return html


def make_link(ref, alias, color=''):
    if color == 'red':
        link = (
            '&nbsp;&nbsp; <a style="color:' + color + ';"' +
            'href="' + ref + '">' +
            '<b>' + alias + '</b></a>&nbsp;&nbsp;'
        )
    else:
        link = (
            '&nbsp;&nbsp; <a style="color:' + color + ';"' +
            'href="' + ref + '">' +
            alias + '</a>&nbsp;&nbsp;'
        )
    return link


def table_content(edm, item_info,
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
    ordered = edm.last_to_first(item_info)
    entries = 0
    out_of_range_colour = 'red' \
        if edm.is_red_item(item_info) else ''
    for date in ordered:
        if entries < max_entries:
            dates.append((date, out_of_range_colour))
            sizes.append((ordered[date], out_of_range_colour))
            ref_abs = edm.test_to_archive(item_info, date)
            ref_relative = ref_abs[ref_abs.find('ART/'):]
            for ref in glob.glob(os.path.join(ref_abs, '*')):
                alias = os.path.basename(ref)
                ref = os.path.join(ref_relative, alias)
                links.append((make_link('../../archive/' + ref, alias),
                              out_of_range_colour))
            out_of_range_colour = ''
    dates = ('Date', dates)
    sizes = ('Size', sizes)
    links = ('Link', links)
    if redirect:
        return [dates, sizes, links]
    elif not redirect:
        return [dates, sizes]


def result_page(edm, item_info):
    title = '_'.join([item_info[key] for key in TEMPLATE_FIELDS
                      if item_info.get(key) is not None])
    html = make_head(title)
    html += '<body>\n'
    header_rows = [key.title() + ': ' + item_info[key]
                   for key in TEMPLATE_FIELDS]
    header_rows.append('Nominal Size: ' +
                       str(edm.get_item(item_info).get('reference')))
    html += make_header(*header_rows)
    html += '<div id="container"' + \
        'style="font-size:20px; line-height:35px">\n'
    html += plot_link(item_info, plot_width='800',
                      levels_from_page=2, from_home=True)
    html += '</div><!--container-->\n'
    html += '<div id="container">\n'
    # html += '</td></tr></table>\n'
    # html += '<p>\n'
    columns = table_content(edm, item_info)
    html += html_table(*columns)
    html += '</div><!--container-->\n'
    html += '</body>\n'
    html += '</html>\n'
    return html


def overview(edm, overview_tuple):
    level = dict((field[0], field[1]) for field in overview_tuple)
    title = '_'.join([level[key] for key in TEMPLATE_FIELDS
                      if level.get(key) is not None])
    html = make_head(title, style_path='../css/def.css')
    # header: title and drop menu
    html += '<body>\n'
    header_rows = [key.title() + ': ' + level[key] for key in level]
    html += make_header(*header_rows)
    # html += '<body>\n'
    html += make_dropdown(edm, level)
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


def make_dropdown(edm, level,
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
    overview_string = edm.item_string(level)
    overview_file = 'overview_' + overview_string + '.html'
    field = edm.depth_field(level)
    html += '<label>' + field.title() + ': </label>\n'
    html += '<select onchange="goToPage(this.options[this.selectedIndex].value)">\n'
    html += '<option selected>' + selected_menu + '</option>\n'
    html += '<option value="../overview_html/' + overview_file + \
        '">Overview</option>\n'
    for key in edm.get_level(level):
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
    html += '<b>' + category + '</b></br>\n'
    html += '<p class="tab">\n'
    for item in contents:
        for i, word in enumerate(item):
            html += word if i < len(item)-1 else word + '\n'
        html += '      </p>\n'
    html += '</div><!--container-->\n'
    return html


def bad_list_page(contents):
    """
    Return html text of the main page, showing all bad items

    Args:
    contents (dict of dicts) -- see returns of bad_page_contents

    """
    html = textwrap.dedent('''
    <!DOCTYPE html>
    <html>
      <head>
        <title>Main</title>
        <link rel="stylesheet" type="text/css" href="css/style.css">
          <style type="text/css">
            body {font-family: verdana}
            table {font-family: arial}
            .tab { margin-left: 40px; }
          </style>
        </head>
        <body>
          <div id="container">
            <div align="center">
              <font size="6">
                <b><i>ATLAS</i> EDM Trigger Size Monitoring Homepage</b>
              </font>
            </p>
          </div>
          <p> 
          </br>
            <div align="center">
              <hr/>
              This page lists <b>only</b> the tests that fall outside the 
              nominal range.<br/>
              Click on the links to monitor the test or use the menu 
              on the left to navigate. <br/>
              If this page is empty all the Trigger EDM sizes are within 
              the accepted range. 
            </div>
        </p>
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


def plot_link(edm, item_info, plot_width='400', levels_from_page=0,
              from_home=False):
    """
    Return html text of link to the plot corresponding to given 
    item_info

    """

    fields = edm.info_tupler(item_info)
    relative = ''.join(['../' for _ in range(levels_from_page)])
    path = relative + image_path(fields, from_home)
    link = '<a href="' + path + '"> <img src="' + \
        path + '" width="' + plot_width + '" /> </a>\n'
    return link


def category_box(edm, item_info):
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
    ref = '../results_html/results_' + edm.item_string(item_info) + \
          '.html'
    alias = 'see full results'
    reference = edm.get_item(item_info).get('reference')
    html += ' <a href="' + ref + '" target="_blank"> <b> &#8594; ' + \
        alias + '</b></a></br>\n'
    html += '<font size="3">Nominal = ' + str(reference) + '</font>\n'
    html += '<br></br>\n'

    columns = table_content(edm, item_info, redirect=False)
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
    html += plot_link(edm, item_info, levels_from_page=2)
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
        body {font-family: verdana}
        table {font-family: arial}
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


def make_category_links(edm, super_level):
    """
    Return html text of links to categories present in given 
    super_level. Links to bad item are dislayed in red

    Args:
    super_level (dict) -- see level in make_dropdown or get_level()
    super_level should contain categories as its keys

    """
    html = textwrap.dedent('''
    <br><div align="center">
    Click on the category to jump to its section:
    in red the category whose test fall outside the nominal range 
    </div>
    <br>
    '''
                           )
    super_category = edm.get_level(super_level)
    for category in super_category:
        category_key = edm.depth_field(super_level)
        item_info = dict(super_level)
        item_info.update({category_key: category})
        link_color = 'red' if edm.is_red_item(item_info) else ''
        ref = '#' + category
        alias = category
        html += make_link(ref, alias, color=link_color)
    html += '</div><!-- container -->\n'
    return html


def html_sample_header(edm, level, selected_menu,
                       style_path='../css/def.css'):
    """
    Return html text of the upper part of a html sample file

    (i.e. header with considered fields, dropdown_menu to select
    samples and links to categories present in selected sample)

    """
    title = '_'.join([level[key] for key in edm.template
                      if level.get(key) is not None])
    html = make_head(title, style_path=style_path)
    # header: title and drop menu
    html += '<body>\n'
    header_rows = [key.title() + ': ' + level[key] for key in level]
    html += make_header(*header_rows)
    html += '<body>\n'
    html += make_dropdown(edm, level, selected_menu)
    # header: links to categories
    sample_level = dict(level)
    sample_key = edm.depth_field(level)
    sample_level.update({sample_key: selected_menu})
    html += make_category_links(edm, sample_level)
    return html


def sample_page(edm, level, selected_menu):
    """
    Return html text of a sample file

    It's composed of sample_header and a category_box (table and plot)
    for every category present in the selected sample of the considered
    branch, project, platform

    """
    html = html_sample_header(edm, level, selected_menu)
    sample_key = edm.depth_field(level)
    samples = dict(level)
    samples.update({sample_key: selected_menu})
    categories = edm.get_level(samples)
    for category in categories:
        item_info = dict(samples)
        item_info.update({'category': category})
        html += category_box(edm, item_info)
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
    html += textwrap.dedent('''
    <html lang="en">
      <head>
        <title>Menu</title>
        <link rel="stylesheet" type="text/css" href="css/style.css"><base target="Right"/>

          <style type="text/css">
            body {font-family: sans-serif}
            table {font-family: sans-serif}
          </style>
          <script type="text/javascript">
          </script>
        </head>

        <body bgcolor="white">
          <center>
            <nav>
              <a class="button -dark center" target="main" href="main.html">Home</a>
            </nav>
            <nav>
              <ul>
    '''
                            )
    for item in menu_items:
        ref, alias = item
        html += '<li><a class="button -regular center" target="main" href="' + ref + '">'
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


def result_page(edm, item_info):
    title = '_'.join([item_info[key] for key in edm.template
                      if item_info.get(key) is not None])
    html = make_head(title)
    html += '<body>\n'
    header_rows = [key.title() + ': ' + item_info[key]
                   for key in edm.template]
    header_rows.append('Nominal Size: ' +
                       str(edm.get_item(item_info).get('reference')))
    html += make_header(*header_rows)
    html += '<div id="container"' + \
        'style="font-size:20px; line-height:35px">\n'
    html += plot_link(edm, item_info,
                      plot_width='800', levels_from_page=2)
    html += '</div><!--container-->\n'
    html += '<div id="container">\n'
    # html += '</td></tr></table>\n'
    # html += '<p>\n'
    columns = table_content(edm, item_info)
    html += html_table(*columns)
    html += '</div><!--container-->\n'
    html += '</body>\n'
    html += '</html>\n'
    return html


def overview(edm, overview_tuple):
    level = dict((field[0], field[1]) for field in overview_tuple)
    title = '_'.join([level[key] for key in edm.template
                      if level.get(key) is not None])
    html = make_head(title, style_path='../css/def.css')
    # header: title and drop menu
    html += '<body>\n'
    header_rows = [key.title() + ': ' + level[key] for key in level]
    html += make_header(*header_rows)
    # html += '<body>\n'
    html += make_dropdown(edm, level)
    fields = [field[0] for field in overview_tuple]
    contents = bad_page_contents(
        edm, fields, levels_from_page=1)
    bad_categories = contents.get(overview_tuple)
    if bad_categories is not None:
        for category in bad_categories:
            html += badlist_category(category,
                                     bad_categories[category])
    html += '</body>\n'
    html += '</html>\n'
    return html


def make_plot(edm, item_info, from_home=False):
    """
    Given item info, create and save a plot where: 
    X axis -- dates of tests of selected item
    Y axis -- sizes of tests

    """
    ordered = edm.first_to_last(item_info)
    # Xdate = [key for key in ordered if ordered[key] > 0]
    Xdate = [timestamp_to_datetime(key).date()
             for key in ordered if ordered[key] > 0]
    Ysize = [float(ordered[key]) for key in ordered if ordered[key] > 0]
    if len(Ysize) > 0:
        item = edm.get_item(item_info)
        plottitle = edm.item_string(item_info, separator='/')
        imagesHome = os.path.join(WWW_HOME, IMAGES_FOLDER)
        plotfile = os.path.join(imagesHome,
                                edm.item_string(item_info) + '.png')
        xfmt = dates.DateFormatter('%d / %b / %y')
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.xaxis.set_major_formatter(xfmt)
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
        ax.grid(which='major', color='k', linestyle='--', linewidth=0.3)

        plt.plot_date(Xdate, Ysize, 'bo-')
        plt.title(plottitle, fontsize=10)
        plt.xlim(Xdate[0], Xdate[-1])
        #plt.xlim(Xdate[0]-datetime.timedelta(days=1), Xdate[-1]+datetime.timedelta(days=1))
        plt.ylim(0, max(Ysize)*1.1)
        plt.xticks(rotation=25)
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


def write_html(path, html_lines):
    f = open(path, 'w')
    for line in html_lines:
        f.write(line)
    f.close()


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
        #title = field.title() + ': ' + name
        title = name
        html += '<b>' + title + '</b> ' \
                if i < len(header)-1 else '[' + title + ']'
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
