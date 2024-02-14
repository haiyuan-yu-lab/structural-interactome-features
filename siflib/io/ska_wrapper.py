from pathlib import Path
from typing import Dict, Tuple
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from subprocess import PIPE, STDOUT
import logging
log = logging.getLogger(__name__)


def run_ska(pdb1: str,
            pdb1_path: str,
            pdb2: str,
            pdb2_path: str,
            out_dir: Path,
            skabin: str,
            env: Dict) -> Tuple[str, str, float, float]:
    subdir = out_dir / pdb1[1:3]
    subdir.mkdir(exist_ok=True)
    outfile = subdir / f"{pdb1}-vs-{pdb2}"
    cmd = f"{skabin} {pdb1_path} {pdb2_path} &> {outfile}"
    subprocess.run(cmd, shell=True, env=env, stdout=PIPE, stderr=STDOUT)

    subdir = subdir / pdb2[1:3]
    subdir.mkdir(exist_ok=True)
    outfile = out_dir / f"{pdb2}-vs-{pdb1}"
    cmd = f"{skabin} {pdb1_path} {pdb2_path} &> {outfile}"
    subprocess.run(cmd, shell=True, env=env, stdout=PIPE, stderr=STDOUT)


def run(query_info: Path,
        database_info: Path,
        output_dir: Path,
        submat: str,
        trolltop: str,
        skabin: str,
        array_idx: int = 0,
        batch_size: int = 1000):
    env = {"TROLLTOP": trolltop, "SUBMAT": submat}

    query = {}
    with query_info.open() as qi:
        for line in qi:
            pdb_id, pdb_path = line.strip().split()
            query[pdb_id] = pdb_path
    query_list = sorted(query.keys())
    query_element = query_list[array_idx]
    database = {}
    log.info("collecting database info...")
    with database_info.open() as di:
        for line in di:
            pdb_id, pdb_path = line.strip().split()
            database[pdb_id] = pdb_path
    total = len(database)
    log.info(f"query = {query_element}")
    log.info(f"Total = {total}")
    with ProcessPoolExecutor() as executor:
        query_path = query[query_element]
        batch = []
        overall_progress = 0
        curr_batch = 1
        for i, (pdb_id, pdb_path) in enumerate(database.items()):
            batch.append(
                executor.submit(run_ska(query_element, query_path,
                                        pdb_id, pdb_path, output_dir,
                                        skabin, env))
            )
            if i % batch_size == 0 or i == total:
                log.info(f"submitted {i} jobs, current batch: {curr_batch}")
                for future in as_completed(batch):
                    overall_progress += 1
                log.info(f"{overall_progress} runs at batch {curr_batch}")
                log.info(f"{overall_progress/total*100:.2f}%")
                curr_batch += 1
                batch = []


# This version is a parallel version that only extracts the PSD values.
# It is kept here to have a reference implementation for later, but the main
# entrypoint for the wrapper should be `run` above.
def run_ska_psd(pdb1: str,
                pdb1_path: str,
                pdb2: str,
                pdb2_path: str,
                skabin: str,
                env: Dict) -> Tuple[str, str, float, float]:
    psd_ab = float("inf")
    psd_ba = float("inf")

    cmd = f"{skabin} {pdb1_path} {pdb2_path}"
    pab = subprocess.run(cmd, shell=True, env=env, stdout=PIPE, stderr=STDOUT)
    rab = pab.stdout
    for line in rab.split("\n"):
        if line.startswith("Structure alignment error"):
            break
        elif line.startswith("PSD"):
            psd_ab = float(line.strip().split()[-1])

    if psd_ab < 10:
        cmd = f"{skabin} {pdb2_path} {pdb1_path}"
        pba = subprocess.run(cmd, shell=True, env=env,
                             stdout=PIPE, stderr=STDOUT)
        rba = pba.stdout
        for line in rba.split("\n"):
            if line.startswith("Structure alignment error"):
                break
            elif line.startswith("PSD"):
                psd_ba = float(line.strip().split()[-1])

    return pdb1, pdb2, psd_ab, psd_ba