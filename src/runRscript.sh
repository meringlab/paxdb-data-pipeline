#!/bin/bash
#cd /home/gabi/PaxDb/

rScript=$1;
shift;

R --vanilla -q --slave -e "source(\"$rScript\")" --args $*