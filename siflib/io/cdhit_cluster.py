from pathlib import Path
import subprocess
import logging
from siflib.io.parsers import parse_fasta
log = logging.getLogger(__name__)


def run(fasta: Path,
        out_file: Path,
        filter_pdb_fasta: bool,
        cdhit_bin: str):
    if filter_pdb_fasta:
        sequences. 
    cmd = (f"{cdhit_bin} -query {fasta} -db cddalias -seg no"
           " -comp_based_stats 1 -evalue 0.01 -outfmt 7"
           f" > {out_file}")
    log.info(f"calling: {cmd}")
    # subprocess.call(cmd, shell=True)
