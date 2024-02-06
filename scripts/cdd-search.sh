echo "Performing CDD Search..."
($CDHIT_BIN -query $INPUT_FASTA -db mycdd -seg no -comp_based_stats 1 -evalue 0.01 -outfmt 7 > $CDD_RESULT)
echo "Done, CDD result saved to $CDD_RESULT"

echo "Processing CDD result file: $CDD_RESULT ..."
python SIF.py parse-cdd -i $CDD_RESULT -o $CALCULATED_DOMAINS -f $INPUT_FASTA
echo "Done, domain result saved to $CALCULATED_DOMAINS"
