from pathlib import Path
import logging
from siflib.io.parsers import parse_fasta, parse_cd_hit
log = logging.getLogger(__name__)


def run(domains_file: Path,
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
