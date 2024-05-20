#!/usr/bin/perl -w
# Correct some tagger idiosyncracies
use warnings;
use strict;
use utf8::all;
use Encode;
#open my $entire, '<', 'xaaentire' or die "couldn't open infile: $!";
open my $entire, '<', 'xaaentire' or die "couldn't open infile: $!";
open my $entirenew, '>', '/home/tom/video/xaaentire.new' or die \
    "couldn't open outfile: $!";
my $index = 0;
while (<$entire>) {
#    if ($index > 39600000) {
        #s/^([^ ()]+?)\(/\($1/;
        s/^ +//;
#    }                    
    print $entirenew $_;
    $index++;
}
close $entire or die "can't close entire file: $!";
close $entirenew or die "can't close entirenew file: $!";
