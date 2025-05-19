#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# DEX2XML
# =======
#
# dex2xml is a Python script to convert DEXonline database to xml format for creating a MOBI dictionary.
#
# Due to Kindle fonts, the diacritics for Romanian language are not displayed properly
# (Romanian standard defines diacritics as letters with comma (, ) and Kindle displays these with cedilla)
# Due to this problem, searching for terms containing diacritics with comma would not return any result.
# This was overcome by exporting terms and inflected forms both with comma and with cedilla.
#
# Tested with Kindle Paperwhite 2013 and Kindle Keyboard 2010
#
# This python script is based on tab2opf.py by Klokan Petr Pøidal (www.klokan.cz)
# The regexs for formatting definitions are adapted from:
# https://github.com/dexonline/dexonline/blob/master/lib/Constant.php#L68
# https://wiki.dexonline.ro/wiki/Ghidul_voluntarului
#
# Requirements:
# -------------
# * Linux or Windows enivronment
# * MySQL server
# * copy of DEXonline database - download and installation instructions: http://wiki.dexonline.ro/wiki/Instruc%C8%9Biuni_de_instalare
# * Python (this script was tested using Python 3.10)
# * PyMySql package (compiled from sources or installed using "pip install pymysql")
#
# optional:
# * kindlegen for generating MOBI format (available for Linux/Windows/Mac at http://www.amazon.com/gp/feature.html?docId=1000765211)
#
# Version history:
# ----------------
#     0.9.2
#         updated to work with Python 3.10
#         fixed "A" chapter not being generated correctly
#         implemented formatting for definitions
#         added workaround for displaying the titles from "Mic dictionar mitologic greco-roman"
#         reworked page formatting, cleaned up templates
#
#     0.9.1
#         added parameter to select how the diacritics should be exported (comma, cedilla, both)
#
#     0.9.0
#         output file compliant with EPUB Publications 3.0 (http://www.idpf.org/epub/30/spec/epub30-publications.html)
#         added TOC
#         added abbreviation page
#         added full interactive mode
#         added full batch mode
#         added usage help
#
#     0.2.2
#         various bugfixes and improvements
#         added posibility to directly run 'kindlegen' to convert the OPF to MOBI
#
#     0.2.1
#         added parameters for connecting to MySql server
#         added posibility to choose the dictionary sources
#
#     0.2
#         initial dex2xml.py version
#
#     0.1
#         initial version of tab2opf.py - Copyright (C) 2007 - Klokan Petr Pøidal (www.klokan.cz)
#
# License
# -------
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.


import os
import re
import sys
import glob
import time
import errno
import codecs
import signal
import getpass
import argparse
import subprocess
from argparse import RawTextHelpFormatter

import pymysql

# VERSION
VERSION = "0.9.2"

source_list = ['27', '40', '65', '36', '22']
# source_list = ['12'] # DER
# source_list = ['19'] # DOOM2
# source_list = ['21', '55'] # MDN
# source_list = ['26'] # Argou
# source_list = ['53'] # MDA2
# source_list = ['23'] # DLRLV
# source_list = ['27', '40', '65', '36', '22', '23', '26', '21', '55'] # full
source_list_names = []
source_list_count = []
inflection_map = {}

mysql_server = ''
mysql_port = ''
mysql_user = ''
mysql_passwd = ''
mysql_db = ''
name = ''
conn = ''
cur = ''
cur2 = ''
to = ''

ReplacementsRegexDict = {
    r' - ': ' – ',  # U+2013
    r' \*\* ': ' ♦ ', # U+2666
    r' \* ': ' ◊ ',  # U+25CA
    r'\\\'': '’',   # U+2019
    r'<': '&lt;',
    r'>': '&gt;',
    r'▶(.*?)◀': '',
    r'(?<!\\)"([^"]*)"': '„\\1”',
    r'(?<!\\)##(.*?)(?<!\\)##': '<span class="abr">\\1</span>',
    r'(?<!\\)#(.*?)(?<!\\)#': '<span class="abr">\\1</span>',
    r'(?<!\\)\{{2}(.*?)(?<![+])\}{2}': ' [Notă: \\1]',
    r'(?<!\\)%(.*?)(?<!\\)%': '\\1',
    r'(?<!\\)@(.*?)(?<!\\)@': '<b>\\1</b>',
    r'(?<!\\)\$(.*?)(?<!\\)\$': '<i>\\1</i>',
    r'(?<!\\)\^(\d)': '<sup>\\1</sup>',
    r'(?<!\\)\^\{([^}]*)\}': '<sup>\\1</sup>',
    r'(?<!\\)_(\d)': '<sub>\\1</sub>',
    r'(?<!\\)_\{([^}]*)\}': '<sub>\\1</sub>',
    r'(?<!\\)\'([a-zA-ZáàäåăắâấÁÀÄÅĂẮÂẤçÇéèêÉÈÊíîî́ÍÎÎ́óöÓÖșȘțȚúüÚÜýÝ])': '<span class="und">\\1</span>',
    r'\\%': '%',
    r'\\$': '$',
}

OPFTEMPLATEHEAD = u"""<?xml version="1.0" encoding="utf-8"?>
<package unique-identifier="uid">
    <metadata>
        <dc-metadata xmlns:dc="http://purl.org/metadata/dublin_core" xmlns:oebpackage="http://openebook.org/namespaces/oeb-package/1.0/">
            <dc:Identifier id="uid">%s</dc:Identifier>
            <!-- Title of the document -->
            <dc:Title><h2>%s</h2></dc:Title>
            <dc:Language>ro</dc:Language>
            <dc:Creator>dex2xml</dc:Creator>
            <dc:Description>DEX online</dc:Description>
            <dc:Source>http://dexonline.ro</dc:Source>
            <dc:Type>dictionary</dc:Type>
            <dc:Date>%s</dc:Date>
        </dc-metadata>
        <x-metadata>
            <output encoding="utf-8" content-type="text/x-oeb1-document"></output>
            <!-- That's how it's recognized as a dictionary: -->
            <DictionaryInLanguage>ro</DictionaryInLanguage>
            <DictionaryOutLanguage>ro</DictionaryOutLanguage>
            <DefaultLookupIndex>word</DefaultLookupIndex>
        </x-metadata>
    </metadata>
    <manifest>
        <item id="cimage" media-type="image/jpeg" href="cover.jpg" properties="cover-image"/>
        <item id="toc" properties="nav" href="%s.xhtml" mediatype="application/xhtml+xml"/>
        <item id="stats" href="%s.html" mediatype="text/html"/>
        <item id="abbr" href="Abrevieri.html" mediatype="text/html"/>
        <!-- list of all the files needed to produce the .prc file -->
"""

OPFTEMPLATEMIDDLE = u"""    </manifest>
    <spine>
        <itemref idref="cimage"/>
        <itemref idref="toc"/>
        <itemref idref="stats"/>
        <itemref idref="abbr"/>
        <!-- list of the html files in the correct order  -->
"""

OPFTEMPLATEEND = u"""   </spine>
    <guide>
        <reference type="toc" title="Table of Contents" href="%s.xhtml"/>
    </guide>
</package>
"""

TOCTEMPLATEHEAD = u"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en"
    lang="ro">
    <head>
        <title>DEXonline - Table of Contens</title>
    </head>
    <body>
        <h4 style="text-align:center">Index</h4>
        <hr>
            <nav epub:type="toc" id="toc">
                    <ol>
                        <li><a href="%s.html">Statistici</a></li>
                        <li><a href="Abrevieri.html">Abrevieri</a></li>"""

TOCTEMPLATEEND = u"""
                    </ol>
            </nav>
    </body>
</html>
"""

FRAMESETTEMPLATEHEAD = u"""<html xmlns:math="http://exslt.org/math" xmlns:svg="http://www.w3.org/2000/svg" xmlns:tl="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf" xmlns:saxon="http://saxon.sf.net/" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:cx="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:mbp="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf" xmlns:mmc="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf" xmlns:idx="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf">
    <head>
        <link href="stylesheet.css" rel="stylesheet" type="text/css"/>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    </head>
    <body>
        <mbp:frameset>"""

FRAMESETTEMPLATEEND = u"""
        </mbp:frameset>
    </body>
</html>
"""

IDXTEMPLATEHEAD = u"""
            <idx:entry name="word" scriptable="yes">
                <idx:orth value="%s">"""

IDXTEMPLATEEND = u"""
                </idx:orth>
                <p class="def">%s</p>
            </idx:entry>
            <hr>"""

IDXINFTEMPLATEHEAD = u"""
                    <idx:infl>"""

IDXINFTEMPLATEEND = u"""
                    </idx:infl>"""

IDXINFVALUETEMPLATE = u"""
                        <idx:iform value="%s" exact="yes" />"""

STATSTEMPLATEHEAD = u"""<html xmlns:math="http://exslt.org/math" xmlns:svg="http://www.w3.org/2000/svg" xmlns:tl="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf" xmlns:saxon="http://saxon.sf.net/" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:cx="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:mbp="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf" xmlns:mmc="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf" xmlns:idx="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <title>Statistici - Dexonline</title>
    </head>
    <body>
        <p><h4 style="text-align:center">Prezenta versiune conține %s definiții din următoarele surse:</h4></p>
        <br>
        <ul>
"""

STATSVALUETEMPLATE = u"""
            <li><b>%s - %s</b></li>"""

STATSTEMPLATEEND = u"""
        </ul>
        <br>
        <h4 style="text-align:center">Generat: %s</h4>
    </body>
</html>"""


def signal_handler(signal, frame):
    global name
    global to

    print('\n\nExport aborted!')
    if name:
        response = input("Do you want to delete the temporary files (%s*.html)? [Y/n]: " % name).lower()
        if (response == 'y') or (response == 'yes'):
            if to:
                to.close()
            deleteFiles(name, mobi=True)
    sys.exit(0)


def replaceWithCedilla(termen):
    findreplace = [
        (u"\u0218", u"\u015E"),
        (u"\u0219", u"\u015F"),
        (u"\u021A", u"\u0162"),
        (u"\u021B", u"\u0163"),
    ]
    for couple in findreplace:
        termen = termen.replace(couple[0], couple[1])
    return termen


def isWithComma(termen):
    chars = set(u"\u0218\u0219\u021A\u021B")
    if any((c in chars) for c in termen):
        return True
    else:
        return False

def printInflections(termen, inflections):
    if "â" in termen and len(termen) > 1:
        to.write(IDXINFVALUETEMPLATE % termen.replace("â", "î"))
    if len(inflections) > 0:
        to.write(IDXINFTEMPLATEHEAD)
        for inflection in inflections:
            to.write(IDXINFVALUETEMPLATE % inflection)
            if "â" in inflection and len(termen) > 1:
                to.write(IDXINFVALUETEMPLATE % inflection.replace("â", "î"))
        to.write(IDXINFTEMPLATEEND)

def inflectionsList(iddef):
    global cur2
    inflections = []

    cur2.execute("""
SELECT DISTINCT inf.formUtf8General AS inflection
FROM InflectedForm AS inf
JOIN Lexeme l ON inf.lexemeId = l.id
JOIN EntryLexeme el ON el.lexemeId = l.id
JOIN Entry e ON el.entryId = e.id
JOIN EntryDefinition ed ON ed.entryId = e.id
JOIN Definition d ON ed.definitionId = d.id
WHERE d.id = %s AND el.main = 1
""" % iddef)

    if cur2.rowcount > 0:
        for i in range(cur2.rowcount):
            inf = cur2.fetchone()
            inflection = inf["inflection"]
            if inflection_map.get(inflection):
                continue
            inflection_map[inflection] = True
            if isWithComma(inflection):
                if (args.diacritics == 'cedilla') or (args.diacritics == 'both'):
                    inflections.append(replaceWithCedilla(inflection))
                if (args.diacritics == 'comma') or (args.diacritics == 'both'):
                    inflections.append(inflection)
            else:
                inflections.append(inflection)
    return inflections

def formatDefinition(definition):
    result = definition

    for key in ReplacementsRegexDict:
        result = re.sub(key, ReplacementsRegexDict[key], result)

    return result

def printTerm(iddef, termen, definition, source):
    global to

    to.write(IDXTEMPLATEHEAD % (termen))
    printInflections(termen, inflectionsList(iddef))

    theDefinition = definition
    if len(source_list) > 2:
        # only show the source tags if multiple dictionary file
        # hide for 1 or 2 similar dictionaries, such as MDN
        theDefinition += " <i>(%s)</i>" % source
    to.write(IDXTEMPLATEEND % theDefinition)

def deleteFile(filename):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise                    # re-raise exception if a different error occured


def deleteFiles(filemask, mobi):
    for fl in glob.glob(u'' + filemask + u'*.html'):
        deleteFile(fl)
    deleteFile(filemask + '_TOC.xhtml')
    deleteFile(filemask + '_STATS.html')
    deleteFile(filemask + '.opf')
    if mobi:
        deleteFile(filemask + '.mobi')


def deleteTemporaryFiles():
    response = 'n'
    if args.interactive:
        response = input("\nDo you want to delete the temporary files (%s*.html and %s.opf) [Y/n]?: " % (name, name)).lower() or 'y'
    if (args.temp_files) or ((response == 'y') or (response == 'yes')):
        deleteFiles(name, mobi=False)
        print("Done removing files.")


def tryConnect():
    global mysql_server
    global mysql_port
    global mysql_user
    global mysql_passwd
    global mysql_db
    global conn
    global cur
    global cur2

    try:
        conn = pymysql.connect(host=mysql_server, port=mysql_port, user=mysql_user, passwd=mysql_passwd, db=mysql_db, charset='utf8')
    except pymysql.OperationalError as e:
        print('\nGot error {!r}, errno is {}'.format(e, e.args[0]))
        print("\nCould not connect to MySQL server using the parameters you entered.\nPlease make sure that the server is running and try again...")
        sys.exit()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur2 = conn.cursor(pymysql.cursors.DictCursor)


def exportDictionaryFiles():
    global to
    global cur

    start_time = time.time()
    cur.execute("""
SELECT 
    d.id,
    d.lexicon,
    d.internalRep,
    s.shortName AS source,
    d.sourceId
FROM Definition d
JOIN Source s ON d.sourceId = s.id
WHERE s.id IN (%s)
    AND d.lexicon <> ''
    AND d.status = 0
ORDER BY d.lexicon ASC,
         s.year DESC""" % ', '.join(source_list))

    if cur.rowcount == 0:
        print("Managed to retrieve 0 definitions from dictionary...\nSomething was wrong...")
        sys.exit()

    manifest = ''
    spine = ''
    letter = ''
    toc = ''
    to = False

    for i in range(cur.rowcount):
        row = cur.fetchone()

        did = row["id"]
        dterm = row["lexicon"]
        ddef = formatDefinition(row["internalRep"])
        dsrc = row["source"]

        # almost all the definions from the "Mic dictionar mitologic greco-roman"
        # are names of heroes / gods / places. This workaround displays the title
        # with a capital letter
        if row["sourceId"] == 36:
            dterm = dterm.title()
        
        specialFirstLetters = ["A", "Ǻ", "Å", "Ă", "Â", "À", "Á"]
        specialFirstLetterWorkaround = not (letter in specialFirstLetters and dterm[0].upper() in specialFirstLetters)

        if letter != dterm[0].upper() and specialFirstLetterWorkaround:
            letter = dterm[0].upper()
            if to:
                to.write(FRAMESETTEMPLATEEND)
                to.close()
            filename = name + '_' + letter + '.html'
            if os.path.isfile(filename):
                to = codecs.open(filename, "a", "utf-8")
            else:
                to = codecs.open(filename, "w", "utf-8")
                to.write(FRAMESETTEMPLATEHEAD)
                manifest = manifest + '\t\t<item id="' + letter + '" href="' + to.name + '" media-type="text/x-oeb1-document"/>\n'
                spine = spine + '\t\t<itemref idref="' + letter + '"/>\n'
                toc = toc + '\n\t\t\t\t\t\t<li><a href="' + to.name + '">' + letter + '</a></li>'

        sys.stdout.write("\rExporting \"%s\" %s of %s..." % (dterm, i + 1, cur.rowcount))
        # if the term contains comma it will export the term again but written with cedilla
        if isWithComma(dterm):
            if (args.diacritics == 'cedilla') or (args.diacritics == 'both'):
                printTerm(did, replaceWithCedilla(dterm), ddef, dsrc)
            if (args.diacritics == 'comma') or (args.diacritics == 'both'):
                printTerm(did, dterm, ddef, dsrc)
        else:
            printTerm(did, dterm, ddef, dsrc)

    end_time = time.time()
    print("\nExport time: %s" % time.strftime('%H:%M:%S', time.gmtime((end_time - start_time))))

    if to:
        to.write(FRAMESETTEMPLATEEND)

    if to:
        to.close()

    generateStats(name, cur.rowcount)

    cur.close()
    cur2.close()

    to = codecs.open("%s.opf" % name, "w", "utf-8")
    to.write(OPFTEMPLATEHEAD % (name, name, time.strftime("%d/%m/%Y"), name + '_TOC', name + '_STATS'))
    to.write(manifest)
    to.write(OPFTEMPLATEMIDDLE)
    to.write(spine)
    to.write(OPFTEMPLATEEND % (name + '_TOC'))
    to.close()

    to = codecs.open("%s_TOC.xhtml" % name, "w", "utf-8")
    to.write(TOCTEMPLATEHEAD % (name + '_STATS'))
    to.write(toc)
    to.write(TOCTEMPLATEEND)
    to.close()


def runKindlegen():
    start_time = time.time()
#   returncode = subprocess.call(['kindlegen', name + '.opf', '-verbose', '-dont_append_source', '-c2'])
    returncode = subprocess.call(['kindlegen', name + '.opf', '-verbose', '-dont_append_source'])
    end_time = time.time()
    if returncode < 0:
        print("\nKindlegen failed with return code %s.\nTemporary files will not be deleted..." % returncode)
        return False
    else:
        print("\nKindlegen finished in %s" % time.strftime('%H:%M:%S', time.gmtime((end_time - start_time))))
        return True


def kindlegen():
    response = 'n'
    try:
        subprocess.call(['kindlegen'], stdout=subprocess.PIPE)
    except OSError as e:
        if e.errno == errno.ENOENT:
            print('Kindlegen was not on your path; not generating .MOBI version...')
            print('You can download kindlegen for Linux/Windows/Mac from http://www.amazon.com/gp/feature.html?docId=1000765211')
            print('and then run: <kindlegen "%s.opf"> to convert the file to MOBI format.' % name)
            return
        else:
            raise

    if args.interactive:
        response = input("\nKindlegen was found in your path.\nDo you want to launch it to convert the OPF to MOBI? [Y/n]: ") or 'y'
    if (args.kindlegen) or ((response == 'y') or (response == 'yes')):
        if runKindlegen():
            deleteTemporaryFiles()


def printSources():
    global cur
    global source_list
    global source_list_names
    global source_list_count

    source_list_count = []
    source_list_names = []
    cur.execute("select id, concat(name, ' ', year) as source, (select count(lexicon) from Definition d where d.status = 0 and d.sourceId = s.id) as defcount from Source s where id in (%s) and canDistribute = 1 order by id" % ', '.join(source_list))
    print("\nSources of dictionaries for export:\n")
    for i in range(cur.rowcount):
        src = cur.fetchone()
        srcid = src["id"]
        srcname = src["source"]
        srccount = src["defcount"]
        print('id:%s defcount:%s name:"%s"' % (srcid, srccount, srcname.encode("utf-8")))
        source_list_names.append(srcname)
        source_list_count.append(srccount)
    print('\n')


def generateStats(filemask, nrdef):
    global source_list_names
    global source_list_count

    stats = codecs.open(filemask + "_STATS.html", "w", "utf-8")
    stats.write(STATSTEMPLATEHEAD % nrdef)

    for src in source_list_names:
        stats.write(STATSVALUETEMPLATE % (source_list_count[source_list_names.index(src)], src))

    stats.write(STATSTEMPLATEEND % time.strftime("%d/%m/%Y"))
    stats.close


def interactiveMode():
    global mysql_server
    global mysql_port
    global mysql_user
    global mysql_passwd
    global mysql_db
    global name
    global source_list
    global source_list_names
    global source_list_count
    global to

    mysql_server = input('Enter the name/ip of the MySQL server [default: %s]: ' % 'localhost') or 'localhost'
    print("Using '%s'" % mysql_server)

    mysql_port = input('Enter the port for the server [default: %s]: ' % 3306) or 3306
    print("Using '%s'" % mysql_port)

    mysql_user = input('Enter the username for the MySQL server [default: %s]: ' % 'root') or 'root'
    print("Using '%s'" % mysql_user)

    mysql_passwd = getpass.getpass('Enter the password for the user %s: ' % mysql_user)
    print("Using '%s'" % ('*' * len(mysql_passwd)))

    mysql_db = input('DEXonline database name [default: %s]: ' % 'dexonline') or 'dexonline'
    print("Using '%s'" % mysql_db)

    name = input("\nEnter the filename of the generated dictionary file.\nExisting files will be deleted.\nMay include path [default: '%s']: " % "DEXonline") or "DEXonline"
    print("Using '%s'" % name)
    diacritics = (input("\nSpecify how the diacritics should be exported [comma/cedilla/BOTH]: ") or "both").lower()
    print("Diacritics will be exported using '%s'" % diacritics.upper())

    tryConnect()

    printSources()

    response = input("Do you want to change the default sources list ? [y/N]: ").lower()
    if (response == 'y') or (response == 'yes'):
        source_list = []
        source_list_names = []
        source_list_count = []
        cur.execute("select id, concat(name, ' ', year) as source, (select count(lexicon) from Definition d where d.status = 0 and d.sourceId = s.id) as defcount from Source s where canDistribute = 1 order by id")
        for i in range(cur.rowcount):
            src = cur.fetchone()
            response = input('\nUse as a source (%s of %s) %s ? [y/N]: ' % (i + 1, cur.rowcount, src["source"].encode("utf-8"))).lower()
            if (response == 'y') or (response == 'yes'):
                srcid = src["id"]
                srcname = src["source"]
                srccount = src["defcount"]
                source_list.append(str(srcid))
                source_list_names.append(srcname)
                source_list_count.append(srccount)

        response = input("Continue [Y/n]: ").lower()
        if (response == 'n') or (response == 'no'):
            sys.exit()
    print

################################################################
# MAIN
################################################################


signal.signal(signal.SIGINT, signal_handler)

parser = argparse.ArgumentParser(add_help=False, formatter_class=RawTextHelpFormatter)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-i", "--interactive", help="run the program in interactive mode", action="store_true")
group.add_argument("-b", "--batch", help="run the program in batch mode, taking parameters from command line", action="store_true")
group.add_argument("-h", "--help", help="print this help file", action="help")
group.add_argument("-v", "--version", help="print the program's version", action="version", version='%(prog)s ' + VERSION)

batchgroup = parser.add_argument_group("Batch arguments")
batchgroup.add_argument("-s", "--server", help="Specify the mysql server to connect to.\nDefault: 'localhost'", type=str, default="localhost")
batchgroup.add_argument("-p", "--port", help="Mysql server port.\nDefault: 3306", type=int, default=3306)
batchgroup.add_argument("-u", "--username", help="Specify the username to connect to mysql server.\nDefault: 'root'", type=str, default="root")
batchgroup.add_argument("-passwd", "--password", help="The password of the mysql server.", type=str, default='')
batchgroup.add_argument("-d", "--database", help="dexonline database on the mysql server.\nDefault: 'dexonline'", type=str, default="dexonline")
batchgroup.add_argument("-src", "--sources", help="List of dictionary sources to extract from database.\nMust contain the sources id's from the table 'sources'.\nIf some source doesn't exist or can't be distributed, it will be removed from the list.\nDefault: 27 36", nargs='+', type=str)
batchgroup.add_argument("-o", "--outputfile", help="Filename of output file.\nMay include path.\nExisting files will be deleted first.\nDefault: 'DEXonline'", type=str, default="DEXonline")
batchgroup.add_argument("--diacritics", help="Specify how the diacritics should be exported.\nDefault: 'both'", choices=['comma', 'cedilla', 'both'], type=str, default="both")

batchgroup2 = batchgroup.add_mutually_exclusive_group()
batchgroup2.add_argument("-k", "--kindlegen", help="Do not run kindlegen to convert the output to MOBI.\nDefault: not set", action="store_false", default=True)
batchgroup2.add_argument("-t", "--temp_files", help="Keep the temporary files after running kindlegen.\nDefault: not set", action="store_false", default=True)

args = parser.parse_args()

if args.interactive:
    args.kindlegen = False
    args.temp_files = False
    interactiveMode()
else:
    mysql_server = args.server
    mysql_port = args.port
    mysql_user = args.username
    mysql_passwd = args.password
    mysql_db = args.database
    name = args.outputfile
    if not args.temp_files:
        print("\nWill not remove temporary files after a (successful) conversion with kindlegen...")
    if not args.kindlegen:
        print("\nWill not automatically try to run kindlegen after exporting the dictionary.\nTemporary files will be preserved...")
        args.temp_files = False

    tryConnect()
    print("\nSuccessfully connected to database '%s' on '%s:%d', using username '%s' and password '%s'..." % (mysql_db, mysql_server, mysql_port, mysql_user, '*' * len(mysql_passwd)))
    if args.sources:
        source_list = args.sources

    printSources()

deleteFiles(name, mobi=True)
exportDictionaryFiles()
kindlegen()

if args.interactive:
    input("\nPress <ENTER> to exit...")
