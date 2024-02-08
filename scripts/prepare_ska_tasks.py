from pathlib import Path
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Tuple, Dict
import subprocess

logger = logging.getLogger('SKA-parallel-runner')
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    "%Y-%m-%d %H:%M:%S")
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)


def run_ska(pdb1: str,
            pdb1_path: str,
            pdb2: str,
            pdb2_path: str,
            tmp_dir: Path,
            bin: str,
            env: Dict) -> Tuple[str, str, float, float]:
    psd_ab = float("inf")
    psd_ba = float("inf")

    resfile_ab = tmp_dir / f"{pdb1}-vs-{pdb2}"
    cmd = f"{bin} {pdb1_path} {pdb2_path} > {resfile_ab}"
    subprocess.call(cmd, shell=True, env=env)
    with resfile_ab.open() as rab:
        for line in rab:
            if line.startswith("Structure alignment error"):
                break
            elif line.startswith("PSD"):
                psd_ab = float(line.strip().split()[-1])

    if psd_ab < 10:
        resfile_ba = tmp_dir / f"{pdb1}-vs-{pdb2}"
        cmd = f"{bin} {pdb2_path} {pdb2_path} > {resfile_ba}"
        subprocess.call(cmd, shell=True, env=env)
        with resfile_ba.open() as rba:
            for line in rba:
                if line.startswith("Structure alignment error"):
                    break
                elif line.startswith("PSD"):
                    psd_ab = float(line.strip().split()[-1])
    resfile_ab.unlink()
    resfile_ba.unlink()
    return pdb1, pdb2, psd_ab, psd_ba


def generate_ska_pairs(query_info: Path, database_info: Path):
    query = {}
    with query_info.open() as qi:
        for line in qi:
            pdb_id, pdb_path = line.strip().split()
            query[pdb_id] = pdb_path
    database = {}
    with database_info.open() as di:
        for line in di:
            pdb_id, pdb_path = line.strip().split()
            database[pdb_id] = pdb_path

    for i1, p1 in query.items():
        for i2, p2 in database.items():
            yield (i1, p1, i2, p2)


def run(query_info: Path,
        database_info: Path,
        output_file: Path,
        tmp_dir: Path,
        submat: str,
        trolltop: str,
        bin: str,
        psd_threshold: float):
    results = []
    env = {"TROLLTOP": trolltop, "SUBMAT": submat}
    with ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(run_ska, i1, p1, i2, p2, tmp_dir, bin,  env)
            for i1, p1, i2, p2 in generate_ska_pairs(query_info, database_info)
        }
        completed = 0

        for future in as_completed(futures):
            results.append(future.result())
            completed += 1
            if completed % 10000 == 0:
                logger.info(f"completed {completed} runs")
    with output_file.open("w") as of:
        of.write("pdb_a\tpdb_b\tPSD(a,b)\tPSD(b,a)\n")
        for p1, p2, psd1, psd2 in results:
            if psd1 <= psd_threshold or psd2 <= psd_threshold:
                of.write(f"{p1}\t{p2}\t{psd1}\t{psd2}\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="builds a file with commands for all pairs of PDB files")
    parser.add_argument("-q", "--query-info", required=True,
                        help="Path to a query map from ID to Path (tsv)")
    parser.add_argument("-d", "--database-info", required=True,
                        help="Path to a query map from ID to Path (tsv)")
    parser.add_argument("-o", "--output-file", required=True,
                        help="Path to the output file")
    parser.add_argument("-t", "--tmp-dir", required=True,
                        help="Path to a directory to store temporary results")
    parser.add_argument("-p", "--psd-threshold", required=True,
                        help="PSD threshold to use")
    parser.add_argument("-s", "--submat", required=True,
                        help="value for the SUBMAT environment variable")
    parser.add_argument("-b", "--bin", required=True,
                        help="Path to the ska binary")
    parser.add_argument("-r", "--trolltop", required=True,
                        help="value for the TROLLTOP environment variable")
    args = parser.parse_args()
    run(Path(args.query_info),
        Path(args.database_info),
        Path(args.output_file),
        Path(args.tmp_dir),
        args.submat,
        args.trolltop,
        args.bin,
        args.psd_threshold)
