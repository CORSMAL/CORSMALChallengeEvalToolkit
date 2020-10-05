#! /bin/bash

python evaluate_training.py --submission team1.csv
python evaluate_training.py --submission team2.csv
python evaluate_training.py --submission team3.csv
python evaluate_training.py --submission team4.csv
python evaluate_training.py --submission team5.csv

python evaluate_training.py --submission test.csv

