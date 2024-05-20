#!/usr/bin/perl
# script to put an extra line after each line in the file
use strict;
use warnings;
#my $linenumber = 0;
#my $counter = 0;
open (INFILE, "<", 'corpus0') or die "couldn't open infile: $!";
my $outfile = 'spaced0';
open (OUTFILE, "+>", $outfile) or die "couldn't open outfile: $!";
while (<INFILE>) {
#  $linenumber++;
#  if ($linenumber % 10000000 == 0) {
#     print $linenumber/10000000 . "0M lines completed \n";
#  }    
#  chomp;
    print OUTFILE $_ . "\n\n";    
}
close (INFILE) or die "can't close input file: $!";
close (OUTFILE) or die "can't close output file: $!";


    
