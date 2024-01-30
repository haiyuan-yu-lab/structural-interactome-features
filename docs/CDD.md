# Getting CDD locally

Our pipeline relies on identifying the domains using CDD, however, in order to
run the search properly, there are some steps you need to do first.

Here, we assume that the working directory is `/wd` and that you have cloned this
repository into it, and that you have write permissions to it. We also assume that
the sequences you want to use are in a file `/wd/data/query.fasta`

1. Get the data:
```bash 
mkdir data/cdd
cd data/cdd
wget https://ftp.ncbi.nih.gov/pub/mmdb/cdd/cdd.tar.gz
```
2. uncompress
```bash
tar xvzf cdd.tar.gz
```
3. Build the CDD database 
```bash
docker1 run --rm -v /wd/data/cdd/:/blast/blastdb_custom:rw -w /blast/blastdb_custom ncbi/blast makeprofiledb -title CDD.v.3.12 -in Cdd.pn -out Cdd -threshold 9.82 -scale 100.0 -dbtype rps -index true
```
4. Return to the working directory, and create the custom CDD BLAST alias file
```bash
cd /wd
echo "CDD_BIN=\"docker run --rm -v /wd/data/:/blast/blastdb_custom:rw -w /blast/blastdb_custom ncbi/blast rpsblast\"" >> .env
```
> __Important__: the `cddalias.pal` file is located in the `data` directory in
> this repository, and assumes that the current working directory is that very 
> same directory. If you are using another path, please update the `DBLIST`
> value accordingly.
