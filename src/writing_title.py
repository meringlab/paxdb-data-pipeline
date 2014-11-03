#!/usr/bin/python
#
# This scripts prepends dataset metadata. 
#
# Author: Mingcong Wang <mingcong.wang@imls.uzh.ch>
# 
import csv
import os.path
import sys

from paxdb.config import PaxDbConfig


cfg = PaxDbConfig()

INPUT = '../output/' + cfg.paxdb_version + '/datasets/'
OUTPUT = "../output/" + cfg.paxdb_version + "/final_whole/"

# this input file is copy/paste from 'PaxDB data information' google doc, first two sheets:
# https://docs.google.com/spreadsheet/ccc?key=0AkvR36gTdQzedFYwenAxMFY3NENJeDRHeWU4TG9IYXc&usp=drive_web#gid=9
# the third column is the original data file name, so u have to modify
# the title writing code to make it read the final file
title_info = open("../input/Pax_DBtitle-v4.0.csv", "r")

try:
    os.mkdir(OUTPUT)
except:
    pass

inter_contain = dict()
title = ""
string1 = ""
string2 = ""
string3 = ""
string4 = ""
with title_info as f:
    reader = csv.reader(f, delimiter=",")
    for row in reader:
        print('processing', row[2])
        speid = str(row[0]).strip()
        # speid.strip()
        spe = str(row[1]).strip()
        # spename.strip()
        ifilename = str(row[2]).strip()  #####here need to adjust the input file name
        score = str(row[3]).strip()
        #score.strip()
        weight = str(row[4]).strip()
        #weight.strip()
        coverage = str(int(float(row[5]) * 100 / float(row[6])))
        organ = str(row[7]).strip().upper()
        #organ.strip()
        integrated = str(row[8]).strip().upper()
        #integrated.strip()
        pub = str(row[9]).strip()
        #pub.strip()
        pub_link = str(row[10]).strip()
        #pub_link.strip()
        condition = str(row[11]).strip()
        #condition.strip()
        quantification = str(row[12]).strip()
        #quantification.strip()
        spe_organ = speid + "_" + organ

        spename = ""
        spe = spe.split(".")
        spename = spe[0].strip() + "." + spe[1].strip()

        quan_method = quantification.split(" ")
        quan = ""
        for i in range(0, len(quan_method)):
            quan = quan + quan_method[i].strip() + "_"

        pub_all = pub.split(",")
        source = ""
        for i in range(0, len(pub_all)):
            source = source + "_" + pub_all[i].strip()

        if not os.path.isfile(INPUT + ifilename):
            print(INPUT, ifilename, " does not exist!")
            continue
        #            sys.exit()

        #ofilename = speid + "-"+ quan + spename + source +".txt"
        #ofile = open("./final_whole/"+ofilename, "a")

        if integrated == "N":
            ofilename = speid + "-" + quan + spename + "_" + organ + "_" + source + ".txt"
            if condition.strip() != "N":
                string1 = "#name: " + spename + ", " + organ + ", " + condition + ", " + pub + "\n"
                string3 = "#description: abundance based on " + quantification + ", " + condition + ", " + "from<a href=\"" + pub_link + "\" target=\"_blank\">" + pub + "</a><br/><b>Interaction consistency score</b>: " + score + "&nbsp<b>Coverage</b>: " + coverage + "\n"
                title = "\'" + spename + ", " + organ + ", " + condition + ", " + pub + "\'(weighting" + weight + "%)"
            elif condition.strip() == "N":
                string1 = "#name: " + spename + ", " + organ + ", " + pub + "\n"
                string3 = "#description: abundance based on " + quantification + ", " + "from<a href=\"" + pub_link + "\" target=\"_blank\">" + pub + "</a><br/><b>Interaction consistency score</b>: " + score + "&nbsp<b>Coverage</b>: " + coverage + "\n"
                title = "\'" + spename + ", " + organ + ", " + pub + "\'(weighting" + weight + "%)"

            if spe_organ in inter_contain:
                inter_contain[spe_organ] = str(inter_contain[spe_organ]) + "," + title
                #print inter_contain[spe_organ]
                #print str(inter_contain[spe_organ]) + "," +title
            else:
                inter_contain[spe_organ] = title

            string2 = "#score: " + score + "\n" + "#weight: " + weight + "%\n"

            if quantification.startswith("Spectral counting"):
                string4 = "#organ: " + organ + "\n" + "#integrated: false\n#\n" + "#internal_id\tstring_external_id\tabundance_ppm\traw_spectral_count\n#\n"
            else:
                string4 = "#organ: " + organ + "\n" + "#integrated: false\n#\n" + "#internal_id\tstring_external_id\tabundance_ppm\n#\n"

                #print inter_contain

        elif integrated == "Y":
            ofilename = speid + "-" + spename + "_" + organ + "-integrated_dataset.txt"
            string1 = "#name: " + spename + ", " + organ + ", PaxDB integrated dataset\n"

            string2 = "#score: " + score + "\n" + "#weight: \n"
            print("integrate")
            #print spe_organ
            if spe_organ in inter_contain:
                string3 = "#description: integrated dataset: weighted average of " + inter_contain[
                    spe_organ] + "<br/><b>Interaction consistency score</b>: " + score + "&nbsp<b>Coverage</b>: " + coverage + "\n"
            else:
                print("no file information available for integrate data")
                sys.exit()

            string4 = "#organ: " + organ + "\n#integrated : true\n#\n#internal_id\tstring_external_id\tabundance\n#\n"
        else:
            print('ERROR, invalid value for integrated dataset column: ', integrated)

        ofile = open(OUTPUT + ofilename, "w")
        ofile.write(string1)
        ofile.write(string2)
        ofile.write(string3)
        ofile.write(string4)

        ifile = open(INPUT + ifilename, "r")
        for line in ifile:
            if not line.startswith("#"):
                ofile.write(line)
        ifile.close()
        ofile.close()

title_info.close()        


