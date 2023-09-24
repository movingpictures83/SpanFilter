from blastparser import HitsDataContainer
import sys

print("Filtering hits by span length...")
#SQLITE_DATABASE_DIR = "../../epitopedia.sqlite3"
#PDB_INPUT="6VXX_A"
#CSVFILE="EPI_SEQ_hits_6VXX_A.tsv"
#span=5
SQLITE_DATABASE_DIR = sys.argv[1]
PDB_INPUT=sys.argv[2]
CSVFILE=sys.argv[3]
span=int(sys.argv[4])
OUTPREFIX=sys.argv[5]

hits = HitsDataContainer()
hits.fromcsv(f"{CSVFILE}")
hits = hits.filterbymatchlen(span)
hits.tocsv(f"{OUTPREFIX}_{PDB_INPUT}.tsv", SQLITE_DATABASE_DIR)
print("Hits filtered by span length")
print(f"Number of hits remaining after span length filter {PDB_INPUT}: {len(hits)}")
