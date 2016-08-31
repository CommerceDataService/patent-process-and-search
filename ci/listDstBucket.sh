#!/usr/bin/env bash

set -e

SCRIPT=$(python -c "import os; print(os.path.realpath('$0'))")
SCRIPT_DIR=$(dirname "$SCRIPT")
PROJECT_ROOT=$(dirname "$SCRIPT_DIR/..")

source "${SCRIPT_DIR}/_common.sh"

pip install -r requirements.txt

py.test .

python reprocess_list_s3_dst_dir.py

