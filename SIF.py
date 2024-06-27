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

    # Extract Domains ECOD
    extract_domains_ecod = subparsers.add_parser(
        "extract-domains-ecod",
        help="Given a list of PDB chains, and a `domains.txt` file from the"
             " ECOD database, produces a mapping file with the chain ID,"
             " ECOD uid, and ecod domain id into a tsv file. Note: a chain may"
             " be associated with multiple ECOD domains.",
    )

    extract_domains_ecod.set_defaults(func=commands.extract_domains_ecod)
    extract_domains_ecod.add_argument("-p", "--pdb-chains-file",
                                      help="Path to the file with a list of"
                                           " PDB chains",
                                      type=str,
                                      required=True)
    extract_domains_ecod.add_argument("-e", "--ecod-domains-file",
                                      help="Path to a ecod domains file",
                                      type=str,
                                      required=True)
    extract_domains_ecod.add_argument("-o", "--out-file",
                                      help="Path to the output file",
                                      type=str,
                                      required=True)

    # Create ECOD PDBs
    create_ecod_pdbs = subparsers.add_parser(
        "create-ecod-pdbs",
        help="Given a file with ectracted ECOD domains created with"
             " `extract-domains-ecod`, parses the PDB files and extracts each"
             " ECOD domain into a PDB file.",
    )

    create_ecod_pdbs.set_defaults(func=commands.create_ecod_pdbs)
    create_ecod_pdbs.add_argument("-p", "--pdb-dir",
                                  help="Path to a PDB directory. It must be"
                                       " indexed by the center of the PDB ID",
                                  type=str,
                                  required=True)
    create_ecod_pdbs.add_argument("-e", "--ecod-mapping-file",
                                  help="Path to a ecod mapping file (tsv)",
                                  type=str,
                                  required=True)
    create_ecod_pdbs.add_argument("-o", "--out-dir",
                                  help="Path to the output directory",
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

    # Make SKA database
    ska_db_map = subparsers.add_parser(
        "ska-db-map",
        help="the same as `ska-db`, taking an additional file mapping queries"
             " to subjects to avoid a full pairwise comparison.",
    )

    ska_db.set_defaults(func=commands.ska_database)
    ska_db.add_argument("-q", "--query-info", required=True,
                        help="Path to a query map from ID to Path (tsv)")
    ska_db.add_argument("-d", "--database-info", required=True,
                        help="Path to a query map from ID to Path (tsv)")
    ska_db.add_argument("-m", "--mapping-file", required=True,
                        help="Path to a query map from target to database")
    ska_db.add_argument("-o", "--output-dir", required=True,
                        help="Path to the output directory")
    ska_db.add_argument("-s", "--submat", required=True,
                        help="value for the SUBMAT environment variable")
    ska_db.add_argument("-b", "--bin", required=True,
                        help="Path to the ska binary")
    ska_db.add_argument("-r", "--trolltop", required=True,
                        help="value for the TROLLTOP environment variable")
    ska_db.add_argument("-i", "--array-idx", type=int, required=True,
                        help="Index of the query to run (will run this batch)")
    ska_db.add_argument("-n", "--batch-size", type=int, required=True,
                        help="Batch size")
    ska_db.add_argument("-c", "--cpu-count", type=int, default=-1,
                        help="Number of cores to use for parallel processing")

    get_neighborhood_clusters = subparsers.add_parser(
        "neighborhood-clusters",
        help="Gets the clusters where structural neighbors are located"
    )
    get_neighborhood_clusters.set_defaults(
        func=commands.get_neighborhood_clusters)
    get_neighborhood_clusters.add_argument("-t", "--targets",
                                           required=True,
                                           help="Path to a list of targets."
                                                " They should have"
                                                " precalculated ska-db files")
    get_neighborhood_clusters.add_argument("-s", "--ska-dir",
                                           required=True,
                                           help="Path to the ska-db directory")
    get_neighborhood_clusters.add_argument("-d", "--domain-ska-dir",
                                           required=True,
                                           help="Path to the domain-ska-db"
                                                " directory")
    get_neighborhood_clusters.add_argument("-e", "--ecod-mapping-file",
                                           required=True,
                                           help="Path to a ecod mapping file"
                                                " (tsv)",
                                           type=str)
    get_neighborhood_clusters.add_argument("-o", "--output-file",
                                           required=True,
                                           help="Path to the output file"
                                                " (tsv)")
    get_neighborhood_clusters.add_argument("-p", "--psd-threshold", type=float,
                                           default=0.6,
                                           help="SKA PSD cutoff")
    get_neighborhood_clusters.add_argument("-c", "--cpu-count", type=int,
                                           default=-1,
                                           help="Number of cores to use for"
                                                " parallel processing")

    # Extract Chains
    expand_clusters = subparsers.add_parser(
        "expand-clusters",
        help="Given the output of the `neighborhood-cluster` command, makes a"
             " file suitable to use in the `ska-db` command as a database.",
    )

    expand_clusters.set_defaults(func=commands.expand_neighborhood_clusters)
    expand_clusters.add_argument("-i", "--in-file",
                                 help="Path to a TSV file mapping queries to"
                                      " cluster representatives",
                                 type=str,
                                 required=True)
    expand_clusters.add_argument("-s", "--ska-output-file",
                                 help="Path to a TSV file suitable for use as"
                                      " a `ska-db` database file (will be"
                                      " created)",
                                 type=str,
                                 required=True)
    expand_clusters.add_argument("-m", "--mapping-output-file",
                                 help="Path to the tsv file mapping targets to"
                                      "cluster members (in TSV format)",
                                 type=str,
                                 required=True)
    expand_clusters.add_argument("-c", "--cdhit-clusters",
                                 help="Path to a CD-HIT output file, which "
                                      " must have the same cluster references"
                                      " as the `--in-file` argument",
                                 type=str,
                                 required=True)
    expand_clusters.add_argument("-p", "--pdb-dir",
                                 help="Path to a PDB directory. It must be"
                                      " indexed by the center of the PDB ID",
                                 type=str,
                                 required=True)

    # Parse the arguments and route the function call
    args = parser.parse_args()
    try:
        args.func(args, config)
    except AttributeError as e:
        print(e)
        parser.parse_args(['--help'])
