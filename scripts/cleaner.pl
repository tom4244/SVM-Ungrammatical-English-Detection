#!/usr/bin/perl
# script to further clean up Google 5gram corpus 
# 1. ensure all '5grams' have at least 4 words with at most 1 quote, period, etc.
# 2. eliminate lines with non-ascii characters and characters like '^' as
#  the corpus is to be used to compare to sequences of ordinary English words
use strict;
use warnings;
my $linenumber = 0;
#my $counter = 0;
open (INFILE, "<", 'corpus0-799') or die "couldn't open infile: $!";
my $outfile = '/home/tom/video/cleaned';
open (OUTFILE, "+>", $outfile) or die "couldn't open outfile: $!";
while (<INFILE>) {
  $linenumber++;
  if ($linenumber % 10000000 == 0) {
     print $linenumber/10000000 . "0M lines completed \n";
  }    
  chomp;
  # ignore lines with non-ascii characters
  if (!/[^\x20-\x7F\t]|[\^_]/) {
    my $single_chars = 0;
    #only allow 1 single-char gram
    if (/(\S+)\s(\S+)\s(\S+)\s(\S+)\s(\S+)/) {
      (my $gram1, my $gram2, my $gram3, my $gram4, my $gram5) =
       (/(\S+)\s(\S+)\s(\S+)\s(\S+)\s(\S+)/);
#      print "grams: " . $gram1 . " " . $gram2 . " " . $gram3 . "\n";
      if ($gram1 =~ m/^[^\d\w]$/) { $single_chars++ };
      if ($gram2 =~ m/^[^\d\w]$/) { $single_chars++ };
      if ($gram3 =~ m/^[^\d\w]$/) { $single_chars++ };      
      if ($gram4 =~ m/^[^\d\w]$/) { $single_chars++ };          
      if ($gram5 =~ m/^[^\d\w]$/) { $single_chars++ };
      if ($single_chars < 2) { print OUTFILE $_ . "\n";}
    }
  }
}
close (INFILE) or die "can't close input file: $!";
#my @foo2 = grep(/( of | in | to | for | with | on | at | by | from | into | about | through )/, @foo);
close (OUTFILE) or die "can't close output file: $!";


    
