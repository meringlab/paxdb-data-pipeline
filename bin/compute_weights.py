#!/usr/bin/python
#
# Input: 2-columns abundance files: [protein name <tab> abundance].
# 
# The script mirrors what Gabi was doing in her correlationDatasetsMRNA_*sh scripts.
#  
# Author: Milan Simonovic <milan.simonovic@imls.uzh.ch>
# Date: 24.09.2014.

# file with dataset names and respective scores
SCORES="../output/v3.1/scores.txt"
OUTPUT="../output/v3.1/weightedFiles/"
INPUT='../input/v3.1/datasets/'
MRNA='../input/v3.1/mrna/'

from DatasetSorter import DatasetSorter
import os
import sys
import glob
import subprocess
from subprocess import CalledProcessError
from os.path import isfile, isdir, join


# TODO weight by tissue! use PaxDbDatasetsInfo() 


def weight(species, mrna, datasets_folder):
    print 'calculating weights for',species,'using',mrna
    outfile=join(OUTPUT, species + '-weightedFiles_mRNAcorrelation.txt')
#    if isfile(outfile):
#        print 'SKIPPING',outfile 
    out_dir = OUTPUT + species + '/'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    sorter = DatasetSorter(SCORES)
    datasets=sorter.sort_datasets(datasets_folder)
    num_files=str(len(datasets))

    opts=['--vanilla -q --slave']
    opts.append('-f weight_withMRNA.R')
    args=['--args', datasets_folder, out_dir, mrna] + datasets

    # all permutations of weights
    weights = [1 for i in range(len(datasets))]

    try:
        # XXX use python-r interface?
        cmd_out = subprocess.check_output(['R'] + opts + args)
        with open(outfile, 'w') as fileout:
            fileout.write(cmd_out)
    except CalledProcessError as ex:
        print('FAILED', ex.output)

def weight_no_mrna(species, datasets_folder):
    print 'calculating weights for',species
    outfile=join(OUTPUT, species + '-weightedFiles_correlation.txt')
#    if isfile(outfile):
#        print 'SKIPPING',outfile 
    out_dir = OUTPUT + species + '/'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    sorter = DatasetSorter(SCORES)
    datasets=sorter.sort_datasets(datasets_folder)
    num_files=str(len(datasets))

    opts=['--vanilla -q --slave']
    opts.append('-f weight_noMRNA.R')
    args=['--args', datasets_folder, out_dir] + datasets

    # all permutations of weights
    weights = [1 for i in range(len(datasets))]

    try:
        # XXX use python-r interface?
        cmd_out = subprocess.check_output(['R'] + opts + args)
        with open(outfile, 'w') as fileout:
            fileout.write(cmd_out)
    except CalledProcessError as ex:
        print('FAILED', ex.output)

def enumerate_species_with_mrna():
""" Only some species have mRNA data. 
 This method will look into the MRNA folder
 and return a list of all species ids extracted
 from files named '<speciesID>.txt'.
"""
    mrna_species = []
    for mrna in glob.glob(MRNA + '*.txt'):
        try:
            speciesID = int(os.path.splitext(os.path.basename(mrna))[0])
            mrna_species.append(str(speciesID))
        except TypeError as e:
            print 'ERROR, bad mrna file (wrong species id):',mrna, e
            continue
    return mrna_species

def integrate_species_with_mrna()
    for species in enumerate_species_with_mrna():
        datasets_folder=join(INPUT,species,'/')
        weight(str(speciesID), mrna, datasets_folder)

    mrna_species=enumerate_species_with_mrna()

def enumerate_species_without_mrna():
''' Enumerates all species from the INPUT folder 
that don't have mRNA data. 
'''
    mrna = enumerate_species_with_mrna():
    non_mrna=[]
    for species in [ d for d in os.listdir(INPUT) if isdir(join(INPUT, d)) ]:
        if species not in mrna_species:
            non_mrna.append(species)

def integrate_species_no_mrna():
    for species in enumerate_species_without_mrna():
        print 'processing species',species
        weight_no_mrna(species, join(INPUT, species))
    # TODO integrate tissue specific datasets separately!
    
if __name__ == "__main__":

    integrate_species_no_mrna()
    integrate_species_with_mrna()
