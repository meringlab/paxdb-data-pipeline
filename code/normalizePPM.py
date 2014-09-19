# this is for normalizing all the paxdb protein abundance file into ppm                   
#import re
import sys
#import psycopg2
#import os

#if len(sys.argv) < 1:
#	print("need file(s) to be converte")
 #   sys.exit()

files = sys.argv[1:]
for f in files:
    inp = open(f,'r')
    out = open(f[:-4] + '.out','w')
    d = [float(line.split('\t')[2]) for line in inp.readlines()]; sumd = sum(d)
    inp = open(f,'r')
    for line in inp.readlines():
        if (line.startswith('#')):
            out.write(line)
        else:
            ab = line.split('\t')
            abu = ((float(ab[2])/sumd)*1000000)
            newline = str(ab[0]) + '\t'+ ab[1]+'\t'+ str(abu) +'\n'
            out.write(newline)
	
inp.close()
out.close()
