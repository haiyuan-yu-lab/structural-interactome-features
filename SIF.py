"""
This script is the main entrypoint for all commands related

Usage:
    python SIF.py <command>

Each command supports a -h flag that explains its purpose and arguments.
"""
from siflib.core import commands
import logging
logging.basicConfig(format="[%(asctime)s](%(levelname)s - %(module)s)"
                    " %(message)s",
                    datefmt="%Y-%m-%d %I:%M:%S %p",
                    level=logging.INFO)

if __name__ == "__main__":
    from dotenv import dotenv_values
    import argparse

    config = dotenv_values(".env")

    parser = argparse.ArgumentParser(
        description="Structurally Informed Features"
    )
    subparsers = parser.add_subparsers(
        help="sub-command help",
        dest="subcommand")

    # Extract Domains
    extract_domains = subparsers.add_parser(
        "extract-domains",
        help="Given the output of rpsblast and the query FASTA used"
             " during the searh, extract the sequences for each domain"
             " found in the search.",
    )

    extract_domains.set_defaults(func=commands.extract_domains)
    extract_domains.add_argument("-i", "--in-file",
                                 help="Path to the results of CDD search",
                                 type=str,
                                 required=True)
    extract_domains.add_argument("-f", "--fasta-file",
                                 help="Path to the target sequences used in"
                                 " CDD search (FASTA FORMAT).",
                                 type=str,
                                 required=True)
    extract_domains.add_argument("-o", "--out-file",
                                 help="Path to the output file (FASTA format)",
                                 type=str,
                                 required=True)

    # Extract Chains
    extract_chains = subparsers.add_parser(
        "extract-chains",
        help="Given a directory, recursively read all .pdb and .ent.gz"
             " files and extracts individual chains into pdb files. All"
             " files will be named <pdb_id>_<chain_id>.pdb, even when"
             " .ent.gz files are being processed. Files will be saved on"
             " the same subdirectory as the corresponding input file.",
    )

    extract_chains.set_defaults(func=commands.extract_chains)
    extract_chains.add_argument("-i", "--in-dir",
                                help="Path to a directory containing PDB files"
                                     " with .pdb or .ent.gz extensions",
                                type=str,
                                required=True)

    # Make SKA database
    ska_db = subparsers.add_parser(
        "ska-db",
        help="given two lists of PDB files and their respective Paths, uses"
             " ska to build a pairwise database in an output directory.",
    )

    ska_db.set_defaults(func=commands.ska_database)
    ska_db.add_argument("-q", "--query-info", required=True,
                        help="Path to a query map from ID to Path (tsv)")
    ska_db.add_argument("-d", "--database-info", required=True,
                        help="Path to a query map from ID to Path (tsv)")
    ska_db.add_argument("-o", "--output-dir", required=True,
                        help="Path to the output directory")
    ska_db.add_argument("-s", "--submat", required=True,
                        help="value for the SUBMAT environment variable")
    ska_db.add_argument("-b", "--bin", required=True,
                        help="Path to the ska binary")
    ska_db.add_argument("-r", "--trolltop", required=True,
                        help="value for the TROLLTOP environment variable")
    ska_db.add_argument("-i", "--array-idx", type=int, required=True,
                        help="Index of the query to run")
    ska_db.add_argument("-n", "--batch-size", type=int, required=True,
                        help="Batch size for the inner loop")
    ska_db.add_argument("-c", "--cpu-count", type=int, default=-1,
                        help="Number of cores to use for parallel processing")
    # Parse the arguments and route the function call
    args = parser.parse_args()
    if args.subcommand == 'predict':
        if args.run_config is None and (args.alias is None or args.obo is None
                                        or args.fasta is None):
            parser.error('If no run configuration is provided, '
                         'you must provide the following arguments:\n'
                         '\t--alias\n'
                         '\t--obo\n'
                         '\t--fasta')

    try:
        args.func(args, config)
    except AttributeError as e:
        print(e)
        parser.parse_args(['--help'])


