Dependencies:

sudo apt-get install libstatistics-descriptive-perl
sudo apt-get install python3-psycopg2

After checkout:

- git submodule update --init
- edit properties in /opt/paxdb/v*/pipeline.ini
- python pipeline.py

# to remove cached files
rm output/paxdb_datasets_info.pickle
