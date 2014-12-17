#!/usr/bin/python
# TODO check if input data is valid

import os
import glob
import subprocess
import logging
from os.path import join
from paxdb.config import PaxDbConfig
from stringdb.repository import StringDbFileRepository
import logger
import stringdb


def check_for_duplicate_entries():
    pass


def compile_java_if_necessary():
    for java in glob.glob('*.java'):
        if not os.path.exists(java.replace('.java', '.class')):
            try:
                cmd_out = subprocess.check_output(['javac', java])
            except:
                logging.error('failed to compile %s: %s', java, cmd_out)


def export_from_postgresql():
    cfg = PaxDbConfig()
    storage = '../input/' + cfg.paxdb_version + '/stringdb/'
    repo = StringDbFileRepository(storage)
    proteins = repo.load_proteins(1148)
    assert (len(proteins) > 100)


# # test if datasetsInfo is up-to-date
def datastsInfo_uptodate(datasetsInfo, INPUT, OUTPUT):
    datasetsBySpecies = dict()
    for f in glob.glob(INPUT + '*/*'):
        species_id = os.path.split(os.path.dirname(f))[1]
        dataset_name = os.path.splitext(os.path.basename(f))[0]
        try:
            datasetsInfo.get_dataset_info(species_id, dataset_name)
        except:
            logging.warning('no info for dataset {0}'.format(f))
        if species_id not in datasetsBySpecies:
            datasetsBySpecies[species_id] = set()
        datasetsBySpecies[species_id].add(dataset_name)

    for species_id in datasetsInfo.datasets:
        if species_id not in datasetsBySpecies:
            logging.error('species {0} missing'.format(species_id))
            continue
        by_organ = datasetsInfo.datasets[species_id]
        for organ in by_organ:
            for d in by_organ[organ]:
                if d.integrated:
                    continue
                dataset_name = os.path.splitext(d.dataset)[0]
                if dataset_name not in datasetsBySpecies[species_id]:
                    logging.error('dataset {0} missing for {1}'.format(dataset_name, species_id))

    for species in datasetsInfo.datasets.keys():
        for organ in datasetsInfo.datasets[species].keys():
            if len(datasetsInfo.datasets[species][organ]) < 2:
                continue
            integrated_dataset = [join(OUTPUT, species, os.path.splitext(d.dataset)[0] + '.integrated') for d in
                                  datasetsInfo.datasets[species][organ] if d.integrated]
            if len(integrated_dataset) == 0:
                # not specified in the data info doc, so just make up one for now
                logging.error('integrated dataset missing {0}-{1}.integrated'.format(species, organ))



if __name__ == '__main__':
    logger.configure_logging()
    export_from_postgresql()
    check_for_duplicate_entries()
    compile_java_if_necessary()
