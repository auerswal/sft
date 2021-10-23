#! /usr/bin/perl -w

# section.pl - print line matching regexp with following indented section
#
# Copyright (C) 2018-2021 by Erik Auerswald <auerswal@unix-ag.uni-kl.de>
#
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without any warranty.

use strict;

if (scalar(@ARGV) == 0) { print "Usage: section PATTERN [FILE...]\n"; exit 1;}

my $pat = $ARGV[0]; shift;
my $in_sec = 0;
my $ind = '';
my $l_ind = '';
my $l_mat = 0;

while (<>) {
	($l_ind) = (/^([ \t]*)/);
	$l_ind =~ s/\t/        /g;
	$l_mat = /$pat/ ? 1 : 0;
	if ($l_mat || ($in_sec && length $l_ind > length $ind)) {
		if (!$in_sec || (length $l_ind < length $ind)) { $ind = $l_ind; }
		$in_sec = 1;
		print;
	} else {
		$in_sec = 0;
		$ind = '';
	}
}
