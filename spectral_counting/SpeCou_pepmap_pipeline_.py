
#!/usr/bin/python

# this is for the spectral counting calculating protein abundance
# and raw spectral count and mapped peptide


import sys
import os
import shlex
import subprocess
from glob import glob
import re
import psycopg2

STRING_DB='string_10_0'
FASTA='../input/v3.1/spectral_counting/fasta'
FASTA_VER='10.0'
INPUT='../input/v3.1/spectral_counting/'
OUTPUT='../output/v3.1/'
SPECIES_IDS=[1148, 3702, 4896, 4932, 6239, 7227, 7460, 7955, 8364, 9031, 9606, 9615, 9823, 9913, 10090, 10116, 39947, 64091, 83332, 99287, 160490, 198214, 224308, 267671, 449447, 511145, 546414, 593117] # no SC for 722438

def spectral_count_species(species_id):
    if not os.path.exists(get_output_dir(species_id)):
        os.mkdir(get_output_dir(species_id))

    path = INPUT + species_id + '/'
    protein_ids_map = load_ids(species_id)

    for pepfile in glob(path + '*.txt'):
        print 'processing',pepfile
        scfile = calculate_abundance_and_raw_spectral_counts(species_id, pepfile)
        map_peptide(species_id, pepfile)
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
    cmd = "java -Xms512m ComputeAbundanceswithSC -s {0} '{1}' '{2}/fasta.v{3}.{0}.fa'"
    cmd = cmd.format(speid, pepfile, FASTA, FASTA_VER)
    scfile = get_output_dir(speid) + get_filename_no_extension(pepfile) + ".SC"
    if os.path.isfile(scfile):
        return
    with open(scfile, "w") as ofile:
        subprocess.Popen(shlex.split(cmd), stdout = ofile).wait()
    return scfile
# inputs: pepetide_counts, seq_fasta file -> protein abundance + count -> mapping to internal id ------- input pepetide_count, seq_fasta file -> mapping peptide

def map_peptide(speid, pepfile):
    """
    maps peptides to proteins, takes peptide counts and fasta file 
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

def load_ids(species_id):
    print('loading protein mapping for ' + species_id)
    dbcon = psycopg2.connect("host=imlslnx-eris.uzh.ch port=8182 user=postgres dbname="+STRING_DB)
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



# main
if __name__ == "__main__":
    for species_id in SPECIES_IDS:
        spectral_count_species(str(species_id))
#else importing into another module
