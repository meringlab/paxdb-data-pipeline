#!/bin/bash

cd ../output/v3.1/zscores
#rename SC to txt so the names match
find . -name '*SC' -print0 | while read -d $'\0' f
do 
    b=`basename "$f" .SC`.txt
    mv  "$f" `dirname "$f"`/"$b"
done

#get the score and print in the google doc order (copy/pasted to expected.txt)
for i in `cat expected.v3.1.txt `
do
    echo -ne "$i" '\t' >> scores.txt
    score=$(sed '4q;d' zscores/zscores_"$i" | sed -e 's/^sed.*//' | sed -e 's/-//')
    echo "$score" >> scores.txt
done
