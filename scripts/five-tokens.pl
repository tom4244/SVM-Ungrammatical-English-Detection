#!/usr/bin/perl
# script to translate Google corpus tokens to Stanford Parser format
use strict;
use warnings;
open INTHANG, "<goog" or die $!;
#open SFILE, "+>shrunk" or die $!;
open OUTTHANG, ">filtered" or die $!;
my @lines = <INTHANG>;
my @five_tokens = grep(/\S+\s\S+\s\S+\s\S+\s\S+\t[0-9]+\t\S+\t\S+\t\S+/, @lines);
print "Filtered raw corpus to only include 5 token entries.\n";
# combine matches from different years and put them on a single line with count
print OUTTHANG @five_tokens;
close (INTHANG);
#close (SFILE);
close (OUTTHANG);

