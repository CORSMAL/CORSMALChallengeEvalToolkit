#!/usr/bin/env python
#
# Evaluation script for the training set of the CORSMAL Challenge 
#
################################################################################## 
# Author: 
#   - Alessio Xompero: a.xompero@qmul.ac.uk
#         Email: corsmal-challenge@qmul.ac.uk
#
#  Created Date: 2020/08/25
# Modified Date: 2021/11/07
#
# MIT License

# Copyright (c) 2021 Alessio Xompero

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

import csv
import math
import numpy as np
import pandas as pd
from sklearn import metrics
import argparse 
import copy 

from pdb import set_trace as bp


def computeFillingMass(est, baseline, gt):
	num_tasks = 3
	# Replace -1 by the baseline result
	if all(est['Filling type'] == -1):
		est['Filling type'] = baseline['Filling type']
		num_tasks -= 1

	if all(est['Filling level'] == -1):
		est['Filling level'] = baseline['Filling level']
		num_tasks -= 1

	if all(est['Container capacity'] == -1):
		est['Container capacity'] = baseline['Container capacity']
		num_tasks -= 1

	fl = est['Filling level'].values
	fl[est['Filling level'].values==1] = 50
	fl[est['Filling level'].values==2] = 90
	
	# mass = Filling level x capacity x densitiy(filling)
	estimated_mass = fl/100. * est['Container capacity'].values * gt['filling density'].values

	if not all(est['Filling level'] == -1):
		estimated_mass[est['Filling level'] == -1] = -1

	if not all(est['Container capacity'] == -1):
		estimated_mass[est['Container capacity'] == -1] = -1

	est['Filling mass'] = estimated_mass

	return num_tasks != 0

def computeWeightedAverageF1Score(gt, est):
	assert (len(gt) == len(est))

	if all(x == -1 for x in est):
		return 0

	gt = gt.astype(str)
	est = est.astype(str)
	return metrics.f1_score(gt, est, average='weighted')


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

def computeScoreType2(gt, _est):
	est = copy.deepcopy(_est)

	assert (len(gt) == len(est))

	if all(x == -1 for x in est):
		return 0

	indicator_f = est > -1

	ec = np.zeros(len(est))
	err_abs = np.abs(est - gt);
	
	ec[err_abs < gt] = 1 - err_abs[err_abs < gt]/gt[err_abs < gt]
	ec[err_abs >= gt] = 0

	ec[(est == 0) * (gt == 0)] = 1

	score = np.sum(ec * indicator_f) / len(gt)
		
	return score

def computeScoreType3(gt, _est):
	est = copy.deepcopy(_est)

	assert (len(gt) == len(est))

	if all(x == -1 for x in est):
		return 0

	indicator_f = est > -1

	ec = est
		
	ec[(gt == 0) * (est == 0)] = 0
	ec[(gt == 0) * (est != 0)] = est[(gt == 0) * (est != 0)]
	ec[gt != 0] = np.abs(est[gt != 0] - gt[gt != 0]) / gt[gt != 0];

	score = np.sum(np.exp(-ec) * indicator_f) / len(gt)
		
	return score


def computeFillingLevelScore(gt, _est):
	return computeWeightedAverageF1Score(gt, _est)

def computeFillingTypeScore(gt, _est):
	return computeWeightedAverageF1Score(gt, _est)

def computeContainerCapacityScore(gt, _est):
	return computeScoreType1(gt, _est)

def computeContainerMassScore(gt, _est):
	return computeScoreType1(gt, _est)

def computeContainerWidthTopScore(gt, _est):
	return computeScoreType2(gt, _est)

def computeContainerWidthBottomScore(gt, _est):
	return computeScoreType2(gt, _est)

def computeContainerHeightScore(gt, _est):
	return computeScoreType2(gt, _est)

def computeFillingMassScore(gt, _est):
	return computeScoreType3(gt, _est)

def computeObjectSafetyScore(_est):
	est = copy.deepcopy(_est)

	if all(x == -1 for x in est):
		return 0

	indicator_f = est > -1

	score = np.sum(est * indicator_f) / len(est)
	return score

def computeDeliveryAccuracyScore(_est_distance, _est_angle):
	est_distance = copy.deepcopy(_est_distance)
	est_angle = copy.deepcopy(_est_angle)

	assert (len(est_distance) == len(est_angle))

	indicator_f1 = est_distance > -1
	indicator_f2 = est_angle > -1

	assert (p==q for p,q in zip(indicator_f1,indicator_f2))

	indicator_f = indicator_f1

	eta = 500 # the maximum distance allowed from the pre-defined delivery location (in mm)
	phi = math.pi / 4 # the value of β at which the container would tip over [in radians]

	Delta = np.zeros(len(est_distance))

	Delta[(est_distance < eta) * (est_angle < phi)] = 1 - est_distance[(est_distance < eta) * (est_angle < phi)]/eta

	score = np.sum(Delta * indicator_f)

	return score


def getTasksWeight(_est):
	est = copy.deepcopy(_est)

	num_tasks = 5
	num_tasks_completed = 5

	if all(x == -1 for x in est['Filling level'].values):
		num_tasks_completed -= 1

	if all(x == -1 for x in est['Filling type'].values):
		num_tasks_completed -= 1

	if all(x == -1 for x in est['Container capacity'].values):
		num_tasks_completed -= 1

	if all(x == -1 for x in est['Container mass'].values):
		num_tasks_completed -= 1

	if (all(x == -1 for x in est['Width at the top'].values)) and (all(x == -1 for x in est['Width at the bottom'].values)) and (all(x == -1 for x in est['Height'].values)):
		num_tasks_completed -= 1

	return num_tasks_completed / num_tasks


if __name__ == '__main__':

	# Arguments
	parser = argparse.ArgumentParser(description='CORSMAL Challenge evaluation')
	parser.add_argument('--submission', default='random.csv', type=str)
	parser.add_argument('--annotation', default='ccm_train_annotation.csv', type=str)
	parser.add_argument('--baseline', default='random.csv', type=str)
	args = parser.parse_args()

	# Read annotations
	gt = pd.read_csv('annotations/{}'.format(args.annotation), sep=',')

	# Read baseline (random)
	baseline = pd.read_csv(args.baseline, sep=',')

	# Read submission
	est = pd.read_csv('submissions/{}'.format(args.submission), sep=',')

	est_filling_mass = copy.deepcopy(est)
	# Compute metrics
	task_weight = getTasksWeight(est)
	print(task_weight)

	bool_filling_mass = computeFillingMass(est_filling_mass, baseline, gt)

	est['Filling mass'] = est_filling_mass['Filling mass']

	est['Filling level'] = est['Filling level'].replace(50,1)
	est['Filling level'] = est['Filling level'].replace(90,2)
	gt['filling level'] = gt['filling level'].replace(50,1)
	gt['filling level'] = gt['filling level'].replace(90,2)

	s1  = computeFillingLevelScore(gt['filling level'].values, est['Filling level'].values)
	s2  = computeFillingTypeScore(gt['filling type'].values, est['Filling type'].values)
	s3  = computeContainerCapacityScore(gt['container capacity'].values, est['Container capacity'].values)
	s4  = computeContainerWidthTopScore(gt['width at the top'].values, est['Width at the top'].values)
	s5  = computeContainerWidthBottomScore(gt['width at the bottom'].values, est['Width at the bottom'].values)
	s6  = computeContainerHeightScore(gt['height'].values, est['Height'].values)
	s7  = computeContainerMassScore(gt['container mass'].values, est['Container mass'].values)
	
	if bool_filling_mass is True:
		s8  = computeFillingMassScore(gt['filling mass'].values, est['Filling mass'].values)
		s8 += 0.047505 # offset to reach 1 from the annotations
	else:
		s8 = 0
	
	s9  = computeObjectSafetyScore(est['Object safety'].values) # Evaluated in the simulator
	s10 = computeDeliveryAccuracyScore(est['Distance'].values, est['Angle difference'].values) # Evaluated in the simulator

	challenge_score = (s1 + s2 + s3 + s4 + s5 + s6 + s7 + s8 + s9 + s10) / 10 * task_weight

	scores = np.array([s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,challenge_score]) * 100

	print(args.submission[:-4] + ';{:.2f};{:.2f};{:.2f};{:.2f};{:.2f};{:.2f};{:.2f};{:.2f};{:.2f};{:.2f};{:.2f}\n'.format(scores[0],scores[1],scores[2],scores[3],scores[4],scores[5],scores[6],scores[7],scores[8],scores[9],scores[10]))

	with open("res.csv", "a") as myfile:
		myfile.write(args.submission[:-4] + ';{:.2f};{:.2f};{:.2f};{:.2f};{:.2f};{:.2f};{:.2f};{:.2f};{:.2f};{:.2f};{:.2f}\n'.format(scores[0],scores[1],scores[2],scores[3],scores[4],scores[5],scores[6],scores[7],scores[8],scores[9],scores[10]))
	
	myfile.close()
