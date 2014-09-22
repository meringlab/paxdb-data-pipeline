#!/bin/bash

rScript=$1;
shift;
outdir=$1;
shift;

tmpf=$( mktemp $outdir/tmp.XXXXXXX )

R --vanilla -q --slave -e "source(\"$rScript\")" --args $* > $tmpf