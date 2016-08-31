#!/usr/bin/env bash

set -e

SCRIPT=$(python -c "import os; print(os.path.realpath('$0'))")
SCRIPT_DIR=$(dirname "$SCRIPT")
PROJECT_ROOT=$(dirname "$SCRIPT_DIR/..")

source "${SCRIPT_DIR}/_common.sh"

pip install -r requirements.txt

py.test .

rm -f run-list.txt

python reprocess_create_run_list.py

