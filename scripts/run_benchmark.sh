#!/bin/bash

source .venv/bin/activate

uv run toolkit/cli.py \
    --submission_csv resources/benchmark/submissions/gt.csv \
    --ground_truth_csv resources/benchmark/gts.csv \
    --metadata resources/benchmark/submission_metadata.json \
    --mode benchmark

deactivate