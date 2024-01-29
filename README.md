# structural-interactome-features
Toolkit to derive structural features for interacting proteins

The pipeline is ispired by [PrePPI](https://doi.org/10.1016/j.jmb.2023.168052),
but this project does not focus on predicting interactions, but rather compute
useful structurally-informed features for proteins and pairs of proteins.


## Requirements

- [AlphaFold](https://github.com/google-deepmind/alphafold)
- [CD-HIT](https://github.com/weizhongli/cdhit)
- [CDD-API](https://www.ncbi.nlm.nih.gov/Structure/cdd/cdd_help.shtml#BatchRPSBWebAPI) (we provide a script to perform the search, but you need to get your own API keys)
- [ska](https://honig.c2b2.columbia.edu/ska) (We provide bash scripts to perform the alignment, but we don't have permission to redistribute the software, you must obtain a licence to run this.)

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

### Data pre-processing

#### PDB Clustering

This relies on [CD-HIT](https://github.com/weizhongli/cdhit), used to generate
non-redundant representatives of a large corpus of proteins to generate the 
neighborhood without having to scan every protein in existence. 

If you need the full structural neighborhood, it is convenient to cluster every
sequence and domain found in the PDB database.

If `data/pdb/` is the directory containing the PDB files, please run the 
following commands to generate the clusters:

```bash
python SIF.py cdhit-cluster --in data/pdb/ --out data/pdb-clusters/ --perc-id 60
```

where `data/pdb-clusters/` is a directory where the calculated clusters will be
stored, and `--perc-id` represents the percent identity threshold used to cluster
the sequences.

> Implementation note: CD-HIT does not cluster PDB structures directly, and 
> this script internally runs the `pdb-extract-sequences` command first. You 
> may benefit from running this first, and using `--sequence-in` instead of
> `--in` when running `cdhit-cluster` to save time on subsequent runs.

#### Domain identification

Protein models are built from their full sequences, as well as the sequences of
their domains. To identify such domains, please run: 

```bash
python SIF.py cdd-search --in sequences.fasta --out data/domains/
```

where `sequences.fasta` contains the full sequences of every protein you want
to consider, and `data/domains/` is the path to a directory where the domains
will be stored.

#### AlphaFold Modeling

Assuming all domains where already generated, we provide a script to invoke the
AlphaFold prediction script in parallel. You must ensure that alphafold is 
installed and accessible, and you must configure the correct command into 
`AF_COMMAND` either as an environment variable or into a `.env` file (examples
are provided in the repository). Then simply run:

```bash
python SIF.py generate-models --in sequences.fasta --domains data/domains/ --out data/structural-models/
```

where `sequences.fasta` contains the full sequences of every protein you want
to consider, `data/domains/` is the path to a directory where the domains
are stored, and `data/structural-models/` is the path to a directory where the 
models will be stored.

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
