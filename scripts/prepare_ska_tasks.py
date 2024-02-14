from pathlib import Path
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict
from siflib.io.ska_wrapper import run_ska_psd

logger = logging.getLogger('SKA-parallel-runner')
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    "%Y-%m-%d %H:%M:%S")
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)


def generate_ska_pairs(query: Dict, database: Dict):

    for i1, p1 in query.items():
        for i2, p2 in database.items():
            yield (i1, p1, i2, p2)


def run(query_info: Path,
        database_info: Path,
        output_file: Path,
        tmp_dir: Path,
        submat: str,
        trolltop: str,
        skabin: str,
        psd_threshold: float,
        batch_size: int = 1000):
    results = []
    env = {"TROLLTOP": trolltop, "SUBMAT": submat}
    logger.info("collecting query info...")
    query = {}
    with query_info.open() as qi:
        for line in qi:
            pdb_id, pdb_path = line.strip().split()
            query[pdb_id] = pdb_path
    database = {}
    logger.info("collecting database info...")
    with database_info.open() as di:
        for line in di:
            pdb_id, pdb_path = line.strip().split()
            database[pdb_id] = pdb_path
    total = len(database) * len(query) * 2
    with ProcessPoolExecutor() as executor:
        batch = []
        curr_batch = 1
        for i, (i1, p1, i2, p2) in enumerate(
                generate_ska_pairs(query, database), start=1):
            batch.append(
                executor.submit(run_ska_psd, i1, p1, i2, p2, skabin, env)
            )

            if i % batch_size == 0 or i == total:
                for future in as_completed(batch):
                    results.append(future.result())
                logger.info(f"done: {i} runs, at batch {curr_batch}")
                logger.info(f"results: {len(results)}")
                curr_batch += 1
                batch = []

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
    parser.add_argument("--batch_size",
                        default=1000,
                        type=int,
                        help="Batch size for parallel computation")
    args = parser.parse_args()
    run(Path(args.query_info),
        Path(args.database_info),
        Path(args.output_file),
        Path(args.tmp_dir),
        args.submat,
        args.trolltop,
        args.bin,
        args.psd_threshold,
        args.batch_size)
