# re-write ortholog files for downloads
import os
import psycopg2
from paxdb.config import PaxDbConfig

paxdb_version = 'v4.2'
input_dir = f'version_update/{paxdb_version}/orthgroups/'
output_dir = f'version_update/{paxdb_version}/downloads/orthgroups/'

cfg = PaxDbConfig()
DB_URL = cfg.pg_url
dbcon = psycopg2.connect(DB_URL)
cur = dbcon.cursor()

os.makedirs(output_dir, exist_ok=True)

for i in os.listdir(input_dir):
    if i.endswith('-orthologs.txt'):
        with open(os.path.join(output_dir, i), 'w') as wf:
            with open(os.path.join(input_dir, i)) as f:
                for l in f:
                    nog = l.split('\t')[0]
                    protein_ids = l.split('\t')[1:]
                    protein_names = []
                    for p in protein_ids:
                        protein_name = None
                        cur.execute("SELECT protein_external_id "
                            "FROM {}.proteins "
                            "WHERE protein_id={}".format
                            (cfg.paxdb_version_sql, p))
                        for s in cur:
                            protein_name = s[0]
                            break
                        if protein_name:
                            protein_names.append(protein_name)
                    print(nog, ':\t', ' '.join(protein_names), sep = '', file = wf)
