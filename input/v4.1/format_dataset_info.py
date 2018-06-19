

#!/usr/bin/python
#
# small util script to dump new datasets info
# that can be copy/pasted into the google doc
# 
import sys

# first arg is the folder containing datasets
dir=sys.argv[1]
# config:
DB_URL='host=imlslnx-eris.uzh.ch port=8182 user=postgres dbname=string_10_0'

## 
import os
import glob
import re
import psycopg2

species_ids=[10090  ,214684  ,283166  ,3702  ,4577  ,4932,  83332  ,9606]
# for spc in os.listdir(dir):
#     if spc.isdigit():
#         species_ids.append(spc)


NAMES=dict()
GENOME_SIZE=dict()
dbcon = psycopg2.connect(DB_URL)
cur = dbcon.cursor()
cur.execute('''
  SELECT s.species_id, s.compact_name, count(p.protein_id)
  FROM items.species as s, items.proteins as p
  WHERE p.species_id = s.species_id
  AND s.species_id in %s
  GROUP BY s.species_id, s.compact_name;
''', [tuple(int(x) for x in species_ids)] )

#  list(map(lambda x: int(x), species_ids)))

for el in cur:
    NAMES[str(el[0])] = el[1]
    GENOME_SIZE[str(el[0])] = el[2]
cur.close()
dbcon.close()

def count_entries(from_file):
    protein_number = 0
    with open(from_file) as file:
        for line in file:
            if re.match('\\s*#.*', line):  # line startwith '#'
                continue
            rec = re.sub("\\s+", " ", line.strip()).split(" ") #empty line
            if len(rec) < 2:
                continue
            protein_number = protein_number + 1

for sid in species_ids:
    spc = str(sid)
    dsetdir = os.path.join(dir,str(spc))
    for d in os.listdir(dsetdir):
        name = NAMES[spc] if spc in NAMES else '-'
        print("{0}\t{1}\t{2}\t0\t100\t{3}\t{4}\twhole_organism\tN\tTODO\tTODO\tN\tSpectral counting".format(spc, name, d, 0, GENOME_SIZE[spc]))



