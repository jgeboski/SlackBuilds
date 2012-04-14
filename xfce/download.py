#!/usr/bin/env python

import logging
import optparse
import os
import re
import string
import sys
import urllib2
import urlparse

from distutils.version import LooseVersion
from glob              import glob
from math              import floor

PACKAGES = [
    "exo",             "garcon",          "gtk-xfce-engine", "libxfce4ui",
    "libxfce4util",    "libxfcegui4",     "mousepad",        "thunar-volman",
    "Terminal",        "Thunar",          "tumbler",         "xfce-utils",
    "xfce4-appfinder", "xfce4-dev-tools", "xfce4-mixer",     "xfce4-notifyd",
    "xfce4-panel",     "xfce4-session",   "xfce4-settings",  "xfce4-volumed",
    "xfconf",          "xfdesktop",       "xfwm4",           "xfwm4-themes"
]

FORCE  = False
MIRROR = "http://archive.xfce.org/src/"
SOURCE = "src"

logging.basicConfig(format = "[%(levelname)s] %(message)s")

log = logging.getLogger("mctl")
log.setLevel(logging.INFO)

def _url_get(url):
    if not url:
        return None
    
    headers = {
        "Accept-Language": "en-US"
    }
    
    try:
        rq = urllib2.Request(url, None, headers)
        ul = urllib2.urlopen(rq)
    except urllib2.URLError, msg:
        log.error("Failed to open: %s: %s", url, msg)
        return None
    
    data = ul.read()
    
    ul.close()
    return data

def _url_join(base, url):
    if not base:
        return url
    
    if not url:
        return base
    
    if base[-1] != "/":
        base += "/"
    
    return urlparse.urljoin(base, url)

CATEGORY_CACHE = {
    'xfce'          : None,
    'apps'          : None,
    'panel-plugins' : None,
    'thunar-plugins': None,
    'art'           : None
}

def _info_get(package):
    success  = False
    category = None
    
    for category in CATEGORY_CACHE.keys():
        url = _url_join(MIRROR, category)
        
        if not CATEGORY_CACHE[category]:
            CATEGORY_CACHE[category] = _url_get(url)
        
        match = re.search("('|\").*%s/%s('|\")" % (category, package),
            CATEGORY_CACHE[category], re.I)
        
        if match:
            success = True
            break;
    
    if not success:
        log.error(
            "Failed to download: %s: category extraction failed" % (
            package
        ))
        return (None, None)
    
    url  = _url_join(url, package.lower())
    data = _url_get(url)
    vers = re.findall(".*%s/%s/([0-9\.]+)" % (category, package), data, re.I)
    vers.sort(key = LooseVersion)
    
    if len(vers) < 1:
        log.error(
            "Failed to download: %s: version extraction failed" % (
            package
        ))
        return (None, None)
    
    url   = _url_join(url, vers[-1])
    data  = _url_get(url)
    archs = re.findall(".*(%s-[0-9\.]+.tar.bz2)" % (package), data, re.I)
    archs.sort(key = LooseVersion)
    
    if len(archs) < 1:
        log.error(
            "Failed to download: %s: archive extraction failed" % (
            package
        ))
        return
    
    url = _url_join(url, archs[-1])
    
    return (archs[-1], url)

def download(package):
    archive, url = _info_get(package)
    
    if not archive or not url:
        return
    
    f = os.path.join(SOURCE, archive)
    
    if not FORCE and os.path.exists(f):
        log.info("Package exists, skipping: %s", archive)
        return
    
    p = os.path.join(SOURCE, "%s-*.tar.bz2" % (package))
    
    for p in glob(p):
        try:
            os.remove(p)
        except OSError, msg:
            log.warning("Failed to remove: %s: %s", p, msg)
    
    try:
        ul = urllib2.urlopen(url)
    except urllib2.URLError, msg:
        log.error("Failed to download: %s: %s", url, msg)
        return
    
    size = int(ul.info().getheader('Content-Length'))
    
    if size < 1:
        log.info("Failed to download: %s: nothing to download", package)
        return
    
    if not os.path.exists(SOURCE):
        try:
            os.makedirs(SOURCE)
        except OSError, msg:
            log.error("Failed to make directory: %s: %s", SOURCE, msg)
            return
    
    try:
        fp = open(f, "w")
    except IOError, msg:
        log.error("Failed to open: %s: %s", f, msg)
        return
    
    if not fp:
        ul.close()
        return
    
    l = 0
    while True:
        data = ul.read(1024)
        
        if not data:
            break
        
        fp.write(data)
        
        if log.level != logging.INFO:
            continue
        
        p = (float(fp.tell()) / float(size)) * 100
        p = int(floor(p))
        
        if l == p:
            continue
        
        sys.stdout.write("\033[2K")
        sys.stdout.write("Downloading(%d%%): %s\r" % (p, archive))
        sys.stdout.flush()
        l = p
    
    ul.close()
    fp.close()
    
    log.info("Downloaded: %s", archive)
    return

def main():
    global FORCE, MIRROR, SOURCE
    
    parser = optparse.OptionParser(
        usage       = "usage: %prog [OPTIONS]",
        description = "XFCE source downloader"
    )
    
    parser.add_option(
        "-f", "--force",
        action  = "store_true",
        dest    = "force",
        help    = "force downloads"
    )
    
    parser.add_option(
        "-m", "--mirror",
        action  = "store",
        dest    = "mirror",
        metavar = "URL",
        help    = "specify a mirror for XFCE packages"
    )
    
    parser.add_option(
        "-l", "--list",
        action  = "store_true",
        dest    = "list",
        help    = "list of supported packages"
    )
    
    parser.add_option(
        "-p", "--packages",
        action  = "store",
        dest    = "packages",
        metavar = "LIST",
        help    = "list of packages to download"
    )
    
    parser.add_option(
        "-s", "--source-dir",
        action  = "store",
        dest    = "source",
        metavar = "DIR",
        help    = "path to download source into"
    )
    
    opts, args = parser.parse_args()
    packages   = PACKAGES
    
    if opts.list:
        if len(packages) < 1:
            print "No packages found"
        
        print "Supported Packages(s):"
        
        for p in packages:
            print "  %s" % (p)
        
        exit(0)
    
    if opts.force:
        FORCE = opts.force
    
    if opts.mirror:
        MIRROR = opts.mirror
    
    if opts.source:
        SOURCE = opts.source
    
    if opts.packages:
        packages = opts.packages.split(",")
    
    for p in packages:
        download(p)
    

if __name__ == "__main__":
    main()
