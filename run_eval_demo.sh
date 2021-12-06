#! /bin/bash

for split in 0 1 2
do

	python evaluate.py  --submission test1.csv  --split $split
	python evaluate.py  --submission test2.csv  --split $split
	python evaluate.py  --submission test3.csv  --split $split
	python evaluate.py  --submission test4.csv  --split $split
	python evaluate.py  --submission test5.csv  --split $split
	python evaluate.py  --submission test6.csv  --split $split
	python evaluate.py  --submission test7.csv  --split $split
	python evaluate.py  --submission test8.csv  --split $split
	python evaluate.py  --submission test9.csv  --split $split
	python evaluate.py  --submission test10.csv  --split $split
	python evaluate.py  --submission test11.csv  --split $split
	python evaluate.py  --submission test12.csv --split $split

	python evaluate.py  --submission random1.csv  --split $split
	python evaluate.py  --submission random2.csv  --split $split
	python evaluate.py  --submission random3.csv  --split $split
	python evaluate.py  --submission random4.csv  --split $split
	python evaluate.py  --submission random5.csv  --split $split
	python evaluate.py  --submission random6.csv  --split $split
	python evaluate.py  --submission random7.csv  --split $split
	python evaluate.py  --submission random8.csv  --split $split
	python evaluate.py  --submission random9.csv  --split $split
	python evaluate.py  --submission random10.csv  --split $split
	python evaluate.py  --submission random11.csv  --split $split

	python evaluate.py  --submission average.csv  --split $split
done