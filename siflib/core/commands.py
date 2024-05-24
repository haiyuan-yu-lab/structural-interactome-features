from pathlib import Path
import logging
log = logging.getLogger(__name__)


def extract_domains(args, config):
    from siflib.io.extract_domains import extract_domains
    in_file = Path(args.in_file)
    fasta_file = Path(args.fasta_file)
    out_file = Path(args.out_file)
    extract_domains(in_file, fasta_file, out_file)


def extract_domains_ecod(args, config):
    from siflib.io.extract_domains import extract_domains_ecod
    pdb_chains_file = Path(args.pdb_chains_file)
    ecod_domains_file = Path(args.ecod_domains_file)
    out_file = Path(args.out_file)
    extract_domains_ecod(pdb_chains_file, ecod_domains_file, out_file)


def extract_chains(args, config):
    from siflib.io.extract_chains import run
    in_dir = Path(args.in_dir)
    run(in_dir)


def ska_database(args, config):
    from siflib.io.ska_wrapper import run
    cc = None if args.cpu_count <= 0 else args.cpu_count
    run(Path(args.query_info),
        Path(args.database_info),
        Path(args.output_dir),
        args.submat,
        args.trolltop,
        args.bin,
        args.array_idx,
        args.batch_size,
        cc)
