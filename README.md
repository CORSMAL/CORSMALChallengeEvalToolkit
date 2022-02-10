# The CORSMAL Challenge evaluation toolkit

This repository contains the official evaluation toolkit for the CORSMAL Challenge.
The version of this toolkit can be used only with the train set of the
[CORSMAL Containers Manipulation dataset](http://corsmal.eecs.qmul.ac.uk/containers_manip.html).
The toolkit provides transparency in how the evaluation is performed, and 
enables the verification of the output using example submissions with annotation
 or random values as estimations.

The repository also contains the submission forms as example for the train set,
annotation files (including filling densities per container) and a demo with 
examples of submissions (see [metadata.md](submissions/metadata.md) for details 
of each submission using the annotation values, random-generated values, and
the average of the annotations for container capacity, mass, dimensions). 

Moreover, we provide a script to parse the dataset: [data_parser](data_parser).
The script can be used to integrate novel solutions. More details in the 
[README](data_parser/README.md) of the data_parser.

Documents:
* Technical details of performance measures and scores: [PDF](docs/PerformanceScores.pdf)
* Submission form for the public testing set: [here](docs/submission_forms/public_test_set.csv)

Requirements:
* Python (Tested with 3.8.3)
* Numpy (Tested with 1.18.5)
* Pandas (Tested with 1.2.3)
* Scikit-learn (Tested with 0.24.1)


## Challenge venues

<!-- Challenge is still on-going and could happen in future venues. Stay tuned! -->

### Current venue
<!-- [CORSMAL Challenge](http://corsmal.eecs.qmul.ac.uk/challenge.html) -->
Audio-visual object classification for human-robot collaboration @[2022 IEEE International Conference on Acoustic, Speech, and Signal Processing](http://corsmal.eecs.qmul.ac.uk/challenge.html)

**Important dates**
| Date             |                             |
|------------------|-------------------------------------|
| February 10, 2022 (11.59 AoE) |  Paper acceptance notification and release of the results in the leaderboards |
| February 16, 2022 (11.59 AoE) | Camera-ready papers due |



### Past venues
* [2021 Intelligent Sensing Winter School](http://cis.eecs.qmul.ac.uk/school2021.html)
* [2020 International Conference on Pattern Recognition](http://corsmal.eecs.qmul.ac.uk/ICPR2020challenge.html)
* [2020 Intelligent Sensing Summer School](http://cis.eecs.qmul.ac.uk/school2020.html)


## Data format

### Input

The input to the [evaluation script](evaluate.py) is a .csv file that contains
the following fields for each row:

| Configuration ID | Container capacity | Container mass | Filling mass | None | Pasta | Rice | Water | Filling type | Empty | Half-full | Full | Filling level | Width at the top | Width at the bottom | Height | Object safety | Distance | Angle difference | Execution time |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

Note that each row should match the row of the annotation file for the train 
set, i.e., the configuration ID.

Container capacity [mL]:
* -1: no estimation
*  x: estimated value (>=0)

Container mass [g]:
* -1: no estimation
*  x: estimated value (>=0)

Filling mass [g]:
* -1: no estimation
*  x: value computed by the script using filling level, filling type, and 
container capacity estimations

None, Pasta, Rice, Water:
* -1: no estimation
* x: estimated probability [0,1]

Filling type:
* -1: no estimation
*  0: no filling
*  1: pasta
*  2: rice
*  3: water

Empty, Half-full, Full:
* -1: no estimation
* x: estimated probability [0,1]

Filling level:
* -1: no estimation
*  0: empty
*  1: half-full (50%)
*  2: full (90%)

Width at the top [mm]:
* -1: no estimation
*  x: estimated value (>=0)

Width at the bottom [mm]:
* -1: no estimation
*  x: estimated value (>=0)

Height [mm]:
* -1: no estimation
*  x: estimated value (>=0)

Object safety:
* -1: no estimation
* x: estimated probability [0,1] (Note that this value will be estimated by the 
organisers when running the simulator)

Distance [mm]:
* -1: no estimation
* x: estimated value (>=0) (Note that this value will be estimated by the 
organisers when running the simulator)

Angle difference [deg]:
* -1: no estimation
* x: estimated value (>=0) (Note that this value will be estimated by the 
organisers when running the simulator)

Execution time [ms]:
* -1: no estimation
* x: estimated value (>=0)


### Output

The [evaluation script](evaluate.py) outputs a .csv file (e.g., 
res_train_set.csv for the train set) with the results (percentage) of 
each submission per row: 

| Team | s1 | s2 | s3 | s4 | s5 | s6 | s7 | s8 | s9 | s10 | Overall | JFTL | CMD |
|------|----|----|----|----|----|----|----|----|----|-----|---------|------|-----|


* s1:  score for the filling level classification task (T1)
* s2:  score for the filling type classification task (T2)
* s3:  score for the container capacity estimation task (T3)
* s4:  score for the container width at the top estimation (container dimensions task, T5)
* s5:  score for the container width at the bottom estimation (container dimensions task, T5)
* s6:  score for the container height (container dimensions task, T5)
* s7:  score for the container mass estimation task (T4)
* s8:  score for the filling mass estimation (computed by the toolkit from T1, T2, and T3)
* s9:  score for the object safety estimation (estimated by the simulator run by the organisers)
* s10: score for the delivery accuracy (estimated by the simulator run by the organisers)
* Overall: aggregation (average) of the previous 10 performance scores (in percentage) and weighed based on the number of tasks submitted.
* JFTL: score for the joint filling type and level classification (additional leaderboard)
* CMD: score for the group tasks of container capacity and dimensions estimation (additional leaderboard)

Only submissions which include the source code for the evaluation on the 
private CCM test set will valid for the ranking. Source codes that are not 
reproducible will get a 0 score.

Note: The score for filling mass estimation is not a linear combination of the 
scores outputted for T1, T2, and T3. The score takes into consideration the 
formula for computing the filling mass based on the estimations of each task
for each configuration. s8 is weighed by the number of tasks executed among
filling level classification, filling type classification, and container capacity
estimation.

Note that s9 and s10 are weighed by the number of tasks executed (up to 5), whereas
s4, s5, and s6 are weighed by 3 as they belong to the same task (container dimensions
estimation).

More details in the technical document: [PDF](docs/PerformanceScores.pdf)


## Demo

An example of submission file with random estimations can be found in 
[submissions/train_set/](submissions/train_set/). Additional examples can be
generated using the bash script [submissions/run_subm_gen.sh]([submissions/run_subm_gen.sh]).

Please see [submissions/metadata.md](submissions/metadata.md) for details
about the generated files that use either annotations, random values, or the 
average of the containers in the train set (only for container mass, capacity, 
and dimensions) as estimations.

To reproduce the results on for the example submissions on the train set, run
```
cd submissions/
source run_subm_gen.sh
cd ..
source run_eval_demo.sh
```

The [evaluation script](evaluate.py) can be run with the following options:
* --submission: path and filename of the submission file (e.g., submissions/pub_test/teamname.csv)
* --set: choose between train, test_pub, test_priv, and test_comb 

Note that these example submissions do not contain estimations for object safety,
distance, and angle difference, and hence results for the scores s8 and s8 are 0, and
the overall score is up to maximum 80 instead of 100.

For reproducibility, we report the results in the table below.

| Team | s1 | s2 | s3 | s4 | s5 | s6 | s7 | s8 | s9 | s10 | overall | JFLT |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| test1 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 0.00 | 0.00 | 80.00 | 100.00 |
| test2 | 100.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 39.00 | 0.00 | 0.00 | 2.78 | 0.00 |
| test3 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 100.00 | 0.00 | 0.00 | 0.00 | 2.00 | 0.00 |
| test4 | 100.00 | 100.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 39.00 | 0.00 | 0.00 | 9.56 | 100.00 |
| test5 | 100.00 | 100.00 | 100.00 | 0.00 | 0.00 | 0.00 | 0.00 | 100.00 | 0.00 | 0.00 | 24.00 | 100.00 |
| test6 | 0.00 | 0.00 | 100.00 | 100.00 | 100.00 | 100.00 | 0.00 | 71.91 | 0.00 | 0.00 | 18.88 | 0.00 |
| test7 | 0.00 | 0.00 | 100.00 | 0.00 | 0.00 | 0.00 | 0.00 | 71.91 | 0.00 | 0.00 | 3.44 | 0.00 |
| test8 | 0.00 | 100.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 42.83 | 0.00 | 0.00 | 2.86 | 0.00 |
| test9 | 0.00 | 0.00 | 0.00 | 100.00 | 100.00 | 100.00 | 0.00 | 0.00 | 0.00 | 0.00 | 6.00 | 0.00 |
| test10 | 0.00 | 0.00 | 100.00 | 0.00 | 0.00 | 0.00 | 100.00 | 71.91 | 0.00 | 0.00 | 10.88 | 0.00 |
| test11 | 100.00 | 100.00 | 100.00 | 0.00 | 0.00 | 0.00 | 100.00 | 100.00 | 0.00 | 0.00 | 40.00 | 100.00 |
| test12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| random1 | 32.01 | 26.68 | 21.72 | 24.62 | 20.87 | 36.24 | 16.73 | 42.83 | 0.00 | 0.00 | 22.17 | 9.60 |
| random2 | 32.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 42.83 | 0.00 | 0.00 | 1.50 | 0.00 |
| random3 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 16.73 | 0.00 | 0.00 | 0.00 | 0.33 | 0.00 |
| random4 | 32.01 | 26.68 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 42.83 | 0.00 | 0.00 | 4.06 | 9.60 |
| random5 | 32.01 | 26.68 | 21.72 | 0.00 | 0.00 | 0.00 | 0.00 | 42.83 | 0.00 | 0.00 | 7.39 | 9.60 |
| random6 | 0.00 | 0.00 | 21.72 | 24.62 | 20.87 | 36.24 | 0.00 | 42.83 | 0.00 | 0.00 | 5.85 | 0.00 |
| random7 | 0.00 | 0.00 | 21.72 | 0.00 | 0.00 | 0.00 | 0.00 | 42.83 | 0.00 | 0.00 | 1.29 | 0.00 |
| random8 | 0.00 | 26.68 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 42.83 | 0.00 | 0.00 | 1.39 | 0.00 |
| random9 | 0.00 | 0.00 | 0.00 | 24.62 | 20.87 | 36.24 | 0.00 | 0.00 | 0.00 | 0.00 | 1.63 | 0.00 |
| random10 | 0.00 | 0.00 | 21.72 | 0.00 | 0.00 | 0.00 | 16.73 | 42.83 | 0.00 | 0.00 | 3.25 | 0.00 |
| random11 | 32.01 | 26.68 | 21.72 | 0.00 | 0.00 | 0.00 | 16.73 | 42.83 | 0.00 | 0.00 | 11.20 | 9.60 |
| average | 32.01 | 26.68 | 31.89 | 63.96 | 50.95 | 66.24 | 30.25 | 50.34 | 0.00 | 0.00 | 35.23 | 9.60 |

## Enquiries, Question and Comments

If you have any further enquiries, question, or comments, please contact 
corsmal-challenge@qmul.ac.uk If you would like to 
file a bug report or a feature request, use the Github issue tracker. 


## Licence

This work is licensed under the MIT License. To view a copy of this license, 
see [LICENSE](LICENSE).

