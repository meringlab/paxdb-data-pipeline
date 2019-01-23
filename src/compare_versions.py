#/usr/bin/python
# requires python3-numpy python3-scipy
from scipy import stats
import os
import glob
from os.path import join
# invoke from the output folder

V1='v4.0'
V2='v4.1'

def read_dataset(f1):
    abundances = []
    with open(f1) as f:
        for line in f:
            
            if line.startswith('#') or len(line.strip())<  2:
                continue
            rec = line.split('\t')
            abundances.append((rec[1], float(rec[2])))
    return sorted(abundances, key=lambda r: (r[1],r[0]))

def to_ranks(a1):
    '''a1 is a sorted array of tuples (protein, abundance), this returns a map (protein -> rank)'''
    ranks = {}
    for i in range(len(a1)):
        ranks[a1[i][0]] = i
    return ranks

def compare_ranks(a1, a2):
    num_missing = 0
    diff = 0
    for p in a1:
        if p not in a2:
            num_missing += 1
            continue
        jump = abs(a1[p] - a2[p])
        if jump != 0:
            diff += jump
    if num_missing !=0:
        print(num_missing, 'proteins missing in second dataset')
    return diff
ks = {}
cummulative = 0
num_prot_changed = 0
for f1 in glob.glob(join(V2, '*/*txt')):
    f2 = f1.replace(V2, V1)
    dataset_name = os.path.basename(f1)
    if not os.path.exists(f2):
        print('%s dataset didnt exist' %  dataset_name)
        continue
    d1  = read_dataset(f1)
    d2 =  read_dataset(f2)
    r1 = to_ranks(d1)
    r2 = to_ranks(d2)

    diff = compare_ranks(r1, r2)
    rvs1 = [e[1] for e in d1]
    rvs2 = [e[1] for e in d2]
    ks =  stats.ks_2samp(rvs1, rvs2)

    if diff == 0:
        print(f1, '\t', 'hasnt changed','\t-\t', ks.statistic, '\t', ks.pvalue)
    else:
        print(f1, '\t', diff, '\t', diff / len(d1), '\t', ks.statistic, '\t', ks.pvalue)
        cummulative += diff
        num_prot_changed += len(d1)
    
print('total diff', cummulative, cummulative / num_prot_changed)

