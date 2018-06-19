#!/usr/bin/perl -w

#
#	filter STRING fasta file by species id
#

use strict;
use warnings;

use Sys::Hostname;
use POSIX;

my $run_info_summary = "## $0 @ARGV ##\n";
$run_info_summary .= "## " . (scalar localtime()) . "\n";
$run_info_summary .= "## " . hostname . " - " . `pwd`;
$run_info_summary .= "##\n";

print STDERR "$run_info_summary";

use Bio::DB::Fasta;	# for fasta-file lookup
use Bio::SeqIO;

print STDERR "call with species id (reads fasta file from STDIN)\n" and exit unless ($ARGV[0]);
my $species = shift;
print "$species\n";


my %sequences;
my $in = Bio::SeqIO->new( -fh => \*STDIN, -format => 'Fasta' );
print $in;
while ( my $seq = $in->next_seq ) {
	my $id = $seq->id();
	next unless ($id =~ /^$species\./);
	next if ($seq->seq() =~ /^Sequence/);
#	$id =~ s/^$species\.//;
	print ">$id\n", $seq->seq(), "\n";
}
