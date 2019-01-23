#!/usr/bin/python3

import os
import glob

for tsv in glob.glob("*tsv"):
    print("processing ", tsv)
    file = open(tsv)

    rewritten_file = os.path.splitext(os.path.splitext(tsv)[0])[0] + '.network_v10_900.txt'
    if os.path.isfile(rewritten_file):
        continue
    with open(rewritten_file, 'w') as rewritten:
        for line in file:
            if line.startswith('#'):
                rewritten.write(line)
                continue
            r = line.split(' ')
            if len(r) < 2: # empty line?
                continue
            score = int(r[2].strip())
#            score = int(float(r[2].strip()) * 1000)
            if score < 900:
                continue
            rewritten.write(r[0][r[0].index('.') + 1:])
            rewritten.write('\t')
            rewritten.write(r[1][r[1].index('.') + 1:])
            rewritten.write('\t')
            rewritten.write(str(score))
            rewritten.write('\n')
    file.close()
