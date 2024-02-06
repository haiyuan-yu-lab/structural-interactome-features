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


