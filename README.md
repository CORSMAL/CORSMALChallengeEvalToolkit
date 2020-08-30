# The CORSMAL Challenge evaluation toolkit

*Author*: Alessio Xompero

Created date: 2020/08/25

Modified date: 2020/08/30

Version: 0.1

Resource type: software

## Description

This repository contains the official evaluation toolkit for the CORSMAL Challenge 
at the [2020 Intelligent Sensing Summer School](http://cis.eecs.qmul.ac.uk/school2020.html).
The toolkit is developed in Python with Numpy, Pandas and Scikit-learn.
The version of this toolkit is only for the evaluation of the training set of the
[CORSMAL Containers Manipulation dataset](http://corsmal.eecs.qmul.ac.uk/containers_manip.html).

Performance measures and scores are described in details in this document: 
[PDF](docs/2020_CORSMAL_Challenge_PerformanceScores.pdf).

The repository also contains the submission form as example for the training set,
annotation files (including filling densities per container) and a demo with examples of submissions.

Submission form for the public testing set: [here](docs/submission_form_pub_test.csv).

## Data format

### Input

The input to the toolkit is .csv file that for each row contains the following
fields:

| Container ID | Sequence | Filling level | Filling type | Container Capacity |
|--------------|----------|---------------|--------------|--------------------|

Note that each row should match the row of the annotation file for the training set.

Containers ID ranges from 1 to 9.

Sequence ranges from 0 to 83 for glasses and cups (containers 1-6) and from 0 to 59
for boxes (containers 7-9).

Filling level values:
* -1: no estimation
*  0: empty
* 50: half-full
* 90: full

Filling type values:
* -1: no estimation
*  0: no filling
*  1: pasta
*  2: rice
*  3: water

Container Capacity:
* -1: no estimation
*  x: estimated value (>=0)

### Output

The Python script outputs a .csv file with the results (percentage) of each submission per row: 

| Team | Task 1 | Task 2 | Task 3 | Overall Task |
|------|--------|--------|--------|--------------|


Task 1: Filling level classification

Task 2: Filling type classification

Task 3: Container capacity estimation

Overall task: Filling mass 


Note: The  final score will be weighed based on the number of tasks submitted 
(i.e. 0.33 for one task, 0.66 for two tasks, 1 for the three tasks).

## Enquiries, Question and Comments

If you have any further enquiries, question, or comments, please contact 
corsmal-challenge@qmul.ac.uk If you would like to 
file a bug report or a feature request, use the Github issue tracker. 


## Licence

This work is licensed under the Creative Commons Attribution-NonCommercial 4.0 
International License. To view a copy of this license, visit 
http://creativecommons.org/licenses/by-nc/4.0/ or send a letter to 
Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

