import logging
import os

import psycopg2

from paxdb import config
from stringdb.domain import Protein


cfg = config.PaxDbConfig()
STORAGE_LOCATION = '../../input/' + cfg.paxdb_version + '/stringdb/'


class StringDbFileRepository(object):
    def __init__(self, storage_location=STORAGE_LOCATION):
        self.storage_dir = storage_location
        self._init()

    def _init(self):
        for species in config.SPECIES_IDS:
            self._export_proteins_to_file(str(species))
            self._export_protein_names_to_file(str(species))


    def _export_proteins_to_file(self, species_id):
        OUTPUT = self.storage_dir + species_id + '-proteins.txt'
        if os.path.isfile(OUTPUT):
            return
        logging.debug('loading protein for %s', species_id)
        dbcon = psycopg2.connect(cfg.pg_url)
        # to properly handle unicode (see http://initd.org/psycopg/docs/usage.html#unicode-handling):
        dbcon.set_client_encoding('UTF8')
        with dbcon.cursor() as cur:
            cur.execute("SELECT protein_id, protein_external_id, preferred_name "
                        "FROM items.proteins "
                        "WHERE species_id=%s",
                        (species_id,))
            with open(OUTPUT, 'w') as file:
                for p in cur:
                    file.write("{0}\t{1}\t{2}\n".format(p[0], p[1], p[2]))


    def _export_protein_names_to_file(self, species_id):
        '''Load [protein_id, List[protein_name]] from db.
        Note: names are not unique, and two proteins can have the same name.
        Example: 14495 and 13549 (SYNGTS_0697, SYNGTS_1643) have 'hemN' as a name.
        '''
        OUTPUT = self.storage_dir + species_id + '-proteins_names.txt'
        if os.path.isfile(OUTPUT):
            return
        logging.debug('loading proteins names for %s', species_id)
        ids = dict()

        with psycopg2.connect(cfg.pg_url) as dbcon:
            # to properly handle unicode (see http://initd.org/psycopg/docs/usage.html#unicode-handling):
            dbcon.set_client_encoding('UTF8')
            with dbcon.cursor() as cur:
                cur.execute("SELECT protein_id, protein_name "
                            "FROM items.proteins_names "
                            "WHERE species_id=%s", (species_id,))
                for el in cur:
                    if not el[0] in ids:
                        ids[el[0]] = []
                    ids[el[0]].append(el[1])
        with open(OUTPUT, 'w') as file:
            for id in ids:
                file.write(str(id))
                file.write('\t')
                # assuming no name contains '\t' character!
                names = ids[id]
                file.write('\t'.join(filter(lambda n: not '\t' in n, names)))
                file.write('\n')


    def load_proteins(self, species_id):
        proteins = []
        with open(self.storage_dir + str(species_id) + '-proteins.txt') as file:
            for line in file:
                r = line.split()
                proteins.append(Protein(int(r[0]), r[1], r[2]))
        return proteins

    def load_proteins_names(self, species_id):
        names = dict()
        with open(self.storage_dir + str(species_id) + '-proteins_names.txt') as file:
            for line in file:
                r = line.split()
                names[int(r[0])] = [n.strip() for n in r[1:]]
        return names

if __name__ == '__main__':
    import logger

    logger.configure_logging(loglevel='DEBUG')
    repository = StringDbFileRepository()
    proteins = repository.load_proteins(1148)
    print("{0} proteins loaded".format(len(proteins)))
    p1 = proteins[0]
    print("p1: {0}, species: {1} ".format(p1, p1.speciesId))
    names = repository.load_proteins_names(1148)
    print("{0} names: {1} ".format(p1.externalId, ','.join(names[p1.id])))