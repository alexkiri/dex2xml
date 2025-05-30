Version history:
----------------
- 0.9.3
  - workaround that adds variants of words with "î" instead of "â" as inflections, redirecting searches for older writing such as "gîndire" -> "gândire"
  - remove dictionary sources with "canDistribute" 0 
  - proper xmlns values, accrding to amazon specs
- 0.9.2
  - updated to work with Python 3.10
  - fixed "A" chapter not being generated correctly
  - implemented formatting for definitions
  - added workaround for displaying the titles from "Mic dictionar mitologic greco-roman"
  - reworked page formatting, cleaned up templates

- 0.9.1
  - added parameter to select how the diacritics should be exported (comma, cedilla, both)

- 0.9.0
  - output file compliant with EPUB Publications 3.0 (http://www.idpf.org/epub/30/spec/epub30-publications.html)
  - added TOC
  - added abbreviation page
  - added full interactive mode
  - added full batch mode
  - added usage help

- 0.2.2
  - various bugfixes and improvements
  - added posibility to directly run 'kindlegen' to convert the OPF to MOBI

- 0.2.1
  - added parameters for connecting to MySql server
  - added posibility to choose the dictionary sources

- 0.2
  - initial dex2xml.py version

- 0.1
  - initial version of tab2opf.py - Copyright (C) 2007 - Klokan Petr Pøidal (www.klokan.cz)
