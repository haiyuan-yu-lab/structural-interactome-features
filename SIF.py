"""
This script is the main entrypoint for all commands related

Usage:
    python SIF.py <command>

Each command supports a -h flag that explains its purpose and arguments.
"""
from src.core import commands

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Structurally Informed Features"
    )
    subparsers = parser.add_subparsers(
        help="sub-command help",
        dest="subcommand")

    # CD-HIT Clustering
    cdhit_cluster = subparsers.add_parser(
        "chhit-cluster",
        description="CD-HIT cluster: invokes CD-HIT to cluster all sequences"
                    " in a directory",
        help="CD-HIT clustering is intended to cluster all the PDB files into"
             " a set of representative candidates to ensure a faster"
             " structural neighborhood calculation."
    )
    cdhit_cluster.set_defaults(func=commands.cdhit_cluster)
    cdhit_cluster.add_argument("-i", "--in",
                               help="Path to a directory containing PDB files",
                               type=str,
                               default="")
    cdhit_cluster.add_argument("-s", "--sequence-in",
                               help="Path to a directory containing sequences"
                                    " that match PDB files. If this argument"
                                    " is set, `--in` is ignored, and"
                                    " no call is made to"
                                    " pdb-extract-sequences",
                               type=str,
                               default="")
    cdhit_cluster.add_argument("-p", "--perc-id",
                               help="Percent identity threshold",
                               type=int,
                               default=60)
    cdhit_cluster.add_argument("-o", "--out",
                               help="Path to the output directory",
                               type=str,
                               required=True)

    # Extract PDB Sequences
    pdb_ex_seqs = subparsers.add_parser(
        "pdb-extract-sequences",
        description="Extract PDB Sequences: given a directory of PDBs, extract"
                    " the amino acid sequence of each chain",
        help="The naming of each sequence will be"
             " <pdb_id>-<modelno>-<chainname>"
    )

    pdb_ex_seqs.set_defaults(func=commands.pdb_ex_seqs)
    pdb_ex_seqs.add_argument("-i", "--in",
                             help="Path to a directory containing PDB files",
                             type=str,
                             required=True)
    pdb_ex_seqs.add_argument("-o", "--out",
                             help="Path to the output file",
                             type=str,
                             required=True)

    # CDD Search
    cdd_search = subparsers.add_parser(
        "cdd-search",
        description="CDD-Search: given a fasta file, identifies domains for"
                    " all sequences using the CDD-Search API",
        help="Remember to set the appropriate enviornment variables"
    )

    cdd_search.set_defaults(func=commands.cdd_search)
    cdd_search.add_argument("-i", "--in",
                            help="Path to a FASTA file containing all query"
                                 " sequences",
                            type=str,
                            required=True)
    cdd_search.add_argument("-o", "--out",
                            help="Path to the output file",
                            type=str,
                            required=True)

    # Generate Models
    generate_models = subparsers.add_parser(
        "generate-models",
        description="Generate Models: given a fasta file, and domains, invokes"
                    " AlphaFold to generate structures for all such sequences",
        help="Remember to set the appropriate enviornment variables"
    )

    generate_models.set_defaults(func=commands.generate_models)
    generate_models.add_argument("-i", "--in",
                                 help="Path to a FASTA file containing all"
                                      " query sequences",
                                 type=str,
                                 required=True)
    generate_models.add_argument("-d", "--domains",
                                 help="Path to the domains calculated using"
                                      " cdd-search",
                                 type=str,
                                 required=True)
    generate_models.add_argument("-o", "--out",
                                 help="Path to the output directory",
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
        args.func(args)
    except AttributeError as e:
        print(e)
        parser.parse_args(['--help'])


