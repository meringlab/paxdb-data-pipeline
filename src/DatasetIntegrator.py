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

import os
import sys
import glob
import subprocess
from subprocess import CalledProcessError
from os.path import isfile, join
import shutil
import logging
import logger
from config import PaxDbConfig
from DatasetSorter import DatasetSorter
from PaxDbDatasetsInfo import PaxDbDatasetsInfo

cfg = PaxDbConfig()

SCORES=join('../output/', cfg.paxdb_version,'scores.txt')
OUTPUT=join('../output/', cfg.paxdb_version,"weightedFiles/")
INPUT=join('../input/', cfg.paxdb_version,"datasets/")
MRNA=join('../input/', cfg.paxdb_version,"mrna/")


class RScriptRunner:
    def __init__(self, rscript, args):
        self.opts=['--vanilla -q --slave', '-f', rscript]
        self.args = ['--args'] + args
        logging.debug('opts: ' + str(self.opts + args))

    def __repr__(self):
        return self.opts[-1]

    def __str__(self):
        return self.opts[-1] + str(self.args)

    def run(self, more_args):
        try:
            # XXX use python-r interface?
            logging.debug('args: ' + str(more_args))
            cmd_out = subprocess.check_output(['R'] + self.opts + self.args + more_args)
            return cmd_out
        except CalledProcessError as ex:
            logging.error(self.rscript, " FAILED: ", ex.output)
            raise RuntimeError(self.rscript, ex.output, ex)

class DatasetIntegrator:
    def __init__(self, output_file, sorted_datasets, scorer):
        self.datasets = sorted_datasets
        self.scorer = scorer
        self.outfile=output_file

    def integrate(self):
        if isfile(self.outfile):
            print('SKIPPING, already computed', self.outfile)
            return

        final_weights=[1.0] * len(self.datasets)
        # I need to reduce over datasets, but python's lambdas look awkward
        
        prev = None
        for k in range(1, len(self.datasets)):
            # 1) take first 2 highest-scoring datasets (or the previously computed integrated dataset)
            d1 = prev if prev else self.datasets[k-1]
            d2 = self.datasets[k]
            logging.debug('integrating %s %s',d1,d2)
            best_score = sys.float_info.min

            # 2) assign weight 1.0 to the first and compute integrated datasets 
            # by changing weights (of the second dataset only?) from 0.1 to 1.0
            for j in range(10, 0, -1):
                weights = ['1.0', str(j/10.0)]
                try:
                    output = self.scorer.run([d1, d2] + weights)
                    # TODO to calculate the score, need to compute Z scores.. 
                    (tmp_integrated, score) = map(lambda x: x.strip(), output.split('\n')) 
                    logging.info("%s: %s", tmp_integrated, score)
                    score = float(output.split('\n')[1].strip())
                except:
                    logging.error('FAILED %s %s %s', d1, d2, sys.exc_info()[0].message)
                    continue
                    # 3) pick the weights that have the highest scores
                if best_score < score:
                    best_score = score
                    final_weights[k] = j/10.0 #best_weights[1]
                    # will be overwritten for next k, need to keep this file
                    shutil.move(tmp_integrated, tmp_integrated+str(k))
                    prev = tmp_integrated + str(k)
                else:
                    try_to_remove(tmp_integrated)
             
        logging.info('integrated dataset: %s', prev)
        logging.info(zip(self.datasets, [str(int(w*100))+'%' for w in final_weights]))
        try: #move to outputfile
            shutil.move(prev, self.outfile)
        except:
            logging.error('FAILED to move %s to %s',prev,self.outfile)
        return final_weights

def try_to_remove(tmpfile):
    try:
        os.remove(tmpfile)
    except:
        pass

def species_mrna():
    """ Only some species have mRNA data. This method will look into
    the MRNA folder  and return a map with species ids as keys, extracted 
    from files named '<speciesID>.txt'.
    """
    species_mrna = dict()
    for mrna in glob.glob(MRNA + '*.txt'):
        try:
            speciesID = int(os.path.splitext(os.path.basename(mrna))[0])
            species_mrna[str(speciesID)] = mrna
        except TypeError as e:
            logging.error('bad mrna file (wrong species id): %s %s',mrna, e.message)
            continue
    return species_mrna

def integrate_species():
    info = PaxDbDatasetsInfo()
    mrna = species_mrna()
    for species in info.datasets.keys():
        for organ in info.datasets[species].keys():
            if len(info.datasets[species][organ]) < 2:
                continue
            
            integrated = [d.dataset for d in info.datasets[species][organ] if d.integrated][0]
            out_file = join(OUTPUT, integrated)
            if isfile(out_file):
                logging.info('SKIPPING %s, already integrated',species)
                continue

            logging.info('calculating weights for %s, tissue %s',species, organ)

            out_dir = OUTPUT+species+'/'
            if not os.path.exists(out_dir):
                os.mkdir(out_dir)
            
            if species in mrna:
                mrna_folder = MRNA + species + '.txt'
                # TODO make R script accept args and pass mrna
                rscript = RScriptRunner('integrate_withMRNA.R', [mrna_folder, out_dir])
            else:
                rscript = RScriptRunner('integrate.R', [out_dir])
            # TODO use PaxDbDatasetsInfo to sort datasets
            by_organ = [os.path.splitext(d.dataset)[0] for d in info.datasets[species][organ]]
            all_datasets = [d for d in DatasetSorter(SCORES).sort_datasets(join(INPUT,species))]
            sorted_by_organ = [d for d in all_datasets if os.path.splitext(d)[0] in by_organ]
            if len(by_organ)-1 != len(sorted_by_organ):
                logging.warn('some datasets are missing listed: %s, scored: %s', 
                            str(by_organ), str(sorted_by_organ))

            datasets=[join(INPUT,species,d) for d in sorted_by_organ]
            integrator = DatasetIntegrator(out_file, datasets, rscript)
            weights = integrator.integrate()
            logging.info(species + ' weights: ' + ','.join([str(w) for w in weights]))

if __name__ == "__main__":
    logger.configure_logging('integrator.log')
    integrate_species()
