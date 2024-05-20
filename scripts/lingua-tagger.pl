#!/usr/bin/perl
# tag text file using Lingua::EN:Tagger
use warnings;
use strict;
use utf8::all;
use Encode;
use Lingua::EN::Tagger;
#use File::Slurp;
my $p = new Lingua::EN::Tagger;
my $infile = $ARGV[0];
my $outfile = $ARGV[1];
open (INFILE, "<", $infile) or die "couldn't open infile: $!";
open (OUTFILE, "+>", $outfile) or die "couldn't open outfile: $!";
binmode OUTFILE, ":utf8";
#my $text = read_file('corpus0');
#my $tagged_text = $p->add_tags( $text );
#print OUTFILE $tagged_text;
#print OUTFILE $text;
while (<INFILE>) {
#  $linenumber++;
#  if ($linenumber % 10000000 == 0) {
#     print $linenumber/10000000 . "0M lines completed \n";
#  }    
#  chomp;
#  my $tagged_text = $p->add_tags($_);
  $_ = $p->add_tags($_);
  s/<(.*?)>(.*?)<.*?>/\(\U$1\E $2\)/g;  
  print OUTFILE $_ . "\n"; 
}
close (INFILE) or die "can't close input file: $!";
close (OUTFILE) or die "can't close output file: $!";


