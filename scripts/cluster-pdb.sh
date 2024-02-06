echo "Filtering PDB sequences located in $PDB_SEQUENCES, keeping proteins only..."
awk '/^>/ {printit = /:protein/} printit {print}' $PDB_SEQUENCES > $PDB_SEQUENCES_FILTERED
echo "Done, filtered FASTA file saved into $PDB_SEQUENCES_FILTERED"

echo "Clustering $PDB_SEQUENCES_FILTERED with CD-HIT..."
($CDHIT_BIN -i $PDB_SEQUENCES_FILTERED -o $CDHIT_CLUSTERS -c 0.6 -n 4 -d 0)
echo "Done, cluster file file saved into $CDHIT_CLUSTERS"
