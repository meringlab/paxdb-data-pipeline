# this is for get the round number of spectral count in the peptide  count file
import sys

if len(sys.argv) < 1:
    print "please input the file name which need to convert"

ifile = sys.argv[1:]

for f in ifile:
    inp = open(f,"r")
    oup = open(f+"round","w")
    for line in inp:
        a = line.split("\t")
        seq = a[0]
        ct = int(round(float(a[1])))
        newline = seq +"\t" +str(ct) +"\n"
        oup.write(newline)
inp.close()
oup.close()
        
