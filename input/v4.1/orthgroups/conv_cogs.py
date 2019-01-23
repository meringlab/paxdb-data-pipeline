#!/usr/bin/python

import psycopg2
import fnmatch
import os

species_ids='882,1148,3055,3702,4081,4577,4896,4932,5061,5691,5833,6239,7165,7227,7460,7955,8364,9031,9598,9606,9615,9796,9823,9913,10090,10116,39947,44689,64091,83332,85962,99287,122586,158878,160490,169963,192222,198214,208964,211586,214092,214684,224308,226186,243159,260799,267671,272623,272624,283166,353153,449447,511145,546414,593117,722438'


dbcon = psycopg2.connect("host=imlslnx-eris.uzh.ch port=8182 user=postgres dbname=string_10_0")
print("loading species data from " + str(dbcon))
cur = dbcon.cursor()
cur.execute("select protein_id, protein_external_id from items.proteins where species_id in ("+species_ids+"  ); ")
ids = dict()
for el in cur.fetchall():
    ids[el[1]] = el[0]
cur.close()
dbcon.close()

for file in os.listdir('.'):
    if fnmatch.fnmatch(file, '*.txt'):
        inp = open(file,"r")
        out = open(file.split('.')[0] + "-orthologs.txt","w")
        print("processing: " + file)
        for line in inp:
            if line.startswith('#'):
                continue
            rec = line.split(":")
            out.write(rec[0])
            for eid in rec[1].strip().split(" "):
                out.write("\t" + str(ids[eid.strip()]))
            out.write("\n")

        inp.close()
        out.close()
        print(file + " rewritten")
