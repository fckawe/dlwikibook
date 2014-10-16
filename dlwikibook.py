#!/usr/bin/python
# -*- coding: utf8 -*-

# -----------------------------------------------------------------------------
# get_wikibook.py
# Copyright (C) 2011  Gerald Backmeister (http://mamu.backmeister.name)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------

# TODO: style sheets won't be downloaded, yet

from BeautifulSoup import BeautifulSoup
from urllib2 import Request, urlopen, quote, unquote
import re
import os
import sys
from getopt import getopt, GetoptError

version = "0.1"
# be careful - the program is tested with "de" only!
language = "de"
encoding = "latin1"

# -----------------------------------------------------------------------------
# Outputs the program's usage to the standard output (--help)
# -----------------------------------------------------------------------------
def print_usage(me):
    print "{0}: downloads a book from wikibooks.org to read it offline.".format(me)
    print ""
    print "USAGE: " + me + " { INFO_OPTION | BOOK_INFO [OPERATION_OPTIONS] }"
    print ""
    print "  INFO_OPTION:"
    print "    -h | --help .............. Shows this help..."
    print "    -v | --version ........... Shows the version of {0}".format(me)
    print "    -l | --license ........... Shows the license and warranty info"
    print ""
    print "  BOOK_INFO:"
    print "    -b book | --book=book .... Specifies the name of the book to download"
    print ""
    print "  OPERATION_OPTIONS:"
    print "    -d dir | --dir=dir ....... Specifies the target directory (default is"
    print "                               current directory)"
    print "    -c | --clean ............. Cleans the pages for use with eReaders"
    print "    -t | --textonly .......... Do not download images."
    print "    -u | --urlencoded ........ Names of the files are urlencoded (no special"
    print "                               chars, important for some E-Readers)."
    print ""
    print "For Kindle users the options -ctu are recommended."
    print ""

# -----------------------------------------------------------------------------
# Outputs the program's version to the standard output (--version)
# -----------------------------------------------------------------------------
def print_version(me):
    print "{0}: version {1}".format(me, version)

# -----------------------------------------------------------------------------
# Outputs the program's license info to the standard output (--license)
# -----------------------------------------------------------------------------
def print_license(me):
    print "{0}  Copyright (C) 2011  Gerald Backmeister (http://mamu.backmeister.name)".format(me)
    print ""
    print "License information:"
    print "This program is free software: you can redistribute it and/or modify"
    print "it under the terms of the GNU General Public License as published by"
    print "the Free Software Foundation, either version 3 of the License, or"
    print "(at your option) any later version."
    print ""
    print "Warranty information:"
    print "This program is distributed in the hope that it will be useful,"
    print "but WITHOUT ANY WARRANTY; without even the implied warranty of"
    print "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the"
    print "GNU General Public License for more details."
    print ""
    print "You should have received a copy of the GNU General Public License"
    print "along with this program.  If not, see <http://www.gnu.org/licenses/>."

# -----------------------------------------------------------------------------
# Returns the base url of the wikibooks page.
# -----------------------------------------------------------------------------
def get_wikibooks_base_url():
    global language
    return "http://{0}.wikibooks.org".format(language)

# -----------------------------------------------------------------------------
# Returns the book's relative book url.
# -----------------------------------------------------------------------------
def get_book_base_href():
    global book_name
    return "/wiki/" + book_name

# -----------------------------------------------------------------------------
# Decides if the given href is a href of the book (True) or not (False).
# -----------------------------------------------------------------------------
def is_book_href(href, separator):
    global book_name
    book_base_href = get_book_base_href()
    if separator == "":
        return href == book_base_href or href.startswith(book_base_href + "/") or href.startswith(book_base_href + ":")
    else:
        return href.startswith(book_base_href + separator)

# -----------------------------------------------------------------------------
# Decides if the given link is a link of the book (True) or not (False).
# -----------------------------------------------------------------------------
def is_book_link(link):
    global book_name
    href = str(dict(link.attrs).get("href"))
    return is_book_href(href, "")

# -----------------------------------------------------------------------------
# Retrieves the page (to the given URL).
# -----------------------------------------------------------------------------
def retrieve_page(page_url):
    req = Request(page_url, headers={"User-Agent" : "Magic Browser"})
    return urlopen(req)

# -----------------------------------------------------------------------------
# Finds and returns the book's pages via the prefix search.
# -----------------------------------------------------------------------------
def retrieve_book_links():
    global language, book_name
    print "retrieving book links..."
    base_url = get_wikibooks_base_url()
    book_url = "{0}/w/index.php?title=Spezial%3APrefixindex&namespace=0&from={1}".format(base_url, book_name)
    page = retrieve_page(book_url)
    soup = BeautifulSoup(page)
    return [link for link in soup("a") if is_book_link(link)]

# -----------------------------------------------------------------------------
# Creates all subdirectories which are necessary to store the book.
# -----------------------------------------------------------------------------
def create_subdirectories(book_links):
    global base_directory, book_name
    print "creating subdirectories..."
    subdirectories = get_subdirectories(book_links)
    for subdirectory in subdirectories:
        path = base_directory + subdirectory
        if os.path.exists(path):
            print "  already exists: " + path
        else:
            print "  create: " + path
            os.makedirs(path)

# -----------------------------------------------------------------------------
# Finds and returns all subdirectories which are necessary to store the book.
# -----------------------------------------------------------------------------
def get_subdirectories(book_links):
    global book_name, images_directory
    subdirectories = [images_directory]
    book_base_href = get_book_base_href()
    for link in book_links:
        href = str(dict(link.attrs).get("href"))
        if href != book_base_href:
            if is_book_href(href, "/"):
                href = href.replace(book_base_href + "/", "", 1)
            elif is_book_href(href, ":"):
                href = href.replace(book_base_href + ":", "", 1)
            parts = href.split("/")
            if len(parts) > 1:
                path = parts[0]
                for i in range(len(parts) - 1):
                    if i > 0:
                        path += "/" + parts[i]
                        if path not in subdirectories:
                            subdirectories.append(path)
                    elif parts[i] not in subdirectories:
                        subdirectories.append(parts[i])
    return subdirectories

# -----------------------------------------------------------------------------
# Converts the given href to its local file name.
# -----------------------------------------------------------------------------
def href_to_file_name(href, absolute):
    global base_directory, book_name
    if is_book_href(href, ""):
        book_base_href = get_book_base_href()
        file_name = u""
        if absolute:
            file_name = unicode(base_directory.rstrip("/"))
        file_name += unicode(href.replace(book_base_href, "", 1))
        if file_name.startswith(":"):
            file_name = unicode(file_name.replace(":", "/", 1))
        elif file_name == "":
            file_name = u"/"
        if os.path.isdir(file_name):
            if not file_name.startswith("/"):
                file_name += u"/"
            file_name += u"index"
        return file_name + u".html"
    return ""

# -----------------------------------------------------------------------------
# Converts the given image source to its local file name.
# -----------------------------------------------------------------------------
def img_src_to_file_name(src):
    global images_directory
    src_new = None
    if src in img_map:
        src_new = img_map[src]
    else:
        src_new = "{0}_{1}".format(str(len(img_map)), os.path.basename(src))
        img_map[src] = src_new
    return "{0}/{1}".format(images_directory, src_new)

# -----------------------------------------------------------------------------
# Converts the page content (cut off things and convert the links).
# -----------------------------------------------------------------------------
def process_page_content(page_content):
    global img_map, base_directory, book_name, clean, text_only, url_encoded
    soup = None
    if clean:
        # cut off the wikibooks template
        pattern = re.compile("NewPP limit report.*Served by.*-->", re.MULTILINE|re.DOTALL)
        page_content = pattern.sub("-->", str(page_content))
        # cut off all "edit section" links
        soup = BeautifulSoup(page_content)
        for span in soup("span"):
            spanclass = unicode(dict(span.attrs).get("class"))
            if spanclass == "editsection":
                span.extract()
        # cut off the wikibook header space
        for div in soup("div"):
            divid = unicode(dict(div.attrs).get("id"))
            if divid == "mw-page-base" or divid == "mw-head-base":
                div.extract()
        # cut off unnecessary header links
        for link in soup("link"):
            rel = unicode(dict(link.attrs).get("rel"))
            if rel == "alternate" or rel == "edit" or rel == "search" or rel == "EditURI":
                link.extract()
        # cut off unnecessary header meta
        for meta in soup("meta"):
            metaname = unicode(dict(meta.attrs).get("name"))
            if metaname == "ResourceLoaderDynamicStyles":
                meta.extract()
    if soup == None:
        soup = BeautifulSoup(page_content)
    # convert the internal links
    for link in soup("a"):
        href_source = dict(link.attrs).get("href")
        if href_source == None:
            continue
        if is_book_href(href_source, ""):
            if url_encoded:
                href_source = quote(href_source)
            href = unicode(href_source)
            file_name = href_to_file_name(href, False)
            if file_name != "":
                if file_name.startswith("/"):
                    file_name = file_name.replace("/", "", 1)
                link['href'] = file_name
    # find all images in order to download or remove them
    for img in soup("img"):
        if text_only:
            img.extract()
        else:
            src = dict(img.attrs).get("src")
            if src.startswith("http://"):
                src_quoted = src
                if url_encoded:
                    src_quoted = quote(src)
                src = unicode(src)
                src_quoted = unicode(src_quoted)
                img_file_relative = img_src_to_file_name(src_quoted)
                img_file_absolute = base_directory.rstrip("/") + "/" + img_file_relative
                download_image(src, img_file_absolute)
                img['src'] = img_file_relative
    if text_only:
        for div in soup("div"):
            div_class = unicode(dict(div.attrs).get("class"))
            if div_class.startswith("thumb"):
                div.extract()
    return str(soup)

# -----------------------------------------------------------------------------
# Downloads an image from the given URL to the given filename
# -----------------------------------------------------------------------------
def download_image(url, file_name):
    from urllib2 import Request, urlopen, URLError, HTTPError
    req = Request(url, headers={"User-Agent" : "Magic Browser"})
    try:
        f = urlopen(req)
        fl = open(unquote(file_name), "w")
        fl.write(f.read())
        fl.close()
    except HTTPError, e:
        print "HTTP Error: ", e.code, url
    except URLError, e:
        print "URL Error: " + e.reason, url

# -----------------------------------------------------------------------------
# Retrieves all the book's pages and stores the files. 
# -----------------------------------------------------------------------------
def retrieve_pages(book_links):
    global base_directory, language, book_name, clean, text_only, encoding, url_encoded
    print "retrieving pages..."
    book_base_href = get_book_base_href()
    for link in book_links:
        href = dict(link.attrs).get("href")
        if url_encoded:
            href_unquoted = href
        else:
            href_unquoted = unquote(href)
        href_display = href_unquoted.replace(book_base_href + "/", "")
        if href.startswith(book_base_href + "/_Vorlage:"):
            print "  don't retrieve template: {0}".format(href_display.encode(encoding))
        else :
            base_url = get_wikibooks_base_url()
            page_url = u"{0}{1}".format(base_url, href)
            page = retrieve_page(page_url)
            page_content = process_page_content(page.read())
            page_file_name = href_to_file_name(href_unquoted, True)
            print "  retrieving: {0} to: {1}".format(href_display.encode(encoding), page_file_name.encode(encoding))
            page_file = open(unicode(page_file_name).encode(encoding), "w")
            page_file.write(page_content)
            page_file.close()

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    book_name = ""
    target_dir = "."
    clean = False
    text_only = False
    url_encoded = False
    me = os.path.basename(sys.argv[0])
    img_map = {}

    try:
        opts, args = getopt(sys.argv[1:], "hvlb:d:ctu", ["help", "version", "license", "book=", "dir=", "clean", "textonly", "urlencoded" ])
    except GetoptError as err:
        print err
        print "for help use --help"
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_usage(me)
            sys.exit()
        elif opt in ("-v", "--version"):
            print_version(me)
            sys.exit()
        elif opt in ("-l", "--license"):
            print_license(me)
            sys.exit()
        elif opt in ("-b", "--book"):
            book_name = arg
        elif opt in ("-d", "--dir"):
            target_dir = arg
        elif opt in ("-c", "--clean"):
            clean = True
        elif opt in ("-t", "--textonly"):
            text_only = True
        elif opt in ("-u", "--urlencoded"):
            url_encoded = True

    if book_name == "":
        print "ERROR: no book name specified!"
        print "for help use --help"
        sys.exit(2)

    base_directory = "{0}/{1}/".format(target_dir.rstrip("/"), book_name)
    images_directory = "images"

    print "Start download of book \"{0}\" to \"{1}\"".format(book_name, base_directory)
    if clean:
        print "Clean mode is active"
    if text_only:
        print "Text-only mode is active"
    if url_encoded:
        print "URL-encoded mode is active"

    book_links = retrieve_book_links()
    create_subdirectories(book_links)
    retrieve_pages(book_links)
