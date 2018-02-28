#!/usr/bin/env python

# /afs/cern.ch/atlas/project/trigger/pesa-sw/validation/trends/TrigSizeMonitoring/summary/rtt/17.5.X.Y-VAL/build/x86_64-slc5-gcc43-opt/offline/TrigAnalysisTest/MC_pp_v3_top

import os
import glob
import datetime
import gzip
import copy
import math
import numpy
import category_size_dict
from settings.constants import *

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import dates
from matplotlib.ticker import FormatStrFormatter

# Set paths

http_baselink = 'https://test-atrvshft.web.cern.ch/test-atrvshft/TriggerEDMSizeMonitoring'

overview_html = os.path.join(web_home[0],'overview_html')
sample_html = os.path.join(web_home[0],'sample_html')
results_html = os.path.join(web_home[0],'results_html')

# List of search patterns
branches_to_include = []
branches_to_include.append('21.0')
# branches_to_include.append('17.3')
# branches_to_include.append('devval')

menuToInclude = []
menuToInclude.append('MC_pp_v4')
menuToInclude.append('test')




# Determine if test is out of range
# =======================
def goodTest(size, release, platform, menu, slice):
    
    nom = category_size_dict.getCategoryNominalSize(release, platform, menu, slice)
    nominal = nom[0]
    range = nom[1]
    
    if (size > 0) and (nominal > 0):
            max = nominal + range
            min = nominal - range
            if (size > max) or (size < min):
                return 0
                
    return 1
# =======================


# Get most recent non-zero size
# =======================
def mostRecentSizeAndDate(release, platform, menu, slice):
    
    summaryFile_abspath = os.path.join(summary_home,'rtt',release,'build',platform,'offline','TrigAnalysisTest',menu,'trigger'+slice+".txt")
    summaryFile_relpath = ".."+summaryFile_abspath[len(project_home):]
    
    summaryFile = open(summaryFile_abspath, "r")

    mostRecentSize = 0            
    mostRecentDate = datetime.date(1900, 1, 1)
    for line in summaryFile:
        line = (line.strip()).split()
        year     = line[0]
        month    = line[1]
        day      = line[2]
        release  = line[3]
        platform = line[4]
        menu     = line[5]
        testDate = datetime.date(int(year), int(month), int(day))
        size = float(line[6])
        if (testDate > mostRecentDate) and (size > 0):
            mostRecentSize = size
            mostRecentDate = testDate
        
    mostRecent = [mostRecentSize, mostRecentDate]
    
    return mostRecent
# =======================


# Get string of nominal size and range information
# =======================
def nomimalSize_String(nom, release, platform, menu, slice):

    nominal_size_str = ''
    if   nom[0] == -1: nominal_size_str = 'Release "'      +release+  '" not found in dictionary'
    elif nom[0] == -2: nominal_size_str = 'Platform "'     +platform+ '" not found in dictionary'
    elif nom[0] == -3: nominal_size_str = 'Trigger menu "' +menu+     '" not found in dictionary'
    elif nom[0] == -4: nominal_size_str = 'Category "'     +slice+    '" not found in dictionary'
    elif nom[0] ==  0: nominal_size_str = 'Not set in dictionary (default 0.0 &plusmn 0.0 kb/evt)'
    else:              nominal_size_str = str(nom[0])+' &plusmn '+str(nom[1])+' kb/evt'
    
    return nominal_size_str
# =======================


# Make html code for tables
# =======================
def html_Table(summaryFile_abspath, num_entries, nominal, range, html, show_links):
    
    summaryFile = open(summaryFile_abspath, "r")
    
    max_entries = num_entries
    if (num_entries < 0): max_entries = 50000
    
    summaryTable = []            
    for line in summaryFile:
        line = (line.strip()).split()
        year     = line[0]
        month    = line[1]
        day      = line[2]
        release  = line[3]
        platform = line[4]
        menu     = line[5]
        testDate = datetime.date(int(year), int(month), int(day))
        size = line[6]
        summaryTable.append([testDate, size])

    # --- Write to html ---
    html.append('                    <table border="1">\n')
    html.append('                    <tr>\n')
    html.append('                    <th>Date</th>\n')
    html.append('                    <th>Size (kb/evt)</th>\n')
    if show_links: html.append('                    <th>Links to Output Files in Archive</th>\n')
    html.append('                    </tr>\n')
    
    # --- Fill table ---
    counter = 0
    mostRecentNonZero = 0
    for entry in sorted(summaryTable, reverse=True):
        counter += 1
        if (counter > max_entries): continue
        date = str(entry[0])
        size = entry[1]
        out_of_range_colour = ''
        if (mostRecentNonZero == 0) and (nominal > 0) and (float(size) > 0):
            mostRecentNonZero = 1
            max = nominal + range
            min = nominal - range
            if ((float(size) > max) or (float(size) < min)):
                out_of_range_colour = '; background-color:red'
        html.append('                    <tr>\n')
        html.append('                    <td style="font-size:15px'+out_of_range_colour+'" align="center">'+date+'</td>\n')
        html.append('                    <td style="font-size:15px'+out_of_range_colour+'" align="center">'+size+'</td>\n')
        
        # Get output files if showing links in table
        if show_links:
            html.append('                    <td style="font-size:15px'+out_of_range_colour+'" align="center">')
            
            year  = str((entry[0]).year)
            month = str((entry[0]).month).zfill(2)
            day   = str((entry[0]).day).zfill(2)
            
            for outputfile in glob.glob( os.path.join( archive_home,'rtt',year,month,day,release,'build',platform,'offline','TrigAnalysisTest',menu,'*' ) ):

                # link = os.path.join( http_baselink, outputfile[len(project_home)+1:] )
                link = '../../'+outputfile[len(project_home)+1:]
                html.append('&nbsp;&nbsp;<a href="'+link+'">'+os.path.basename(link)+'</a>&nbsp;&nbsp;')
                
            html.append('</td>\n')
        
        html.append('                    </tr>\n')
    # ---------------------
   
    html.append('                    </table>\n')

    # ---------------------

    return
# =======================



# Make main page
# =======================
def makepage_Main(bad_list_main):

    html = []

    html.append('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n')
    html.append('<html>\n')
    html.append('    <head>\n')
    html.append('        <title>Main</title>\n')
    html.append('        <link rel="stylesheet" type="text/css" href="css/def.css">\n')
    html.append('        <style type="text/css">\n')
    html.append('            body {font-family: sans-serif}\n')
    html.append('            table {font-family: sans-serif}\n')
    html.append('            .tab { margin-left: 40px; }\n')
    html.append('        </style>\n')
    html.append('    </head>\n')
    html.append('    <body>\n')
    html.append('    <div id="container">\n')
    html.append('    <div align="center">\n')
    html.append('    <font size="6">\n')
    html.append('    ATLAS EDM Trigger Size Monitoring\n')
    html.append('    </font>\n')
    html.append('    </p>\n')
    html.append('    </div>\n')
    if len(bad_list_main) > 0:
        html.append('    <p>\n')
        html.append('    </br>\n')
        html.append('    The following is a list of the most recent EDM size tests that fall outside the nominal range. Click on the links to go to a summary of the results.\n')
        html.append('    </p>\n')
    html.append('    </div>\n')

    # --- List of bad tests ---
    added_list_RP = []
    for item in bad_list_main:
        release  = item[0]
        platform = item[1]
        if [release, platform] not in added_list_RP:
            added_list_RP.append([release, platform])
            print release, platform
            
            html.append('        <div id="container">\n')
            html.append('        <font size="4">\n')
            html.append('        '+release+' ['+platform+']\n')
            html.append('        </font>\n')
            html.append('        </p>\n')


            added_list = []
            for subitem in bad_list_main:
                slice = subitem[3]
                if (subitem[0] == release and subitem[1] == platform) and slice not in added_list:
                    added_list.append(slice)
                    html.append('            Category - '+slice+'</br>\n')
                    html.append('            <p class="tab">\n')
                    for entry in bad_list_main:
                        if entry[0] == release and entry[1] == platform and entry[3] == slice:
                            menu = entry[2]
                            size = entry[4]
                            date = entry[5]
                            # link = os.path.join(http_baselink, 'webpage', 'sample_html', 'sample_'+release+'_'+platform+'_'+menu+'.html#'+slice)
                            link = './'+os.path.join('sample_html', 'sample_'+release+'_'+platform+'_'+menu+'.html#'+slice)
                            html.append('             '+str(date)+' - <a href="'+link+'">'+menu+'</a></br>\n')
                    html.append('            </p>\n')
                            
            
            html.append('       </div><!-- container -->\n')
    # --- List of bad tests ---
    

    
    html.append('    </body>\n')
    html.append('</html>\n')


    html_file = open(  os.path.join(web_home, 'main.html'), 'w'  )
    for line in html:
        html_file.write(line)
# =======================


# Make left-side menu
# =======================
def makepage_Menu(ReleasePlatform):
    
    html = []
        
    html.append('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n')
    html.append('<html xmlns="http://www.w3.org/1999/xhtml">\n')
    html.append('    <head>\n')
    html.append('        <title>Menu</title>\n')
    html.append('        <link rel="stylesheet" type="text/css" href="css/def.css">\n')
    html.append('        <base target="Right">\n')
    html.append('        <style>\n')
    html.append('            body {font-family: sans-serif}\n')
    html.append('            table {font-family: sans-serif}\n')
    html.append('        </style>\n')
    html.append('    </head>\n')
    html.append('    <body bgcolor="black">\n')
    html.append('        <center>\n')
    html.append('            <nav>\n')
    html.append('                <ul>\n')
    html.append('                    <li><a target="main" href="main.html">Home</a></li>\n')
    html.append('                </ul>\n')
    html.append('            </nav>\n')
    html.append('            <nav>\n')
    html.append('                <ul>\n')

    for item in sorted(ReleasePlatform):
        release  = item[0]
        platform = item[1]
        # link = os.path.join(http_baselink, 'webpage', 'overview_html', 'overview_'+release+'_'+platform+'.html')
        link = './'+os.path.join('overview_html', 'overview_'+release+'_'+platform+'.html')
        html.append('                    <li><a target="main" href="'+link+'">'+release+'<br/>'+platform+'</a></li>\n')

    html.append('                 </ul>\n')
    html.append('            </nav>\n')
    html.append('        </center>\n')
    html.append('    </body>\n')
    html.append('</html>\n')

    html_file = open( os.path.join(web_home,'menu.html'), 'w' )
    for line in html:
        html_file.write(line)
        
    return
# =======================


# Make overview pages
# =======================
def makepage_Overview(ReleasePlatformMenu, bad_list):

    release  = (ReleasePlatformMenu[0])[0]
    platform = (ReleasePlatformMenu[0])[1]
    
    html = []
    
    html.append('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n')
    html.append('<html>\n')
    html.append('    <head>\n')
    html.append('        <title>'+release+' ['+platform+']</title>\n')
    html.append('        <link rel="stylesheet" type="text/css" href="../css/def.css">\n')
    html.append('        <style type="text/css">\n')
    html.append('            body {font-family: sans-serif}\n')
    html.append('            table {font-family: sans-serif}\n')
    html.append('            .tab { margin-left: 40px; }\n')
    html.append('        </style>\n')
    html.append('        <script type="text/javascript">\n')
    html.append('        </script>\n')
    html.append('    </head>\n')
    html.append('    <body>\n')
    html.append('         <script type="text/javascript">\n')
    html.append('            function goToPage(url)\n')
    html.append('            {\n')
    html.append('            if (url != "")\n')
    html.append('            {\n')
    html.append('            //this.open(url);\n')
    html.append('            location = url;\n')
    html.append('            }\n')
    html.append('            }\n')
    html.append('        </script>\n')
    html.append('        <div id="container">\n')
    html.append('        <div style="font-size:20px; line-height:35px">\n')
    html.append('            Release     : '+release+'</br>\n')
    html.append('            Platform    : '+platform+'</br>\n')
    html.append('            <div style="line-height:10px"></br></div>\n')
    html.append('        </div>\n')
    html.append('        <form>\n')
    html.append('            <label>Menu/Sample : </label>\n')
    html.append('            <select onchange="goToPage(this.options[this.selectedIndex].value)">\n')
    html.append('                <option selected>Please select a Trigger Menu / MC Sample</option>\n')
    html.append('                <option value="../overview_html/overview_'+release+'_'+platform+'.html">Overview</option>\n')
    
    for item in sorted(ReleasePlatformMenu, reverse=True):
        menu_dropdown = item[2]
        html.append('                <option value="../sample_html/sample_'+release+'_'+platform+'_'+menu_dropdown+'.html">'+menu_dropdown+'</option>\n')
        
    html.append('            </select>\n')
    html.append('        </form>\n')
    if len(bad_list) > 0:
        html.append('       <p>\n')
        html.append('       </br>\n')
        html.append('       </br>\n')
        html.append('       The following is a list of the most recent EDM size tests that fall outside the nominal range. Click on the links to go to a summary of the results.\n')
        html.append('       </p>\n')
    html.append('       </div><!-- container -->\n')
    
    # --- List of bad tests ---
    added_list = []
    for item in bad_list:
        slice = item[3]
        if slice not in added_list:
            added_list.append(slice)
            html.append('        <div id="container">\n')
            html.append('            Category - '+slice+'</br>\n')
            html.append('            <p class="tab">\n')
            for subitem in bad_list:
                if subitem[3] == slice:
                    menu = subitem[2]
                    size = subitem[4]
                    date = subitem[5]
                    html.append('             '+str(date)+' - <a href="../sample_html/sample_'+release+'_'+platform+'_'+menu+'.html#'+slice+'">'+menu+'</a></br>\n')
            html.append('            </p>\n')
            html.append('       </div><!-- container -->\n')
    # --- List of bad tests ---
    
    html.append('    </body>\n')
    html.append('</html>\n')

    html_file = open(  os.path.join(overview_html, 'overview_'+release+'_'+platform+'.html'), 'w'  )
    for line in html:
        html_file.write(line)

    return
# =======================

# Make MCsample pages
# =======================
def makepage_MCsample(ReleasePlatformMenu, ReleasePlatformMenuSlice):

    release  = (ReleasePlatformMenuSlice[0])[0]
    platform = (ReleasePlatformMenuSlice[0])[1]
    menu     = (ReleasePlatformMenuSlice[0])[2]

    html = []

    html.append('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n')
    html.append('<html>\n')
    
    # --- head ---
    html.append('    <head>\n')
    html.append('        <title>'+release+' ['+platform+'] - '+menu+'</title>\n')
    html.append('        <link rel="stylesheet" type="text/css" href="../css/def.css">\n')
    html.append('        <style type="text/css">\n')
    html.append('            body {font-family: sans-serif}\n')
    html.append('            table {font-family: sans-serif}\n')
    html.append('        </style>\n')
    html.append('        <script type="text/javascript">\n')
    html.append('        </script>\n')
    html.append('    </head>\n')
    # --- head ---
    
    html.append('    <body>\n')
    
    # --- script ---
    html.append('         <script type="text/javascript">\n')
    html.append('            function goToPage(url)\n')
    html.append('            {\n')
    html.append('            if (url != "")\n')
    html.append('            {\n')
    html.append('            //this.open(url);\n')
    html.append('            location = url;\n')
    html.append('            }\n')
    html.append('            }\n')
    html.append('        </script>\n')
    # --- script ---
    
    # --- title bar ---
    html.append('        <div id="container">\n')
    html.append('        <div style="font-size:20px; line-height:35px">\n')
    html.append('            Release     : '+release+'</br>\n')
    html.append('            Platform    : '+platform+'</br>\n')
    html.append('            <div style="line-height:10px"></br></div>\n')
    html.append('        </div>\n')
    html.append('        <form>\n')
    html.append('            <label>Menu/Sample : </label>\n')
    html.append('            <select onchange="goToPage(this.options[this.selectedIndex].value)">\n')
    html.append('                <option selected>'+menu+'</option>\n')
    html.append('                <option value="../overview_html/overview_'+release+'_'+platform+'.html">Overview</option>\n')

    for item in sorted(ReleasePlatformMenu, reverse=True):
        menu_dropdown = item[2]
        html.append('                <option value="../sample_html/sample_'+release+'_'+platform+'_'+menu_dropdown+'.html">'+menu_dropdown+'</option>\n')

    html.append('            </select>\n')
    html.append('        </form>\n')
    
    # --- slice links ---
    html.append('        <br>\n')
    html.append('        Click on links below to jump to results section on this page (red links indicate problems)\n')
    html.append('        </br>\n')
    for item in sorted(ReleasePlatformMenuSlice):
        slice = item[3]
        size = mostRecentSizeAndDate(release, platform, menu, slice)
        if goodTest(size[0], release, platform, menu, slice) == 1:
            html.append('        <a href="#'+slice+'">'+slice+'</a>&nbsp;\n')
        if goodTest(size[0], release, platform, menu, slice) == 0:
            html.append('        <a style="color:red;" href="#'+slice+'"><b>'+slice+'</b></a>&nbsp;\n')
    
    # --- slice links ---
    
    html.append('        </div><!-- container -->\n')
    # --- title bar ---
    
    
    
    for item in sorted(ReleasePlatformMenuSlice):
        # ---------------------------------------------------------
        slice = item[3]
        
        summaryFile_abspath = os.path.join(summary_home,'rtt',release,'build',platform,'offline','TrigAnalysisTest',menu,'trigger'+slice+".txt")
        summaryFile_relpath = ".."+summaryFile_abspath[len(project_home):]
        
        nom = category_size_dict.getCategoryNominalSize(release, platform, menu, slice)
        nominal_size_str = nomimalSize_String(nom, release, platform, menu, slice)
        
        plotFile_abs  = os.path.join(plots_home,release+'_'+platform+'_'+menu+'_'+slice+'.png')
        plotFile_rel = "../../"+plotFile_abs[len(project_home)+1:]
        # ---------------------------------------------------------
        
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        
        # --- slice container ---
        html.append('        <div id="container">\n')
                
                # --- left table ---
        html.append('        <div id="left">\n')
        html.append('            <a name="'+slice+'"></a>\n')
        html.append('            <table width="90%"><tr><td>\n')
        html.append('                <p>\n')
        html.append('                   '+slice+' ( <a href="../results_html/results_'+release+'_'+platform+'_'+menu+'_'+slice+'.html" target="_blank"> <b>full results</b></a> )</br>\n')
        html.append('                   <font size="3">Nominal = '+nominal_size_str+'</font>\n')
        html.append('                   <br></br>\n')
        
        # make table
        html_Table(summaryFile_abspath, 7, nom[0], nom[1], html, 0)
        
        html.append('                </p>\n')
        html.append('            </td></tr></table>\n')
        html.append('            <p><br></p>\n')
        html.append('        </div><!-- left -->\n')
                # --- left table ---
                
                # --- right image ---        
        html.append('        <div id="right">\n')
        if os.path.exists(plotFile_abs):
            html.append('        <a href="'+plotFile_rel+'"> <img src="'+plotFile_rel+'" width="400" /> </a>\n')
        html.append('        </div><!-- right -->\n')
                # --- right image ---
                
        html.append('        <div class="clear"></div>\n')
        html.append('        </div><!-- container -->    \n')
        # --- slice container ---
        
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            
    html.append('    </body>\n')
    html.append('</html>\n')

    html_file = open(  os.path.join(sample_html,'sample_'+release+'_'+platform+'_'+menu+'.html'), 'w'  )
    for line in html:
        html_file.write(line)


    return
# =======================


# Make results page for each slice in Release/Platform/Menu
# =======================
def makepage_Results(ReleasePlatformMenuSlice):

    release  = (ReleasePlatformMenuSlice[0])[0]
    platform = (ReleasePlatformMenuSlice[0])[1]
    menu     = (ReleasePlatformMenuSlice[0])[2]

    for item in ReleasePlatformMenuSlice:
        # ---------------------------------------------------------
        slice = item[3]
        
        summaryFile_abspath = os.path.join(summary_home,'rtt',release,'build',platform,'offline','TrigAnalysisTest',menu,'trigger'+slice+".txt")
        summaryFile_relpath = ".."+summaryFile_abspath[len(project_home):]
        
        nom = category_size_dict.getCategoryNominalSize(release, platform, menu, slice)
        nominal_size_str = nomimalSize_String(nom, release, platform, menu, slice)
        
        plotFile_abs  = os.path.join(plots_home,release+'_'+platform+'_'+menu+'_'+slice+'.png')
        plotFile_rel = "../../"+plotFile_abs[len(project_home)+1:]
        # ---------------------------------------------------------
        
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        html = []
    
        html.append('<html>\n')

        html.append('    <head>\n')
        html.append('        <title>'+release+' ['+platform+'] - '+menu+' - '+slice+'</title>\n')
        html.append('        <link rel="stylesheet" type="text/css" href="../css/def.css">\n')
        html.append('        <style type="text/css">\n')
        html.append('            body {font-family: sans-serif}\n')
        html.append('            table {font-family: sans-serif}\n')
        html.append('        </style>\n')
        html.append('        <script type="text/javascript">\n')
        html.append('        </script>\n')
        html.append('    </head>\n')

        html.append('    <body>\n')
        
        html.append('        <div id="container" style="font-size:20px; line-height:35px">\n')
        html.append('            Release      : '+release+'</br>\n')
        html.append('            Platform     : '+platform+'</br>\n')
        html.append('            Menu/Sample  : '+menu+'</br>\n')
        html.append('            Category     : '+slice+'</br>\n')
        html.append('            Nominal Size : '+nominal_size_str+'</br>\n')
        html.append('        </div><!-- container -->\n')
                
        if os.path.exists(plotFile_abs):
            html.append('        <div id="container">\n')
            html.append('            <a href="'+plotFile_rel+'"> <img src="'+plotFile_rel+'" width="800" /> </a>\n')
            html.append('        </div><!-- container -->\n')
        
        html.append('        <div id="container">\n')
        html.append('            </td></tr></table>\n')
        html.append('                <p>\n')
        
        # make table
        html_Table(summaryFile_abspath, -1, nom[0], nom[1], html, 1)
        
        html.append('                </p>\n')
        html.append('            </td></tr></table>\n')
        html.append('        </div><!-- container -->    \n')
        
        html.append('    </body>\n')
        html.append('</html>\n')
    
        html_file = open(  os.path.join(results_html,'results_'+release+'_'+platform+'_'+menu+'_'+slice+'.html'), 'w' )
        for line in html:
            html_file.write(line)
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    
    return
# =======================    

#--------------------------------------------------------------------------------------------------------------------------------


# Find all Builds in summary files to include in web page
# =======================
Build = []
num_builds = 0

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
            accepted_range = size * .05
            category = os.path.basename(summary_file)[len('trigger'):-len('.txt')]


for file in glob.glob(  os.path.join(summary_home,'rtt','*','build','*','offline','TrigAnalysisTest','*','*.txt')  ):

    # Get the test build info from the full path name
    parts = file[len(summary_home):].split('/')
    release  = parts[2]
    platform = parts[4]
    menu     = parts[7]
    slice    = parts[8][len('trigger'):-len('.txt')]

    for releasePattern in branches_to_include:
        added = 0
        if release.count(releasePattern) and not added:
            for menuPattern in menuToInclude:
                if menu.count(menuPattern) and not added:                    
                    Build.append([release, platform, menu, slice])
                    num_builds += 1
                    added = 1
            
print 'Number of files to process = %s' % str(num_builds)
# =======================

# for item in Build:
    # print item

# Create directory to hold plots of builds
if not os.path.exists(plots_home):
    print "------> Images directory does not exist"
    print "------> Making Images directory : %s" % plots_home
    os.makedirs(plots_home)
    
if not os.path.exists(overview_html):
    print "------> Overview directory does not exist"
    print "------> Making Overview directory : %s" % overview_html
    os.makedirs(overview_html)
    
if not os.path.exists(sample_html):
    print "------> Samples directory does not exist"
    print "------> Making Samples directory : %s" % sample_html
    os.makedirs(sample_html)
    
if not os.path.exists(results_html):
    print "------> Results directory does not exist"
    print "------> Making Results directory : %s" % results_html
    os.makedirs(results_html)

# # Remove old images from image directory
remove_list = glob.glob(  os.path.join(plots_home, '*')  )
for item in remove_list:
    os.remove(item)
    
# Remove old html sub-pages in web_home
remove_list = glob.glob(  os.path.join(overview_html, 'overview_*.html')  )
for item in remove_list:
    os.remove(item)
remove_list = glob.glob(  os.path.join(sample_html, 'sample_*.html')  )
for item in remove_list:
    os.remove(item)
remove_list = glob.glob(  os.path.join(results_html, 'results_*.html')  )
for item in remove_list:
    os.remove(item)


# Make plots of all builds to be included in web page
# =======================
for item in Build:
    release  = item[0]
    platform = item[1]
    menu     = item[2]
    slice    = item[3]
    
    summaryFile_abspath = os.path.join(summary_home,'rtt',release,'build',platform,'offline','TrigAnalysisTest',menu,'trigger'+slice+".txt")

    plotfile  = os.path.join(plots_home,release+'_'+platform+'_'+menu+'_'+slice+'.png')
    plottitle = release+' / '+platform+' / '+menu+' / '+slice
    
    summaryFile = open(summaryFile_abspath, 'r')

    # Make plots
    Xdate = []
    Ysize = []
    for line in summaryFile:
	line = line.split()	
	X = datetime.date(int(line[0]), int(line[1]), int(line[2]))
	Y = float(line[6])
	if Y > 0.000:
		Xdate.append(X)
		Ysize.append(Y)

    if len(Ysize) > 0:
        xfmt = dates.DateFormatter('%Y %b %d')
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.xaxis.set_major_formatter(xfmt)
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
        
        plt.plot_date(Xdate, Ysize, 'bo-')
        plt.title(plottitle, fontsize=10)
        plt.xlim(Xdate[0]-datetime.timedelta(days=1), Xdate[-1]+datetime.timedelta(days=1))
        plt.ylim(0, max(Ysize)*1.1)
        plt.xticks(rotation='vertical')
        plt.xlabel('Date')
        plt.ylabel('Size/Evt (kb)')
        plt.gcf().subplots_adjust(bottom=0.25)
        
        plt.savefig(plotfile)

# =======================


# Make list of Release/Platform (no double entries)
# =======================
ReleasePlatform = []
for item in Build:
    release  = item[0]
    platform = item[1]
    menu     = item[2]
    slice    = item[3]
    found_RP = 0
    for entry in ReleasePlatform:
        if (entry[0] == release) and (entry[1] == platform):
            found_RP = 1
    if not found_RP:
        ReleasePlatform.append([release, platform])
        
makepage_Menu(ReleasePlatform)
# =======================

# Loop over each Release/Platform
# =======================
bad_list_main = []
for RP in ReleasePlatform:

    # For each Release/Platform, make list of all available Menus (no double entries)
    # ----------------------
    ReleasePlatformMenu = []
    for item in Build:
        release  = item[0]
        platform = item[1]
        menu     = item[2]
        slice    = item[3]
        if (release == RP[0]) and (platform == RP[1]):
            found_RPM = 0
            for RPM in ReleasePlatformMenu:
                if (release == RPM[0]) and (platform == RPM[1]) and (menu == RPM[2]):
                    found_RPM = 1
            if not found_RPM:
                ReleasePlatformMenu.append([release, platform, menu])
                
    
    # ----------------------

    # For each Release/Platform/Menu, make list of all available Slices
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@
    bad_list = []
    for RPM in ReleasePlatformMenu:
        ReleasePlatformMenuSlice = []
        for item in Build:
            release  = item[0]
            platform = item[1]
            menu     = item[2]
            slice    = item[3]
            if (release == RPM[0]) and (platform == RPM[1]) and (menu == RPM[2]):
                found_RPMS = 0
                for RPMS in ReleasePlatformMenuSlice:
                    if (release == RPMS[0]) and (platform == RPMS[1]) and (menu == RPMS[2]) and (slice == RPMS[3]):
                        found_RPMS = 1
                if not found_RPMS:
                    size = mostRecentSizeAndDate(release, platform, menu, slice)
                    if goodTest(size[0], release, platform, menu, slice) == 0:
                        bad_list.append([release, platform, menu, slice, size[0], size[1]])
                        bad_list_main.append([release, platform, menu, slice, size[0], size[1]])
                    ReleasePlatformMenuSlice.append([release, platform, menu, slice])
        
        makepage_Overview(ReleasePlatformMenu, bad_list)
        makepage_MCsample(ReleasePlatformMenu, ReleasePlatformMenuSlice)
        makepage_Results(ReleasePlatformMenuSlice)
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@

# =======================

makepage_Main(bad_list_main)
