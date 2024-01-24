import json
from datetime import datetime
sp_set = set()
## file needs to be udpated if string version changes, current version 11.5
with open('/mnt/mnemo6/qingyao/paxDB/jpt_notebooks/input/2023-6/species_ids.txt') as f:
    for l in f:
        sp_set.add(l.strip())
        
name_file = '/mnt/mnemo6/damian/STRING_freeze_v11.5/ncbi/names.dmp'
names_map = []
with open(name_file) as f:
    for l in f:
        content = l.split('|')
        if content[-2].strip() == 'scientific name':
            sp_id = content[0].strip()
            if sp_id in sp_set:
                names_map.append({'id':sp_id, 'name':content[1].strip()})

print(len(names_map))
names_map.sort(key = lambda x:x['name'])
for sp_id in reversed(list(map(str, [9606, 511145, 4932, 7227, 3702, 10090, 9544, 7955]))):
    for i,j in enumerate(names_map):
      if j['id'] == sp_id:
        names_map.insert(0, names_map.pop(i))
        break
      
print(len(names_map))

with open('version_update/v5.0/UI_files/string_v11_5_species.js', 'w') as wf:
    print(f'// created by UI_string_species.py at {datetime.now()}', file = wf)
    print('export default ', end='', file = wf)
with open('version_update/v5.0/UI_files/string_v11_5_species.js', 'a') as wf:
    json.dump(names_map, indent = 2 ,fp=wf)