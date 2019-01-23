for spc in `ls`; do
    for i in `ls $spc/*.abu`; do
	cat $i | grep -v '##' | cut -f 2,3 | sed "s/^$spc\.//" > $i.norm
	mv $i.norm $i
    done
done