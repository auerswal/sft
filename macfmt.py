#! /usr/bin/env python
# coding=utf8

# macfmt.py - print MAC addresses in various formats
# Copyright (C) 2019-2021  Erik Auerswald <auerswal@unix-ag.uni-kl.de>
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

"""Format MAC addresses.

Since there is no generally used standard format for the representation
of MAC addresses, different implementations use different formats. This
module provides functions to read a MAC address in any common format, and
create a string representation of a MAC address in many different formats.
"""

# Make coding more python3-ish
from __future__ import (
    absolute_import, division, print_function, unicode_literals
)
__metaclass__ = type  # pylint: disable=invalid-name

# Note: doctests require Python 3 (python3 -m doctest macfmt.py)

PROG = 'macfmt.py'
VERS = '0.2.1'
DESC = 'Print MAC address(es) in specified format.'
EPIL = """\
The MAC addresses given as input are printed in the selected format, one MAC
address per line. Input is either in the form of command line arguments (one
MAC address per argument) or read from standard input (one MAC address per
line). Standard input is ignored if any MAC addresses are given as command
line arguments.
"""

HEX_DIGITS = {d for d in '0123456789abcdefABCDEF'}
MAC_LEN = 12

# MAC format is a tupel or an alias
# tupel (<prefix>, <group size>, <group separator>, <case>, <suffix>)
# the <group size> is the number of hexadecimal characters (nybbles) of a group
MAC_FORMAT = {
    'arista': 'cisco',
    'bcm': 'broadcom',
    'broadcom': ('', 4, ':', 'upper', ''),
    'cisco': ('', 4, '.', 'lower', ''),
    'cabletron': ('', 2, ':', 'upper', ''),
    'ct': 'cabletron',
    'default': ('', 2, '-', 'upper', ''),
    'enterasys': 'default',
    'ets': 'default',
    'exos': 'linux',
    'hex': ('', 12, '', 'lower', ''),
    'hexpostfix': 'hexsuffix',
    'hexprefix': ('0x', 12, '', 'lower', ''),
    'hexsuffix': ('', 12, '', 'upper', 'h'),
    'hp': ('', 6, '-', 'lower', ''),
    'huawei': ('', 4, '-', 'lower', ''),
    'ieee': 'default',
    'ietf': 'linux',
    'linux': ('', 2, ':', 'lower', ''),
    'mikrotik': 'cabletron',
    'netsight': ('', 2, '.', 'upper', ''),
    'pgsql': ('', 6, ':', 'lower', ''),
    'pxe': ('', 2, ' ', 'upper', ''),
    'vmps': ('', 4, '.', 'upper', ''),
}


def keep_hex(in_str):
    """Return list of hexadecimal digits (nybbles) from in_str.

    Examples:
    >>> keep_hex('01:23:45:67:89:ab')
    ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b']
    >>> keep_hex(' 01-23-45-67-89-AB ')
    ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B']
    >>> keep_hex('112233445566')
    ['1', '1', '2', '2', '3', '3', '4', '4', '5', '5', '6', '6']
    >>> keep_hex('')
    []
    >>> keep_hex('01 23-45:67.89')
    ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    >>> keep_hex('abcdef-ABCDEF')
    ['a', 'b', 'c', 'd', 'e', 'f', 'A', 'B', 'C', 'D', 'E', 'F']
    >>> keep_hex(' [00:00:00_00:00:00] ') == ['0'] * 12
    True
    >>> keep_hex('.,<>;:-[]() gG%$/')
    []

    """
    return [c for c in in_str if c in HEX_DIGITS]


def find_separator(in_str):
    """Return separator in MAC address, or None.

    Examples:
    >>> find_separator('01:23')
    ':'
    >>> find_separator(' 01-23 ')
    '-'
    >>> find_separator('') is None
    True
    >>> find_separator('1:2_3:4') is None
    True
    >>> find_separator(' 1 2-3 ') is None
    True

    """
    candidates = {c for c in in_str.strip() if c not in HEX_DIGITS}
    if len(candidates) == 1:
        return candidates.pop()
    return None


def keep_zero_padded_hex(in_str):
    """Return zero-padded list of nybbles if s is a MAC address, or None.

    Examples:
    >>> keep_zero_padded_hex('01:23:45:67:89:ab')
    ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b']
    >>> keep_zero_padded_hex('   01:23:45:67:89:ab   ')
    ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b']
    >>> keep_zero_padded_hex('123.4567.89Ab')
    ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'b']
    >>> keep_zero_padded_hex('   12345-6789ab   ')
    ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b']
    >>> keep_zero_padded_hex(' 2:4:96:90:0:e ')
    ['0', '2', '0', '4', '9', '6', '9', '0', '0', '0', '0', 'e']
    >>> keep_zero_padded_hex(' 204:9690:e ')
    ['0', '2', '0', '4', '9', '6', '9', '0', '0', '0', '0', 'e']
    >>> keep_zero_padded_hex('') is None
    True
    >>> keep_zero_padded_hex('11') is None
    True
    >>> keep_zero_padded_hex('123.4567:89Ab') is None
    True
    >>> keep_zero_padded_hex('112233445566') is None
    True
    >>> keep_zero_padded_hex('1122334455667') is None
    True

    """
    sep = find_separator(in_str)
    if sep is None:
        return None
    groups = in_str.strip().split(sep)
    group_size = MAC_LEN // len(groups)
    nybbles = []
    for grp in groups:
        nybbles.extend(['0'] * (group_size - len(grp)))
        nybbles.extend(grp)
    return nybbles


def is_mac(nybbles):
    """Return True if nybbles represents a MAC address.

    Examples:
    >>> is_mac('112233445566')
    False
    >>> is_mac(['1', '1', '2', '2', '3', '3', '4', '4', '5', '5', '6', '6'])
    True
    >>> is_mac(['1', '1', '2', '2', '3', '3', '4', '4', '5', '5', '6'])
    False
    >>> is_mac(['1','1','2','2','3','3','4','4','5','5','6','6','7'])
    False
    >>> is_mac('')
    False
    >>> is_mac([])
    False

    """
    return len(nybbles) == MAC_LEN and nybbles == keep_hex(nybbles)


def lookup_format(name):
    """Find format tuple corresponding to name.

    Examples:
    >>> lookup_format('default')
    ('', 2, '-', 'upper', '')
    >>> lookup_format('cisco')
    ('', 4, '.', 'lower', '')
    >>> lookup_format('arista')
    ('', 4, '.', 'lower', '')
    >>> lookup_format('')
    Traceback (most recent call last):
        ...
    KeyError: ''
    >>> for f in MAC_FORMAT.keys():
    ...     if not isinstance(lookup_format(f), tuple):
    ...         print('FAIL')

    """
    fmt = MAC_FORMAT[name]
    if isinstance(fmt, tuple):
        return fmt
    return lookup_format(fmt)


def format_mac(in_str, fmt):
    """Return str representation of MAC address formatted according to fmt.

    Examples:
    >>> format_mac('01:23:45:67:89:Ab', 'linux')
    '01:23:45:67:89:ab'
    >>> format_mac('1:23:45:67:89:Ab', 'arista')
    '0123.4567.89ab'
    >>> format_mac(' 12345 6789Ab ', 'default')
    '01-23-45-67-89-AB'
    >>> format_mac(' 11 22:33-44.55/aB ', 'default')
    '11-22-33-44-55-AB'
    >>> format_mac('a b', 'pxe')
    '00 00 0A 00 00 0B'
    >>> format_mac('2:4:96:90:0:e', 'hex')
    '02049690000e'
    >>> format_mac('2:4:96:90:0:e', 'hexprefix')
    '0x02049690000e'
    >>> format_mac('2:4:96:90:0:e', 'hexsuffix')
    '02049690000Eh'
    >>> format_mac('', 'ets')
    Traceback (most recent call last):
        ...
    ValueError: "" is not a valid MAC address representation
    >>> format_mac('1:23:45-67:89:Ab', 'default')
    Traceback (most recent call last):
        ...
    ValueError: "1:23:45-67:89:Ab" is not a valid MAC address representation
    >>> format_mac('11-22-33-44-55-6', 'vmps')
    '1122.3344.5506'
    >>> format_mac('11223344556', 'vmps')
    Traceback (most recent call last):
        ...
    ValueError: "11223344556" is not a valid MAC address representation
    >>> format_mac('11-22-33-44-55-66', 'vmps')
    '1122.3344.5566'
    >>> format_mac('11-22-33-44-55-66-7', 'vmps')
    Traceback (most recent call last):
        ...
    ValueError: "11-22-33-44-55-66-7" is not a valid MAC address representation
    >>> format_mac('01:23:45:67:89:Ab', '')
    Traceback (most recent call last):
        ...
    KeyError: ''
    >>> format_mac('01:23:45:67:89:Ab', 'invalid format')
    Traceback (most recent call last):
        ...
    KeyError: 'invalid format'
    >>> format_mac('01:23:45:67:89:Ab', 47)
    Traceback (most recent call last):
        ...
    KeyError: 47

    """
    out_lst = []
    pref, grp_sz, sep, case, suf = lookup_format(fmt)
    nybbles = keep_hex(in_str)
    if not is_mac(nybbles):
        nybbles = keep_zero_padded_hex(in_str)
    if nybbles is None or not is_mac(nybbles):
        raise ValueError('"%s" is not a valid MAC address representation'
                         % in_str)
    for i, nyb in enumerate(nybbles):
        if i > 0 and i % grp_sz == 0:
            out_lst.append(sep)
        out_lst.append(nyb)
    out_str = ''.join(out_lst)
    out_str = out_str.upper() if case == 'upper' else out_str.lower()
    return pref + out_str + suf


def output_formats_with_example_mac():
    """Print list of output formats.

    Each line comprises the output format name, and an example MAC address in
    this format.

    >>> output_formats_with_example_mac()
    arista    :  0123.4567.89ab
    bcm       :  0123:4567:89AB
    broadcom  :  0123:4567:89AB
    cabletron :  01:23:45:67:89:AB
    cisco     :  0123.4567.89ab
    ct        :  01:23:45:67:89:AB
    default   :  01-23-45-67-89-AB
    enterasys :  01-23-45-67-89-AB
    ets       :  01-23-45-67-89-AB
    exos      :  01:23:45:67:89:ab
    hex       :  0123456789ab
    hexpostfix:  0123456789ABh
    hexprefix :  0x0123456789ab
    hexsuffix :  0123456789ABh
    hp        :  012345-6789ab
    huawei    :  0123-4567-89ab
    ieee      :  01-23-45-67-89-AB
    ietf      :  01:23:45:67:89:ab
    linux     :  01:23:45:67:89:ab
    mikrotik  :  01:23:45:67:89:AB
    netsight  :  01.23.45.67.89.AB
    pgsql     :  012345:6789ab
    pxe       :  01 23 45 67 89 AB
    vmps      :  0123.4567.89AB

    """
    mac = '01-23-45-67-89-AB'
    name_width = max(map(len, MAC_FORMAT.keys()))
    for fmt in sorted(MAC_FORMAT.keys()):
        print("%-*s:  %s" % (name_width, fmt, format_mac(mac, fmt)))


if __name__ == '__main__':
    # pylint3 version 1.8.3 from Ubuntu 18.04 gets confused here
    # pylint: disable=all
    import argparse
    import sys

    cmd_line = argparse.ArgumentParser(
        prog=PROG, description=DESC, epilog=EPIL,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    cmd_line.add_argument('-V', '--version', action='version',
                          version=PROG + ' ' + VERS)
    cmd_line.add_argument('-F', '--format', choices=sorted(MAC_FORMAT.keys()),
                          default='default',
                          help='output format for MAC addresses')
    cmd_line.add_argument('-l', '--list-formats', action='store_true',
                          help='show all output formats with an example')
    cmd_line.add_argument('MAC', nargs='*', help='MAC addresses to format')
    args = cmd_line.parse_args()

    exit_code = 0
    if args.list_formats:
        output_formats_with_example_mac()
        sys.exit(exit_code)

    mac_addresses = args.MAC if args.MAC else sys.stdin
    for mac in mac_addresses:
        try:
            print(format_mac(mac, args.format))
        except ValueError as exc:
            exit_code = 1
            print('%s: ERROR: %s' % (PROG, exc), file=sys.stderr)

    sys.exit(exit_code)

# vim:tabstop=4:shiftwidth=4:expandtab:
