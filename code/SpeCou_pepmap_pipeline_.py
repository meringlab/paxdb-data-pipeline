# this is for the spectral counting calculating protein abundance and raw spectral count and mapped peptide
# protocol : input pepetide_count, seq_fasta file -> protein abundance + count -> mapping to internal id ------- input pepetide_count, seq_fasta file -> mapping peptide

import sys
import os
import shlex
import subprocess

FASTA='../input/v3.0/fasta'

if len(sys.argv) <3:
    print "need species ID, path, peptide count file to convert as argvment "
    sys.exit()
    # filename without ".txt"
speid = sys.argv[1]
path = sys.argv[2]
pepfile = sys.argv[3:]

SCfile = ""
for f in pepfile:
    # calculating protein abundance and raw spectral count
    out = f + ".SC"
    ofile = open(path +"/"+ out,"w")
    seqcom1 = "java -Xms512m ComputeAbundanceswithSC -s " + speid + " " + path + "/" + f + ".txt " + FASTA +"/fasta.v9.0." + speid + ".fa"
    scom1 = shlex.split(seqcom1)
    subprocess.Popen(scom1, stdout = ofile).wait()
    ofile.close()
    SCfile = path + "/" + out + " " 
    # map peptide
    
    out2 = f +"_peptide.txt"
    ofile2 = open(path + "/" + out2, "a")
    ofile2.write("#string_external_id	peptide_sequence	spectral_count")
    seqcom2 = "java -Xms512m ComputeAbundancesMappep -p 4 -s " + speid + " "+ path + "/" + f + ".txt " + FASTA +"/fasta.v9.0." + speid + ".fa |tee > " + out2
    scom2 = shlex.split(seqcom2)
    subprocess.Popen(scom2, stdout = ofile2).wait()
    ofile2.close()    

    # map to string internal id
    mapcomd = "python map_to_string_ids.py " + speid + " " +SCfile
    scom3 = shlex.split(mapcomd)
    subprocess.Popen(scom3).wait()
