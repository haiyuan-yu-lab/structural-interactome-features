# structural-interactome-features
Toolkit to derive structural features for interacting proteins

The pipeline is ispired by [PrePPI](https://doi.org/10.1016/j.jmb.2023.168052),
but this project does not focus on predicting interactions, but rather compute
useful structurally-informed features for proteins and pairs of proteins.

## Installation instructions

Please install all the required python packages running:

```bash
pip install -r requirements.txt
```

## External Requirements

- [AlphaFold](https://github.com/google-deepmind/alphafold)
- [CD-HIT](https://github.com/weizhongli/cdhit)
- [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cdd_help.shtml#RPSBFtp) (we provide a script to perform the search, but you must install CDDs requirements and get the data)
- [ska](https://honig.c2b2.columbia.edu/ska) (We provide bash scripts to perform the alignment, but we don't have permission to redistribute the software, you must obtain a licence to run this.)
- [PeSTo](https://github.com/LBM-EPFL/PeSTo) (We provide bash scripts to run PeSTo, assuming you have installed a proper Docker image in your system. You may modify this by configuring the environment variables in the `.env` file)

## Configuration Variables

We rely on multiple external tools to run the entire pipeline. For example, it
is recommended that you create a Docker container to run PeSTo and AlphaFold, 
and depending on your system it may make more sense to ivoke CD-HIT and ska 
also from their isolated Docker containers.

To allow for a composable pipeline, we rely on environment variables to control
such cases:

- `AF_PREDICT`: this should be configured to the command to run
  `python docker/run_docker.py` from the AlphaFold pipeline, we simply wrap our
  script API around this command call.
- `PESTO_PREDICT`: Similar to the above, this is the command you'd need to run
  PeSTo's model. In the repository, this is unfortunately given as a jupyter
  notebook. You may use 
  [this fork](https://github.com/torresmateo/PeSTo/blob/main/apply_model.py)
  to create your own Docker container, or overwrite the command yourself.
- `SKA_BIN`: If present in your system, this should simply point to the ska
  binary (you should previously set ska's own environment variables). We 
  recommend using a Docker container instead.
- `CDHIT_BIN`: Similar to ska, this should point to the CD-HIT binary, or the
  `docker run` command to run. We simply take care of passing the arguments.
- `CDD_BIN`: Similar to ska, this should point to the `rpsblast` binary, or the
  `docker run` command to run. We simply take care of passing the arguments.

## Pipeline details

The pipeline consists on 2 main parts:

- a single-protein pipeline to identify a structural neighborhood for protein,
  which requires a single sequence, passed as a FASTA file. This results in the
  generation of a structural model, as well as the structural neighbors of such 
  model. 

- a pairwise feature extraction that takes two protein models and their 
  respective structural neighborhoods, and results in a series of interaction
  templates (pairs of interacting proteins in PDB), as well as
  structurally-informed features for downstream tasks.

### Getting the data 

It is recommended that you get a copy of the [PDB database](https://www.rcsb.org)
(click [here](https://www.wwpdb.org/ftp/pdb-ftp-sites) for mirror and FTP info)

You also need to get a copy of [CDD](https://ftp.ncbi.nih.gov/pub/mmdb/cdd/cdd.tar.gz),
then uncompress it and build the relevant BLAST databases (see instructions
[here](https://ftp.ncbi.nih.gov/pub/mmdb/cdd/README)). We recommend runinng 
everything using docker, as described [here](docs/CDD.md).

### Data pre-processing

#### Domain identification

Protein models are built from their full sequences, as well as the sequences of
their domains. To identify such domains, please run: 

```bash
python SIF.py cdd-search -i sequences.fasta -o data/domains.tsv -d data/domains.tmp
```

where `sequences.fasta` contains the full sequences of every protein you want
to consider, `data/domains.tsv` is the path to a file where the domains
will be stored, and `data/domains.tmp` is a file where the raw output from 
`rpsblast` will be stored.

> __Important:__ if you're using Docker for `CDD_BIN`, remember that 
> `sequences.fasta` needs to be a path relative to the configured volume, while
> the other paths are relative to the host.

#### PDB Clustering

This relies on [CD-HIT](https://github.com/weizhongli/cdhit), used to generate
non-redundant representatives of a large corpus of proteins to generate the 
neighborhood without having to scan every protein in existence. 

If you need the full structural neighborhood, it is convenient to cluster every
sequence and domain found in the PDB database.

First, download the [PDB sequences](https://files.rcsb.org/pub/pdb/derived_data/pdb_seqres.txt.gz)
and run the following to uncompress the file:
```bash
gunzip pdb_seqres.txt
```
and then to keep only protein sequences
```bash
awk '/^>/ {printit = /:protein/} printit {print}' pdb_seqres.txt > pdb_prot_seq.fasta
```
From the previous section, we also need to identify the domains on these 
sequences. Run:
```bash
python SIF.py cdd-search -i pdb_prot_seq.fasta -o pdb-domains.tsv -d pdb-domains.tmp
```
Finally, to cluster the domains, use
```bash
python SIF.py cdhit-cluster --in-file filtered.fasta --out-file pdb-clusters --perc-id 60
```
where `pdb-clusters` is a file where the calculated clusters will be
stored, and `--perc-id` represents the percent identity threshold used to cluster
the sequences.

> Implementation note: CD-HIT does not cluster PDB structures directly, and 
> this script internally filters the sequences in
> [the PDB provided sequences](https://files.rcsb.org/pub/pdb/derived_data/pdb_seqres.txt.gz)
> by using only those tagged as `:protein`. If you're using a different FASTA
> header format and don't need this skipping step, please add `--skip-pdb-filter`
> to the command above. 
>
> Also, CD-HIT will generate intermediary files, and if you're using Docker, 
> these will be placed on the output path, which is relative to the current
> working directory of the container.


#### AlphaFold Modeling

Assuming all domains where already generated, we provide a script to invoke the
AlphaFold prediction script in parallel. You must ensure that alphafold is 
installed and accessible, and you must configure the correct command into 
`AF_PREDICT` either as an environment variable or into a `.env` file (examples
are provided in the repository). Then simply run:

```bash
python SIF.py generate-models -i sequences.fasta -d domains.tsv --out data/structural-models/
```

where `sequences.fasta` contains the full sequences of every protein you want
to consider, `data/domains.tsv` is the path to a file where the domains
are stored, and `data/structural-models/` is the path to a directory where the 
models will be stored.

> __Important:__ if you're using Docker for `AF_PREDICT`, remember that 
> `sequences.fasta` and `data/domains.tsv` needs to be a path relative to the
> configured volume, while the other paths are relative to the host.

### Structural Neighbors

You can identify structural neighbors running the following command:

```bash
python SIF.py structural-neighborhood --seq sequences.fasta --domains data/domains/ --str-models data/structural-models --out data/structural-neighborhood --tau 0.6
```

where `sequences.fasta` contains the full sequences of every protein you want
to consider, `data/domains/` is the path to a directory where the domains
are stored, and `data/structural-models/` is the path to a directory where the 
models are stored, and `data/structural-neighborhood` is the path to a 
directory where the structural neighborhood will be stored.

### Interaction templates

Once structural neighbors have been identified, you can find the interaction 
templates (neighbors on the same PDB complex) running

```bash
python SIF.py find-interaction-templates --str-neigh data/structural-neighborhood --out data/interaction-templates.tsv
```

where `data/structural-neighborhood` is the path to a 
directory where the structural neighborhood are stored, and 
`data/interaction-templates.tsv` is the path to a file where the interaction
templates will be stored.

### Structure-based alignment

This is the last step of the pipeline, simply run:

```bash
python SIF.py calculate-features --str-neigh data/structural-neighborhood --str-models data/structural-models --out data/structural-features.tsv
```

where `data/structural-models/` is the path to a directory where the 
models are stored, and `data/structural-neighborhood` is the path to a 
directory where the structural neighborhood are stored, and 
`data/structural-features.tsv` is the path to the output file containing the
calculated features. 
