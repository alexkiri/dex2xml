DEX2XML
=======

dex2xml is aPython script to convert DEXonline database to xml format for creating a MOBI dictionary.

Due to Kindle fonts, the diacritics for Romanian language are not displayed properly
(Romanian standard defines diacritics as letters with comma (,) and Kindle displays these with cedilla)
Due to this problem, searching for terms containing diacritics with comma would not return any result.
This was overcome by exporting terms and inflected forms both with comma and with cedilla.

Tested with Kindle Paperwhite 2013

This python script is based on tab2opf.py by Klokan Petr Pøidal (www.klokan.cz)

Requirements:
-------------
* Linux or Windows enivronment
* MySQL server
* copy of DEXonline database - download and installation instructions: http://wiki.dexonline.ro/wiki/Instruc%C8%9Biuni_de_instalare
* Python (this script was created and tested using Python 2.7)
* PyMySql package (compiled from sources or installed using "pip install pymysql")

optional:
* kindlegen for generating MOBI format (available for Linux/Windows/Mac at http://www.amazon.com/gp/feature.html?docId=1000765211)

Usage:
------

    dex2xml.py [-i | -b | -h | -v] [-s SERVER] [-p PORT] [-u USERNAME]
                [-passwd PASSWORD] [-d DATABASE]
                [-src SOURCES [SOURCES ...]] [-o OUTPUTFILE] [-k | -t]


    optional arguments:

    -i, --interactive     run the program in interactive mode
    -b, --batch           run the program in batch mode, taking parameters from command line
    -h, --help            print this help file
    -v, --version         print the program's version
    -k, --kindlegen       Run kindlegen to convert the output to MOBI.
                          Default: set
    -t, --temp_files      Delete the temporary files after running kindlegen.
                          Default: set


    Batch arguments:

    -s SERVER, --server SERVER
                        Specify the mysql server to connect to.
                        Default: 'localhost'
    -p PORT, --port PORT  Mysql server port.
                        Default: 3306
    -u USERNAME, --username USERNAME
                        Specify the username to connect to mysql server.
                        Default: 'root'
    -passwd PASSWORD, --password PASSWORD
                        The password of the mysql server.
    -d DATABASE, --database DATABASE
                        DEX database on the mysql server.
                        Default: 'DEX'
    -src SOURCES [SOURCES ...], --sources SOURCES [SOURCES ...]
                        List of dictionary sources to extract from database.
                        Must contain the sources id's from the table 'sources'.
                        Default: 27 28 29 31 32 33 36
    -o OUTPUTFILE, --outputfile OUTPUTFILE
                        Filename of output file.
                        May include path.
                        Existing files will be deleted first.
                        Default: 'DEXonline'

Version history:
----------------
    0.9.0
        output file compliant with EPUB Publications 3.0 (http://www.idpf.org/epub/30/spec/epub30-publications.html)
        added TOC
        added abbreviation page
        added full interactive mode
        added full batch mode
        added usage help

    0.2.2
        various bugfixes and improvements
        added posibility to directly run 'kindlegen' to convert the OPF to MOBI

    0.2.1
        added parameters for connecting to MySql server
        added posibility to choose the dictionary sources

    0.2
        initial dex2xml.py version

    0.1
        initial version of tab2opf.py - Copyright (C) 2007 - Klokan Petr Pøidal (www.klokan.cz)

License
-------
This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Library General Public
License as published by the Free Software Foundation; either
version 2 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Library General Public License for more details.

You should have received a copy of the GNU Library General Public
License along with this library; if not, write to the
Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.


