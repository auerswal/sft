#! /bin/bash

# Generate an IPv6 ULA Global Prefix.

# Copyright (C) 2017,2021 Erik Auerswald <auerswal@unix-ag.uni-kl.de>

# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without any warranty.

# Version 2021-09-19-01

set -e
set -u

# see RFC 4193 section 3.2.2 for algorithm idea
# (https://datatracker.ietf.org/doc/html/rfc4193#section-3.2.2)
# [SHA-256 instead of SHA-1 as "PRF"]

# determine the current time
if type ntpq >/dev/null 2>&1; then
  cur_time_hex="$(ntpq -n -c 'rv 0 clock' localhost \
                  | sed 's/^.*=\([^.]\+\)\.\([^ ]\+\) .*$/\1\2/')"
elif type date >/dev/null 2>&1; then
  cur_time_hex="$(printf -- '%016x' "$(date +%s%N)")"
else
  echo 'ERROR: neither "ntpq" nor "date" available, cannot determine time'
  exit 1
fi
test "${#cur_time_hex}" -eq 16 ||
  { echo 'ERROR: could not determine current time'; exit 1; }

# determine a "suitably unique identifier, local to the node" (suid)
if ip -6 address 2>/dev/null | grep -Fq ff:fe; then
  suid="$(ip -6 address | grep -F ff:fe | head -n1 | awk '{print $2}' \
          | sed 's,^.*:\([^:]\+:[^:]\+:[^:]\+:[^:]\+\)/.*$,\1,' \
          | sed -e 's/\(^\|:\)\([^:]\)\(:\|$\)/\1000\2\3/g' \
                -e 's/\(^\|:\)\([^:]\{2\}\)\(:\|$\)/\100\2\3/g' \
                -e 's/\(^\|:\)\([^:]\{3\}\)\(:\|$\)/\10\2\3/g' \
          | tr -d :)"
elif ip link 2>/dev/null | grep -Fq link/ether; then
  suid="$(ip link 2>/dev/null | grep -F link/ether | head -n1 \
          | awk '{print $2}' \
          | awk -F: '{print $1$2$3"fffe"$4$5$6}')"
else
  suid="$(uname -a 2>/dev/null | sha256sum 2>/dev/null | cut -c1-16)"
fi
test "${#suid}" -eq 16 ||
  { echo 'ERROR: could not determine a suitably unique identifier'; exit 1; }

# use current time and suid as hash input
trunc_digest="$(printf -- '%s%s' "${cur_time_hex}" "${suid}" \
                | sha256sum \
                | cut -c55-64)"

# create ULA prefix from truncated digest
base="fc00"
local_bit="0100"
word0="$(( 0x${base} | 0x${local_bit} | 0x${trunc_digest:0:2} ))"
word1="${trunc_digest:2:4}"
word2="${trunc_digest:6:4}"
prefix="$(printf -- '%x:%s:%s::/48' "${word0}" "${word1}" "${word2}")"
echo "${prefix}"
exit 0
