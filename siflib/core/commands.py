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


def create_ecod_pdbs(args, config):
    from siflib.io.create_ecod_pdbs import create_ecod_pdbs
    pdb_dir = Path(args.pdb_dir)
    ecod_mapping_file = Path(args.ecod_mapping_file)
    out_dir = Path(args.out_dir)
    create_ecod_pdbs(pdb_dir, ecod_mapping_file, out_dir)


def extract_chains(args, config):
    from siflib.io.extract_chains import run
    in_dir = Path(args.in_dir)
    run(in_dir)


def ska_database(args, config):
    from siflib.io.ska_wrapper import run
    num_cpu = None if args.cpu_count <= 0 else args.cpu_count
    run(Path(args.query_info),
        Path(args.database_info),
        Path(args.output_dir),
        args.submat,
        args.trolltop,
        args.bin,
        args.array_idx,
        args.batch_size,
        num_cpu)


def ska_database_map(args, config):
    from siflib.io.ska_wrapper import run_with_mapping
    num_cpu = None if args.cpu_count <= 0 else args.cpu_count
    run_with_mapping(Path(args.query_info),
                     Path(args.database_info),
                     Path(args.mapping_file),
                     Path(args.output_dir),
                     args.submat,
                     args.trolltop,
                     args.bin,
                     args.array_idx,
                     args.batch_size,
                     num_cpu)


def get_neighborhood_clusters(args, config):
    from siflib.core.neighborhood import get_neighborhood_clusters
    num_cpu = None if args.cpu_count <= 0 else args.cpu_count
    get_neighborhood_clusters(Path(args.targets),
                              Path(args.ska_dir),
                              Path(args.domain_ska_dir),
                              Path(args.ecod_mapping_file),
                              Path(args.output_file),
                              args.psd_threshold,
                              num_cpu)


def expand_neighborhood_clusters(args, config):
    from siflib.core.neighborhood import expand_neighborhood_clusters
    expand_neighborhood_clusters(Path(args.in_file),
                                 Path(args.cdhit_clusters),
                                 Path(args.pdb_dir),
                                 Path(args.ska_output_file),
                                 Path(args.mapping_output_file),
                                 )


def extract_ska_alignments(args, config):
    from siflib.io.extract_alingments import (extract_alignments_ska_dir,
                                              extract_alingments_to_file)
    extract_alingments_to_file(
        extract_alignments_ska_dir(Path(args.ska_dir)),
        Path(args.output_file)
    )


def extract_homstrad_alignments(args, config):
    from siflib.io.extract_alingments import (extract_alignments_homstrad_file,
                                              extract_alingments_to_file)
    extract_alingments_to_file(
        extract_alignments_homstrad_file(Path(args.homstrad_file)),
        Path(args.output_file)
    )


def evaluate_alignment(args, config):
    fkkk
