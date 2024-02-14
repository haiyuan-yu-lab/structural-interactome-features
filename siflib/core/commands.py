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


def ska_database(args, config):
    from siflib.io.ska_wrapper import run
    run(Path(args.query_info),
        Path(args.database_info),
        Path(args.output_dir),
        args.submat,
        args.trolltop,
        args.bin,
        args.psd_threshold,
        args.array_idx,
        args.batch_size)
