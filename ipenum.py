#! /usr/bin/env python3

# ipenum.py - enumerate IP addresses
# Copyright (C) 2022-2025  Erik Auerswald <auerswal@unix-ag.uni-kl.de>
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
VERS = '0.5.0'
COPY = 'Copyright (C) 2022-2025  Erik Auerswald <auerswal@unix-ag.uni-kl.de>'
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

If an address range specified with start and end addresses is enclosed
in Parenthesis or Square Bracket characters, the range is interpreted
as a closed, half-open, or open IP address interval, using the respective
notation from ISO 31-11.

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

DEBUG = False


def cmd_line_args():
    """Parse command line arguments."""
    cmd_line = argparse.ArgumentParser(
        prog=PROG, description=DESC, epilog=EPIL,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    cmd_line.add_argument('-V', '--version', action='version',
                          version='\n'.join([PROG + ' ' + VERS, COPY, LICE]))
    cmd_line.add_argument('-H', '--hosts-only', action='store_true',
                          help='print only host addresses (affects CIDR only)')
    cmd_line.add_argument('-D', '--debug', action='store_true',
                          help='emit debug information')
    cmd_line.add_argument('RANGE', nargs='*',
                          help='IPv4 or IPv6 address range')
    return cmd_line.parse_args()


def dbg(msg):
    """Print debug information to standard error."""
    if DEBUG:
        print(f'{PROG}: DEBUG:', msg, file=sys.stderr)


def err(msg):
    """Print message with error prefix to standard error."""
    print(f'{PROG}: ERROR:', msg, file=sys.stderr)


def print_cidr(net, hosts_only):
    """Print addresses of CIDR range.

    >>> r = print_cidr('192.0.2.16/29', False)
    192.0.2.16
    192.0.2.17
    192.0.2.18
    192.0.2.19
    192.0.2.20
    192.0.2.21
    192.0.2.22
    192.0.2.23
    >>> r == 0
    True
    >>> r = print_cidr('192.0.2.16/29', True)
    192.0.2.17
    192.0.2.18
    192.0.2.19
    192.0.2.20
    192.0.2.21
    192.0.2.22
    >>> r == 0
    True
    >>> r = print_cidr('192.0.2.8/31', False)
    192.0.2.8
    192.0.2.9
    >>> r == 0
    True
    >>> r = print_cidr('192.0.2.8/31', True)
    192.0.2.8
    192.0.2.9
    >>> r == 0
    True
    >>> r = print_cidr('2001:db8::/126', False)
    2001:db8::
    2001:db8::1
    2001:db8::2
    2001:db8::3
    >>> r == 0
    True
    >>> r = print_cidr('2001:db8::/126', True)
    2001:db8::1
    2001:db8::2
    2001:db8::3
    >>> r == 0
    True
    >>> r = print_cidr('2001:db8::/127', False)
    2001:db8::
    2001:db8::1
    >>> r == 0
    True
    >>> r = print_cidr('2001:db8::/127', True)
    2001:db8::
    2001:db8::1
    >>> r == 0
    True
    >>> r = print_cidr('fe80::a%en0/127', False)
    fe80::a%en0
    fe80::b%en0
    >>> r == 0
    True
    """
    zone_id = ''
    pos_perc = net.find('%')
    if pos_perc > -1:
        pos_slash = net.rfind('/', pos_perc)
        if pos_slash == -1:
            err(f"cannot parse CIDR with zone index '{net}'")
            return 1
        zone_id = net[pos_perc:pos_slash]
        net = net[:pos_perc] + net[pos_slash:]
        dbg(f'{net=}, {zone_id=}')
    try:
        addresses = ipaddress.ip_network(net, strict=False)
    except ValueError as exc:
        err(f"cannot parse CIDR '{net}': {exc}")
        return 1
    if zone_id and not isinstance(addresses, ipaddress.IPv6Network):
        err(f'{net}: zone ID supported with IPv6 only')
        return 1
    if hosts_only:
        addresses = addresses.hosts()
    for addr in addresses:
        print(addr, zone_id, sep='')
    return 0


def parse_start_end(rng):
    """Extract start and end addresses from range expression.

    >>> s, e, zone_id, ok = parse_start_end('192.0.2.47...192.0.2.48')
    >>> s == ipaddress.IPv4Address('192.0.2.47')
    True
    >>> e == ipaddress.IPv4Address('192.0.2.48')
    True
    >>> zone_id == ''
    True
    >>> ok == True
    True
    >>> s, e, zone_id, ok = parse_start_end('2001:db8::a - 2001:db8::b')
    >>> s == ipaddress.IPv6Address('2001:db8::a')
    True
    >>> e == ipaddress.IPv6Address('2001:db8::b')
    True
    >>> zone_id == ''
    True
    >>> ok == True
    True
    >>> s, e, zone_id, ok = parse_start_end('ff02::10%eth0..ff02::20%eth0')
    >>> s == ipaddress.IPv6Address('ff02::10')
    True
    >>> e == ipaddress.IPv6Address('ff02::20')
    True
    >>> zone_id == '%eth0'
    True
    >>> ok == True
    True
    """
    start = end = is_ok = None
    zone_id = ''
    # use a regular expression to accept a wide variety of separators
    tmp = re.split(r'\s*(?:\s+(?:to\s)?|,?\.{2,},?|-+>?|[,;→⇒—…])\s*', rng)
    dbg(f'tmp = {tmp}')
    tmp = [elem for elem in tmp if elem]  # remove empty list elements
    dbg(f'tmp = {tmp}')
    num_addrs = len(tmp)
    if num_addrs < 1:
        err(f"cannot parse range '{rng}': found no addresses")
    elif num_addrs > 2:
        err(f"cannot parse range '{rng}': found more than two addresses")
        is_ok = False
    else:
        is_ok = True
        if num_addrs == 1:
            tmp.append(tmp[0])
        start, end = tmp
        start_pos_perc, end_pos_perc = start.find('%'), end.find('%')
        if ((start_pos_perc == -1 and end_pos_perc != -1) or
                (start_pos_perc != -1 and end_pos_perc == -1)):
            err(f"inconsistent zone ID specification for range '{rng}'")
            is_ok = False
        start_zone_id = end_zone_id = ''
        if start_pos_perc != -1:
            start_zone_id = start[start_pos_perc:]
            start = start[:start_pos_perc]
        if end_pos_perc != -1:
            end_zone_id = end[end_pos_perc:]
            end = end[:end_pos_perc]
        if start_zone_id != end_zone_id:
            err(f'{rng}: zone ID of start and end address must be the same')
            is_ok = False
        else:
            zone_id = start_zone_id
        try:
            start = ipaddress.ip_address(start)
        except ValueError as exc:
            err(f"cannot parse start address '{start}': {exc}")
            is_ok = False
        try:
            end = ipaddress.ip_address(end)
        except ValueError as exc:
            err(f"cannot parse end address '{end}': {exc}")
            is_ok = False
        if is_ok and start.version != end.version:
            err(f'{rng}: start and end addresses must be of same IP version')
            is_ok = False
        if is_ok and zone_id and start.version != 6:
            err(f'{rng}: zone ID supported with IPv6 only')
            is_ok = False
    return (start, end, zone_id, is_ok)


def parse_interval(interval):
    """Extract start and end addresses from interval expression.

    [start, end] includes both start and end addresses.
    [start, end) includes the start addess, but not the end address.
    [start, end[ includes the start addess, but not the end address.
    (start, end] excludes the start address and includes the end address.
    ]start, end] excludes the start address and includes the end address.
    (start, end) excludes both start and end addresses.
    ]start, end[ excludes both start and end addresses.
    >>> s, e, zone_id, ok = parse_interval('[2001:db8::a,2001:db8::c]')
    >>> s == ipaddress.IPv6Address('2001:db8::a')
    True
    >>> e == ipaddress.IPv6Address('2001:db8::c')
    True
    >>> zone_id == ''
    True
    >>> ok == True
    True
    >>> s, e, zone_id, ok = parse_interval('(2001:db8::a,2001:db8::c]')
    >>> s == ipaddress.IPv6Address('2001:db8::b')
    True
    >>> e == ipaddress.IPv6Address('2001:db8::c')
    True
    >>> zone_id == ''
    True
    >>> ok == True
    True
    >>> s, e, zone_id, ok = parse_interval(']2001:db8::a,2001:db8::c]')
    >>> s == ipaddress.IPv6Address('2001:db8::b')
    True
    >>> e == ipaddress.IPv6Address('2001:db8::c')
    True
    >>> zone_id == ''
    True
    >>> ok == True
    True
    >>> s, e, zone_id, ok = parse_interval('[2001:db8::a,2001:db8::c)')
    >>> s == ipaddress.IPv6Address('2001:db8::a')
    True
    >>> e == ipaddress.IPv6Address('2001:db8::b')
    True
    >>> zone_id == ''
    True
    >>> ok == True
    True
    >>> s, e, zone_id, ok = parse_interval('[2001:db8::a,2001:db8::c[')
    >>> s == ipaddress.IPv6Address('2001:db8::a')
    True
    >>> e == ipaddress.IPv6Address('2001:db8::b')
    True
    >>> zone_id == ''
    True
    >>> ok == True
    True
    >>> s, e, zone_id, ok = parse_interval('(2001:db8::a,2001:db8::c)')
    >>> s == ipaddress.IPv6Address('2001:db8::b')
    True
    >>> e == ipaddress.IPv6Address('2001:db8::b')
    True
    >>> zone_id == ''
    True
    >>> ok == True
    True
    >>> s, e, zone_id, ok = parse_interval(']2001:db8::a,2001:db8::c[')
    >>> s == ipaddress.IPv6Address('2001:db8::b')
    True
    >>> e == ipaddress.IPv6Address('2001:db8::b')
    True
    >>> zone_id == ''
    True
    >>> ok == True
    True
    >>> s, e, zone_id, ok = parse_interval(']fe80::a%1,fe80::d%1[')
    >>> s == ipaddress.IPv6Address('fe80::b')
    True
    >>> e == ipaddress.IPv6Address('fe80::c')
    True
    >>> zone_id == '%1'
    True
    >>> ok == True
    True
    """
    start, end, zone_id, is_ok = parse_start_end(interval[1:-1].strip())
    if not is_ok:
        return (start, end, is_ok)
    if interval[0] in '(]':
        start += 1
    if interval[-1] in ')[':
        end -= 1
    return (start, end, zone_id, is_ok)


def print_start_end(start, end, zone_id):
    """Print IP addresses from start to end (inclusive).

    >>> s = ipaddress.IPv4Address('192.0.2.1')
    >>> e = ipaddress.IPv4Address('192.0.2.0')
    >>> r = print_start_end(s, e, '')
    >>> r == 0
    True
    >>> s = ipaddress.IPv4Address('192.0.2.1')
    >>> e = ipaddress.IPv4Address('192.0.2.1')
    >>> r = print_start_end(s, e, '')
    192.0.2.1
    >>> r == 0
    True
    >>> s = ipaddress.IPv4Address('192.0.2.1')
    >>> e = ipaddress.IPv4Address('192.0.2.2')
    >>> r = print_start_end(s, e, '')
    192.0.2.1
    192.0.2.2
    >>> r == 0
    True
    >>> s = ipaddress.IPv6Address('2001:db8::1')
    >>> e = ipaddress.IPv6Address('2001:db8::')
    >>> r = print_start_end(s, e, '')
    >>> r == 0
    True
    >>> s = ipaddress.IPv6Address('2001:db8::1')
    >>> e = ipaddress.IPv6Address('2001:db8::1')
    >>> r = print_start_end(s, e, '')
    2001:db8::1
    >>> r == 0
    True
    >>> s = ipaddress.IPv6Address('2001:db8::1')
    >>> e = ipaddress.IPv6Address('2001:db8::2')
    >>> r = print_start_end(s, e, '')
    2001:db8::1
    2001:db8::2
    >>> r == 0
    True
    >>> s = ipaddress.IPv6Address('fe80::a')
    >>> e = ipaddress.IPv6Address('fe80::b')
    >>> r = print_start_end(s, e, '%eth0')
    fe80::a%eth0
    fe80::b%eth0
    >>> r == 0
    True
    """
    address = start
    while address <= end:
        print(address, zone_id, sep='')
        address += 1
    return 0


def print_ip_range(range_or_cidr, hosts_only):
    """Print an IP range given in any supported format.

    >>> r = print_ip_range('192.0.2.0/30', False)
    192.0.2.0
    192.0.2.1
    192.0.2.2
    192.0.2.3
    >>> r == 0
    True
    >>> r = print_ip_range('2001:db8::7/127', True)
    2001:db8::6
    2001:db8::7
    >>> r == 0
    True
    >>> r = print_ip_range('2001:db8::7/126', True)
    2001:db8::5
    2001:db8::6
    2001:db8::7
    >>> r == 0
    True
    >>> r = print_ip_range('2001:db8::7/126', False)
    2001:db8::4
    2001:db8::5
    2001:db8::6
    2001:db8::7
    >>> r == 0
    True
    >>> r = print_ip_range('fe80::46%eth3:4/127', False)
    fe80::46%eth3:4
    fe80::47%eth3:4
    >>> r == 0
    True
    >>> r = print_ip_range('fe80::46%eth3:4/127', True)
    fe80::46%eth3:4
    fe80::47%eth3:4
    >>> r == 0
    True
    >>> r = print_ip_range('2001:db8::1234..2001:db8::1236', False)
    2001:db8::1234
    2001:db8::1235
    2001:db8::1236
    >>> r == 0
    True
    >>> r = print_ip_range('2001:db8::1234..2001:db8::1236', True)
    2001:db8::1234
    2001:db8::1235
    2001:db8::1236
    >>> r == 0
    True
    >>> r = print_ip_range('[ 2001:db8::1234 ... 2001:db8::1236 )', True)
    2001:db8::1234
    2001:db8::1235
    >>> r == 0
    True
    >>> r = print_ip_range('2001:db8::abcd', True)
    2001:db8::abcd
    >>> r == 0
    True
    >>> r = print_ip_range('fe80::a%eth0-fe80::b%eth0', False)
    fe80::a%eth0
    fe80::b%eth0
    >>> r == 0
    True
    >>> r = print_ip_range(' fe80::e%eth0 fe80::f%eth0 ', False)
    fe80::e%eth0
    fe80::f%eth0
    >>> r == 0
    True
    >>> r = print_ip_range('[fe80::33%eth0.100,fe80::36%eth0.100)', False)
    fe80::33%eth0.100
    fe80::34%eth0.100
    fe80::35%eth0.100
    >>> r == 0
    True
    >>> r = print_ip_range('fe80::47%eth0:1,fe80::49%eth0:1', False)
    fe80::47%eth0:1
    fe80::48%eth0:1
    fe80::49%eth0:1
    >>> r == 0
    True
    >>> r = print_ip_range('fe80::1%1:1..fe80::2%1:1', False)
    fe80::1%1:1
    fe80::2%1:1
    >>> r == 0
    True
    >>> r = print_ip_range('fe80::1%enx02123456789a-fe80::2%enx02123456789a',
    ... False)
    fe80::1%enx02123456789a
    fe80::2%enx02123456789a
    >>> r == 0
    True
    """
    if '/' in range_or_cidr:
        return print_cidr(range_or_cidr, hosts_only)
    elif (len(range_or_cidr) > 1
          and range_or_cidr[0] in '[]('
          and range_or_cidr[-1] in '[])'):
        start, end, zone_id, is_ok = parse_interval(range_or_cidr)
        if not is_ok:
            return 1
    else:
        start, end, zone_id, is_ok = parse_start_end(range_or_cidr)
        if not is_ok:
            return 1
    return print_start_end(start, end, zone_id)


if __name__ == '__main__':
    ARGS = cmd_line_args()
    if ARGS.debug:
        DEBUG = True
    EXIT_CODE = 0
    RANGES = ARGS.RANGE if ARGS.RANGE else sys.stdin
    for r in RANGES:
        EXIT_CODE += print_ip_range(r.strip(), ARGS.hosts_only)
    if EXIT_CODE:
        EXIT_CODE = 1
    sys.exit(EXIT_CODE)

# vim:tabstop=4:shiftwidth=4:expandtab:
