#! /usr/bin/env python3

# net2ips.py - print addresses of an IP network
# Copyright (C) 2022-2024  Erik Auerswald <auerswal@unix-ag.uni-kl.de>
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

"""Print addresses of IP networks, one per line.

IPv4 and IPv6 networks in CIDR notation can be specified as positional
command line arguments.  Without positional command line arguments,
IPv4 and IPv6 networks in CIDR notation are read from standard input,
one network per line.

The IP addresses of the given IP networks are printed to standard output,
one IP address per line.  By default, every IP address inside a CIDR range
is printed, including the network number and subnet directed broadcast
address for IPv4, and the Subnet-Router anycast address for IPv6.
"""

import argparse
import ipaddress
import sys

PROG = 'net2ips.py'
VERS = '0.2.0'
COPY = 'Copyright (C) 2022-2024  Erik Auerswald <auerswal@unix-ag.uni-kl.de>'
LICE = '''\
License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
'''
DESC = 'Print addresses of IP networks, one per line.'
EPIL = '''\
IPv4 and IPv6 networks in CIDR notation can be specified as positional
command line arguments.  Without positional command line arguments,
IPv4 and IPv6 networks in CIDR notation are read from standard input,
one network per line.

The IP addresses of the given IP networks are printed to standard output,
one IP address per line.  By default, every IP address inside a CIDR range
is printed, including the network number and subnet directed broadcast
address for IPv4, and the Subnet-Router anycast address for IPv6.
'''


if __name__ == '__main__':
    cmd_line = argparse.ArgumentParser(
        prog=PROG, description=DESC, epilog=EPIL,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    cmd_line.add_argument('-V', '--version', action='version',
                          version='\n'.join([PROG + ' ' + VERS, COPY, LICE]))
    cmd_line.add_argument('-H', '--hosts-only', action='store_true',
                          help='print only host addresses')
    cmd_line.add_argument('NETWORK', nargs='*',
                          help='IPv4 or IPv6 network in CIDR format')
    args = cmd_line.parse_args()

    exit_code = 0

    networks = args.NETWORK if args.NETWORK else sys.stdin
    for net in networks:
        net = net.strip()
        idx_perc = net.find('%')
        idx_cidr = net.rfind('/')
        scope_id = ''
        if idx_perc > -1 and idx_cidr > -1 and net[idx_cidr + 1:].isdigit():
            scope_id = net[idx_perc:idx_cidr]
            net = net[:idx_perc] + net[idx_cidr:]
        try:
            addresses = ipaddress.ip_network(net, strict=False)
        except ValueError as exc:
            exit_code = 1
            print('%s: ERROR: %s' % (PROG, exc), file=sys.stderr)
        if args.hosts_only:
            addresses = addresses.hosts()
        for addr in addresses:
            print(str(addr) + scope_id)

    sys.exit(exit_code)

# vim:tabstop=4:shiftwidth=4:expandtab:
