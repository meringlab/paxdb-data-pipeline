#!/usr/bin/python

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

dbcon = psycopg2.connect("host=imlslnx-eris.uzh.ch port=8182 user=postgres dbname=string_9_0")
cur = dbcon.cursor()
cur.execute("select protein_id, protein_name from items.proteins_names where species_id in (" + species_id + ")")
ids = dict()
#print(cur.fetchmany(5))
for el in cur:
    ids[el[1]] = el[0]
#    print("\t".join(map(str, el)))
cur.close()
dbcon.close()

#print(",".join(str(x) + " " + str(ids[x]) for x in ids.keys()[:5]))

files = sys.argv[2:]
for f in files:
    inp = open(f, "r")
    out = open(f + ".out","w")
    for line in inp.readlines():
        if (line.startswith('#')):
            out.write(line)
        else:
            rec = re.sub("\\s+", " ", line.strip()).split(" ")
            if len(rec) < 2:
                continue
            if rec[0] not in ids:
                sys.stderr.write(rec[0] + "\t" + rec[1]+ "\t" +" in " + f + ": no mapping\n")
            else:
                newline = str(ids[rec[0]]) + "\t" + species_id + "." + rec[0] + '\t' +  rec[1] +"\t" +rec[2] + "\n"
                out.write(newline)

inp.close()
out.close()
