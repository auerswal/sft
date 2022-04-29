#! /usr/bin/env python3

# ipenum.py - enumerate IP addresses
# Copyright (C) 2022  Erik Auerswald <auerswal@unix-ag.uni-kl.de>
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

"""Print IP addresses, one per line.

IPv4 and IPv6 ranges can be specified as positional command line
arguments.  Without positional command line arguments, ranges are read
from standard input, one range per line.
"""

import argparse
import ipaddress
import re
import sys

PROG = 'ipenum.py'
VERS = '0.2.1'
COPY = 'Copyright (C) 2022  Erik Auerswald <auerswal@unix-ag.uni-kl.de>'
LICE = '''\
License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
'''
DESC = 'Enumerate and print addresses of IP ranges, one address per line.'
EPIL = '''\
IPv4 and IPv6 ranges can be specified as positional command line
arguments.  Without positional command line arguments, ranges are read
from standard input, one range per line.

IPv4 and IPv6 ranges are specified either in CIDR format or using start
and end addresses.  Start and end addresses are separated with a usual
range or sequence indication, e.g, Tabulator or Space characters, two or
more Period characters, a Comma character, a Semicolon character, or a
Dash character.

An address range where the start address is greater than the end address
is valid and interpreted as an empty range.

A single IP address is treated as an address range with identical start
and end addresses.

The IP addresses of the given IP ranges are printed to standard output,
one IP address per line.

By default, every IP address inside a CIDR range is printed, including
the network number and subnet directed broadcast address for IPv4,
and the Subnet-Router anycast address for IPv6.

IP address ranges specified via start and end addresses include both
the start and end address.
'''


def cmd_line_args():
    cmd_line = argparse.ArgumentParser(
        prog=PROG, description=DESC, epilog=EPIL,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    cmd_line.add_argument('-V', '--version', action='version',
                          version='\n'.join([PROG + ' ' + VERS, COPY, LICE]))
    cmd_line.add_argument('-H', '--hosts-only', action='store_true',
                          help='print only host addresses (affects CIDR only)')
    cmd_line.add_argument('RANGE', nargs='*',
                          help='IPv4 or IPv6 address range')
    return cmd_line.parse_args()


def err(msg):
    print(f'{PROG}: ERROR:', msg, file=sys.stderr)


def print_cidr(net, hosts_only):
    try:
        addresses = ipaddress.ip_network(net, strict=False)
    except ValueError as exc:
        err(f"cannot parse CIDR '{net}': {exc}")
        return 1
    if hosts_only:
        addresses = addresses.hosts()
    for addr in addresses:
        print(addr)
    return 0


def parse_start_end(r):
    start = end = ok = None
    # use a regular expression to accept a wide variety of separators
    tmp = re.split(r'\s*(?:\s+(?:to\s)?|,?\.{2,},?|-+>?|[,;→⇒—…])\s*', r)
    #print('%%% DEBUG: tmp =', tmp)
    tmp = [ elem for elem in tmp if elem ]  # remove empty list elements
    #print('%%% DEBUG: tmp =', tmp)
    num_addrs = len(tmp)
    if num_addrs < 1:
        err(f"cannot parse range '{r}': found no addresses")
    elif num_addrs > 2:
        err(f"cannot parse range '{r}': found more than two addresses")
        ok = False
    else:
        if num_addrs == 1:
            tmp.append(tmp[0])
        start, end = tmp
        ok = True
        try:
            start = ipaddress.ip_address(start)
        except ValueError as exc:
            err(f"cannot parse address '{start}': {exc}")
            ok = False
        try:
            end = ipaddress.ip_address(end)
        except ValueError as exc:
            err(f"cannot parse address '{end}': {exc}")
            ok = False
        if ok and start.version != end.version:
            err('start and end addresses must be of the same IP version')
            ok = False
    return (start, end, ok)


def print_start_end(start, end):
    address = start
    while address <= end:
        print(address)
        address += 1
    return 0


def print_ip_range(r, hosts_only):
    if '/' in r:
        return print_cidr(r, hosts_only)
    else:
        start, end, ok = parse_start_end(r)
        if not ok:
            return 1
        return print_start_end(start, end)


if __name__ == '__main__':
    args = cmd_line_args()
    exit_code = 0
    ranges = args.RANGE if args.RANGE else sys.stdin
    for r in ranges:
        exit_code += print_ip_range(r.strip(), args.hosts_only)
    if exit_code:
        exit_code = 1
    sys.exit(exit_code)

# vim:tabstop=4:shiftwidth=4:expandtab: