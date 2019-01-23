#/usr/bin/python
# requires python3-plotly

import plotly
import plotly.graph_objs as go
import os
from os.path import join
import math
# invoke from the output folder

V1='v4.0'
V2='v4.1'

to_plot = ['99287/99287-WHOLE_ORGANISM-integrated.txt','214684/214684-WHOLE_ORGANISM-integrated.txt','10090/10090-WHOLE_ORGANISM-integrated.txt','5833/5833-WHOLE_ORGANISM-integrated.txt','9913/9913-WHOLE_ORGANISM-integrated.txt','3702/3702-LEAF-integrated.txt','9606/9606-WHOLE_ORGANISM-integrated.txt','83332/83332-WHOLE_ORGANISM-integrated.txt','4932/4932-WHOLE_ORGANISM-integrated.txt','85962/85962-WHOLE_ORGANISM-integrated.txt','7955/7955-WHOLE_ORGANISM-integrated.txt','10090/10090-BRAIN-integrated.txt','10090/10090-CELL_LINE-integrated.txt','7227/7227-WHOLE_ORGANISM-integrated.txt','9606/9606-HEART-integrated.txt','9606/9606-CELL_LINE-integrated.txt']

def read_dataset(f1):
    abundances = []
    with open(f1) as f:
        for line in f:
            if line.startswith('#') or len(line.strip())<  2:
                continue
            rec = line.split('\t')
            try:
                abundances.append(math.log(float(rec[2])))
            except:
                print("failed to log ", rec[2])
    return sorted(abundances)

for d in to_plot:
    f1 = join(V1, d)
    f2 = f1.replace(V1, V2)
    dataset_name = os.path.basename(f1)
    if not os.path.exists(f2) or not os.path.exists(f1):
        print('%s dataset doesnt exist' %  dataset_name)
        continue
    d1  = read_dataset(f1)
    d2 =  read_dataset(f2)
    
    data = [go.Histogram(x=d1)]
    plotly.offline.plot(data, filename=dataset_name.replace('.txt','-'+V1))
    data = [go.Histogram(x=d2)]
    plotly.offline.plot(data, filename=dataset_name.replace('.txt','-'+V2))


