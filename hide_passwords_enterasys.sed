#! /bin/sed -f

# Replace passwords in Enterasys configuration files with XXXXXXXX.
#
# Copyright (C) 2013 Erik Auerswald <auerswal@unix-ag.uni-kl.de>
#
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without any warranty.
#
# Version 2013-07-05-01

s/ :[0-9a-fA-F][0-9a-fA-F]*:/ XXXXXXXX/g
s/ :[0-9a-fA-F][0-9a-fA-F]*$/ XXXXXXXX/
s/set snmp community [^ ]*/set snmp community XXXXXXXX/
/snmp .* v[12]/s/user [^ ]* /user XXXXXX /
/message-digest-key/s/md5 [^ ]* /md5 XXXXXXXX /
/message-digest-key/s/md5 [^ ]*$/md5 XXXXXXXX/
s/password [^ ]*/password XXXXXXXX/
s/authentication simple [^ ]* /authentication simple XXXXXXXX /
s/authentication simple [^ ]*$/authentication simple XXXXXXXX/
s/authentication md5 [^ ]* /authentication md5 XXXXXXXX /
s/authentication md5 [^ ]*$/authentication md5 XXXXXXXX/
