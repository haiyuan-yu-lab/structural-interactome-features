from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Optional, Dict, Tuple
from siflib.io.parsers import parse_ska_db
import logging
import queue
import threading
log = logging.getLogger(__name__)


def _get_neighboorhood_clusters_worker(target: str,
                                       ska_file: Path,
                                       domain_file: Path,
                                       ecod_mapping_file: Path,
                                       psd_threshold: float,
                                       ) -> Tuple[str, Dict[str, float]]:
    """
    returns a list of cluster representatives that match to the target with 
    a PSD <= `psd_threshold` either directly or through one of the component
    ECOD domains.


    Parameters
    ----------
    target: str
        the query to be processed, it is used to keep track of the results only
    ska_file: Path
        Path to the SKA-db result file
    domain_file: Path
        Path to the domain SKA-db result file
    ecod_mapping_file: Path
        Path to the ECOD `domain.txt` files
    psd_threshold : float, optional
        if provided, only PSD values below this threshold will be included in
        the result.

    Returns
    -------
    str
        `target`
    Dict
        Keys are subjects found in `ska_file`, and the value is the minimum
        PSD found to it or one of its domains.
    """
    results = {}
    # domain to list of chains
    ecod_mapping = {}

    with ecod_mapping_file.open() as emf:
        for line in emf:
            if line.startswith("#"):
                continue
            pdb_chain, _, ecod_domain_id, _ = line.strip().split("\t")
            if ecod_domain_id not in ecod_mapping:
                ecod_mapping[ecod_domain_id] = []
            ecod_mapping[ecod_domain_id].append(pdb_chain)
    ska_matches = parse_ska_db(ska_file,
                               psd_threshold=psd_threshold)
    ska_domain_matches = parse_ska_db(domain_file,
                                      psd_threshold=psd_threshold)

    # from the full mapping, representatives are added directly
    for subject, scores in ska_matches.items():
        if subject not in results:
            results[subject] = scores["PSD"]
        results[subject] = min(results[subject], scores["PSD"])

    # from the domain mapping, representatives need checked in the mapping
    for domain, scores in ska_domain_matches.items():
        subjects = ecod_mapping.get(domain, [])
        for subject in subjects:
            if subject not in results:
                results[subject] = scores["PSD"]
            results[subject] = min(results[subject], scores["PSD"])
    return target, results


def get_neighborhood_clusters(targets_file: Path,
                              ska_directory: Path,
                              ska_domains_dir: Path,
                              ecod_mapping_file: Path,
                              output_file: Path,
                              psd_threshold: float,
                              num_cpu: Optional[int] = None):
    assert targets_file.is_file(), "The target file must be a file"
    assert ska_directory.is_dir(), "The SKA db is not a directory"
    assert ska_domains_dir.is_dir(), "The SKA domains db is not a directory"
    assert ecod_mapping_file.is_file(), "The ECOD mapping is not a file"
    assert psd_threshold > 0, "the PSD cutoff must be positive"
    log.info("Reading targets file")

    # contains tuples of (ska, domain) Paths
    targets = []
    with targets_file.open() as t:
        for line in t:
            target = line.strip()
            ska_file = ska_directory / f"{target}.ska"
            domain_file = ska_domains_dir / f"{target}.ska"
            if ska_file.is_file() and domain_file.is_file():
                targets.append((target, ska_file, domain_file))
            else:
                log.info(f"SKA files for {target} not found, skipping")
    total = len(targets)
    log.info(f"Checking {total} targets")

    results = {}
    results_queue = queue.Queue()

    def gatherer_worker():
        while True:
            target, data = results_queue.get()
            if target is None and data is None:
                break
            results[target] = data
            results_queue.task_done()

    gatherer_thread = threading.Thread(target=gatherer_worker)
    gatherer_thread.start()

    # TODO(mateo): make this into an argument if useful
    batch_size = 1000
    with ProcessPoolExecutor(max_workers=num_cpu) as executor:
        futures = []
        for i, (target, ska_file, domain_file) in enumerate(targets, start=1):
            futures.append(
                executor.submit(_get_neighboorhood_clusters_worker,
                                target, ska_file, domain_file,
                                ecod_mapping_file, psd_threshold)
            )
            if i % batch_size == 0 or i == total:
                log.info(f"submitted {i} jobs {i/total*100:.2f}%")
        log.info("Gathering results in parallel...")
        gathered = 0
        for future in as_completed(futures):
            results_queue.put(future.result())
            gathered += 1
            if gathered % batch_size == 0 or gathered == total:
                log.info(f"gathered {gathered} jobs {gathered/total*100:.2f}%")
    log.info("Submitting sentinel to queue...")
    results_queue.put(None, None)
    gatherer_thread.join()

    log.info(f"Writing results to {output_file}")
    with output_file.open("w") as of:
        of.write("target\trepresentative\tscore\n")
        for target, data in results.items():
            for representative, score in data.items():
                of.write(f"{target}\t{representative}\t{score}\n")
    log.info("Done")
