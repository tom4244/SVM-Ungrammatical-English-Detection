#!/usr/bin/perl -w
# script to extract trigrams from 5gram corpus
use strict;
use warnings;
use utf8::all;
use Encode;
open my $corpus, '<', 'google_corpus' or die "cannot open infile: $!";
open my $trigrams, '>', 'trigrams' or die "cannot open outfile: $!";

while (<$corpus>) {
    if ($_ =~ /^\(\S+\s\S+\)\(\S+\s\S+\)\(\S+\s\S+\)\(\S+\s\S+\)\(\S+\s\S+\)\s\d+\s\d+$/) {
         s/^\(\S+\s\S+\)(\(\S+\s\S+\)\(\S+\s\S+\)\(\S+\s\S+\))\(\S+\s\S+\)(\s\d+\s\d+)/$1$2/;
         print $trigrams $_;
    }
}
close $corpus or die "can't close infile: $!";
close $trigrams or die "can't close outfile: $!";

