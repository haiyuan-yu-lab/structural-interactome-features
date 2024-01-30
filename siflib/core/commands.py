from pathlib import Path
import logging
log = logging.getLogger(__name__)


def cdhit_cluster(args, config):
    pass


def pdb_ex_seqs(args, config):
    pass


def cdd_search(args, config):
    from siflib.io.cdd_search import run
    assert "CDD_BIN" in config

    in_file = Path(args.in_file)
    assert in_file.is_file()

    # domains file
    domains_file = Path(args.domains_file)
    out_file = Path(args.out_file)
    run(in_file, out_file, domains_file, config["CDD_BIN"])


def generate_models(args, config):
    pass
