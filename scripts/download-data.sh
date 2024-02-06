cd $DATA_DIRECTORY

echo "Downloading CDD domains..."
wget $CDD_URL

echo "Downloading PDB sequences..."
wget $PDB_SEQUENCES_URL

echo "Downloading PDB structures..."
mkdir pdb
cd pdb
wget $PDB_STRUCTURES_URL

