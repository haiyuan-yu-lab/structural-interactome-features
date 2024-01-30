from pathlib import Path
import subprocess
import logging
log = logging.getLogger(__name__)


def run(fasta: Path,
        domains_file: Path,
        out_file: Path,
        cdd_bin: str):
    cmd = (f"{cdd_bin} -query {fasta} -db cddalias -seg no"
           " -comp_based_stats 1 -evalue 0.01 -outfmt 7"
           f" > {domains_file}")
    log.info(f"calling: {cmd}")
    subprocess.call(cmd, shell=True)
