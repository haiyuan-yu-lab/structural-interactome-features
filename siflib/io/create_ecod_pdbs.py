from pathlib import Path
from Bio.PDB import PDBParser, PDBIO
from Bio.PDB.PDBIO import Select
import logging
log = logging.getLogger(__name__)


class ECODDomain(Select):

    def __init__(self, residues):
        self.residues = residues

    def accept_residue(self, residue):
        if residue.get_id()[1] in self.residues:
            return 1
        return 0


def create_ecod_pdbs(pdbs_dir: Path,
                     chain_ranges: Path,
                     out_dir: Path):
    log.info("reading ranges")
    parser = PDBParser()
    with chain_ranges.open() as cr:
        for line in cr:
            if line.startswith("#"):
                continue
            pdb_chain, ranges, ecod_domain_id, _ = line.strip().split("\t")
            pdb_id, chain = pdb_chain.split("_")
            pdb_dir_index = pdb_id[1:3]
            source_pdb = pdbs_dir / pdb_dir_index / f"pdb{pdb_chain}.pdb"
            if not source_pdb.is_file():
                log.error(f"Couldn't find a suitable PDB file for {pdb_chain}")
                break
            s = parser.get_structure(pdb_chain, source_pdb)
            residues = []
            for r in ranges.split(","):
                _, ran = r.split(":")
                start, end = ran.split("-")
                residues.extend(range(int(start), int(end)+1))
            out_file = str(out_dir / f"{ecod_domain_id}.pdb")
            io = PDBIO()
            io.set_structure(s)
            io.save(out_file, ECODDomain(residues))
