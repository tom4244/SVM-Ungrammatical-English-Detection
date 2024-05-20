#!/usr/bin/perl -w
# checks pre-tagged 5gram lines against processed 
# (split into word-per-line, tagged, recombined, and formatted)
# lines to ensure nothing was lost
use warnings;
use strict;
use utf8::all;
use Encode;
use Tie::File;
tie my @cleaned, 'Tie::File', "xaccleaned" or die \
                   "couldn't open input file: $!";
open my $entire, '<', 'xacentire' or die "couldn't open infile: $!";
open my $mismatches, '>', 'mismatches' or die "couldn't open mismatches: $!";
my $index = 0;
my $firstE;
my $firstC;
#my $badones;
while (<$entire>) {
#   if ($index < 41000000) {
#       $index++;
#       next;
#   }
   if ($index % 100000 == 0) { print $index . "\n"; }        
   chomp;    
   my $firstEword = $_;
   my $firstCword = $cleaned[$index];   
#   $firstEword =~ (s/^\(([^ ]+?) (.+$)/$1/);   
#   $firstCword =~ (s/^([^ ]+) .+$/$1/);
   if ($firstEword =~ /^\(([^ ]+?) (.+$)/) {
       $firstE = $1;
   }
   if ($firstCword =~ /^([^ ]+) .+$/) {
       $firstC = $1;
   }  
   # if ($firstEword ne $firstCword) {
   if ($firstE ne $firstC) {
       printf $mismatches "They are not equal. Index is %d\n", $index;
       printf $mismatches "Eword: xxx%sxxx\n", $firstEword;
       printf $mismatches "Cword: xxx%sxxx\n", $firstCword;
       print $mismatches $cleaned[$index] . "\n";
       print $mismatches $_;
       print $mismatches "\n";
#      $badones++;
   }
#   if ($badonees > 10) { last; }
   $index++;
}
close $entire or die "can't close entire file: $!";
close $mismatches or die "can't close mismatches file: $!";
