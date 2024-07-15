from typing import List, Dict, Tuple
from pathlib import Path
import logging


log = logging.getLogger(__name__)


def evaluate_alignment(ground_truth: List[Tuple],
                       method_alignments: List[Tuple]) -> Dict:
    """
    Evaluates the sensitivity and precision of sequence alingments.

    Parameters
    ----------
    ground_truth: list of 4-tuples
        tuples are acc1, acc2, seq1, seq2. If len(seq1) != len(seq2), the entry
        will be ignored

    method_alignments: list of 4-tuples
        tuples are acc1, acc2, seq1, seq2. If len(seq1) != len(seq2), the entry
        will be ignored

    Returns
    -------
    Dict
        A dictionary with the following structure:
        {
            ("acc1", "acc2"):(sensitivity, precision),
        }
    """
