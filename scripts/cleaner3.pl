#!/usr/bin/perl
# script to further clean up Google 5gram corpus 
# remove quotes and words that got melded into one item; ex: (''begin NNP)

use strict;
use warnings;
open my $badcorpus, "<", 'google_corpus' or die "couldn't open infile: $!";
open my $goodcorpus, ">", "/home/tom/video/google_corpus" or die \
    "couldn't open outfile: $!";
while (<$badcorpus>) {
  chomp;
  s/(\(\'\'[^ ]+ [^ ]+\))//g;
  print $goodcorpus $_ . "\n";
}
close $badcorpus or die "can't close input file: $!";
close $goodcorpus or die "can't close output file: $!";

