#!/usr/bin/perl -w
# script to pad each line in files with spaces to uniform length
# so it can be rapidly searched with binary search and file.seek()

use strict;
use warnings;
use utf8::all;
use Encode;

my @files = grep { -f } glob( '*_corpus' );
while (<@files>) {
  print "processing " . $_ . "\n";    
  open my $corpusfile, "<", $_ or die "couldn't open infile: $!";
  my $padded = $_ . "new";
  open my $padfile, '>', $padded or die "cannot open outfile: $!";
  while (<$corpusfile>) {
    chomp();
    print $padfile pack("A63", $_) . "\n";
  }
  close $corpusfile or die "can't close infile: $!";
  close $padfile or die "can't close outfile: $!";
}
