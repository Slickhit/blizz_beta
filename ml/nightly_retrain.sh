#!/bin/sh
# Simple nightly retraining script
SCRIPT_DIR="$(dirname "$0")"
python "$SCRIPT_DIR/train.py"
