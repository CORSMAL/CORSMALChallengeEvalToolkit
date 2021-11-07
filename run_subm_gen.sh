#!/bin/sh

python randgen.py --task1 --filename='team1.csv'
python randgen.py --task2 --filename='team2.csv'
python randgen.py --task3 --filename='team3.csv'
python randgen.py --task4 --filename='team4.csv'
python randgen.py --task5 --filename='team5.csv'
python randgen.py --task1 --task2 --filename='team6.csv'
python randgen.py --task3 --task5 --filename='team7.csv'
python randgen.py --task1 --task2 --task3 --filename='team8.csv'
