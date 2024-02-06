# structural-interactome-features
Toolkit to derive structural features for interacting proteins

The pipeline is ispired by [PrePPI](https://doi.org/10.1016/j.jmb.2023.168052),
but this project does not focus on predicting interactions, but rather compute
useful structurally-informed features for proteins and pairs of proteins.

# Installation instructions

Please install all the required python packages running:

```bash
pip install -r requirements.txt
```

# External Requirements

- [AlphaFold](https://github.com/google-deepmind/alphafold)
- [CD-HIT](https://github.com/weizhongli/cdhit)
- [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cdd_help.shtml#RPSBFtp) (we provide a script to perform the search, but you must install CDDs requirements and get the data)
- [ska](https://honig.c2b2.columbia.edu/ska) (We provide bash scripts to perform the alignment, but we don't have permission to redistribute the software, you must obtain a licence to run this.)
- [PeSTo](https://github.com/LBM-EPFL/PeSTo) (We provide bash scripts to run PeSTo, assuming you have installed a proper Docker image in your system. You may modify this by configuring the environment variables in the `.env` file)

# Configuration Variables

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

For a full list of the required variables please look at the example
[.env](dot.env.example) file provided in this repository.

# Pipeline steps

1. download required datasets. If you've already downloaded the files, please [create a configuration file](#example-configuration-file) before continuing.
2. run CD-HIT to cluster PDB sequences at 60% identity, (both full sequences and domains)
3. Build the blast database for CDD domains.
4. Use `rpsblast` against CDD on the target sequences to identify domains on the queries
5. Extract domain sequences from the BLAST results
6. get AlphaFold models from AlphaFoldDB (or run AlphaFold for those that don't have an entry avaiable throug the API)
7. generate the structural neighborhood
8. calculate structural features 

For more details please read the [main.sh](main.sh) script provided in this 
repository
