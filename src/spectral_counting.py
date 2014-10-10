#!/usr/bin/python

# this is for the spectral counting calculating protein abundance
# and raw spectral count and mapped peptide
#

import sys
import os
import shlex
import subprocess
import re
import psycopg2
from glob import glob
from os.path import isfile, isdir, join
from config import PaxDbConfig

cfg = PaxDbConfig()

FASTA='../input/'+cfg.paxdb_version+'/spectral_counting/fasta'
FASTA_VER=cfg.fasta_version #'10.0'
INPUT='../input/'+cfg.paxdb_version+'/spectral_counting/'
OUTPUT='../output/'+cfg.paxdb_version+'/'

def run_spectral_counting():
    input_folders = sorted(filter(keep_only_numbers_filter, os.listdir(INPUT)))
    for species_id in input_folders:
        spectral_count_species(species_id)
    
def keep_only_numbers_filter(elem):
    if not isinstance(elem, str):
        raise ValueError('accepting strings only! ' +type(elem))
    return elem.isdigit()

def spectral_count_species(species_id):
    if not os.path.exists(get_output_dir(species_id)):
        os.mkdir(get_output_dir(species_id))

    path = INPUT + species_id + '/'
    protein_ids_map = load_ids(species_id)

    for f in [join(path, f) for f in os.listdir(path)]:
        print 'processing',pepfile
        scfile = calculate_abundance_and_raw_spectral_counts(species_id, pepfile)
        # map_peptide(species_id, pepfile) #where is this used?
        add_string_internalids_column(species_id, scfile, protein_ids_map)

def get_output_dir(species):
    return OUTPUT+species + '/'

def get_filename_no_extension(filename):
    base = os.path.basename(filename)
    return os.path.splitext(base)[0]

def calculate_abundance_and_raw_spectral_counts(speid, pepfile):
    """
    takes peptide counts and fasta file and produces protein abundance + counts
    """
    scfile = get_output_dir(speid) + get_filename_no_extension(pepfile) + ".SC"
    if os.path.isfile(scfile):
        return

    cmd = "java -Xms512m ComputeAbundanceswithSC -s {0} '{1}' '{2}/fasta.v{3}.{0}.fa'"
    cmd = cmd.format(speid, pepfile, FASTA, FASTA_VER)
    with open(scfile, "w") as ofile:
        subprocess.Popen(shlex.split(cmd), stdout = ofile).wait()
    return scfile

def map_peptide(speid, pepfile):
    """
    maps peptides to proteins: takes peptide counts and fasta file 
    and produces protein/peptide/counts
    """
    out = get_output_dir(speid)+ get_filename_no_extension(pepfile) + "_peptide.txt"
    cmd  = "java -Xms512m ComputeAbundancesMappep -p 4 -s {0} '{1}' '{2}/fasta.v{3}.{0}.fa' | tee > {4} "
    cmd  = cmd.format(speid, pepfile, FASTA, FASTA_VER, out)
    if os.path.isfile(out):
        return
    with open(out, "a") as ofile:
        ofile.write("#string_external_id	peptide_sequence	spectral_count\n")
        ofile.flush()
        subprocess.Popen(shlex.split(cmd), stdout = ofile).wait()

#TODO rename to load_protein_names_ids_map
def load_ids(species_id):
    '''Load [id, protein_name] from db.
    Hm, this might be a problem, names are not unique, and two 
    proteins can have the same name. Example: 14495 and 13549
    (SYNGTS_0697, SYNGTS_1643) have 'hemN' as a name.

    Maybe it's ok because names used as external ids are unique (are they?).    
    Here's how to check:
    # get non_unique_names:
    for s in 10090 198214 267671 39947 4896 511145 593117 64091 7227 7955 8364 9606 9823 99287 10116 160490 224308 3702 449447 4932 546414 6239 722438 7460   83332  9031   9615 9913 ; do echo $s; psql  -h db_host -p <port> -d string_10_0 -c "select DISTINCT(p1.protein_name) from items.proteins_names as p1, items.proteins_names as p2 where p1.species_id = $s and p2.species_id = $s and p1.protein_name = p2.protein_name and p1.protein_id != p2.protein_id" | sort > ../output/v3.1/$s/non_unique_names.txt; done
    # for each check if there's an overlap:
    for s in 10090 198214 267671 39947 4896 511145 593117 64091 7227 7955 8364 9606 9823 99287 10116 160490 224308 3702 449447 4932 546414 6239 722438 7460   83332  9031   9615 9913 ; do cd $s; for i in `ls *SC`; do comm -12 <(cat non_unique_names.txt | sort) <(cat $i | cut -f 1 | sort); done; cd .. ; done
    '''
    print('loading proteins names for ' + species_id)
    dbcon = psycopg2.connect(cfg.pg_url)
    cur = dbcon.cursor()
    cur.execute("SELECT protein_id, protein_name FROM items.proteins_names WHERE species_id=" + species_id)
    ids = dict()
    #print(cur.fetchmany(5))
    for el in cur:
        ids[el[1]] = el[0]
        #    print("\t".join(map(str, el)))
    cur.close()
    dbcon.close()
    return ids

def add_string_internalids_column(species_id, SCfile, ids):
    """
    adds another column with STRINGDB internal ids
    """
    if SCfile == None:
        return
    print('adding string internal ids')
    #print(",".join(str(x) + " " + str(ids[x]) for x in ids.keys()[:5]))
    if os.path.isfile(SCfile +'.out'):
        return

    with open(SCfile, "r") as inp:
        with open(SCfile + ".out","w") as out:
            for line in inp.readlines():
                if (line.startswith('#')):
                    out.write(line)
                else:
                    rec = re.sub("\\s+", " ", line.strip()).split(" ")
                    if len(rec) < 2:
                        continue
                    if not ids.has_key(rec[0]):
                        sys.stderr.write(rec[0] + "\t" + rec[1]+ "\t" +" in " + SCfile + ": no mapping\n")
                    else:
                        newline = str(ids[rec[0]]) + "\t" + species_id + "." + rec[0] + '\t' +  rec[1] 
                        if len(rec) > 2:
                            newline = newline +"\t" +rec[2] 
                        newline = newline + "\n"
                        out.write(newline)



if __name__ == "__main__":
    run_spectral_counting()

#else importing into another module
