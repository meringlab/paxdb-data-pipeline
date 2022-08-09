Dependencies:

sudo apt-get install libstatistics-descriptive-perl
sudo apt-get install python3-psycopg2 python3-pip
sudo apt-get install python3-oauth2client

After checkout:

- git submodule update --init
- edit properties in /opt/paxdb/v*/pipeline.ini
- get the paxdb.team's google api key and put at /opt/paxdb/google-api-key.json (https://console.developers.google.com/iam-admin/serviceaccounts/details/115514263757920582063;edit=true?previousPage=%2Fapis%2Fapi%2Fsheets.googleapis.com%2Fcredentials%3Fproject%3Ddata-pipeline-246410&project=data-pipeline-246410)
- cd src
- python pipeline.py

# to remove cached files
rm output/paxdb_datasets_info.pickle
