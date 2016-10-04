#! /usr/bin/env python3

# priv_pass.py - Calculate ROMMON priv password for (some) Cisco routers.
#
# Copyright (C) 2016 Erik Auerswald <auerswal@unix-ag.uni-kl.de>
#
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without any warranty.

'''Calculate the ROMMON priv password for (some) Cisco routers.

Usage: priv_pass.py FIRST_10_or_16_BYTES_OF_COOKIE

Use 16 bytes for the Cisco 1841.
Use 10 bytes for the Cisco SR-520, 1812W.

The number of bytes might differ with ROMMON version on the same hardware.
'''

from sys import argv

cookie = ''.join(argv[1:])
values, tmp = [], ''
for char in cookie:
    tmp += char
    if len(tmp) % 4 == 0:
        values.append(int(tmp, 16))
        tmp = ''
chksum = sum(values) & 0xFFFF
print('%04x' % (chksum))
