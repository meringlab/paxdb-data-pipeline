#!/usr/bin/python

"""
Take 'direct_mapping' files, convert to external_ids and add internal ids
"""

import re
import sys
import psycopg2
import os

from spectral_counting import keep_only_numbers_filter
from config import PaxDbConfig

cfg = PaxDbConfig()

DB_URL=cfg.pg_url
INPUT_DIR='../input/' + cfg.paxdb_version + '/direct_mapping/'
OUTPUT_DIR='../output/' + cfg.paxdb_version + '/'


def map_file(species_id, f, ids, ids2, ides):
    print('species {0}, mapping file {1}'.format(species_id,f))
    inp = open(f, "r")
    out = open(OUTPUT_DIR + os.path.basename(f),"w")
    print 'output to',out.name
    remains = {} # this is for storing the no mapping entries
    mapped = {}
    for line in inp.readlines():
        if (line.startswith('#')):
            out.write(line)
        else:
            rec = re.sub("\\s+"," ", line.strip()).split(" ")
            if len(rec) < 2:
                continue
	    pro_ex_id = str(species_id + "." + rec[0])
            if pro_ex_id not in ids:
                sys.stderr.write(pro_ex_id + " in protein_external_id " + f + ": no mapping\n")
                remains[rec[0]] = rec[1]
            else:
            	mapped[pro_ex_id] = ids[pro_ex_id]
                newline = str(ids[pro_ex_id]) + "\t" + pro_ex_id + '\t' +  rec[1] +"\n"
                out.write(newline)

    for k, v in remains.iteritems():
	    if k not in ids2:
		    sys.stderr.write(k + " in protein " + f + ": no mapping\n")
	    else:
		    if ides[ids2[k]] not in mapped:
			    newline = str(ids2[k]) + "\t" + ides[ids2[k]]+ '\t' +  v +"\n"
			    out.write(newline)
			    mapped[ides[ids2[k]]] = ids2[k]
		    else:
			    sys.stderr.write(k + " mapped to the exist internal ID " + ides[ids2[k]] + "\n")
    # bugfix, don't forget to close the file before continuing the iteration:
    inp.close()
    out.close()

def load_ids(species_id):
        dbcon = psycopg2.connect(DB_URL)
        cur = dbcon.cursor()
        cur.execute("select protein_id, protein_external_id from items.proteins where species_id in (" + species_id + ")")
        ids = dict()
        ides = dict()
        #print(cur.fetchmany(5))
        for el in cur:
            ids[el[1]] = el[0]
            ides[el[0]] = el[1]
        #    print("\t".join(map(str, el)))
        cur.close()
        dbcon.close()
        return (ids, ides)

def load_names(species_id):
        dbcon2 = psycopg2.connect(DB_URL)
        cur2 = dbcon2.cursor()
        cur2.execute("select protein_id, protein_name from items.proteins_names where species_id in (" + species_id + ")")
        ids2 = dict()
        #print(cur.fetchmany(5))
        for el in cur2:
            ids2[el[1]] = el[0]
        #    print("\t".join(map(str, el)))
        cur2.close()
        dbcon2.close()
        return ids2

def map_species(species_id, files):
        print('mapping species {0}'.format(species_id))
        (ids, ides) = load_ids(species_id)
        ids2 = load_names(species_id)

        for f in files:
            map_file(species_id, f, ids, ids2, ides)

def run_direct_mapping():
    species_list = sorted(filter(keep_only_numbers_filter, os.listdir(INPUT_DIR)))
    
    for species in species_list:
        spc_dir = os.path.join(INPUT_DIR, species)
        files = [ os.path.join(spc_dir, d) for d in os.listdir(spc_dir)]
        map_species(str(species), files)

if __name__ == '__main__':
    run_direct_mapping()
