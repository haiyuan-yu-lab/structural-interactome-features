from pathlib import Path


def cdhit_cluster(args):
    pass


def pdb_ex_seqs(args):
    pass


def cdd_search(args):
    from siflib.io.cdd_search import run
    from siflib.io.parsers import parse_fasta
    in_file = Path(args.in_file)
    out_file = Path(args.out_file)
    sequences = parse_fasta(in_file)
    # Set default values
    params = {
        "cdsid": "",
        "cddefl": "false",
        "qdefl": "false",
        "smode": "auto",
        "useid1": "true",
        "maxhit": 250,
        "filter": "true",
        "db": "cdd",
        "evalue": 0.01,
        "dmode": "rep",
        "clonly": "false",
        "tdata": "hits"
    }
    run(params, sequences, out_file)


def generate_models(args):
    pass
