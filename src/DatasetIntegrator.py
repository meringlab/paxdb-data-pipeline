#!/usr/bin/python
#
# This script computes intergrated datasets (per organ 
# weighted average of other datasets). From the PaxDb paper:
# "First, the best-scoring data set is given a weight of 1.0,
# and then for the second-best data set a weight is chosen
#   that maximizes the score for the resulting weighted combination. 
#   This is repeated until the addition of another data set no 
#   longer increases the overall score of the integrated data set. 
#   Occasionally, the addition of a data set would not raise the 
#   overall score, but would bring in additional proteins and thus
#   increase the overall coverage. In this case, it is included 
#   if its quality is deemed acceptable."
#
# Input: 2-columns abundance files: [protein_name <tab> abundance].
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
import shutil
import logging
from multiprocessing import Pool

from paxdb import scores

class RScriptRunner:
    def __init__(self, rscript, args):
        self.opts = ['--vanilla -q --slave', '-f', rscript]
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
            decoded = cmd_out.decode("utf-8")
            #            logging.info("WEIGHT_SCORE_LOG (%s): %s", str(more_args), decoded.strip())
            return decoded
        except CalledProcessError as ex:
            logging.error(self.opts[-1] + self.args, " FAILED: ", str(ex.output))  #can be binary sometimes...
            raise RuntimeError([self.opts[-1]] + self.args + more_args, ex.output, ex)


def score_task(tmp_integrated, interactions_file, weight):
    score = scores.compute_scores(tmp_integrated, interactions_file)[1]  # median
    return (weight, score, tmp_integrated)

class DatasetIntegrator:
    def __init__(self, output_file, sorted_datasets, scorer, bool_max_weights=False):
        self.datasets = sorted_datasets
        self.scorer = scorer
        self.outfile = output_file
        self.bool_max_weights = bool_max_weights
        self.pool = Pool(10)

    def integrate(self, interactions_file):
        final_weights = [1.0] * len(self.datasets)
        # I need to reduce over datasets, but python's lambdas look awkward

        prev = None
        for k in range(1, len(self.datasets)):
            # 1) take first 2 highest-scoring datasets (or the previously computed integrated dataset)
            d1 = prev if prev else self.datasets[k - 1]
            d2 = self.datasets[k]
            logging.debug('integrating %s %s', d1, d2)
            best_score = - (sys.float_info.max - 1)

            # 2) assign weight 1.0 to the first and compute integrated datasets 
            # by changing weights (of the second dataset only) from 0.1 to 1.0
            jobs = []
            for j in range(10, 0, -1):
                weights = ['1.0', str(j / 10.0)]
                output = self.scorer.run([d1, d2] + weights)
                (tmp_integrated, score) = map(lambda x: x.strip(), output.split('\n'))
                if self.bool_max_weights:
                    # might be overwritten for next k, need to keep this file
                    shutil.move(tmp_integrated, tmp_integrated + str(k))
                    prev = tmp_integrated + str(k)
                    break
                jobs.append(self.pool.apply_async(score_task, args=[tmp_integrated, interactions_file, weights[1]]))

            for job in jobs:
                try:
                    (weight, score, tmp_integrated) = job.get()
                    # TODO to calculate the score, need to compute Z scores.. 
                    logging.info("WEIGHT_SCORE [%s, %s at %s]: %s", '&'.join(self.datasets[:k]), d2, weight, score)
                except:
                    logging.error('FAILED %s %s %s', d1, d2, sys.exc_info()[1])
                    continue
                    # 3) pick the weights that have the highest scores
                if best_score < score:
                    best_score = score
                    final_weights[k] = float(weight)  # best_weights[1]
                    # will be overwritten for next k, need to keep this file
                    shutil.move(tmp_integrated, tmp_integrated + str(k))
                    prev = tmp_integrated + str(k)
                else:
                    try_to_remove(tmp_integrated)

        logging.info('integrated dataset: %s, weights: %s', prev, str(final_weights))
        with open(os.path.splitext(self.outfile)[0] + '.weights', 'w') as weights_file:
            for i in range(len(self.datasets)):
                weights_file.write(os.path.basename(self.datasets[i]))
                weights_file.write(': ')
                weights_file.write(str(int(final_weights[i] * 100)))
                weights_file.write('\n')
        try:  #move to outputfile
            shutil.move(prev, self.outfile)
        except:
            logging.error('FAILED to move %s to %s', prev, self.outfile)
        return final_weights

    def __del__(self):
        try:
            self.pool.close()
        except:
            logging.error('failed to close the pool while integrating ', self.outfile)

def try_to_remove(tmpfile):
    try:
        os.remove(tmpfile)
    except:
        pass


def species_mrna(MRNA):
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
            logging.error('bad mrna file (wrong species id): %s %s', mrna, e.message)
            continue
    return species_mrna
