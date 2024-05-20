#!/usr/bin/perl
# Count all words in a text file and place each word's number beside it
use warnings;
use strict;
use utf8::all;
use Encode;

#use File::Slurp;
my $infile = $ARGV[0];
my $outfile = $ARGV[0] . '_numbered';
open my $in_fh, "<", $infile or die "couldn't open infile: $!";
open my $out_fh, ">", $outfile or die "couldn't open outfile: $!";
binmode $out_fh, ":utf8";
my $word_num = 0;
while (<$in_fh>) {
   #my @words = ($_, split(/\s+|([[:punct:]])/));
   my @words = split(/\s/, $_);        
   foreach my $word (@words) {
      # have to skip [0] which is entire sentence
      next if $word eq $_;
      # split punctuation attached to the end of words
      my @no_punct = split(/([[:punct:]])/, $word);
      foreach my $no_punct (@no_punct) {         
          print $out_fh $no_punct . " " . $word_num . "  ";
          $word_num++;
      }      
   }   
}
close $in_fh or die "can't close input file: $!";
close $out_fh or die "can't close output file: $!";


