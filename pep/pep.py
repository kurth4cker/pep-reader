#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function

import ssl
import re
import sys
import os
import argparse
from pathlib import Path

## python 2
try:
    from urllib.request import urlopen
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import urlopen
    from urllib2 import HTTPError

# turn off certificate verify
ssl._create_default_https_context = ssl._create_unverified_context

__version__='0.1.0'

class Pep:

    peppath = '%s/.peps' % os.environ['HOME']

    def __init__(self, num, editor):
        self.num = int(num)

        if editor is None:
            self.editor = 'less'
        else:
            self.editor = editor

    def get(self):
        url = "https://raw.githubusercontent.com/python/peps/master/pep-%04d.txt"\
              % self.num

        print("Downloading %s..." % url)

        try:
            with urlopen(url) as r:
                txt = r.read().decode()
                title = re.findall(r"Title: (.+?)\n", txt)[0]
                self.fname = "%s/PEP-%04d %s.txt" % (self.peppath, self.num, title)
        except HTTPError as e:
            print(e)
            sys.exit(1)

        self._mk_path(self.peppath)

        try:
            with open(self.fname, 'w') as f:
                f.write(txt)
        except IOError as e:
            print(e)
            sys.exit(1)

    def read(self, p):
        sys.exit(os.system("%s '%s'" % (self.editor, p)))

    def read_or_get(self):
        fn = "PEP-%04d*" % self.num
        try:
            p = next(Path(self.peppath).glob(fn))
            self.read(str(p))
        except StopIteration:
            self.get()
            self.read(self.fname)

    def _mk_path(self, path):
        p = Path(path)
        if not p.exists():
            p.mkdir()

def main():
    parser = argparse.ArgumentParser(description="Download and read a PEP.")
    parser.add_argument('pep_num', help="PEP number")
    parser.add_argument('-e', '--editor',
                        help="Choose a editor, default is less.")
    args = parser.parse_args()
    pep = Pep(args.pep_num, args.editor)
    pep.read_or_get()

if __name__ == "__main__":
    main()
