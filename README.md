DEX2XML
=======

dex2xml is a Python script to convert DEXonline database to xml format for creating a MOBI dictionary.

Due to Kindle fonts, the diacritics for Romanian language are not displayed properly. (Romanian standard defines diacritics as letters with comma (,) and Kindle displays these with cedilla). Due to this problem, searching for terms containing diacritics with comma would not return any result. This was overcome by exporting terms and inflected forms both with comma and with cedilla.

Tested with Kindle Paperwhite 2013 and Kindle Keyboard 2010

This python script is based on tab2opf.py by Klokan Petr Pøidal (www.klokan.cz)

The regular expressions used for formatting definitions are adapted from:
- https://github.com/dexonline/dexonline/blob/master/lib/Constant.php#L68
- https://wiki.dexonline.ro/wiki/Ghidul_voluntarului

Requirements:
-------------
* Linux or Windows enivronment
* MySQL server
* copy of DEXonline database - download and installation instructions: http://wiki.dexonline.ro/wiki/Instruc%C8%9Biuni_de_instalare
* Python (this script was tested using Python 3.10)
* PyMySql package (compiled from sources or installed using "pip install pymysql")
* _optional_: kindlegen for generating MOBI format (available for Linux/Windows/Mac at http://www.amazon.com/gp/feature.html?docId=1000765211)

Workflow:
---------
* The `Deploy` workflow from the Github Actions section of the repo can also be used to create the .mobi dictionary. This has the advantage of not requiring to install anything. You can find the generated file(s) in the "artifacts" section of a succesful build.

Usage:
------
dex2xml.py [-h] [-v] [-r SERVER] [-c PORT] [-u USERNAME] [-p PASSWORD]
                  [-d DATABASE] [-s SOURCES [SOURCES ...]] [-o OUTPUTFILE]
                  [--diacritics {comma,cedilla,both}] [-k | -t]

options:
  -h, --help            print this help file
  -v, --version         print the program's version

Batch arguments:
  -r SERVER, --server SERVER
                        Specify the mysql server to connect to.
                        Default: 'localhost'
  -c PORT, --port PORT  Mysql server port.
                        Default: 3306
  -u USERNAME, --username USERNAME
                        Specify the username to connect to mysql server.
                        Default: 'root'
  -p PASSWORD, --password PASSWORD
                        The password of the mysql server.
  -d DATABASE, --database DATABASE
                        dexonline database on the mysql server.
                        Default: 'dexonline'
  -s SOURCES [SOURCES ...], --sources SOURCES [SOURCES ...]
                        List of dictionary sources to extract from database.
                        Must contain the sources id's from the table 'sources'.
                        If some source doesn't exist or can't be distributed, it will be removed from the list.
                        Default: 27 36
  -o OUTPUTFILE, --outputfile OUTPUTFILE
                        Filename of output file.
                        May include path.
                        Existing files will be deleted first.
                        Default: 'DEXonline'
  --diacritics {comma,cedilla,both}
                        Specify how the diacritics should be exported.
                        Default: 'both'
  -k, --kindlegen       Do not run kindlegen to convert the output to MOBI.
                        Default: not set
  -t, --temp_files      Keep the temporary files after running kindlegen.
                        Default: not set

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
