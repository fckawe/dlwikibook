dlwikibook
==========

With the python script dlwikibook.py you can download books from http://www.wikibooks.org. That way you can read the book offline. Primary goal (at least for me) is downloading books to use the with Calibre and read them on e-reader devices (like Kindle).

Features
--------

* Download a book from wikibooks.org in order to read it offline. For the moment it only works with books from the german wikibooks-repository, though.
* Graphics used in the book will be downloaded, too. To skip them use option `--textonly`.
* To use the books on an e-reader unneccesary parts of the pages can be removed automatically. Use option `--clean` for that.

Installation
------------

Just download, extract and use it!
Of course you need to have Python (version 2.7.1+) installed, though. Get it on http://www.python.org. In addition to that you will need BeautifulSoup (3.2.0) to make this program work!
Download BeautifulSoup from http://www.crummy.com/software/BeautifulSoup/ and extract it with:

    tar xzvf BeautifulSoup-3.2.0.tar.gz

Put the `BeautifulSoup.py` into the directory in which `dlwikibook.py` resides.

Contact
-------

To contact me use the contact formular on my website http://mamu.backmeister.name. Please understand, though, that I cannot offer regular support for my programs.
