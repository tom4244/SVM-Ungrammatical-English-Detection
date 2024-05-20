#!/usr/bin/perl -w
# remove lines longer than 63 chars as they are specialized terms,
# proper nouns, and german
use strict;
use warnings;
use utf8::all;
use Encode;

open my $corpusfile, "<", $ARGV[0] or die "couldn't open infile: $!";
open my $outfile, ">", $ARGV[0] . "new" or die "couldn't open outfile: $!";
while (<$corpusfile>) {
  chomp();
  if (length() < 64) {
      print $outfile $_ . "\n";
  }
}
close $corpusfile or die "can't close infile: $!";
close $outfile or die "can't close outfile: $!";
