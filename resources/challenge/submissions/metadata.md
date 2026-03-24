This file documents the list of example and testing submissions to verify the toolkit.

For each testing submission, the table below report the addressed tasks and the type of estimations done, i.e., using the real annotations or generating random results. There is also a sanity check case with all estimations set to -1. For the random case, each submission is generated from scratch and hence the scores can differ between each other. 

As the submissions provide only the solutions to the tasks without the results from the simulator for the object safety and the delivery location (distance) and angle, the overall challenge score is up to 80 points. This is the maximum score achievable when the estimations for all tasks are correctly estimated (corresponding to the annotated values).

We also includes a use case where the estimations for container capacity, container mass, and container dimensions are set to the average of the values in the (train) set as another reference. Solutions by the teams should not use this option and their performance should be higher or lower than the results achieved by this case. 


|   Name  | Container Capacity | Filling Type | Filling Level | Container Mass | Container Dimensions |
|:-------:|:------------------:|:------------:|:-------------:|:--------------:|:--------------------:|
| Test1   |         GT         |      GT      |       GT      |       GT       |          GT          |
| Test2   |         -1         |      -1      |       GT      |       -1       |          -1          |
| Test3   |         -1         |      -1      |       -1      |       GT       |          -1          |
| Test4   |         -1         |      GT      |       GT      |       -1       |          -1          |
| Test5   |         GT         |      GT      |       GT      |       -1       |          -1          |
| Test6   |         GT         |      -1      |       -1      |       -1       |          GT          |
| Test7   |         GT         |      -1      |       -1      |       -1       |          -1          |
| Test8   |         -1         |      GT      |       -1      |       -1       |          -1          |
| Test9   |         -1         |      -1      |       -1      |       -1       |          GT          |
| Test10  |         GT         |      -1      |       -1      |       GT       |          GT          |
| Test11  |         GT         |      GT      |       GT      |       GT       |          -1          |
| Test12  |         -1         |      -1      |       -1      |       -1       |          -1          |
| RAND1   |        rand        |     rand     |      rand     |      rand      |         rand         |
| RAND2   |         -1         |      -1      |      rand     |       -1       |          -1          |
| RAND3   |         -1         |      -1      |       -1      |      rand      |          -1          |
| RAND4   |         -1         |     rand     |      rand     |       -1       |          -1          |
| RAND5   |        rand        |     rand     |      rand     |       -1       |          -1          |
| RAND6   |        rand        |      -1      |       -1      |       -1       |         rand         |
| RAND7   |        rand        |      -1      |       -1      |       -1       |          -1          |
| RAND8   |         -1         |     rand     |       -1      |       -1       |          -1          |
| RAND9   |         -1         |      -1      |       -1      |       -1       |         rand         |
| RAND10  |        rand        |      -1      |       -1      |      rand      |         rand         |
| RAND11  |        rand        |     rand     |      rand     |      rand      |          -1          |
| Average |       Average      |     rand     |      rand     |     Average    |        Average       |
