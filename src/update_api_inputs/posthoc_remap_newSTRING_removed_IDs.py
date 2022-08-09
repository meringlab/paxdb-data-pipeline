# post-hoc re-map with log from step 7 (trying to remap protein IDs to internal IDs and do not find)
import os, shutil, logging
from datetime import date
paxdb_version = 'v4.2'
output_dir = '/mnt/mnemo6/qingyao/paxDB/data-pipeline/output'
string_dir = f'/mnt/mnemo6/qingyao/paxDB/data-pipeline/input/{paxdb_version}/stringdb'
log_dir = '/mnt/mnemo6/qingyao/paxDB/data-pipeline/logs'

FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(format=FORMAT)
logger_file = logging.getLogger("write_log")
log_path = f'{log_dir}/{date.today().isoformat()}_remap.log'
logger_file.addHandler(logging.FileHandler(log_path))
logger_file.setLevel(10)
logger_file.propagate = False

for species in ['10090','3702', '4577', '189518']: #'9606'
    os.chdir(os.path.join(output_dir, paxdb_version, species))

    string_proteins = set()
    with open(f'{string_dir}/{species}-proteins.txt') as f:
        for l in f:
            string_proteins.add(l.split()[1])

    problem_files = set()
    for i in os.listdir():
        if i.endswith('.abu'):
            count = 0
            with open(i) as f:
                for j,l in enumerate(f):
                    if l.split()[0] not in string_proteins:
                        count+=1
            if count > 0:
                problem_files.add(i)
                print(i, count, j)
        
    IDmapper = {}
    with open(os.path.join(string_dir, species+'-proteins.txt')) as f:
        for l in f:
            iid, eid = l.strip().split()[:2]
            IDmapper[iid] = eid
                
    nameMapper = {}
    with open(os.path.join(string_dir,species+'-proteins_names.txt')) as f:
        for l in f:
            items = l.strip().split()
            iid = items[0]
            
            for n in items[1:]:
                nameMapper[n] = iid
            
    ### check multiple output from one ID -> to remove

    for i in problem_files:
        output_len = {}
        count = 0
        with open(i) as f:
            for j,l in enumerate(f):
                name = l.split()[0]
                if name not in string_proteins:
                    try:
                        iid = nameMapper[name.replace(species+'.','')]
                        
                    except KeyError:
                        count+=1
                        
                    else:
                        name = IDmapper[iid]
                    
                if name in output_len:
                    output_len[name] +=1 
                else:
                    output_len[name] =1 
                    
        if count > 0:
            print(i, count, j)

        print(i, len([i for i,j in output_len.items() if j > 1]))

        multi_output_collection = set()
        for i,j in output_len.items():
            if j > 1:
                multi_output_collection.add(i)

    logger_file.info(species + ': ' + ','.join(list(multi_output_collection)))

    input(f'Please check above and log file ({log_path}) before proceed. [ENTER]')

    ## move original file to mapping/ folder and write new files
    os.makedirs('mapping', exist_ok=True)
    mapper = {}
    for i in problem_files:
        output_len = {}
        count = 0
        with open(i) as f:
            l_to_write = []
            for j,l in enumerate(f):
                name = l.split()[0]
                if name not in string_proteins:
                    try:
                        iid = nameMapper[name.replace(species+'.','')]
                        
                    except KeyError:
                        count+=1
                        
                    else:
                        name = IDmapper[iid]
                        mapper[l.split()[0]] = name
                    
                if name in output_len:
                    output_len[name] +=1 
                else:
                    output_len[name] =1 
                    
                l_to_write.append((name, '\t'.join([name] + l.split()[1:])))
        multi_output = [i for i,j in output_len.items() if j > 1]
        
        shutil.copyfile(i, 'mapping/'+i)
        with open(i,'w') as wf:
            for name, l in l_to_write:
                if name in multi_output:
                    continue
                print(l, file = wf)

    for i in os.listdir('mapping'):
        try:
            os.remove(os.path.splitext(i)[0]+'.pax')
            os.remove(os.path.splitext(i)[0]+'.pax_rounded')
            os.remove(os.path.splitext(i)[0]+'.txt')
            os.remove(os.path.splitext(i)[0]+'.zscores')
        except:
            continue
                    