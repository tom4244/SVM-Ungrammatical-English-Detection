#!/usr/bin/perl -w
# put a random number of defined types of 
# English grammatical errors chosen randomly 
# in random appropriate places in a text file 
use warnings;
use strict;
use autodie;
use File::Slurp;
use List::Util qw(shuffle);

#my $text = read_file("training-docs-with-errors/1e");
#open my $goodtext, '<', $ARGV[0];
my @files = grep { -f } glob( 'training-docs-no-errors/*e' );
while (<@files>) {
#while (my $thisfile = <@files>) {
  open my $goodtext, '<', $_;
  open my $badtext, '>',  $_ . "_err";
  my $text = read_file($goodtext);
  my $adj_errors = 0;
  my $determ_errors = 0;
  my $verb_errors = 0;
  my $total_errors = 0;

my @dtrm;

$dtrm[0] = sub {
   # dtrm-a
   #my $errors_qty = int(rand(2)) + 1;
   my $errors_qty = 1;
   my $n = 0;
   while($errors_qty--) {
      $text = $text . " I don't have a eraser.";
      $determ_errors += 1;
      $total_errors += 1;
   }
};

$dtrm[1] = sub {
   # dtrm-an
   #my $errors_qty = int(rand(2)) + 1;
   my $errors_qty = 1;
   my $n = 0;
   while($errors_qty--) {
      $text = $text . " I saw an big boat.";
      $determ_errors += 1;
      $total_errors += 1;
   }
};

$dtrm[2] = sub {
   # dtrm-both
   #my $errors_qty = int(rand(2)) + 1;
   my $errors_qty = 1;
   my $n = 0;
   while($errors_qty--) {
      $text = $text . " I talked with both of Joe and Bob.";
      $determ_errors += 1;
      $total_errors += 1;
   }
};

$dtrm[3] = sub {
   # dtrm-dsp
   #my $errors_qty = int(rand(2)) + 1;
   my $errors_qty = 1;
   my $n = 0;
   while($errors_qty--) {
      $text = $text . " She doesn't like a train station dogs.";
      $determ_errors += 1;
      $total_errors += 1;
   }
};


$dtrm[4] = sub {
   # dtrm-noun
   #my $errors_qty = int(rand(2)) + 1;
   my $errors_qty = 1;
   my $n = 0;
   while($errors_qty--) {
      $text = $text . " I wanted thing to fix the car.";
      $determ_errors += 1;
      $total_errors += 1;
   }
};

$dtrm[5] = sub {
   # dtrm-some
   #my $errors_qty = int(rand(2)) + 1;
   my $errors_qty = 1;
   my $n = 0;
   while($errors_qty--) {
      $text = $text . " He doesn't need some salt.";
      $determ_errors += 1;
      $total_errors += 1;
   }
};


# run individual error placing subroutines
@dtrm = shuffle @dtrm;
#print "dtrm is " . @dtrm . "\n";
my $subs = scalar(@dtrm);
my $d = 0;
#my $error_types = int(rand(3)) + 1;
my $error_types = int(rand(2)) + 1;
#print "error types is " . $error_types . "\n";
while ($d < $error_types) {
   $dtrm[$d++] ->();
}   

  print $badtext $text;
  close $goodtext;
  close $badtext;
}
