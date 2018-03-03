#! /bin/sh

# Use tcpdump to capture traffic for a given time.
#
# Copyright (C) 2016-2018 Erik Auerswald <auerswald@unix-ag.uni-kl.de>
#
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without any warranty.

# It is simpler to use Dumpcap from the Wireshark distribution, but
# sometimes Dumpcap is not available, but tcpdump is.

CF='capture.pcap'
DURATION="1m"
IF="$1"

test -z "$1" && { echo usage: $0 INTERFACE; exit 1; }

rm -fv "$CF"
# XXX "tcpdump -G60 -W1" does not stop if interface down
# XXX tcpdump needs duration in seconds, just as POSIX sleep
# tcpdump -i "$IF" -G"$DURATION" -W1 -w "$CF" -v
# Dumpcap example:
# dumpcap -i "$IF" -a duration:"$DURATION" -w "$CF"
# Since tcpdump -G is not reliable, and dumpcap is not available, start
# a tcpdump process and kill it after the given duration:
tcpdump -w "$CF" -i "$IF" -v &
DUMPPID=$!
sleep "$DURATION"
kill "$DUMPPID"
wait
