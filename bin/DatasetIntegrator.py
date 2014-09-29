#!/usr/bin/python
#
# This script computes intergrated datasets (per organ 
# weighted average of other datasets). From the PaxDb paper:
#   "First, the best-scoring data set is given a weight of 1.0, 
#   and then for the second-best data set a weight is chosen 
#   that maximizes the score for the resulting weighted combination. 
#   This is repeated until the addition of another data set no 
#   longer increases the overall score of the integrated data set. 
#   Occasionally, the addition of a data set would not raise the 
#   overall score, but would bring in additional proteins and thus
#   increase the overall coverage. In this case, it is included 
#   if its quality is deemed acceptable."
#
# Input: 2-columns abundance files: [protein name <tab> abundance].
# 
# The script mirrors what Gabi was doing in her weightallFiles_allProteins_*sh scripts.
# 
# Author: Milan Simonovic <milan.simonovic@imls.uzh.ch>
# Date: 24.09.2014.

# file with dataset names and respective scores
SCORES="../output/v3.1/scores.txt"
OUTPUT="../output/v3.1/weightedFiles/"
INPUT='../input/v3.1/datasets/'
MRNA='../input/v3.1/mrna/'

from DatasetSorter import DatasetSorter
from PaxDbDatasetsInfo import DatasetInfo, PaxDbDatasetsInfo
import os
import sys
import glob
import subprocess
from subprocess import CalledProcessError
from os.path import isfile, isdir, join

class RScriptRunner:
    def __init__(self, rscript, args):
        self.opts=['--vanilla -q --slave', '-f', rscript]
        self.args = ['--args'] + args

    def run(self, more_args):
        try:
            # XXX use python-r interface?
            cmd_out = subprocess.check_output(['R'] + self.opts + self.args + more_args)
            return cmd_out
        except CalledProcessError as ex:
            print (self.rscript + " FAILED: " +ex.output)
            raise RuntimeError(self.rscript, ex.output, ex)

class DatasetIntegrator:
    def __init__(self, species, sorted_datasets, output, organ, datasets_folder, scorer):
        self.datasets_folder = datasets_folder
        self.datasets = sorted_datasets
        self.scorer = scorer
        self.outfile=join(output, species + '-' + organ + '-weightedFiles_mRNAcorrelation.txt')
        #    if isfile(outfile):
        #        print 'SKIPPING',outfile 
        self.out_dir = output + species + '/'
        if not os.path.exists(self.out_dir):
            os.mkdir(self.out_dir)

    def integrate(self):
        """
        The algorithm works like this now:
         1) take first 2 highest-scoring datasets 
         2) assign weights 1, 1
         3) compute integrated datasets by changing weights (of the second dataset only?) from 0.1 to 0.9
         4) pick the weights that have the highest scores
         5) repeat the process for remaining datasets by using the previously computed integrated dataset
        """
        final_weights=[]
        # I need to reduce over datasets, but python's lambdas look awkward
        
        prev = None
        for k in range(1, len(self.datasets)):
            d1 = prev if prev else join(self.datasets_folder, self.datasets[k-1])
            d2 = join(self.datasets_folder, self.datasets[k])
            best_weights = None
            best_score = sys.float_info.min
            for i in range(10, 0, -1):
                for j in range(10, 0, -1):
                    weights = [i/10.0, j/10.0]
                    try:
                        score = float(self.scorer.run([d1, d2] + weights))
                    except:
                        print('FAILED', sys.exc_info()[0])
                        continue

                    if best_score < score:
                        best_score = score
                        best_weights = weights
                        # overwrite previous
                        #with open(outfile, 'w') as fileout:
                            #fileout.write(cmd_out)
                        #TODO del prev if not None
                        #  prev = newly_created_integrated_ds.txt
                        prev = "integrData_weighted" + str(weights[0])+'_'+str(weights[1]) + ".txt" #TODO
            if k == 1:
                final_weights = best_weights
            else:
                final_weights.append(best_weights[1])

        return final_weights

        
def integrate_species_with_mrna():
    for species in enumerate_species_with_mrna():
        datasets_folder=join(INPUT,species,'/')
        weight(str(speciesID), mrna, datasets_folder)

def integrate_species_no_mrna():
    for species in enumerate_species_without_mrna():
        print 'processing species',species
        weight_no_mrna(species, join(INPUT, species))
    # TODO integrate tissue specific datasets separately!

def weight(species, mrna, datasets_folder):
    print 'calculating weights for',species,'using',mrna
    outfile=join(OUTPUT, species + '-weightedFiles_mRNAcorrelation.txt')
#    if isfile(outfile):
#        print 'SKIPPING',outfile 
    out_dir = OUTPUT + species + '/'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    opts=['--vanilla -q --slave', '-f integrate_withMRNA.R']
    args=['--args', mrna, out_dir]

# TODO use PaxDbDatasetsInfo to sort datasets
    sorter = DatasetSorter(SCORES)
    datasets=sorter.sort_datasets(datasets_folder)
    # integrate datasets by organ

    #The algorithm works like this now:
    # 1) take first 2 highest-scoring datasets 
    # 2) assign weights 1, 1
    # 3) compute integrated datasets by changing weights (of the second dataset only?) from 0.1 to 0.9
    # 4) pick the weights that have the highest scores
    # 5) repeat the process for remaining datasets by using the previously computed integrated dataset

    final_weights=[]
    # I need to reduce over datasets, but python's lambdas look awkward

    prev = None
    for k in range(1, len(datasets)):
        d1 = prev if prev else join(datasets_folder, datasets[k-1])
        d2 = join(datasets_folder, datasets[k])
        best_weights = None
        best_score = sys.float_info.min
        for i in range(10, 1):
            for j in range(10,1):
                weights = [i/10.0, j/10.0]
                try:
                    # XXX use python-r interface?
                    cmd_out = subprocess.check_output(['R'] + opts + args + [d1, d2] + weights)
                    score = extract_score(cmd_out)
                    if best_score < score:
                        best_score = score
                        best_weights = weights
                        # overwrite previous
                        with open(outfile, 'w') as fileout:
                            fileout.write(cmd_out)
                        #TODO del prev if not None
                        #  prev = newly_created_integrated_ds.txt
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

# TODO weight by tissue! use PaxDbDatasetsInfo() 
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
    return mrna_species #use frozenset?


def enumerate_species_without_mrna():
    ''' Enumerates all species from the INPUT folder 
    that don't have mRNA data. 
    '''
    mrna = enumerate_species_with_mrna()
    non_mrna=[]
    for species in [ d for d in os.listdir(INPUT) if isdir(join(INPUT, d)) ]:
        if species not in mrna:
            non_mrna.append(species)
    return non_mrna

    
if __name__ == "__main__":
    integrate_species_no_mrna()
#    integrate_species_with_mrna()
