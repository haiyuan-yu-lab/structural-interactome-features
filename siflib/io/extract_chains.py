from pathlib import Path
import logging
import gzip
from rich.progress import track
log = logging.getLogger(__name__)


def extract_chains(pdb_path: Path):
    ext = ".pdb"
    if pdb_path.name.endswith(".pdb"):
        lines = pdb_path.open().readlines()
    elif pdb_path.name.endswith(".ent.gz"):
        lines = gzip.open(pdb_path, "rt").readlines()
        ext = ".ent.gz"
    chains_lines = {}
    multimodel = False
    for line in lines:
        if line.startswith("MODEL"):
            multimodel = True
        elif line[0:6] in ["ATOM  ", "HETATM", "TER   "]:
            chain_id = line[21]
            if chain_id not in chains_lines:
                chains_lines[chain_id] = []
            chains_lines[chain_id].append(line)
        elif line.startswith("ENDMDL"):
            if multimodel:
                break
            else:
                log.error(f"Found ENDML without a MODEL {pdb_path}")
    for chain, clines in chains_lines.items():
        stem = pdb_path.name.replace(ext, '')
        outfile = pdb_path.parent / f"{stem}_{chain}.pdb"
        with outfile.open("w") as of:
            of.writelines(clines)


def run(in_dir: Path):
    log.info("searching for plain text PDBs (.pdb)")
    plain_texts = list(in_dir.glob("**/*.pdb"))
    log.info(f"found {len(plain_texts)} plain text PDBs")

    log.info("searching for gzipped PDBs (.ent.gz)")
    gzipped = list(in_dir.glob("**/*.ent.gz"))
    log.info(f"found {len(gzipped)} gzipped PDBs")

    for pdb in track(plain_texts + gzipped, description="extracting..."):
        extract_chains(pdb)
