#!/usr/bin/python

"""
Take 'direct_mapping' files, convert to external_ids and add internal ids
"""

import re
import sys
import psycopg2
import os

from spectral_counting import keep_only_numbers_filter
import dataset
from config import PaxDbConfig

cfg = PaxDbConfig()

DB_URL=cfg.pg_url
INPUT_DIR='../input/' + cfg.paxdb_version + '/direct_mapping/'
OUTPUT_DIR='../output/' + cfg.paxdb_version + '/'


def run_direct_mapping():
    species_list = sorted(filter(keep_only_numbers_filter, os.listdir(INPUT_DIR)))
    
    for species in species_list:
        spc_dir = os.path.join(INPUT_DIR, species)
        datasets = [ os.path.join(spc_dir, d) for d in os.listdir(spc_dir)]
        dataset.map_datasets(species, datasets)

if __name__ == '__main__':
    run_direct_mapping()
