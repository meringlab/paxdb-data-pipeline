## make ortholog level name file
import os, yaml, re

config_file = os.path.join('../paxdb/config.yml')

with open(config_file) as f:
    config = yaml.load(f, Loader= yaml.BaseLoader)
    PAXDB_VERSION = config['VERSION']['PAXDB']
    LEVEL_IDS = config['ORTHOLOG_LEVEL']
    ortholog_lvl_file = config['FILE_PATHS']['ORTHOLOG_LEVEL']

output_dir = f'../version_update/{PAXDB_VERSION}'
id_name_map = {}
with open(ortholog_lvl_file) as f:
    for l in f:
        ortholog_id = l.split()[0]
        if ortholog_id in LEVEL_IDS:
            if 'scientific name' in l:            
                name = l.split('|')[1].strip()
                id_name_map[ortholog_id] = name.lower()

with open(os.path.join(output_dir,'cogs.txt'), 'w') as fw:
    for ortholog_id, name in id_name_map.items():
        if ortholog_id == '1':
            name = 'luca'
        print(ortholog_id + ': ' + name, file = fw)
