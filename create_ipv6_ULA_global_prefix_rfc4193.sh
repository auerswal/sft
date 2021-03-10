#! /bin/bash

# Generate an IPv6 ULA Global Prefix.

# Copyright (C) 2017 Erik Auerswald <auerswal@unix-ag.uni-kl.de>

# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without any warranty.

# Version 2017-03-11-01

set -e
set -u

# see RFC 4193 section 3.2.2 for algorithm idea
# (https://datatracker.ietf.org/doc/html/rfc4193#section-3.2.2)
# [SHA-256 instead of SHA-1 as "PRF"]

cur_time_hex=$(ntpq -n -c 'rv 0 clock' localhost \
               | sed 's/^.*=\([^.]\+\)\.\([^ ]\+\) .*$/\1\2/')
test "${#cur_time_hex}" -eq 16 ||
  { echo 'ERROR: could not determine current time'; exit 1; }
eui64=$(ip -6 address | fgrep ff:fe | head -n1 | awk '{print $2}' \
        | sed 's,^.*:\([^:]\+:[^:]\+:[^:]\+:[^:]\+\)/.*$,\1,' \
        | sed -e 's/\(^\|:\)\([^:]\)\(:\|$\)/\1000\2\3/g' \
              -e 's/\(^\|:\)\([^:]\{2\}\)\(:\|$\)/\100\2\3/g' \
              -e 's/\(^\|:\)\([^:]\{3\}\)\(:\|$\)/\10\2\3/g' \
        | tr -d :)
test "${#eui64}" -eq 16 ||
  { echo 'ERROR: could not determine a local EUI-64 identifier'; exit 1; }
trunc_digest=$(printf -- '%s%s' "${cur_time_hex}" "${eui64}" \
               | sha256sum \
               | cut -c55-64)
base="fc00"
local_bit="0100"
word0="$(( 0x${base} | 0x${local_bit} | 0x${trunc_digest:0:2} ))"
word1="${trunc_digest:2:4}"
word2="${trunc_digest:6:4}"
prefix=$(printf -- '%x:%s:%s::/48' "${word0}" "${word1}" "${word2}")
echo "${prefix}"
exit 0
