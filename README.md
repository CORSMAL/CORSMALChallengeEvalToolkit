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
* Python
* Numpy
* Pandas
* Scikit-learn


## Challenge venues

<!-- Challenge is still on-going and could happen in future venues. Stay tuned! -->

### Current venue
<!-- [CORSMAL Challenge](http://corsmal.eecs.qmul.ac.uk/challenge.html) -->
Audio-visual object classification for human-robot collaboration @[2022 IEEE International Conference on Acoustic, Speech, and Signal Processing](http://corsmal.eecs.qmul.ac.uk/challenge.html)

**Important dates**
| Date             |                             |
|------------------|-------------------------------------|
| January 10, 2022 | Release of the public test data set |
| January 24, 2022 (11.59 PDT) | Submission of (i) papers, (ii) estimation results (T1-T5) on the public test data set, and (iii) and source code |
| February 10, 2022 (11.59 PDT) |  Paper acceptance notification and release of the results in the leaderboards |
| January 17, 2022 (11.59 PDT) | Camera-ready papers due |


Papers must be formatted according to the instructions in the 
[ICASSP 2022 Paper Kit](https://2022.ieeeicassp.org/papers/paper_kit.php) and 
submitted to corsmal-challenge@qmul.ac.uk. 


### Past venues
* Multi-modal fusion and learning for robotics @[2020 International Conference on Pattern Recognition](http://corsmal.eecs.qmul.ac.uk/ICPR2020challenge.html)
* Multi-modal fusion and learning for robotics @[2020 Intelligent Sensing Summer School](http://cis.eecs.qmul.ac.uk/school2020.html)


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

The Python script outputs a .csv file with the results (percentage) of each submission per row: 

| Team | Task 1 | Task 2 | Task 3 | Overall Task |
|------|--------|--------|--------|--------------|


Task 1: Filling level classification

Task 2: Filling type classification

Task 3: Container capacity estimation

Overall task: Filling mass 


Note: The overall task is not a linear combination of the scores outputted for
Task 1, Task 2, and Task 3. The score for the overall task takes into consideration
the formula for computing the filling mass based on the estimations of each task
for each configuration. More details in the technical document: 
[PDF](docs/PerformanceScores.pdf)

Note: The  final score (overall task) will be weighed based on the number of 
tasks submitted (i.e. 0.33 for one task, 0.66 for two tasks, 1 for the three tasks).


## Demo

An example of submission file with random estimations can be found in 
[submissions/train_set/](submissions/train_set/). Additional examples can be
generated using the bash script [submissions/run_subm_gen.sh]([submissions/run_subm_gen.sh]).

Please see [submissions/metadata.md](submissions/metadata.md) for details
about the generated files that use either annotations, random values, or the 
average of the containers in the train set (only for container mass, capacity, 
and dimensions) as estimations.

To generate the 

## Enquiries, Question and Comments

If you have any further enquiries, question, or comments, please contact 
corsmal-challenge@qmul.ac.uk If you would like to 
file a bug report or a feature request, use the Github issue tracker. 


## Licence

This work is licensed under the MIT License. To view a copy of this license, 
see [LICENSE](LICENSE).

