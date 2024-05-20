#!/usr/bin/perl -w
#  Correct some HunPos tagger idiosyncracies to better match
#    the Penn Treebank Tag-set
use warnings;
use strict;

open (TAGS, '<', 'hunpos-ceejus.txt') or die "couldn't open infile: $!";
my $outfile = 'hunpos-fixed.txt';
my @splittag;
open (OUTFILE, "+>", $outfile) or die "couldn't open outfile: $!";
while (<TAGS>) {
    s/[\[\]]//g;
    s/(\('.*?)([.,!:;])(', '.*?'\),)/$1$3 \('$2', '$2'\),/g;
    @splittag = (@splittag,split("\n"));
}
my $arysize = scalar @splittag;
print "ary1 is $arysize\n";
for (my $n=0; $n < $arysize; $n++) {        
  print OUTFILE $splittag[$n],"\n";
}

close (TAGS) or die "can't close input file: $!";
close (OUTFILE) or die "can't close output file: $!";
