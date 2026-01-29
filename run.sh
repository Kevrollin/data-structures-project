#!/usr/bin/env bash
# convenience script to run the Mini Campus Funding Manager
set -euo pipefail
cd "$(dirname "$0")/campus_funding"
python3 main.py
