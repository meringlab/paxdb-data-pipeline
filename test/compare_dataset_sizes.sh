#!/usr/bin/env bash

cd output/v4.0
for i in `ls */*txt`
do
    p=$(cat $i | wc -l); n=$(cat ../v4.1/$i | wc -l);
    if [  $p -ne $n ];
    then
        echo "$i, $p, $n";
    fi
done