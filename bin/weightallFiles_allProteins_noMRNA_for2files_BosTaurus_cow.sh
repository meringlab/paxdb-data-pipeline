#!/bin/bash

#INPUT PARAMETERS:
#path where are the datasets (abundance files)
path[0]='input/species/9913_BosTaurus_cow/datasets/'
#path for created weighted files
path[1]='outputfiles/weightedFiles/9913_BosTaurus_cow/'
mkdir -p ${path[1]} 

#names of file (exacly) without .txt 
#files MUST NOT have a header 
#dataset with best score first
#name must not start with a number (R can not use it)
#name must not contain a '-' (R can not use it)
namesOfFiles[0]='cow_atlas_build_320.SC'
namesOfFiles[1]='GPM_2012_09_Bos_taurus.SC'

# gabi's code says useRscript='weightAllFiles_allProteins_withMRNA_for2files.R' but it's wrong
useRscript='weightAllFiles_allProteins_noMRNA_for2files.R'

#function
runRscript() {
	allInputParameters=("${path[@]}" "${namesOfFiles[@]}" "${weights[@]}")
	bin/runRscript.sh bin/$useRscript ${allInputParameters[@]}
}

calcWeights() {

#weights (same order as namesOfFiles[] )
    weights[0]=1
    weights[1]=1
    echo ${weights[@]}

    runRscript
# change weights
    for l in {1..9}; do
	weights[1]=$( echo - | awk -v float=$l '{ print float/10}') ;
	echo ${weights[@]}
	runRscript
    done
}

calcWeights


