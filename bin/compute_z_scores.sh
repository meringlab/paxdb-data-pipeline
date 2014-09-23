#!/bin/bash
#
# Computes z-scores for all datasets. Requires libstatistics-descriptive-perl package installed (ubuntu)!
# 
#  For each dataset:
#   runs PaxDbScore*.pl 3 times, then takes the median
#
# Input files: 
#  1) abundance file: eris species/{specie}/datasets/file.SC (ie ../species/9615/GPM_2012_09_Canis_familiaris.SC.txt)
#  2) interaction file: eris interactions/protein.links.v9.0.{species}_ncbi_900.txt (ie ../interactions/protein.links.v9.0.CanisFamiliaris_dog_9615_900.txt 
# 
# Output files:
#  * for each abundance file - a new one with zscores_ prepended to the name (ie zscores_file.SC)
# 
####
# Notes:
#
# Some input files had rows with only a single field (protein, no counts).
# To check if there are any use this command:
#   for i in *txt; do echo $i; awk '{ if (NF < 2) {printf ("%s\n", $1);exit;}}' $i; done
#
# To filter these lines out use this command:
#
#   awk '{ if (NF >= 2) printf ("%s\t%s\n", $1, $2);}' troublesome_file.txt > tmp; mv tmp troublesome_file.txt
#
# as a test I compared lines in troublesome_file.txt with 
#   $(cat troublesome_file.txt  | cut -f 2 | sort | grep -v '^$' | wc -l) 
# and looks like it works fine
# 
# 
# Originally written by Gabi
# 
echo "started processing, $(date)"

for speciesId in 10090 10116 1148 160490 198214 224308 267671 3702 39947 449447 4896 4932 511145 546414 593117 6239 64091 722438 7227 7460 7955 83332 8364 9031 9606 9615 9823 9913 99287; 
do
    echo "processing species $speciesId"
    interactions="$(ls ../input/v3.0/interactions/protein.links.v9.0.*_"$speciesId"_900.txt)"
    pathIN="../input/v3.1/$speciesId/"
    pathOUT="../output/v3.1/$speciesId/"
    mkdir -p $pathOUT

# can't use for f in `find ` because some files have whitespace so:
#    for abundance_file in `find $pathIN -type f`;
    find $pathIN -type f -print0 | while read -d $'\0' abundance_file
    do
	echo -n "abundance_file: $abundance_file "
	#outputfile=${1/$pathIN/zscores_} # it's just zscores_ prepended to base name:
	bname=`basename "$abundance_file"`
	outputfile=(zscores_"$bname") 	# to correctly handle filenames with whitespace:
	outofile=${outputfile//\//_}
	outfile="$pathOUT$outofile"
	if [ -a "$outfile" ];
	then
	    echo "output file exists, SKIPPING.."
	    continue
	fi
	echo
	echo "output: $outfile"
	
	for i in {1..3}; do
	    score=$(/usr/bin/perl -w PaxDbScore_delta.pl "$abundance_file" "$interactions")
	    if [ $? -ne 0 ]; 
	    then
		echo "ERRORS, skipping this file: $score"
		break 2 # go to next abundance_file
	    fi
	    array[$i]=$score
	    echo ${array[$i]}
	done
	
	echo -n '# '  >> "$outfile" # no newline
	date +"%Y-%m-%d">> "$outfile"
	echo -n '# '  >> "$outfile"
	echo 'delta' >> "$outfile"
	dataset=${1//*\//}
	echo -n '# '  >> "$outfile"
	echo $dataset >> "$outfile"
	
	for l in ${array[@]}; do
	    echo $l 
	done | sort >> "$outfile"

	# DEHUBBING is outdated!!!!
	#####         #####
	#####dehubbing#####
	#####         #####
	#echo DEHUBBING
	#
	#
	#for k in {1..3}; do
	#
	#	variable=$(/usr/bin/perl -w PaxDbScore_delta_dehubbing.pl $1 $2) #abundance file #interaction file
	##	push variable to array
	#	array_dehub[$k]=$variable #'\n'
	#	echo ${array_dehub[$k]}  #output on terminal
	#done
	#
	#
	#cd /home/gabi/PaxDb/outputfiles/
	#
	#
	#echo -n '# '  >> $outfile # no newline
	#echo 'dehubbing' >> $outfile
	#
	#echo ${array_dehub[1]} >> $outfile 
	#echo ${array_dehub[2]} >> $outfile
	#echo ${array_dehub[3]} >> $outfile
	#
	#for m in ${array_dehub[@]}; do
	#	echo $m 
	#done | sort >> $outfile
	
    done
# to cleanup failed files:
#for i in */*; do num_lines=$(cat $i  | wc -l); if [ $num_lines -lt 4 ]; then rm $i; fi; done
    
done

echo "done processing, $(date)" 
