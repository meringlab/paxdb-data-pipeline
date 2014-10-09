#!/usr/bin/python
#
# Maps to StringDb protein internal ID using protein external ID 
# instead of protein alias table (makes the mapping more strict).
# For the remaining un-mapped fall back to the protein alias table, 
# whilst checking for conflicts. 

"""
adds STRING internal ids to all .txt abundance files
"""

import re
import sys
import psycopg2
import os



DB_URL="host=imlslnx-eris.uzh.ch port=8182 user=postgres dbname=string_10_0"
INPUT_DIR='../input/v3.1/direct_mapping/'
OUTPUT_DIR='../output/v3.1/'
name_ids = {
        'deGodoy_et_al_yeast_data.txt' : 4932,
        'Ghaemmaghami_et_al_yeast_data.txt' : 4932,
        'Human_heart_ThinThinAye_MolecularBioSystems2010_APEX.txt' : 9606,
        'Human_liver_Chinese_2010_J._Proteome_Res.txt' : 9606,
        'human_lungProteins_Abdul-Salam_2010_Circulation_PeptideIonIntensityValues.txt' : 9606,
        'Lu_ecoli_2007.txt' : 511145,
        'mouse_brain_kislinger2006_cell.txt' : 10090,
        'mouse_glomeruli_kidney_F.Waanders2009_PNAs.txt' : 10090,
        'mouse_heart_kislinger2006_cell.txt' : 10090,
        'mouse_kidney_kislinger2006_cell.txt' : 10090,
        'mouse_liver_kislinger2006_cell.txt' : 10090,
        'mouse_lung_kislinger2006_cell.txt' : 10090,
        'mouse_pancreas_F.Waanders2009_PNAs_combine.txt' : 10090,
        'mouse_placenta_kislinger2006_cell.txt' : 10090,
        'Mycoplasma_pneumoniae_M129_Kuhner_et_al_Science2009.txt' : 722438,
        'Newman_et_al_yeast_data_SD.txt' : 4932,
        'Newman_et_al_yeast_data_YEPD.txt' : 4932,
        'pombe_cell2012_protein.txt' : 4896,
        'Taniguchi_2010_Table_S6.txt' : 511145,
        'Yeast_Lu_2007_YMD.txt' : 4932,
        'Yeast_Lu_2007_YPD.txt' : 4932
}


def map_file(species_id, f, ids, ids2, ides):
    print 'mapping file',f
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
        print 'mapping species',species_id
        (ids, ides) = load_ids(species_id)
        ids2 = load_names(species_id)

        for f in files:
            map_file(species_id, f, ids, ids2, ides)

for species in set(name_ids.values()):
        files = [INPUT_DIR + f for f,id in name_ids.items() if id == species]
        map_species(str(species), files)

