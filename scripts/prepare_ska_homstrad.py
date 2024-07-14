from pathlib import Path
from typing import Tuple
import logging


logger = logging.getLogger('SKA-parallel-runner')
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    "%Y-%m-%d %H:%M:%S")
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)


def run(homstrad_file: Path, output_file: Path, pdb_dir: Path):

    def get_pdbfile(pdb: str) -> Tuple:
        pdb_subdir = pdb[1:3]
        if len(pdb) == 4:  # no chain
            candidates = sorted((pdb_dir / pdb_subdir).glob(f"pdb{pdb}*"))
            if len(candidates) == 1:
                return pdb, str(candidates[0])
        elif len(pdb) == 5:  # last char is the chain, case insensitive
            chain = pdb[-1]
            candidates = sorted((pdb_dir / pdb_subdir).glob(f"pdb{pdb}*"))
            for candidate in candidates:
                file_chain = str(candidate).split("_")[-1].replace(".pdb", "")
                if file_chain.upper() == chain.upper():
                    return pdb, str(candidate)
        return None, None

    pdbs = set()
    with homstrad_file.open() as hf:
        for line in hf:
            _, pdb1, pdb2 = line.strip().split()
        # we only want to keep the pairs with existing PDBs
        p1, path1 = get_pdbfile(pdb1)
        p2, path2 = get_pdbfile(pdb2)
        if p1 is not None and p2 is not None:
            pdbs.add((p1, path1))
            pdbs.add((p2, path2))

    with output_file.open("w") as of:
        for pdb, path in pdbs:
            of.write(f"{pdb}\t{path}\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Build a id to pdb path map for all required entries")
    parser.add_argument("-i", "--homstrad-pairs-file", required=True,
                        help="Path to a file with homstrad pairs (3 columns)")
    parser.add_argument("-p", "--pdb-dir", required=True,
                        help="Path to the PDB directory")
    parser.add_argument("-o", "--output-file", required=True,
                        help="Path to the output file")
    args = parser.parse_args()
    run(Path(args.homstrad_pairs_file),
        Path(args.output_file),
        Path(args.pdb_dir),
        )
