#!/usr/bin/python
# this one maps to string 10 protein internal ID from protein external ID instead of protein alias table, this makes the mapping more strict.
# For the rest which can not map with the protein_external_id, still use the protein alias table, with checking whether there is any protein share the same internal ID
"""
adds STRING internal ids to all .txt abundance files
"""

import re
import sys
import psycopg2
import os

if len(sys.argv) < 3:
	print("need species ID and file(s) to be converted as arguments")
	sys.exit()

species_id = sys.argv[1]

dbcon = psycopg2.connect("host=imlslnx-eris.uzh.ch port=8182 user=postgres dbname=string_10_0")
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

dbcon2 = psycopg2.connect("host=imlslnx-eris.uzh.ch port=8182 user=postgres dbname=string_10_0")
cur2 = dbcon2.cursor()
cur2.execute("select protein_id, protein_name from items.proteins_names where species_id in (" + species_id + ")")
ids2 = dict()
#print(cur.fetchmany(5))
for el in cur2:
    ids2[el[1]] = el[0]
#    print("\t".join(map(str, el)))
cur2.close()
dbcon2.close()

#print(",".join(str(x) + " " + str(ids[x]) for x in ids.keys()[:5]))

files = sys.argv[2:]
for f in files:
    inp = open(f, "r")
    out = open(f + ".new","w")
    remains = {}# this is for storing the no mapping entries
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
inp.close()
out.close()
