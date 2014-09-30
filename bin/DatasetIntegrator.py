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
import shutil

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
    def __init__(self, output_file, sorted_datasets, scorer):
        self.datasets = sorted_datasets
        self.scorer = scorer
        self.outfile=output_file
        #    if isfile(outfile):
        #        print 'SKIPPING',outfile 

    def integrate(self):
        """
        The algorithm works like this now:
         1) take first 2 highest-scoring datasets 
         2) assign weights 1, 1
         3) compute integrated datasets by changing weights (of the second dataset only?) from 0.1 to 1.0
         4) pick the weights that have the highest scores
         5) repeat the process for remaining datasets by using the previously computed integrated dataset
        """
        final_weights=[1.0 for i in range(0, len(self.datasets))]
        # I need to reduce over datasets, but python's lambdas look awkward
        
        prev = None
        for k in range(1, len(self.datasets)):
            d1 = prev if prev else self.datasets[k-1]
            d2 = self.datasets[k]
            best_score = sys.float_info.min
            for j in range(10, 0, -1):
                weights = ['1.0', str(j/10.0)]
                try:
                    output = self.scorer.run([d1, d2] + weights)
                    (tmp_integrated, score) = map(lambda x: x.strip(), output.split('\n')) 
                    print(tmp_integrated + ': ' + score)
                    score = float(output.split('\n')[1].strip())
                except:
                    print('FAILED', d1, d2, sys.exc_info()[0])
                    continue

                if best_score < score:
                    best_score = score
                    final_weights[k] = j/10.0 #best_weights[1]
                    # remove before losing the reference!
                    try_to_remove(prev)
                    prev = tmp_integrated
                else:
                    try_to_remove(tmp_integrated)  # temp files, we can clean this up manually...
             
        print('integrated dataset: ' + prev) #move to outputfil
        try:
            shutil.move(prev, self.outfile)
        except:
            print('failed to move',prev,self.outfile)
        return final_weights

def try_to_remove(tmpfile):
    try:
        os.remove(tmpfile)
    except:
        pass

def integrate_species_no_mrna():
    for species in enumerate_species_without_mrna():
        print 'processing species',species
        weight_no_mrna(species, join(INPUT, species))
    # TODO integrate tissue specific datasets separately!

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
    mrna_species.sort()
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


def integrate_species_with_mrna():
    for species in enumerate_species_with_mrna():
        mrna = MRNA + species + '.txt'
        print 'calculating weights for',species
        out_dir = OUTPUT+species+'/'
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        rscript = RScriptRunner('integrate_withMRNA.R', [mrna, out_dir])

        # TODO use PaxDbDatasetsInfo to sort datasets
        ds = join(INPUT,species)
        datasets=[join(ds,d) for d in DatasetSorter(SCORES).sort_datasets(ds)]
        # TODO integrate datasets by organ
        integrator = DatasetIntegrator(OUTPUT+species+'-integrated.txt', datasets, rscript)
        weights = integrator.integrate()
        print('weights: ' + weights)

    
if __name__ == "__main__":
#    integrate_species_no_mrna()
    integrate_species_with_mrna()
