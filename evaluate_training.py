#!/usr/bin/env python
#
# Evaluation script for the training set of the CORSMAL Challenge 
# at Intelligent Sensing Summer School 2020, 1-4 Sep
#
################################################################################## 
#        Author: Alessio Xompero
#         Email: corsmal-challenge@qmul.ac.uk
#
#  Created Date: 2020/08/25
# Modified Date: 2020/08/25
#
# Centre for Intelligent Sensing, Queen Mary University of London, UK
# 
################################################################################## 
# License
# This work is licensed under the Creative Commons Attribution-NonCommercial 4.0
# International License. To view a copy of this license, visit 
# http://creativecommons.org/licenses/by-nc/4.0/ or send a letter to 
# Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
##################################################################################
#
import csv
import numpy as np
import pandas as pd
from sklearn import metrics
import argparse 
import copy 


def computeWAFS(gt, est):
	gt = gt.astype(str)
	est = est.astype(str)
	return metrics.f1_score(gt, est, average='weighted')

def computeWARE(gt, _est, containers):
	est = copy.deepcopy(_est)
	est[est==-1] = 0
	score = .0
	for container in np.unique(containers):
		ec = np.abs(gt[containers==container] - est[containers==container]) / gt[containers==container]
		score += np.sum(ec)
	return score/len(gt)

def computeFillingfMassWARE(gt, _est, containers):
	est = copy.deepcopy(_est)

	score = .0
	for container in np.unique(containers):
		gt_c = gt[containers==container]
		est_c = est[containers==container]
		ec = np.abs(gt_c - est_c) / gt_c
		ec[(gt_c==0) & (est_c==0)] = 0
		ec[(gt_c == 0) & (est_c != 0)] = est_c[(gt_c == 0) & (est_c != 0)]
		score_c = np.exp(-ec);
		score_c[est_c==-1]=0
		score += np.sum(score_c)
	# return score/len(gt) + 0.0046
	return score/len(gt) + 0.0475

def computeWAREscore(gt, _est, containers):
	est = copy.deepcopy(_est)
	est[est==-1] = 10**9
	score = .0
	for container in np.unique(containers):
		ec = np.exp(-(np.abs(gt[containers==container] - est[containers==container]) / gt[containers==container]))
		score += np.sum(ec)
	return score/len(gt)

def computeCombined(est, baseline, densities_dict):
	num_tasks  = 3

	if all(est['Filling type'] == -1):
		est['Filling type'] = baseline['Filling type']
		num_tasks -= 1

	densities=[]
	for i in range(len(est)):
		if est['Filling type'][i] == -1:
			densities.append(0)
		else:
			densities.append(densities_dict.loc[est['Container ID'][i]-1][est['Filling type'][i]+1])
	densities = np.array(densities)

	# Replace -1 by the baseline result
	if all(est['Filling level'] == -1):
		est['Filling level'] = baseline['Filling level']
		num_tasks -= 1

	if all(est['Container Capacity'] == -1):
		est['Container Capacity'] = baseline['Container Capacity [mL]']
		num_tasks -= 1
	
	# mass = Filling level x capacity x densitiy(filling)
	estimated_mass = est['Filling level'].values/100. * est['Container Capacity'].values * baseline['Filling density [g/mL]'].values

	if not all(est['Filling level'] == -1):
		estimated_mass[est['Filling level'] == -1] = -1

	if not all(est['Container Capacity'] == -1):
		estimated_mass[est['Container Capacity'] == -1] = -1	

	est.insert(est.shape[1], 'Filling mass [g]', estimated_mass)

	return num_tasks / 3.

if __name__ == '__main__':

	# Arguments
	parser = argparse.ArgumentParser(description='CORSMAL Challenge evaluation')
	parser.add_argument('--submission', default='team1.csv', type=str)
	args = parser.parse_args()

	# Read annotations
	gt = pd.read_csv('annotation_training_set.csv', sep=',')

	# Read annotated densities (for combined task)
	densities_dict = pd.read_csv('density_annotations.csv', sep=';')

	# Read submission
	est = pd.read_csv('submissions/{}'.format(args.submission), sep=',')

	# Compute metrics
	T1 = computeWAFS(gt['Filling level'].values, est['Filling level'].values)
	T2 = computeWAFS(gt['Filling type'].values, est['Filling type'].values)
	T3 = computeWAREscore(gt['Container Capacity [mL]'].values, est['Container Capacity'].values, gt['Container ID'].values)
	task_weight = computeCombined(est, gt, densities_dict)
	T4 = computeFillingfMassWARE(gt['Filling mass [g]'], est['Filling mass [g]'], gt['Container ID'].values)

	print(args.submission[:-4] , ' | {:.2f} | {:.2f} | {:.3f} | {:.3f}'.format(T1*100,T2*100,T3,T4*task_weight))
	with open("res.csv", "a") as myfile:
		myfile.write(args.submission[:-4] + ';{:.2f};{:.2f};{:.2f};{:.2f}\n'.format(T1*100,T2*100,T3*100,T4*100*task_weight))
	
	myfile.close()
