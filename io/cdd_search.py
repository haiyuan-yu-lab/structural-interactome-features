import sys
import time
import requests

# URL to the Batch CD-Search server
BWRPSB_URL = "https://www.ncbi.nlm.nih.gov/Structure/bwrpsb/bwrpsb.cgi"

# Read list of queries from stdin
queries = [line.strip() for line in sys.stdin if line.strip()]
if not any(queries):
    sys.exit("No valid queries!\n")


def run(params, sequneces):

    # Submitting the search
    response = requests.post(BWRPSB_URL, data=params)
    response.raise_for_status()

    rid = None
    for line in response.text.splitlines():
        if line.startswith("#cdsid"):
            rid = line.split()[1]
            break

    if not rid:
        sys.exit("Submitting the search failed,"
                 " can't make sense of response: {}".format(response.text))

    print("Search with Request-ID {} started.".format(rid))

    # Checking for completion
    done = False
    while not done:
        time.sleep(5)
        response = requests.post(BWRPSB_URL,
                                 data={"tdata": "hits", "cdsid": rid})
        response.raise_for_status()

        print(response.text)
        sys.exit("asd")

        status_line = next((
            line for line in response.text.splitlines()
            if line.startswith("#status")), None)
        if status_line:
            status = int(status_line.split()[1])
            if status == 0:
                done = True
                print("Search has been completed, retrieving results ..")
            elif status == 1:
                sys.exit("Invalid request ID\n")
            elif status == 2:
                sys.exit("Invalid input, missing query information or search ID\n")
            elif status == 3:
                print(".", end="", flush=True)
            elif status == 4:
                sys.exit("Queue Manager Service error\n")
            elif status == 5:
                sys.exit("Data corrupted or no longer available\n")
        else:
            sys.exit("Checking search status failed,"
                     " can't make sense of response: {}".format(response.text))

    # Retrieve and display results
    response = requests.post(bwrpsb, data={
        "tdata": params['tdata'],
        "cddefl": params['cddefl'],
        "qdefl": params['qdefl'],
        "dmode": params['dmode'],
        "clonly": params['clonly'],
        "cdsid": rid
    })
    response.raise_for_status()
    print(response.text)


if __name__ == "__main__":
    import argparse

    # Set default values
    params = {
        "cdsid": "",
        "cddefl": "false",
        "qdefl": "false",
        "smode": "auto",
        "useid1": "true",
        "maxhit": 250,
        "filter": "true",
        "db": "cdd",
        "evalue": 0.01,
        "dmode": "rep",
        "clonly": "false",
        "tdata": "hits"
    }

    # Argument parser setup
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--database")
    parser.add_argument("-e", "--evalue", type=float)
    parser.add_argument("-f", "--filter", action="store_true")
    parser.add_argument("-f", "--max-hit", type=int)
    parser.add_argument("-t", "--target-data")
    parser.add_argument("-s", "--superfamilies-only", action='store_true')
    parser.add_argument("-a", "--all", action='store_true')
    parser.add_argument("-q", "--qdefl", action='store_true')
    parser.add_argument("-i", "--input")
    args = parser.parse_args()

    # Update parameters based on arguments
    if args.d:
        params['db'] = args.d
    if args.e:
        params['evalue'] = args.e
    if args.F:
        params['filter'] = "false" if args.F == "F" else "true"
    if args.b:
        params['maxhit'] = args.b
    if args.t:
        params['tdata'] = args.t
    if args.s:
        params['clonly'] = "true"
    if args.a:
        params['dmode'] = "all"
    if args.q:
        params['qdefl'] = "true"

    fo
