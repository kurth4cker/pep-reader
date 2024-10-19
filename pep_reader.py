from __future__ import print_function

import ssl
import re
import sys
import os
import argparse
from glob import glob

from urllib.request import urlopen
from urllib.error import HTTPError

# turn off certificate verify
ssl._create_default_https_context = ssl._create_unverified_context

__version__ = '0.1.1'


class Pep:

    peppath = '{}/.peps'.format(os.environ['HOME'])
    pepurls = (
        "https://raw.githubusercontent.com/python/peps/master/pep-{:04d}.txt",
        "https://raw.githubusercontent.com/python/peps/master/pep-{:04d}.rst",
    )

    def __init__(self, num, editor="less"):
        self.num = int(num)
        self.editor = editor

    def get(self):
        for pepurl in self.pepurls:
            url = pepurl.format(self.num)
            print(f"Downloading {url}...")

            try:
                r = urlopen(url)
                txt = r.read().decode()
            except HTTPError:
                continue

            title = re.findall(r"Title: (.+?)\n", txt)[0]
            self.fname = f"{self.peppath}/PEP-{self.num:04d} {title}.txt"
            break
        else:
            print(f"Unable to download PEP {self.num}")
            sys.exit(1)

        self._mk_path(self.peppath)

        try:
            with open(self.fname, 'w') as f:
                f.write(txt)
        except IOError as e:
            print(e)
            sys.exit(1)

    def read(self, p):
        sys.exit(os.system(f"{self.editor} {p!r}"))

    def read_or_get(self):
        g = f"{self.peppath}/PEP-{self.num:04d}*"
        try:
            p = glob(g)[0]
            self.read(p)
        except IndexError:
            self.get()
            self.read(self.fname)

    def _mk_path(self, path):
        if not os.path.exists(path):
            os.mkdir(path)


def main():
    default_pager = "less"
    for pager in 'PAGER', 'VISUAL', 'EDITOR':
        if pager in os.environ:
            default_pager = os.environ[pager]
            break

    parser = argparse.ArgumentParser(description="Download and read a PEP.")
    parser.add_argument('pep_num', help="PEP number")
    parser.add_argument('-e', '--editor',
                        default=default_pager,
                        help="Choose a editor, default is less.")
    args = parser.parse_args()
    pep = Pep(args.pep_num, args.editor)
    pep.read_or_get()


if __name__ == "__main__":
    main()
