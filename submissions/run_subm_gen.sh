#!/bin/sh

#DATA_SET=train
#DATA_SET=test_pub
DATA_SET=test_priv

################################################################################
python generate_annotation_submissions.py --filename='test1.csv'  --set $DATA_SET --mode annotation --task1 --task2 --task3 --task4 --task5 
python generate_annotation_submissions.py --filename='test2.csv'  --set $DATA_SET --mode annotation --task1 
python generate_annotation_submissions.py --filename='test3.csv'  --set $DATA_SET --mode annotation --task4 
python generate_annotation_submissions.py --filename='test4.csv'  --set $DATA_SET --mode annotation --task1 --task2 
python generate_annotation_submissions.py --filename='test5.csv'  --set $DATA_SET --mode annotation --task1 --task2 --task3 
python generate_annotation_submissions.py --filename='test6.csv'  --set $DATA_SET --mode annotation --task3 --task5 
python generate_annotation_submissions.py --filename='test7.csv'  --set $DATA_SET --mode annotation --task3 
python generate_annotation_submissions.py --filename='test8.csv'  --set $DATA_SET --mode annotation --task2 
python generate_annotation_submissions.py --filename='test9.csv'  --set $DATA_SET --mode annotation --task5 
python generate_annotation_submissions.py --filename='test10.csv' --set $DATA_SET --mode annotation --task3 --task4 
python generate_annotation_submissions.py --filename='test11.csv' --set $DATA_SET --mode annotation --task1 --task2 --task3 --task4 
python generate_annotation_submissions.py --filename='test12.csv' --set $DATA_SET --mode annotation 

python generate_annotation_submissions.py --filename='random2.csv'  --set $DATA_SET --mode random --task1 
python generate_annotation_submissions.py --filename='random3.csv'  --set $DATA_SET --mode random --task4 
python generate_annotation_submissions.py --filename='random4.csv'  --set $DATA_SET --mode random --task1 --task2 
python generate_annotation_submissions.py --filename='random5.csv'  --set $DATA_SET --mode random --task1 --task2 --task3 
python generate_annotation_submissions.py --filename='random6.csv'  --set $DATA_SET --mode random --task3 --task5 
python generate_annotation_submissions.py --filename='random7.csv'  --set $DATA_SET --mode random --task3 
python generate_annotation_submissions.py --filename='random8.csv'  --set $DATA_SET --mode random --task2 
python generate_annotation_submissions.py --filename='random9.csv'  --set $DATA_SET --mode random --task5 
python generate_annotation_submissions.py --filename='random10.csv' --set $DATA_SET --mode random --task3 --task4 
python generate_annotation_submissions.py --filename='random11.csv' --set $DATA_SET --mode random --task1 --task2 --task3 --task4

python generate_annotation_submissions.py --filename='average.csv' --set $DATA_SET --mode average --task1 --task2 --task3 --task4 --task5


