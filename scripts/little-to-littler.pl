#!/usr/bin/perl
# Filter out ngram lines that do not appear to contain valid ngrams
use strict;
use warnings;
open INTHANG, "<little" or die $!;
open OUTTHANG, ">littler" or die $!;
my @lines = <INTHANG>;
my @foo = grep(/\S+\s\S+\s\S+\s\S+\s\S+\t\S+\t\S+\t\S+\t\S+/, @lines);
print OUTTHANG @foo;
close (INTHANG);
close (OUTTHANG);

