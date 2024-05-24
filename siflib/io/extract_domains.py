from pathlib import Path
import logging
from siflib.io.parsers import parse_fasta, parse_cd_hit, parse_ecod_domains
log = logging.getLogger(__name__)


def extract_domains(domains_file: Path,
                    fasta_file: Path,
                    out_file: Path):
    log.info("reading domains")
    domains = parse_cd_hit(domains_file)
    log.info("reading FASTA file")
    fasta = parse_fasta(fasta_file, uniprot_header=False, skip_metadata=True)
    with out_file.open("w") as of:
        for accession, seq_info in fasta.items():
            for i, match in enumerate(domains.get(accession, [])):
                of.write(f'>{accession}-D{i}'
                         f' CDD_ID={match["subject acc.ver"]}'
                         f' evalue={match["evalue"]}'
                         f' perc_id={match["% identity"]}\n')
                start = match["q. start"] - 1
                end = match["q. end"]
                domain_seq = seq_info["sequence"][start:end]
                of.write(f"{domain_seq}\n")


def extract_domains_ecod(pdb_chains_file: Path,
                         ecod_domains_file: Path,
                         out_file: Path):
    log.info("reading domains")
    domains = parse_ecod_domains(ecod_domains_file)
    log.info("reading PDB chains")
    targets = []
    with pdb_chains_file.open() as f:
        for line in f:
            targets.append(line.strip())
    with out_file.open("w") as of:
        of.write("#pdb_chain\tecod_uid\tecod_domain_id\n")
        for target in targets:
            for match in domains.get(target, []):
                of.write(f'{target}\t'
                         f'{match["pdb_range"]}\t'
                         f'{match["ecod_domain_id"]}\t'
                         f'{match["uid"]}\n')
