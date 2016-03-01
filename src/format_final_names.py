#!/usr/bin/python

import os
import glob
from os.path import join
from paxdb.config import PaxDbConfig
import shutil

cfg = PaxDbConfig()
OUTPUT = join('../output', cfg.paxdb_version)
final = join(OUTPUT, 'final')
if not os.path.exists(final):
    os.mkdir(final)

for f in glob.glob(OUTPUT + '/*/*txt'):
    parent = os.path.dirname(f)
    species_id = os.path.split(parent)[1]
    dataset_name = os.path.basename(f)
    if not dataset_name.startswith(species_id):
        dataset_name = species_id + '-' + dataset_name
    elif not dataset_name.startswith(species_id + '-'):
        dataset_name = dataset_name.replace(species_id, species_id + '-')
        dataset_name = dataset_name.replace('-_', '-')

    shutil.copy(f, join(final, dataset_name))
