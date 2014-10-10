#!/usr/bin/perl -w
##################################################################################################
#
#
#
##################################################################################################

use strict;
use warnings;


##################################################################################################
#					Variables						 #
##################################################################################################

my $file = shift @ARGV; #"/Users/gabriele/testBASH/2weightFiles_allProteins_withMRNA_for3files_SchizosaccharomycesPombe_fissionYeast.txt";

##################################################################################################
#					Main Program					 #
##################################################################################################



open (FILE, $file) or die "couldn't open file $file"; 
my @fileArray=<FILE>; #read file into an array
close FILE;



my $countWeightedFiles=0;
foreach my $line (@fileArray) {
	chomp $line;
	if ($line=~ /## NEW FILE ##/) { $countWeightedFiles++; }
}



#these numbers are the same for all integrated datasets
# number proteins of integrated ds
my $nrProtsIDS=$fileArray[8]; $nrProtsIDS=~ /\[1\] number proteins of integrated dataset:  (.+)$/; my $nrProts=$1;
# total number mRNA
my $nrProtsMRNA=$fileArray[10]; $nrProtsMRNA=~ /\[1\] total number of mRNA:  (.+)$/; my $nrMRNA=$1;
# shared mRNA proteins
my $sharedProtsWithMRNA=$fileArray[15]; $sharedProtsWithMRNA=~ /\[1\] shared mRNA proteins:  (.+)$/; my $sharedProts=$1; 

print "headline____".$nrProts."__".$nrMRNA."__".$sharedProts."\n";


my $line1=3; 	# weight1
my $line2=4; 	# weight2
my $line3=5; 	# weight3
my $line4=6; 	# weight3
my $line5=14;	# correlation	
for (1..$countWeightedFiles) {
		
	my $wantedWeight1=$fileArray[$line1]; $wantedWeight1=~ /^\[1\]\s(\d\.?\d?).*/; my $weight1=$1;
	my $wantedWeight2=$fileArray[$line2]; $wantedWeight2=~ /^\[1\]\s(\d\.?\d?).*/; my $weight2=$1;
	my $wantedWeight3=$fileArray[$line3]; $wantedWeight3=~ /^\[1\]\s(\d\.?\d?).*/; my $weight3=$1;
	my $wantedWeight4=$fileArray[$line4]; $wantedWeight4=~ /^\[1\]\s(\d\.?\d?).*/; my $weight4=$1;
	
	my $correlationMRNA=$fileArray[$line5]; $correlationMRNA=~ /\[1\] correlation: (.+)$/; my $correlation=$1; 
		
	print $weight1."_".$weight2."_".$weight3."_".$weight4."____".$correlation."\n";
	
	$line1+=17;
	$line2+=17;
	$line3+=17;
	$line4+=17;
	$line5+=17;
}










#0 [1] ################# NEW FILE ########################
#1 [1] 
#2 [1] weights of files: 
#3 [1] 1 Brunner
#4 [1] 0.3 SPCbuildJune2010
#5 [1] 0.2 SPCbuildJuly2009
#6 [1] 0.8 DM_BuildSep2011
#7 [1] 
#8 [1] number proteins of integrated dataset:  8901
#9 [1] 
#10 [1] total number of mRNA:  13292
#11 [1] 
#12 [1] CORRELATION
#13 [1] mRNA  -  integratedDataset
#14 [1] correlation: 0.642
#15 [1] shared mRNA proteins:  6707                  
#16 [1] 

#[1] ################# NEW FILE ########################
#[1] 
#[1] weights of files: 
#[1] 1 Brunner
#[1] 0.5 SPCbuildJune2010
#[1] 0.1 SPCbuildJuly2009
#[1] 0.7 DM_BuildSep2011
#[1] 
#[1] number proteins of integrated dataset:  8901
#[1] 
#[1] total number of mRNA:  13292
#[1] 
#[1] CORRELATION
#[1] mRNA  -  integratedDataset
#[1] correlation: 0.642
#[1] shared mRNA proteins:  6707                  
#[1] 











		