### for UI there are a few added nodes for homepage or cladogram: see cladogram.py
import os, yaml, re

added_nodes = [28211,8292,7898]

config_file = os.path.join('../paxdb/config.yml')

with open(config_file) as f:
    config = yaml.load(f, Loader= yaml.BaseLoader)
ORTHOLOG_LEVEL = config['ORTHOLOG_LEVEL']
PAXDB_VERSION = config['VERSION']['PAXDB']

added_ortholog_ids = list(map(str,added_nodes))

ortholog_lvl_file = config['FILE_PATHS']['ORTHOLOG_LEVEL']
    
id_name_map = {}
with open(ortholog_lvl_file) as f:
    for l in f:
        ortholog_id = l.split()[0]
        if ortholog_id in ORTHOLOG_LEVEL+added_ortholog_ids: 
            if 'scientific name' in l:
                name = l.split('|')[1].strip()
                id_name_map[ortholog_id] = name.lower()   

output_dir = f'../version_update/{PAXDB_VERSION}'            
with open(os.path.join(output_dir,'UI_files','cogs.js'), 'w') as fw:
    print('export const orthologs = {', file = fw)
    for ortholog_id, name in id_name_map.items():
        if ortholog_id == '1':
            name = 'All species'
        else:
            name = name.capitalize()
        print('  "'+ortholog_id + '": "' + name+'",', file = fw)
    print('};', file = fw)
