#!/usr/bin/perl
# add year and quantity numbers back to corpus lines after tagging
use warnings;
use strict;
use Tie::File;

tie my @numbers, 'Tie::File', "xaccleaned" or die "couldn't open input file: $!";
open my $corpus, '<', "/home/tom/video/xacentire" or die "couldn't open input file: $!";
open my $corpusnew, '>', "/home/tom/akb/xacentire-yrqty" or die "couldn't open output file: $!";
my $record = 0;
while (<$corpus>) {
   chomp;
   #my $year_qty = $numbers[$record];
   #$year_qty =~ s/.+( [0-9]+ [0-9]+$)/$1\n/;
   # get year and quantity fields to add to 5gram line
   if ($numbers[$record] =~ /.+( [0-9]+ [0-9]+$)/) {       
       print $corpusnew $_ . $1 . "\n";
   }
   else { printf "didn't match number fields in line %d\n", $record; }             
   $record++;
}
# close ($NUMBERS) or die "can't close input file: $!";
close $corpus;
close $corpusnew;

