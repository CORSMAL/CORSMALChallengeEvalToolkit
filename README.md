# The CORSMAL Evaluation Toolkit

The toolkit allows to evaluate a submission for the CORSMAL Benchmark protocol, a submission for the tasks of the CORSMAL Challenge, a submission for the on-site Human-to-Robot Handover competition track, or results related to the safe real-to-simulation framework we provided.  


## Installation

## Usage

Benchmark protocol: 

```bash

uv run toolkit/cli.py \
    --submission_csv resources/benchmark/submissions/gt.csv \
    --ground_truth_csv resources/benchmark/gts.csv \
    --metadata resources/benchmark/submission_metadata.json \
    --mode benchmark
```


## Enquiries, Question and Comments

For questions, bug reports, or feature requests please use the Github issue tracker. 


## Licence

This work is licensed under the MIT License. To view a copy of this license, 
see [LICENSE](LICENSE).

