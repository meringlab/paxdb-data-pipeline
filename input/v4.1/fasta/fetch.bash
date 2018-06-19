#!/bin/bash

for i in 882 1148 3055 3702 4081 4577 4896 4932 5061 5691 5821 5833 6239 7165 7227 7460 7955 8364 9031 9598 9606 9615 9796 9823 9913 10090 10116 39947 44689 64091 83332 85962 99287 122586 158878 160490 169963 192222 198214 208964 211586 214092 214684 224308 226186 243159 260799 267671 272623 272624 283166 352914 353153 449447 511145 546414 593117 722438
do
    dest=fasta.v10.5.$i.fa
    if [ ! -e $dest ]
    then
	sudo scp -P 22222 -i /home/server-adm/.ssh/id_rsa server-adm@aquarius.meringlab.org:/home/stringdb/string_10_5_data_backup/protein.sequences.v10.5/$i.protein.sequences.v10.5.fa.gz $dest
#       cp /mnt/mnemo2/damian/STRING_v10/STRING_derived_v10/fastafiles/$i.fa $dest
    fi
done
