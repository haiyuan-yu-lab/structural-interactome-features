from pathlib import Path


def run(query_info: Path, database_info: Path, output_file: Path) -> None:
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
    with output_file.open("w") as of:
        for i1, p1 in query.items():
            for i2, p2 in database.items():
                of.write(f"ska {p1} {p2} > {i1}-vs-{i2}\n")
                of.write(f"ska {p2} {p1} > {i2}-vs-{i1}\n")


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
    args = parser.parse_args()
