from pathlib import Path
from typing import Dict, Optional
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


def parse_cdd(cdd_file: Path) -> Dict:
    """
    Parses the output of rpsblast

    Parameters
    ----------
    cdd_file : Path
        Path to the output file produced by rpsblast

    Returns
    -------
    Dict
        A dictionary with the following structure:
        {
            "query acc.ver": [{
                "subject acc.ver": "..."
                "% identity": "...",
                "alignment length": "...",
                "mistmatches": "...",
                "gap opens": "...",
                "q. start": "...",
                "q. end": "...",
                "s. start": "...",
                "s. end": "...",
                "evalue": "...",
                "bit socre": "..."
            },
            ...],
            ...
        }
    """
    assert cdd_file.is_file()
    domains = {}
    with cdd_file.open() as f:
        for line in f:
            if line.startswith("#"):
                continue
            (qacc, sacc, pid, al, mism,
             gop, qs, qe, ss, se, ev, bs) = line.strip().split("\t")
            if qacc not in domains.keys():
                domains[qacc] = []
            domains[qacc].append({
                "subject acc.ver": sacc,
                "% identity": float(pid),
                "alignment length": int(al),
                "mistmatches": int(mism),
                "gap opens": int(gop),
                "q. start": int(qs),
                "q. end": int(qe),
                "s. start": int(ss),
                "s. end": int(se),
                "evalue": float(ev),
                "bit socre": float(bs)
            })
    return domains


def parse_cdhit_clusters(cdhit_file: Path) -> Dict:
    """
    Parses CD-HIT cluster files

    Parameters
    ----------
    cdhit_file : Path
        Path to a cluster definition file generated with CD-HIT

    Returns
    -------
    Dict
        A dictionary with the following structure:
        {
            "Cluster id":{
                "representative": <representative accession>,
                "members": [
                    {
                        "qty_aminoacids": "...",
                        "accession": "...",
                        "perc_id": "...",
                        "representative": "...",
                    },
                    ...
                ],
            }
            ...
        }
    """

    def get_perc(perc):
        if "%" in perc:
            return float(perc.split()[-1][:-1]), False
        return 100.0, True
    clusters = {}
    key = None
    with cdhit_file.open() as cdh:
        for line in cdh:
            if line.startswith(">Cluster"):
                key = line.strip()[1:]
                clusters[key] = {
                    "members": [],
                }
            else:
                _, aa, member, perc = line.strip().split(maxsplit=3)
                perc_id, repr = get_perc(perc)
                clusters[key]["members"].append({
                    "qty_aminoacids": aa[:-1],
                    "accession": member[1:-3],
                    "perc_id": perc_id,
                    "representative": repr,
                })
                if repr:
                    clusters[key]["representative"] = member[1:-3]
    return clusters


def parse_ecod_domains(ecod_domains_file: Path) -> Dict:
    """
    Parses ECOD `domain.txt` files

    Parameters
    ----------
    ecod_domains_file : Path
        Path to the ECOD `domain.txt` files

    Returns
    -------
    Dict
        A dictionary with the following structure:
        {
            "<PDB ID>_<PDB chain>": [{
                "uid": "...",
                "ecod_domain_id": "...",
                "manual_rep": "...",
                "t_id": "...",
                "pdb": "...",
                "chain": "...",
                "pdb_range": "...",
                "seqid_range": "...",
                "unp_acc": "...",
                "arch_name": "...",
                "x_name": "...",
                "h_name": "...",
                "t_name": "...",
                "f_name": "...",
                "asm_status": "...",
                "ligand": "...",
            },
            ...],
            ...
        }
    """
    assert ecod_domains_file.is_file()
    domains = {}
    with ecod_domains_file.open() as f:
        for line in f:
            if line.startswith("#"):
                continue
            (uid, ecod_domain_id, manual_rep, t_id, pdb, chain, pdb_range,
             seqid_range, unp_acc, arch_name,
             x_name, h_name, t_name, f_name,
             asm_status, ligand) = line.strip().split("\t")
            key = f"{pdb}_{chain}"
            if key not in domains.keys():
                domains[key] = []

            # pdbr_chain, pdbr_range = pdb_range.split(":")
            # pdbr_start, pdbr_end = pdbr_range.split("-")
            # seqidr_chain, seqidr_range = seqid_range.split(":")
            # seqidr_start, seqidr_end = seqidr_range.split("-")
            domains[key].append({
                "uid": uid,
                "ecod_domain_id": ecod_domain_id,
                "manual_rep": manual_rep,
                "t_id": t_id,
                "pdb": pdb,
                "chain": chain,
                "pdb_range": pdb_range,
                "seqid_range": seqid_range,
                "unp_acc": unp_acc,
                "arch_name": arch_name,
                "x_name": x_name,
                "h_name": h_name,
                "t_name": t_name,
                "f_name": f_name,
                "asm_status": asm_status,
                "ligand": ligand,
            })
    return domains


def parse_ska_db(ska_file: Path,
                 psd_threshold: Optional[float] = None) -> Dict:
    """
    Parses files generated by our `ska-db` command

    Parameters
    ----------
    ska_file : Path
        Path to the ECOD `domain.txt` files
    psd_threshold : float, optional
        if provided, only PSD values below this threshold will be included in
        the result.

    Returns
    -------
    Dict
        A dictionary with the following structure:
        {
            "<query>":{
                "<subject>": {
                    "PSD": "...",
                    "RMSD": "...",
                    "alignment": {
                                    "start_query": "..."
                                    "sse_query": "..."
                                    "seq_query": "..."
                                    "start_subject": "..."
                                    "sse_subject": "..."
                                    "seq_subject": "..."
                                 }
                },
                ...
            },
            ...
        }

    Note
    ----

    for a given query and subject, if there is an alignmet error in the SKA
    file, the subject entry won't be added.
    """
    # TODO(mateo): resSeq appears with iCode sometimes, maybe fix this
    if psd_threshold is None:
        psd_threshold = float("inf")
    ska_matches = {}
    query = ""
    subject = ""
    current_match = {
        "alignment": {
            "sse_query": "",
            "seq_query": "",
            "sse_subject": "",
            "seq_subject": ""
        }
    }
    with ska_file.open() as db:
        for line in db:
            if line.startswith("SKA:"):
                if all([query, subject, "PSD" in current_match]) and \
                        current_match["PSD"] <= psd_threshold:
                    if query not in ska_matches:
                        ska_matches[query] = {}
                    ska_matches[query][subject] = current_match
                _, pair = line.strip().split(":")
                quer, subj = pair.split(",")
                _, query = quer.split("=")
                _, subject = subj.split("=")
                current_match = {
                    "alignment": {
                        "sse_query": "",
                        "seq_query": "",
                        "sse_subject": "",
                        "seq_subject": ""
                    }
                }
            elif line.startswith("RMSD"):
                _, rmsd = line.strip().split(":")
                rmsd = float(rmsd)
                current_match["RMSD"] = rmsd
            elif line.startswith("PSD"):
                _, psd = line.strip().split(":")
                psd = float(psd)
                current_match["PSD"] = psd
            elif line.strip().startswith("tc_sse:"):
                # get query alignment
                row = line.split()
                if len(row) == 3\
                        and "start_query" not in current_match["alignment"]:
                    # current_match["alignment"]["start_query"] = int(row[1])
                    # PDB ID/index of first residue in query
                    current_match["alignment"]["start_query"] = row[1]
                current_match["alignment"]["sse_query"] += row[-1]
                next_line = db.readline()
                last = next_line.split()[-1]
                current_match["alignment"]["seq_query"] += last

                # get subject alignment
                next_line = db.readline()
                row = next_line.split()
                if len(row) == 3 \
                        and "start_subject" not in current_match["alignment"]:
                    # current_match["alignment"]["start_subject"] = int(row[1])
                    # PDB ID/index of first residue in subject
                    current_match["alignment"]["start_subject"] = row[1]
                current_match["alignment"]["sse_subject"] += row[-1]
                next_line = db.readline()
                last = next_line.split()[-1]
                current_match["alignment"]["seq_subject"] += last

    if all([query, subject, "PSD" in current_match]) and\
            current_match["PSD"] <= psd_threshold:
        if query not in ska_matches:
            ska_matches[query] = {}
        ska_matches[query][subject] = current_match
    return ska_matches


def parse_homstrad_alignments(homstrad_file: Path):
    """
    Parses the `homstrad_alignments.txt` file distributed with Foldseek

    Parameters
    ----------
    homstrad_file : Path
        Path to the `homstrad_alignments.txt` files

    Returns
    -------
    Dict
        A dictionary with the following structure:
        {
            "<query>":{
                "<subject>": {
                    "<method>": {
                        "sensitivity": "...",
                        "precision": "...",
                        "alignment": {
                            "start_query": "..."
                            "seq_query": "..."
                            "start_subject": "..."
                            "seq_subject": "..."
                         }
                    },
                },
                ...
            },
            ...
        }

    Note
    ----
    Header lines in the `homstrad_alingments.txt` file should be unmodified,
    and have the following structure:
    >prot_name acc1 acc2 method_name sensitivity: <value> precision: <value>
    """
    res = {}
    with homstrad_file.open() as hf:
        current_elem = None
        for line in hf:
            if line.startswith(">"):
                pname, a1, a2, me, _, s, _, p = line[1:].strip().split()
                try:
                    s = float(s)
                except ValueError:
                    s = 0.0
                try:
                    p = float(p)
                except ValueError:
                    p = 0.0
                if a1 not in res:
                    res[a1] = {}
                if a2 not in res[a1]:
                    res[a1][a2] = {}
                if me not in res[a1][a2]:
                    res[a1][a2][me] = {
                        "sensitivity": s,
                        "precision": p,
                        "seq_query": "",
                        "seq_subject": "",
                    }
                current_elem = res[a1][a2][me]
            elif line.strip():
                _, idx, seq = line.strip().split()
                if "start_query" not in current_elem:
                    current_elem["start_query"] = idx
                current_elem["seq_query"] += seq
                next_line = hf.readline()
                _, idx, seq = next_line.strip().split()
                if "start_subject" not in current_elem:
                    current_elem["start_subject"] = idx
                current_elem["seq_subject"] += seq
    return res
