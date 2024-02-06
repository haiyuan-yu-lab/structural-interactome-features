from pathlib import Path
import logging
log = logging.getLogger(__name__)


def extract_domains(args, config):
    from siflib.io.extract_domains import run
    in_file = Path(args.in_file)
    fasta_file = Path(args.fasta_file)
    out_file = Path(args.out_file)
    run(in_file, fasta_file, out_file)


def extract_chains(args, config):
    from siflib.io.extract_chains import run
    in_dir = Path(args.in_dir)
    run(in_dir)
