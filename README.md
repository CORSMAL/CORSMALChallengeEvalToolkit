# The CORSMAL Challenge evaluation toolkit

This repository contains the official evaluation toolkit for the CORSMAL Challenge at the [2021 Intelligent Sensing Winter School](http://cis.eecs.qmul.ac.uk/school2021.html). 
The version of this toolkit can be used only with the training set of the
[CORSMAL Containers Manipulation dataset](http://corsmal.eecs.qmul.ac.uk/containers_manip.html).
The toolkit provides transparency in how the evaluation is performed, and 
enables the verification of the output using example submissions with annotation
 or random values as estimations.

The repository also contains the submission forms as example for the training set,
annotation files (including filling densities per container) and a demo with 
examples of submissions (see [metadata.md](submissions/metadata.md) for details 
of each submission using the annotation values, random-generated values, and
the average of the annotations for container capacity, mass, dimensions). 

Moreover, we provide a script to parse the dataset: [data_parser](data_parser).
The script can be used to integrate novel solutions. More details in the 
[README](data_parser/README.md) of the data_parser.

Documents:
* Technical details of performance measures and scores: [PDF](docs/PerformanceScores.pdf)
* PowerPoint template for preparing the presentation of the solution on Friday 10 December: [PPT](docs/2020.12.10_Presentation_Template.pptx)

Requirements:
* Python (Tested with 3.8.3)
* Numpy (Tested with 1.18.5)
* Pandas (Tested with 1.2.3)
* Scikit-learn (Tested with 0.24.1)


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


For this challenge the 2021 Intelligent Sensing Winter School, only the column *Container capacity* should be filled with the estimation of the team solution. 

### Output

The [evaluation script](evaluate.py) outputs three .csv files (e.g., 
res_split0_set.csv for the first split of the training set) with the results 
(score in percentage) of each submission per row: 

| Team | score |
|------|-------|



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
* --submission: path and filename of the submission file (e.g., submissions/train_set/teamname_split0.csv)



## Enquiries, Question and Comments

If you have any further enquiries, question, or comments, please contact 
corsmal-challenge@qmul.ac.uk If you would like to 
file a bug report or a feature request, use the Github issue tracker. 


## Licence

This work is licensed under the MIT License. To view a copy of this license, 
see [LICENSE](LICENSE).

