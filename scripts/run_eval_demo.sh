#! /bin/bash

DATA_SET=train
# DATA_SET=test_pub
# DATA_SET=test_priv
# DATA_SET=test_comb

python evaluate.py --set $DATA_SET --submission test1.csv 
python evaluate.py --set $DATA_SET --submission test2.csv 
python evaluate.py --set $DATA_SET --submission test3.csv 
python evaluate.py --set $DATA_SET --submission test4.csv 
python evaluate.py --set $DATA_SET --submission test5.csv 
python evaluate.py --set $DATA_SET --submission test6.csv 
python evaluate.py --set $DATA_SET --submission test7.csv 
python evaluate.py --set $DATA_SET --submission test8.csv 
python evaluate.py --set $DATA_SET --submission test9.csv 
python evaluate.py --set $DATA_SET --submission test10.csv 
python evaluate.py --set $DATA_SET --submission test11.csv 
python evaluate.py --set $DATA_SET --submission test12.csv

python evaluate.py --set $DATA_SET --submission random1.csv 
python evaluate.py --set $DATA_SET --submission random2.csv 
python evaluate.py --set $DATA_SET --submission random3.csv 
python evaluate.py --set $DATA_SET --submission random4.csv 
python evaluate.py --set $DATA_SET --submission random5.csv 
python evaluate.py --set $DATA_SET --submission random6.csv 
python evaluate.py --set $DATA_SET --submission random7.csv 
python evaluate.py --set $DATA_SET --submission random8.csv 
python evaluate.py --set $DATA_SET --submission random9.csv 
python evaluate.py --set $DATA_SET --submission random10.csv 
python evaluate.py --set $DATA_SET --submission random11.csv 

python evaluate.py --set $DATA_SET --submission average.csv 
