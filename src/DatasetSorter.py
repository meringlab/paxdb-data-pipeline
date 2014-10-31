#!/usr/bin/python
#
# Input: 2-columns scores file: [dataset name <tab> score].
# 
# Author: Milan Simonovic <milan.simonovic@imls.uzh.ch>
# Date: 25.09.2014.

import os
from os import listdir
from os.path import isfile, join
import sys


class DatasetSorter():
    def __init__(self, scores_file):
        # is it ok to call methods from __init__?
        self._scores = self._read_scores(scores_file)

    def _read_scores(self, scores_file):
        print('reading scores from', scores_file)
        with open(scores_file) as f:
            scores = dict()
            for line in f:
                r = [r.strip() for r in line.split('\t') if len(r.strip()) > 0]
                if len(r) > 1:
                    # without extension since it's easier than keepin track if its SC,txt, out...
                    scores[os.path.splitext(r[0])[0]] = float(r[1])
        if len(scores) == 0:
            raise Exception('no scores found in ' + scores_file)
        return scores

    def _get_dataset_score(self, d):
        name = os.path.splitext(d)[0]
        if name in self._scores:
            return self._scores[name]
        print('WARN, no score for', d)
        return -sys.maxsize - 1  # just put it at the end

    def sort_datasets(self, folder):
        datasets = self.read_datasets(folder)
        return self.sort(datasets)

    def sort(self, datasets):
        by_score = sorted(datasets, key=lambda d: self._get_dataset_score(d))
        by_score.reverse()
        return by_score

    def read_datasets(self, folder):
        datasets = [f for f in listdir(folder) if isfile(join(folder, f))]
        if len(datasets) == 0:
            raise Exception('no datasets found in ' + folder)
        return datasets


if __name__ == "__main__":
    from config import PaxDbConfig

    cfg = PaxDbConfig()

    s = DatasetSorter('../output/' + cfg.paxdb_version + '/scores.txt')
    d = s.sort_datasets('../input/' + cfg.paxdb_version + '/spectral_counting/511145/')
    print(d)
