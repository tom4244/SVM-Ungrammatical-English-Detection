#!/usr/bin/perl -w
# Check that lines in a cleaned corpus file are
#   properly formed ngram lines
use warnings;
use strict;
use utf8::all;
use Encode;

open (INFILE, '<', 'cleaned') or die "couldn't open infile: $!";
#my $outfile = '/home/tom/video/cleaned-split';
#my @words;
#open (OUTFILE, "+>", $outfile) or die "couldn't open outfile: $!";
open my $OUTFILE, ">", "baddies" or die "couldn't open outfile: $!";
my $goodies = 0;
my $empties = 0;
my $baddies = 0;
my $total = 0;
while (<INFILE>) {
    if (/^([^ ]+? ){6}[^ ]+?$/) { $goodies++ }
    else { $baddies++;
           print $OUTFILE $_;
    }
    if ($baddies > 10) { last; }
        
#    s/\d+ \d+$//g; #remove two numeric terms at the end    
#    s/ /\n/g; #put one word per line
#    binmode OUTFILE, ":utf8";

}
printf "goodies: %d  baddies: %d\n", $goodies, $baddies;
close (INFILE) or die "can't close input file: $!";
close $OUTFILE or die "can't close output file: $!";
