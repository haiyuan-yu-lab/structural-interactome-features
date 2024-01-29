from pathlib import Path
from typing import Dict
import warnings
import re


def parse_fasta(fasta_file: Path,
                uniprot_header=True,
                skip_metadata=False) -> Dict:
    """
    Parses a fasta file and produces a dictionary that maps the accession ID
    to the sequence and other metadata if available.

    Parameters
    ----------
    fasta_file : Path
        Path to the FASTA file
    uniprot_header : bool, default True
        If true, parses the Protein ID line using the following header as
        defined by UniProt. "UniqueIdentifier" will be used as the accession ID
        and all other elements will be added as metadata to each element

        if False, everything after ">" will be used as the accession ID, and
        the only metadata will be the sequence
    skip_metadata : bool, default False
        If true, only "sequence" will be included in the resulting dictionary.

    Returns
    -------
    Dict
        A dictionary with the following structure:
        {
            "accession_id": {
                "sequence": "...", # only this one is guaranteed to be included
                "db": "..."
                "EntryName": "..."
                ...
            }
        }
    """
    assert fasta_file.is_file()
    uniprot_re = None
    if uniprot_header:
        regex = (r"^>(?P<db>[a-zA-Z]+)\|(?P<UniqueIdentifier>\w+)\|"
                 r"(?P<EntryName>\w+)\s(?P<ProteinName>.*)\s"
                 r"OS=(?P<OrganismName>.*)\sOX=(?P<OrganismIdentifier>\w*)\s"
                 r"(?:GN=(?P<GeneName>.*)\s)?PE=(?P<ProteinExistence>.*)\s"
                 r"SV=(?P<SequenceVersion>\w+).*$")
        uniprot_re = re.compile(regex)

    sequences = {}
    metadata = {}
    curr_seq = ""
    curr_acc = ""
    with fasta_file.open() as f:
        for line in f:
            if line.startswith(">"):
                if curr_seq != "":
                    sequences[curr_acc] = {
                        "sequence": curr_seq
                    }
                    if not skip_metadata:
                        for m, v in metadata.items():
                            sequences[curr_acc][m] = v
                        metadata = {}
                    curr_seq = ""
                if uniprot_header:
                    match = uniprot_re.match(line)
                    if match:
                        metadata = match.groupdict()
                        curr_acc = metadata["UniqueIdentifier"]
                    else:
                        warnings.warn("Could not parse header, defaulting to"
                                      f"simple header for this entry {line}")
                        curr_acc = line[1:].split()[0]
                else:
                    curr_acc = line[1:].split()[0]
            else:
                curr_seq += line.strip()
    return sequences


def parse_cd_hit(cd_hit_file: Path) -> Dict:
    pass
