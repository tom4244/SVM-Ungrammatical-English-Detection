#!/usr/bin/perl -w
# Compare part-of-speech tagging of three different POS taggers
#   for the same file
use warnings;
use strict;

open (TAG1, '<', 'pfp-jeecus.txt') or die "couldn't open infile: $!";
open (TAG2, '<', 'ceejus-jeecus.txt') or die "couldn't open infile: $!";
open (TAG3, '<', 'hunpos-fixed.txt') or die "couldn't open infile: $!";
my $outfile = 'comparison.txt';
my @splittag1;
my @splittag2;
my @splittag3;
open (OUTFILE, "+>", $outfile) or die "couldn't open outfile: $!";
#my $ea = each_array(@a, @b, @c);
#while ( my ($a, $b, $c) = $ea->() )   { .... }
#my $iteration = 0;
while (<TAG1>) {
    s/(\(.*?\))/$1\n/g;
#    if ($iteration == 0) { print $_; }
#    $iteration++;                                   
    @splittag1 = (@splittag1, split("\n"));
}    
while (<TAG2>) {
    s/(\(.*?\))/$1\n/g;
    @splittag2 = (@splittag2,split("\n"));
}
while (<TAG3>) {
    #s/[\[\]]//g;
    #s/\('(.*?)([.,!:;])', '(.*?)'\),/\($3 $1\)\n\($2 $2\)\n/g;
    s/\('(.*?)', '(.*?)'\),/\($2 $1\)\n/g;
    @splittag3 = (@splittag3,split("\n"));
}
my $arysize1 = scalar @splittag1;
my $arysize2 = scalar @splittag2;
my $arysize3 = scalar @splittag3;
my $smallest;
my $newln = "\n";
print "ary1 is $arysize1, ary2 is $arysize2, and ary3 is $arysize3\n";

if ($arysize1 < $arysize2) {$smallest = $arysize1;}
else {$smallest = $arysize2; }
if ($arysize3 < $smallest) {$smallest = $arysize3;}
print "smallest is $smallest\n";
for (my $n1=0; $n1 < $smallest; $n1++) {
  printf OUTFILE "%-18s %-18s %-18s\n", $splittag1[$n1], $splittag2[$n1], $splittag3[$n1];
#  print OUTFILE $splittag3[$n1],"\n";
}
close (TAG1) or die "can't close input file: $!";
close (TAG2) or die "can't close input file: $!";
close (TAG3) or die "can't close input file: $!";
close (OUTFILE) or die "can't close output file: $!";
