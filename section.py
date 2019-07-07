#! /usr/bin/env python
# coding=utf8

# section.py - print line matching regexp with following indented section
#
# Copyright (C) 2019 by Erik Auerswald <auerswal@unix-ag.uni-kl.de>
#
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without any warranty.

# Please note that this program uses Python regular expressions which are
# not compatible with POSIX extended regular expressions (ERE).
# Please note that using this program with Python 3 with a non-POSIX
# locale may result in UnicodeDecodeError with non-UTF-8 input.

# Make coding more python3-ish
from __future__ import (
    absolute_import, division, print_function, unicode_literals
)
__metaclass__ = type

import fileinput
import re
import sys

if len(sys.argv) < 2:
    print("Usage: section.py PATTERN [FILE...]", file=sys.stderr)
    sys.exit(2)

pattern = re.compile(sys.argv[1])
indent = re.compile(r"[ \t]*")
tab = re.compile(r"\t")
eight_spc = " " * 8
in_sec = False
ind = ""
line_ind = ""

for line in fileinput.input(sys.argv[2:]):
    line_ind = indent.match(line)
    if line_ind:
        line_ind = line_ind.group(0)
        line_ind = tab.subn(eight_spc, line_ind)[0]
    else:
        line_ind = ""
    if pattern.search(line) or (in_sec and len(line_ind) > len(ind)):
        if (not in_sec) or (len(line_ind) < len(ind)):
            ind = line_ind
        in_sec = True
        print(line, end='')
    else:
        in_sec = False
        ind = ""

# vim:tabstop=4:shiftwidth=4:expandtab:
