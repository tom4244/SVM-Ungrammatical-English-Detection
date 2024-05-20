#!/usr/bin/perl
use warnings;
use strict;
# reformat hunpos tagged corpus output to nice list of 5grams
# also correct hunpos tags for single-character tokens like $

open (HUN_TAGS, '<', "/home/tom/akb/cleaned-split-tagged") or die "couldn't open input file: $!";
#open (HUN_TAGS, '<', "sample") or die "couldn't open input file: $!";
open (NEWONE, '>', 'entire_google') or die "couldn't open output file: $!";
my $sentence = "";
while (<HUN_TAGS>) {
    if (/^\n/) {
        $sentence = $sentence . "\n";
        print NEWONE $sentence;
        $sentence = "";
    } else {
        s/([^ a-zA-Z0-9])\t[^ ]+\t/($1 $1)/;
        s/([^ ]+?)\t([^ ]+?)\t/($1 $2)/;
        chomp;
        $sentence = $sentence . $_;
    }
    #print $sentence;        
}    
 close (HUN_TAGS) or die "can't close input file: $!";
 close (NEWONE) or die "can't close output file: $!";
