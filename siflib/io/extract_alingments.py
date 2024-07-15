from pathlib import Path
from typing import Dict
from siflib.io.parsers import parse_ska_db, parse_homstrad_alignments
import logging


log = logging.getLogger(__name__)


def extract_alignments_homstrad_file(homstrad_file: Path) -> Dict:
    """
    Extracts alignment dictionaries from a homstrad_file

    Parameters
    ----------
    homstrad_file : Path
        Path to the `homstrad_alignments.txt` files

    Returns
    -------
    Dict:
        keys are the tuple (acc1, acc2, method),
        and values are tuples (seq1, seq2)
    """
    res = {}
    homstrad_alignments = parse_homstrad_alignments(homstrad_file)
    for a1, data_a1 in homstrad_alignments.items():
        for a2, data_a2 in data_a1.items():
            for method, data_method in data_a2.items():
                key = (a1, a2, method)
                res[key] = (
                    data_method["start_query"],
                    data_method["seq_query"],
                    data_method["start_subject"],
                    data_method["seq_subject"]
                )
    return res


def extract_alignments_ska_dir(ska_dir: Path) -> Dict:
    """
    Extracts alignment dictionaries from a homstrad_file

    Parameters
    ----------
    ska_dir : Path
        Path to a directory containing .ska files

    Returns
    -------
    Dict:
        keys are the tuple (acc1, acc2, "ska"),
        and values are tuples (seq1, seq2)
    """
    res = {}
    for ska_file in ska_dir.glob("*.ska"):
        log.info(ska_file)
        ska_alignment = parse_ska_db(ska_file)
        for a1, data_a1 in ska_alignment.items():
            for a2, data_a2 in data_a1.items():
                key = (a1, a2, "ska")
                d = data_a2["alignment"]
                try:
                    res[key] = (
                        d["start_query"],
                        d["seq_query"],
                        d["start_subject"],
                        d["seq_subject"]
                    )
                except:
                    print(key)
                    continue


    return res


def extract_alingments_to_file(alignments: Dict, output_file: Path):
    pass
