from pathlib import Path
import logging
log = logging.getLogger(__name__)


def cdhit_cluster(args, config):
    from siflib.io.cdhit_cluster import run
    assert "CDHIT_BIN" in config

    in_file = Path(args.in_file)
    out_file = Path(args.out_file)
    run(in_file, out_file, config["CDHIT_BIN"])


def cdd_search(args, config):
    from siflib.io.cdd_search import run
    assert "CDD_BIN" in config

    in_file = Path(args.in_file)
    domains_file = Path(args.domains_file)
    out_file = Path(args.out_file)
    run(in_file, out_file, domains_file, config["CDD_BIN"])


def generate_models(args, config):
    pass
