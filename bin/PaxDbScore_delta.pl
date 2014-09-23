#!/usr/bin/perl -w
##################################################################################################
#
#
#
##################################################################################################

use strict;
use warnings;
use Statistics::Descriptive;

# subroutines:
sub get_zscore($);
sub get_median($);
sub fisher_yates_shuffle($);
sub read_abundances($$);
sub read_interactions($$$);

# for debugging:
#srand(42);

die "Please provide the abundance file as first argument\n and interaction file as second\n" unless (@ARGV == 2);

##################################################################################################
#					Variables						 #
##################################################################################################

my $abunFile = shift @ARGV; # name of abundance file

#my $interFile = "interactions/protein.links.v9.0.ApisMellifera_honeybee_7460_900.txt"; # interactions
my $interFile = shift @ARGV; # name of interaction file

my $ScoreCutOff = 900;	# cutoff for interaction scores
my $deHubbing = 0;		# set to "1" to switch on dehubbing

##################################################################################################
#					Main Program					 #
##################################################################################################



# read file with abundances into hash:
my %abunHash;
read_abundances($abunFile, \%abunHash);

#read interactions from new yeast file (only interactions above 900)
my %interactions;
read_interactions($interFile, \%interactions, $ScoreCutOff);

#my $pairCounter;
my @abundances = values %abunHash;
my @medians;		# all medians, $medians[0] contains the original (unshuffled) median
##randomization of abundance column
my @sorted_keys = sort { $interactions{$b} <=> $interactions{$a} } keys %interactions;
foreach my $k(0..500) {
	my @deltas;
	
	#---------go through sorted interactions
#	foreach my $pair (sort { $interactions{$b} <=> $interactions{$a} } keys %interactions){
	foreach my $pair (@sorted_keys) {
		my ($prot1, $prot2) = split (/,/, $pair);

		# skip proteins that don't have abundance or have been set to undefined:
		next unless (exists $abunHash{$prot1} and defined $abunHash{$prot1});
		next unless (exists $abunHash{$prot2} and defined $abunHash{$prot2});
		
		my $delta = abs(log($abunHash{$prot1}/$abunHash{$prot2})/log(2)); #to the base of 2
		push (@deltas,$delta);
		
		# for dehubbing, set abundance to undef so the proteins are not reused in this loop:
		if ($deHubbing) {
			$abunHash{$prot1} = undef;
			$abunHash{$prot2} = undef;
		}

	}#END SORTED PROTEIN ARRAY
	if (!@deltas) { 
	    print 'WARNING, no overlap between interactions and abundant proteins!';
	    exit 1;
	}
	my $median = get_median(\@deltas); 
#	print STDERR "median: $median\n";
	push(@medians, $median); #for z-score

	# now shuffle:
	fisher_yates_shuffle(\@abundances);
	
	# reassign randomized abundances to proteins:
	my $index = 0;
	foreach my $prot (keys %abunHash) {
		$abunHash{$prot} = $abundances[$index];
		$index++;
	}
	
}# END 500

# CALCULATE Z-SCORE
if (@medians) {
    my $zscore = sprintf ("%.2f\n", get_zscore(\@medians));
    print $zscore;
}

##################################################################################################
#					Subroutines						#
##################################################################################################

#shuffle an array
sub fisher_yates_shuffle($) {
	my $deck = shift; # $deck is a reference to an array
	my $i = @$deck;
	while ($i--) {
		my $j = int rand ($i+1);
		@$deck[$i,$j] = @$deck[$j,$i];
	}
	return @$deck;
}


#CALCULATE MEDIAN#
sub get_median($) {
	my $stat = Statistics::Descriptive::Full->new();
	$stat->add_data( @{shift @_} );
	# returns the median value of the data:
	return $stat->median(); 
}

#CALCULATE Z-SCORE#
sub get_zscore($) {
	my @all = @{shift @_};
	my $original = shift @all;
	my $stat = Statistics::Descriptive::Full->new();
	$stat->add_data(@all);
	my $mean = $stat->mean();
	my $stdDev = $stat->standard_deviation();
	
	return ($original - $mean) / $stdDev;
}


sub read_abundances($$) {
    my ($filename, $hashref) = @_;
    open (ABUN, $filename) or die "couldn't open file $filename"; # protein \t abundance \n
    while (my $row = <ABUN>) { 
	chomp $row;
	next if ($row =~ m/^\s*#/ or $row =~ m/^\s*$/); # whitespace lines
	# fix for files having mixed tabs/spaces:
	$row =~ s/\s+/ /;
	my @col = split(' ', $row); #split /\t/;
	die "illegal line in $filename:\n$_\n\n" unless (scalar(@col) >= 2);
	my ($protein, $abund) = @col;
	if($abund != 0) {
	    $hashref->{$protein}=$abund; #all proteins with their abundance
	}
    }
    close ABUN;
}

sub read_interactions($$$) {
	my ($filename, $hashref, $cutoff) = @_;
	open (INTER, $filename) or die "couldn't open file $filename"; # protein1 \t protein2 \t score \n
	while (<INTER>) {	
		chomp; 
		next if (/^\s*#/ or /^\s*$/);
		my @col = split /\t/;
	    die "$filename not in correct format: $_\n" unless (scalar(@col) >= 3);
		my ($prot1, $prot2, $score) = @col;
	    next unless ($score >= $cutoff);
	    next if (exists $hashref->{$prot2.",".$prot1});	# don't save inverse relationship
		$hashref->{$prot1.",".$prot2} = $score; #all interactions between two proteins of the file
	}
	close INTER;
}
