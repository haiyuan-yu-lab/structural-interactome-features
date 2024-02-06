echo "creating the database for CDD domains..."
($CDHIT_MAKEDB -title CDD.v.3.12 -in Cdd.pn -out Cdd -threshold 9.82 -scale 100.0 -dbtype rps -index true)

