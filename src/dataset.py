#!/usr/bin/python3
#
#

import re
from os.path import join
import logging

from split.split import partition
from paxdb.config import PaxDbConfig
from stringdb.repository import StringDbFileRepository


cfg = PaxDbConfig()
DB_URL = cfg.pg_url
OUTPUT_DIR = join('../output/', cfg.paxdb_version)


def map_dataset(species_id, input_file, output_file, stringdb_storage):
    logging.info('loading proteins for %s', species_id)

    repo = StringDbFileRepository(stringdb_storage)
    externalId_id_map = dict()
    for p in repo.load_proteins(species_id):
        externalId_id_map[p.externalId] = p.id

    protein_names = dict()
    names = repo.load_proteins_names(species_id)
    '''
    Hm, this might be a problem, names are not unique, and two
    proteins can have the same name. Example: 14495 and 13549
    (SYNGTS_0697, SYNGTS_1643) have 'hemN' as a name.

    Maybe it's ok because names used as external ids are unique (are they?).
    Here's how to check:
    # get non_unique_names:
    for s in 10090 198214 267671 39947 4896 511145 593117 64091 7227 7955 8364 9606 9823 99287 10116 160490 224308 3702 449447 4932 546414 6239 722438 7460   83332  9031   9615 9913 ; do echo $s; psql  -h db_host -p <port> -d string_10_0 -c "select DISTINCT(p1.protein_name) from items.proteins_names as p1, items.proteins_names as p2 where p1.species_id = $s and p2.species_id = $s and p1.protein_name = p2.protein_name and p1.protein_id != p2.protein_id" | sort > ../output/v4.0/$s/non_unique_names.txt; done
    # for each check if there's an overlap:
    for s in 10090 198214 267671 39947 4896 511145 593117 64091 7227 7955 8364 9606 9823 99287 10116 160490 224308 3702 449447 4932 546414 6239 722438 7460   83332  9031   9615 9913 ; do cd $s; for i in `ls *SC`; do comm -12 <(cat non_unique_names.txt | sort) <(cat $i | cut -f 1 | sort); done; cd .. ; done
    '''
    for id in names:
        for name in names[id]:
            protein_names[name] = id

    # protein_names = load_protein_names(species_id)

    mapper = DatasetMapper(species_id, externalId_id_map, protein_names)
    mapper.map_dataset(input_file, output_file)


class DatasetMapper:
    '''Maps to StringDb protein internal ID using protein external ID 
    instead of protein alias table (makes the mapping more strict).
    For the remaining un-mapped identifiers it falls back to the protein 
    names table, whilst checking for conflicts (name -> mapped_external_id). 
    '''

    def __init__(self, species_id, externalId_id_map, protein_names):
        self.species = str(species_id)
        self.externalId_id_map = externalId_id_map
        self.id_externalId_map = {v: k for k, v in externalId_id_map.items()}
        self.protein_names = protein_names

    def map_dataset(self, f, output_file):
        logging.info('mapping %s', f)
        entries = read_entries_from_file(f) if isinstance(f, str) else read_entries(f)
        mapped = self.map_to_external_ids(entries)
        self.write_mapping(output_file, f, mapped, entries)

    def map_to_external_ids(self, entries):
        predicate = lambda k: to_external_id(self.species, k) in self.externalId_id_map
        (mapped_ids, unmapped_ids) = partition(predicate, entries)
        mapped = dict((mid, to_external_id(self.species, mid)) for mid in mapped_ids)
        external_ids = set(mapped.values())
        unmapped = []
        for identifier in unmapped_ids:
            if not identifier in self.protein_names:
                unmapped.append(identifier)
                continue
            external_id = self.id_externalId_map[self.protein_names[identifier]]
            if external_id in external_ids:
                logging.warn('%s mapped to the existing external id %s', identifier, external_id)
                continue
            external_ids.add(external_id)
            mapped[identifier] = external_id

        if len(unmapped) > 0:
            logging.warn('no mappings for %s proteins: %s', len(unmapped), list(unmapped)[:10])
        return mapped

    def write_mapping(self, outfile, header_from, mapped, entries):
        logging.info('output to %s', outfile)
        out = open(outfile, "w")

        # write header
        with  open(header_from, "r") as open_file:
            for line in open_file.readlines():
                if (line.startswith('#')):
                    out.write(line)
                else:
                    break
        for identifier in mapped:
            # internal id
            out.write(str(self.externalId_id_map[mapped[identifier]]))
            out.write('\t')
            # external id
            out.write(mapped[identifier])
            out.write('\t')
            # rest
            out.write(entries[identifier])
            out.write('\n')
        out.close()


def to_external_id(species_id, identifier):
    '''turn identifier into external id.
    example: (511145, "b1260") -> "511145.b1260"
    '''
    return str(species_id) + '.' + identifier


def read_entries_from_file(filepath):
    with open(filepath, "r") as open_file:
        return read_entries(open_file)


def read_entries(filelike):
    '''reads lines from the iterable and creates a map: the first column (tab separated) 
    is the key, and the reminder (as a string) is the value
    '''
    entries = {}
    for line in filelike.readlines():
        if re.match('\\s*#.*', line):  # TODO another loop while lines startwith '#'
            continue
        rec = re.sub("\\s+", " ", line.strip()).split(" ")
        if len(rec) < 2:
            continue
        entries[rec[0]] = '\t'.join(rec[1:])
    print(str(len(entries)) + ' entries read')
    return entries

