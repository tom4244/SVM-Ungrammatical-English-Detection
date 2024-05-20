#!/usr/bin/perl
# Reformat lines in Google corpus csv file to space delimited lines.
#   Discard lines that don't appear to be valid 5-gram lines.
use strict;
use warnings;
open INTHANG, "<typical.csv" or die $!;
open OUTTHANG, ">typical.fivetoken" or die $!;
#my @lines = <INTHANG>;
#foreach my $line (@lines) {
while (<INTHANG>) {    
  if (m/\S+ \S+ \S+ \S+ \S+\t\d+\t\d+\t\d+\t\d+/) {
    print OUTTHANG $_;
  }
}
#my @foo = grep(/\S+\s\S+\s\S+\s\S+\s\S+\t[0-9]+\t\S+\t\S+\t\S+/, @lines);
#my @foo = grep(/\S+ \S+ \S+ \S+ \S+\t\d+\t\d+\t\d+\t\d+/, @lines);
#print OUTTHANG @foo;
close (INTHANG);
close (OUTTHANG);

