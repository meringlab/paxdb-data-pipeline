#!/bin/bash

interaction='input/interactions/protein.links.v9.0.Ecoli_511145_900.txt'
path='outputfiles/weightedFiles/511145_Ecoli/'
outputfile="$path/tmp/all_511145_Ecoli"

# gabi originally had this to integrData_weighted_1_0.9_*,
# why would she calculate all possible weights but then only
# look at files where the weights for 2 datasets are fixed
# (they happen to be ecoli2_resolutionCombination_PRIDE.SC
# and Ecoli_511145_strainK12_PRIDE.SC)? 
# This is the only species where she does this, all other look at all computed files


fileArray=$(ls $path | grep '^integrData_weighted_1_0.9_*')
#fileArray=$(ls $path | grep '^integrData_weighted_1_1_1*')
for k in $fileArray; do
    abundance=${k/#/$path}
    for i in {1..3}; do
	tmpfile=$outputfile-$k-$i
	perl -w bin/PaxDbScore_delta.pl $abundance $interaction > $tmpfile 
    done
done
