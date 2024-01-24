# How to update paxDB when integration of datasets are done (step 6)
## File location: /mnt/mnemo6/qingyao/paxDB/data-pipeline/src/update_api_inputs/
1. Update species.yml, with correct short species names (will be displayed in website) w/ new_species.yml (will be used for marking new species in cladogram)
2. [!] Update sql database (will need it for pipeline step 8 to get internal ID) -> takes many hours to a day to create index etc.
3. Run the cladogram.py, and check the new species nodes and adjust included nodes.
4. Remove files in `datapipeline/input/{version_no}/stringdb/` (if there's string update) or remove files of size 0 (`find  datapipeline/input/{version_no}/stringdb/ -size 0c -delete`) and run `repository.py` in stringdb module with updated SQL database.
5. Run step 7 till end in pipeline (relies on updated stringdb) -> finalized datasets
6. Run remaining scripts in this folder.
7. Go to the git projects (Docker: paxdb-api, paxdb-orthology-api, paxdb-search, paxdb-orthology-storage; UI: ui-test) to update accordingly.