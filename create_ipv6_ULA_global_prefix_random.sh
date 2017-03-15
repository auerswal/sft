#! /bin/bash

# Generate an IPv6 ULA Global Prefix.

# Copyright (C) 2017 Erik Auerswald <auerswal@unix-ag.uni-kl.de>

# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without any warranty.

# Version 2017-03-17-01

set -e
set -u

# use /dev/random as source for a random global ID
# see https://tools.ietf.org/html/rfc4193#section-3.2.1

global_id=$(dd if=/dev/random bs=5 count=1 2>/dev/null | xxd -p)
base="fc00"
local_bit="0100"
word0="$(( 0x${base} | 0x${local_bit} | 0x${global_id:0:2} ))"
word1="${global_id:2:4}"
word2="${global_id:6:4}"
prefix=$(printf -- '%x:%s:%s::/48' "${word0}" "${word1}" "${word2}")
echo "${prefix}"
exit 0
