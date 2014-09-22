#!/bin/bash

#INPUT PARAMETER:

#path where are the datasets (abundance files)
path[0]='input/species/511145_Ecoli/datasets/'
#path for created weighted files
path[1]='outputfiles/weightedFiles/511145_Ecoli/'

#mRNA file
path[2]='input/species/511145_Ecoli/mrna/E.coli_mRNA_MarkusW_2004.txt' 

#names of file (exacly) without .txt 
#files MUST NOT have a header 
#dataset with best score first
#name must not start with a number (R can not use it)
#name must not contain a '-' (R can not use it)
namesOfFiles[0]='ecoli2_resolutionCombination_PRIDE.SC'
namesOfFiles[1]='Ecoli_511145_strainK12_PRIDE.SC'
namesOfFiles[2]='ecoli1_HCD_CID_PRIDE.SC'
namesOfFiles[3]='Lu'
namesOfFiles[4]='Lewis_wt'
namesOfFiles[5]='Taniguchi'

outdir="${path[1]}/tmp/"
outfile="${path[1]}/weightedFiles_mRNAcorrelation_for6files_Ecoli.txt"
useRscript='bin/weightAllFiles_allProteins_withMRNA_for6files.R'

rm -r -f $outdir
mkdir -p $outdir

#function
runRscript() {
	allInputParameters=("${path[@]}" "${namesOfFiles[@]}" "${weights[@]}")
	bin/runRscript_withMRNA.sh $useRscript $outdir ${allInputParameters[@]}
}


#weights (same order as namesOfFiles[] )
weights[0]=1    # fixed
weights[1]=0.9  # fixed
weights[2]=1
weights[3]=1
weights[4]=1
weights[5]=1
echo ${weights[@]}

runRscript


############################# change weights #################################

#for one in {1..9}; do
#	weights[1]=$( echo - | awk -v float=$one '{ print float/10}') ;
#	echo ${weights[@]}
	for two in {1..9}; do
		weights[2]=$( echo "$two 10.0"  | awk '{ printf "%1.1f", $1 / $2}') ; 
		echo ${weights[@]}

		for three in {1..9}; do
		weights[3]=$( echo - | awk -v float=$three '{ print float/10}') ;
		echo ${weights[@]}
		
			for four in {1..9}; do
			weights[4]=$( echo - | awk -v float=$four '{ print float/10}') ;
			echo ${weights[@]}
			
				for five in {1..9}; do
				weights[5]=$( echo - | awk -v float=$five '{ print float/10}') ; 
				echo ${weights[@]}
						
				runRscript
				
				done
			done
		done
	done
#done

cat $outdir/* > $outfile

rm -r $outdir
