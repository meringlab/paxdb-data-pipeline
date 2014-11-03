"""
Created on Oct 16, 2014

@author: Milan Simonovic <milan.simonovic@imls.uzh.ch>
"""

import os
import re
import logging

from pip._vendor.distlib.util import cached_property
import psycopg2

from paxdb import config


cfg = config.PaxDbConfig()
STORAGE = '../input/' + cfg.paxdb_version + '/stringdb/'


class Protein(object):
    """
    Represents a StringDb protein 
    """

    _externalIdPattern = re.compile(r'(\d+)\.\w+')

    def __init__(self, internal_id, external_id, preferred_name):
        if type(internal_id) != int or internal_id < 1:
            raise ValueError("internal id must be int > 1")
        if type(external_id) != str or not _externalIdPattern.match(external_id):
            raise ValueError("invalid external id: " + external_id)
        self.id = internal_id
        self.externalId = external_id
        self.name = preferred_name

    @cached_property
    def speciesId(self):
        return int(_externalIdPattern.match(self.externalId).group(1))

    # @cached_property
    def __repr__(self):
        return "Protein(id: {0.id}, externalId: {0.externalId}, name: {0.name})".format(self)

    def __str__(self):
        return "id: {0.id}, externalId: {0.externalId}, name: {0.name}".format(self)


class Species(object):
    def __init__(self, id, name, proteins_list):
        self.id = id
        self.name = name
        self.proteins = proteins_list
        # TODO init mappings (internal-external...)


def load_proteins(species_id):
    proteins = []
    with open(STORAGE + str(species_id) + '-proteins.txt') as file:
        for line in file:
            r = line.split()
            proteins.append(Protein(int(r[0]), r[1], r[2]))
    return proteins

def export_from_postgresql():
    for species in config.SPECIES_IDS:
        export_proteins_to_file(str(species))
        export_protein_names_to_file(str(species))


def export_proteins_to_file(species_id):
    OUTPUT = STORAGE + species_id + '-proteins.txt'
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

def export_protein_names_to_file(species_id):
    '''Load [protein_id, List[protein_name]] from db.
    Note: names are not unique, and two proteins can have the same name.
    Example: 14495 and 13549 (SYNGTS_0697, SYNGTS_1643) have 'hemN' as a name.
    '''
    OUTPUT = '../input/' + cfg.paxdb_version + '/stringdb/' + species_id + '-proteins_names.txt'
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


if __name__ == '__main__':
    proteins = load_proteins(1148)
    print("{0} proteins loaded".format(len(proteins)))
    p1 = proteins[0]
    print("p1: {0}, species: {1} ".format(p1, p1.speciesId))
