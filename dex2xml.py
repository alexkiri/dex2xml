#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
base_filename = ''
cursor1 = ''
cursor2 = ''
file_output = ''

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
OPFTEMPLATEMANIFEST = u"""
        <item id="%s" href="%s" media-type="text/x-oeb1-document"/>"""

OPFTEMPLATEMIDDLE = u"""    </manifest>
    <spine>
        <itemref idref="cimage"/>
        <itemref idref="toc"/>
        <itemref idref="stats"/>
        <itemref idref="abbr"/>
        <!-- list of the html files in the correct order  -->
"""

OPFTEMPLATESPINE = u"""
        <itemref idref="%s"/>"""

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
        <hr />
        <nav epub:type="toc" id="toc">
            <ol>
                <li><a href="%s.html">Statistici</a></li>
                <li><a href="Abrevieri.html">Abrevieri</a></li>"""
TOCTEMPLATEMIDDLE = u"""
                <li><a href="%s">%s</a></li>"""

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
            <hr />"""

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
        <br />
        <ul>
"""

STATSVALUETEMPLATE = u"""
            <li><b>%s - %s</b></li>"""

STATSTEMPLATEEND = u"""
        </ul>
        <br />
        <h4 style="text-align:center">Generat: %s</h4>
    </body>
</html>"""

SQL_QUERY_INFLECTIONS = """
SELECT DISTINCT inf.formUtf8General AS inflection
FROM InflectedForm AS inf
JOIN Lexeme l ON inf.lexemeId = l.id
JOIN EntryLexeme el ON el.lexemeId = l.id
JOIN Entry e ON el.entryId = e.id
JOIN EntryDefinition ed ON ed.entryId = e.id
JOIN Definition d ON ed.definitionId = d.id
WHERE d.id = %s AND el.main = 1
"""

SQL_QUERY_DEFINITIONS = """
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
ORDER BY
    d.lexicon ASC,
    s.year DESC
"""

SQL_QUERY_SOURCES = """
SELECT 
    id,
    concat(name, ' ', year) AS source,
    (SELECT COUNT(lexicon) FROM Definition d
        WHERE d.status = 0
        AND d.sourceId = s.id)
    AS defcount
FROM Source s
WHERE id IN (%s)
    AND canDistribute = 1
ORDER BY id
"""
def signal_handler(signal, frame):
    print('\n\nExport aborted!')
    if base_filename:
        response = input("Do you want to delete the temporary files (%s*.html)? [Y/n]: " % base_filename).lower()
        if (response == 'y') or (response == 'yes'):
            if file_output:
                file_output.close()
            deleteFiles(base_filename, mobi=True)
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
    if len(inflections) > 0:
        file_output.write(IDXINFTEMPLATEHEAD)
        for inflection in inflections:
            file_output.write(IDXINFVALUETEMPLATE % inflection)
            if "â" in inflection and len(inflection) > 1:
                file_output.write(IDXINFVALUETEMPLATE % inflection.replace("â", "î"))
        file_output.write(IDXINFTEMPLATEEND)

def inflectionsList(iddef):
    inflections = []

    cursor2.execute(SQL_QUERY_INFLECTIONS % iddef)

    if cursor2.rowcount > 0:
        for i in range(cursor2.rowcount):
            inf = cursor2.fetchone()
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
    file_output.write(IDXTEMPLATEHEAD % (termen))
    printInflections(termen, inflectionsList(iddef))

    theDefinition = definition
    if len(source_list) > 3:
        # only show the source tags if multiple dictionary file
        # hide for 1 - 3 similar dictionaries, such as DEX, MDN, etc
        theDefinition += " <i>(%s)</i>" % source
    file_output.write(IDXTEMPLATEEND % theDefinition)

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
    if (args.temp_files):
        deleteFiles(base_filename, mobi=False)
        print("Done removing files.")


def tryConnect():
    global cursor1
    global cursor2

    try:
        mysql_connection = pymysql.connect(host=mysql_server, port=mysql_port, user=mysql_user, passwd=mysql_passwd, db=mysql_db, charset='utf8')
    except pymysql.OperationalError as e:
        print('\nGot error {!r}, errno is {}'.format(e, e.args[0]))
        print("\nCould not connect to MySQL server using the parameters you entered.\nPlease make sure that the server is running and try again...")
        sys.exit()
    cursor1 = mysql_connection.cursor(pymysql.cursors.DictCursor)
    cursor2 = mysql_connection.cursor(pymysql.cursors.DictCursor)


def exportDictionaryFiles():
    global file_output

    start_time = time.time()
    cursor1.execute(SQL_QUERY_DEFINITIONS % ', '.join(source_list))

    if cursor1.rowcount == 0:
        print("Managed to retrieve 0 definitions from dictionary...\nSomething was wrong...")
        sys.exit()

    manifest = ''
    spine = ''
    letter = ''
    toc = ''
    file_output = False

    for i in range(cursor1.rowcount):
        row = cursor1.fetchone()

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
            if file_output:
                file_output.write(FRAMESETTEMPLATEEND)
                file_output.close()
            filename = base_filename + '_' + letter + '.html'
            if os.path.isfile(filename):
                file_output = codecs.open(filename, "a", "utf-8")
            else:
                file_output = codecs.open(filename, "w", "utf-8")
                file_output.write(FRAMESETTEMPLATEHEAD)
                manifest = manifest + OPFTEMPLATEMANIFEST % (letter, file_output.name)
                spine = spine + OPFTEMPLATESPINE % letter
                toc = toc + TOCTEMPLATEMIDDLE % (file_output.name, letter)

        sys.stdout.write("\rExporting \"%s\" %s of %s..." % (dterm, i + 1, cursor1.rowcount))
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

    if file_output:
        file_output.write(FRAMESETTEMPLATEEND)
        file_output.close()

    generateStats(base_filename, cursor1.rowcount)

    cursor1.close()
    cursor2.close()

    file_output = codecs.open("%s.opf" % base_filename, "w", "utf-8")
    file_output.write(OPFTEMPLATEHEAD % (base_filename, base_filename, time.strftime("%d/%m/%Y"), base_filename + '_TOC', base_filename + '_STATS'))
    file_output.write(manifest)
    file_output.write(OPFTEMPLATEMIDDLE)
    file_output.write(spine)
    file_output.write(OPFTEMPLATEEND % (base_filename + '_TOC'))
    file_output.close()

    file_output = codecs.open("%s_TOC.xhtml" % base_filename, "w", "utf-8")
    file_output.write(TOCTEMPLATEHEAD % (base_filename + '_STATS'))
    file_output.write(toc)
    file_output.write(TOCTEMPLATEEND)
    file_output.close()


def runKindlegen():
    start_time = time.time()
#   returncode = subprocess.call(['kindlegen', base_filename + '.opf', '-verbose', '-dont_append_source', '-c2'])
    returncode = subprocess.call(['kindlegen', base_filename + '.opf', '-verbose', '-dont_append_source'])
    end_time = time.time()
    if returncode < 0:
        print("\nKindlegen failed with return code %s.\nTemporary files will not be deleted..." % returncode)
        return False
    else:
        print("\nKindlegen finished in %s" % time.strftime('%H:%M:%S', time.gmtime((end_time - start_time))))
        return True


def kindlegen():
    try:
        subprocess.call(['kindlegen'], stdout=subprocess.PIPE)
    except OSError as e:
        if e.errno == errno.ENOENT:
            print('Kindlegen was not on your path; not generating .MOBI version...')
            print('You can download kindlegen for Linux/Windows/Mac from http://www.amazon.com/gp/feature.html?docId=1000765211')
            print('and then run: <kindlegen "%s.opf"> to convert the file to MOBI format.' % base_filename)
            return
        else:
            raise

    if (args.kindlegen):
        if runKindlegen():
            deleteTemporaryFiles()


def printSources():
    global source_list_names
    global source_list_count

    source_list_count = []
    source_list_names = []
    cursor1.execute(SQL_QUERY_SOURCES % ', '.join(source_list))
    print("\nSources of dictionaries for export:\n")
    for i in range(cursor1.rowcount):
        src = cursor1.fetchone()
        srcid = src["id"]
        srcname = src["source"]
        srccount = src["defcount"]
        print('id:%s defcount:%s name:"%s"' % (srcid, srccount, srcname))
        source_list_names.append(srcname)
        source_list_count.append(srccount)
    print('\n')


def generateStats(filemask, nrdef):
    stats = codecs.open(filemask + "_STATS.html", "w", "utf-8")
    stats.write(STATSTEMPLATEHEAD % nrdef)

    for src in source_list_names:
        stats.write(STATSVALUETEMPLATE % (source_list_count[source_list_names.index(src)], src))

    stats.write(STATSTEMPLATEEND % time.strftime("%d/%m/%Y"))
    stats.close

################################################################
# MAIN
################################################################


signal.signal(signal.SIGINT, signal_handler)

parser = argparse.ArgumentParser(add_help=False, formatter_class=RawTextHelpFormatter)
parser.add_argument("-h", "--help", help="print this help file", action="help")
parser.add_argument("-v", "--version", help="print the program's version", action="version", version='%(prog)s ' + VERSION)

batchgroup = parser.add_argument_group("Batch arguments")
batchgroup.add_argument("-r", "--server", help="Specify the mysql server to connect to.\nDefault: 'localhost'", type=str, default="localhost")
batchgroup.add_argument("-c", "--port", help="Mysql server port.\nDefault: 3306", type=int, default=3306)
batchgroup.add_argument("-u", "--username", help="Specify the username to connect to mysql server.\nDefault: 'root'", type=str, default="root")
batchgroup.add_argument("-p", "--password", help="The password of the mysql server.", type=str, default='')
batchgroup.add_argument("-d", "--database", help="dexonline database on the mysql server.\nDefault: 'dexonline'", type=str, default="dexonline")
batchgroup.add_argument("-s", "--sources", help="List of dictionary sources to extract from database.\nMust contain the sources id's from the table 'sources'.\nIf some source doesn't exist or can't be distributed, it will be removed from the list.\nDefault: 27 36", nargs='+', type=str)
batchgroup.add_argument("-o", "--outputfile", help="Filename of output file.\nMay include path.\nExisting files will be deleted first.\nDefault: 'DEXonline'", type=str, default="DEXonline")
batchgroup.add_argument("--diacritics", help="Specify how the diacritics should be exported.\nDefault: 'both'", choices=['comma', 'cedilla', 'both'], type=str, default="both")

batchgroup2 = batchgroup.add_mutually_exclusive_group()
batchgroup2.add_argument("-k", "--kindlegen", help="Do not run kindlegen to convert the output to MOBI.\nDefault: not set", action="store_false", default=True)
batchgroup2.add_argument("-t", "--temp_files", help="Keep the temporary files after running kindlegen.\nDefault: not set", action="store_false", default=True)

args = parser.parse_args()

mysql_server = args.server
mysql_port = args.port
mysql_user = args.username
mysql_passwd = args.password
mysql_db = args.database
base_filename = args.outputfile
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

deleteFiles(base_filename, mobi=True)
exportDictionaryFiles()
kindlegen()
