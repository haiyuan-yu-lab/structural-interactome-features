#!/bin/bash

# WARNING, we do NOT validate commands in this scriptm, and they are loaded 
# directly from environment variables, you should verify your
# configuration file contains only safe commands before executing this (and any
# other) script on your computer.

# Load environment variables
set -a  # automatically export all variables
source .env
set +a  # stop automatically exporting


# Now call other scripts
./scripts/print-vars.sh

# 1. Download all datasets
# ./scripts/download-data.sh

# 2. Cluster PDB sequences
# ./scripts/cluster-pdb.sh

# 3. Make CDD database
./scripts/cdd-makedb.sh

# 4. CDD search
./scripts/cdd-search.sh

($AF_PREDICT asd)

