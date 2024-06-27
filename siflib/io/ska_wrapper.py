from pathlib import Path
from typing import Dict, Tuple, Optional
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
import queue
import threading
from subprocess import PIPE, STDOUT
import logging
import io
import shutil


log = logging.getLogger(__name__)


def run_ska(pdb1: str,
            pdb1_path: str,
            pdb2: str,
            pdb2_path: str,
            skabin: str,
            env: Dict) -> Tuple[str, str, str]:
    cmd = f"{skabin} {pdb1_path} {pdb2_path}"
    p = subprocess.run(cmd, shell=True, env=env,
                       stdout=PIPE, stderr=STDOUT, text=True)
    return pdb1, pdb2, p.stdout


# This implementation writes each result to an individual file
def run_ska_file(pdb1: str,
                 pdb1_path: str,
                 pdb2: str,
                 pdb2_path: str,
                 out_dir: Path,
                 skabin: str,
                 env: Dict) -> None:
    subdir = out_dir / pdb1[1:3]
    subdir.mkdir(exist_ok=True)
    outfile = subdir / f"{pdb1}-vs-{pdb2}"
    if not outfile.exists():
        with outfile.open("w") as of:
            of.write(run_ska(pdb1, pdb1_path,
                             pdb2, pdb2_path,
                             skabin, env))


def run(query_info: Path,
        database_info: Path,
        output_dir: Path,
        submat: str,
        trolltop: str,
        skabin: str,
        array_idx: int = 0,
        batch_size: int = 1000,
        num_cpu: Optional[int] = None):
    env = {"TROLLTOP": trolltop, "SUBMAT": submat}

    query = {}
    with query_info.open() as qi:
        for line in qi:
            pdb_id, pdb_path = line.strip().split()
            query[pdb_id] = pdb_path
    query_list = sorted(query.keys())
    query_element = query_list[array_idx]
    log.info(f"query_list[{array_idx}] = {query_element}")

    outfile = output_dir / f"{query_element}.ska"
    donefile = output_dir / f"{query_element}.ska.done"

    if donefile.exists():
        log.info("Computation already finished, done")
        exit(0)

    database = {}
    log.info("collecting database info...")
    with database_info.open() as di:
        for line in di:
            pdb_id, pdb_path = line.strip().split()
            database[pdb_id] = pdb_path
    total = len(database)

    log.info(f"query = {query_element}")
    log.info(f"Total = {total}")

    results = {}
    results_queue = queue.Queue()

    def gatherer_worker():
        while True:
            _, subject, output = results_queue.get()
            if subject is None and output is None:
                break
            results[subject] = output
            results_queue.task_done()

    gatherer_thread = threading.Thread(target=gatherer_worker)
    gatherer_thread.start()

    with ProcessPoolExecutor(max_workers=num_cpu) as executor:
        query_path = query[query_element]
        futures = []
        for i, (pdb_id, pdb_path) in enumerate(database.items(), start=1):
            futures.append(
                executor.submit(run_ska, query_element, query_path,
                                pdb_id, pdb_path, skabin, env)
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
    results_queue.put((None, None, None))
    gatherer_thread.join()
    log.info("Building result buffer")
    result_buffer = io.StringIO()
    for key, output_str in results.items():
        result_buffer.write(f"SKA: query={query_element}, subject={key}\n")
        result_buffer.write(f"{output_str}\n")
    log.info(f"Writing results to {outfile}")

    with outfile.open("w") as of:
        shutil.copyfileobj(result_buffer, of)
    with donefile.open("w") as of:
        of.write("FINISHED")
    log.info("Done")


def run_with_mapping(query_info: Path,
                     database_info: Path,
                     mapping_file: Path,
                     output_dir: Path,
                     submat: str,
                     trolltop: str,
                     skabin: str,
                     array_idx: int = 0,
                     batch_size: int = 1000,
                     num_cpu: Optional[int] = None):
    env = {"TROLLTOP": trolltop, "SUBMAT": submat}

    log.info(f"Loading mapping file: {mapping_file}")
    query_pdb_id = ""
    jobs = []
    with mapping_file.open() as mf:
        curr_arr_idx = -1
        curr_query = None
        header = True
        for line in mf:
            if header:
                header = False
                continue
            q, cmember = line.strip().split()
            if q != curr_query:
                curr_query = q
                curr_arr_idx += 1
                if curr_arr_idx == array_idx:
                    query_pdb_id = q
                elif curr_arr_idx < array_idx:
                    continue
                else:
                    break
            if curr_arr_idx == array_idx:
                jobs.append(cmember)
    log.info(f"Number of comparisons for index {array_idx}: {len(jobs)}")

    query_element = "not_found"
    with query_info.open() as qi:
        for line in qi:
            pdb_id, pdb_path = line.strip().split()
            if pdb_id == query_pdb_id:
                query_element = pdb_path
    log.info(f"query_list[{array_idx}] = {query_element}")

    if query_element == "not_found":
        log.error(f"could not find path for {query_pdb_id}")
    outfile = output_dir / f"{query_element}.ska"
    donefile = output_dir / f"{query_element}.ska.done"

    if donefile.exists():
        log.info("Computation already finished, done")
        exit(0)

    database = {}
    log.info("collecting database info...")
    with database_info.open() as di:
        for line in di:
            pdb_id, pdb_path = line.strip().split()
            if pdb_id in jobs:
                database[pdb_id] = pdb_path
    total = len(database)

    log.info(f"query = {query_element}")
    log.info(f"Total = {total}")
    log.info(f"Total(jobs) = {len(jobs)}")

    results = {}
    results_queue = queue.Queue()

    def gatherer_worker():
        while True:
            _, subject, output = results_queue.get()
            if subject is None and output is None:
                break
            results[subject] = output
            results_queue.task_done()

    gatherer_thread = threading.Thread(target=gatherer_worker)
    gatherer_thread.start()

    with ProcessPoolExecutor(max_workers=num_cpu) as executor:
        query_path = query_element
        futures = []
        for i, (pdb_id, pdb_path) in enumerate(database.items(), start=1):
            futures.append(
                executor.submit(run_ska, query_element, query_path,
                                pdb_id, pdb_path, skabin, env)
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
    results_queue.put((None, None, None))
    gatherer_thread.join()
    log.info("Building result buffer")
    result_buffer = io.StringIO()
    for key, output_str in results.items():
        result_buffer.write(f"SKA: query={query_element}, subject={key}\n")
        result_buffer.write(f"{output_str}\n")
    log.info(f"Writing results to {outfile}")

    with outfile.open("w") as of:
        shutil.copyfileobj(result_buffer, of)
    with donefile.open("w") as of:
        of.write("FINISHED")
    log.info("Done")

# This is an earlier version that writes each result to a file, which may
# result in a I/O bottleneck


def run_file(query_info: Path,
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
        for i, (pdb_id, pdb_path) in enumerate(database.items(), start=1):
            batch.append(
                executor.submit(run_ska_file(query_element, query_path,
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
