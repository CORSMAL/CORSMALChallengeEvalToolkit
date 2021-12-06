#!/usr/bin/env python
#
# Evaluation script for the train set of the CORSMAL Challenge 
#
################################################################################## 
# Author: 
#   - Alessio Xompero: a.xompero@qmul.ac.uk
#         Email: corsmal-challenge@qmul.ac.uk
#
#  Created Date: 2020/08/25
# Modified Date: 2021/12/06
#
# MIT License

# Copyright (c) 2021 CORSMAL

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#--------------------------------------------------------------------------------

import os
import csv
import math
import numpy as np
import pandas as pd
from sklearn import metrics
import argparse 
import copy 

# from pdb import set_trace as bp


# Score computed for container capacity and mass estimation
def computeScoreType1(gt, _est):
	est = copy.deepcopy(_est)

	assert (len(gt) == len(est))

	if all(x == -1 for x in est):
		return 0

	indicator_f = est > -1

	ec = np.exp(-(np.abs(gt - est) / gt)) * indicator_f
	
	score = np.sum(ec) / len(gt)
	
	return score


def computeContainerCapacityScore(gt, _est):
	return computeScoreType1(gt, _est)


if __name__ == '__main__':

	# Arguments
	parser = argparse.ArgumentParser(description='CORSMAL Challenge evaluation')
	parser.add_argument('--submission', default='random.csv', type=str)
	args = parser.parse_args()

	outfile = 'res_training_set.csv'
	offset = 0.047505
	
	annotationfile = 'annotations/ccm_train_annotation.csv'
	baselinefile = 'submissions/train_set/random1.csv'
	submissionfile = 'submissions/train_set/{}'.format(args.submission)

	# Read annotations
	gt = pd.read_csv(annotationfile, sep=',')

	# Read baseline (random)
	baseline = pd.read_csv(baselinefile, sep=',')

	# Read submission
	est = pd.read_csv(submissionfile, sep=',')
	
	capacity_score  = computeContainerCapacityScore(gt['container capacity'].values, est['Container capacity'].values)
	

	print(args.submission[:-4] + ';{:.2f}\n'.format(capacity_score*100))
	if not os.path.exists(outfile):
	  results_file = open(outfile, 'w')
	  results_file.write('Team;score\n')
	  results_file.close()

	with open(outfile, 'a') as myfile:
		myfile.write(args.submission[:-4] + ';{:.2f}\n'.format(capacity_score*100))
	
	myfile.close()
