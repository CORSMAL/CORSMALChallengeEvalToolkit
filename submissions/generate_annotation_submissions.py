#!/usr/bin/env python
#
# Evaluation script for the training set of the CORSMAL Challenge
#
################################################################################## 
#        Author: Alessio Xompero
#         Email: corsmal-challenge@qmul.ac.uk
#
#  Created Date: 2020/09/02
# Modified Date: 2020/10/04
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
import random
import argparse

import pandas as pd
import numpy as np

from pdb import set_trace as bp



def getDummyDataFrame(num_configs):
  cols_headers = ['Configuration ID','Container capacity','Container mass',\
  'Filling mass','None','Pasta','Rice','Water','Filling type','Empty',\
  'Half-full','Full','Filling level','Width at the top','Width at the bottom',\
  'Height','Object safety','Distance','Angle difference','Execution time']

  dummy_mat = -np.ones((num_configs,20))
  
  df = pd.DataFrame(data=dummy_mat,columns=cols_headers)

  return df

def populateAnnotationEstimations(gt, args):
  num_configs = len(gt['id'].values)

  df = getDummyDataFrame(num_configs)

  df['Configuration ID'] = gt['id']

  num_tasks=0

  if args.task1:
    df['Empty'] = (gt['filling level'].values == 0).astype(int)
    df['Half-full'] = (gt['filling level'].values == 1).astype(int)
    df['Full'] = (gt['filling level'].values == 2).astype(int)
    df['Filling level'] = gt['filling level']
    num_tasks += 1

  if args.task2:
    df['None'] = (gt['filling type'].values == 0).astype(int)
    df['Pasta'] = (gt['filling type'].values == 1).astype(int)
    df['Rice'] = (gt['filling type'].values == 2).astype(int)
    df['Water'] = (gt['filling type'].values == 3).astype(int)
    df['Filling type'] = gt['filling type']
    num_tasks += 1

  if args.task3:
    df['Container capacity'] = gt['container capacity']
    num_tasks += 1

  if args.task4:
    df['Container mass'] = gt['container mass']
    num_tasks += 1

  if args.task5:
    df['Width at the top'] = gt['width at the top']
    df['Width at the bottom'] = gt['width at the bottom']
    df['Height'] = gt['height']
    num_tasks += 1

  # if num_tasks > 0:
    # df['Execution time'] = est['Execution time']

  return df

def populateRandomEstimations(est, gt, args):
  num_configs = len(est['Configuration ID'].values)

  df = getDummyDataFrame(num_configs)

  df['Configuration ID'] = est['Configuration ID']

  num_tasks=0

  if args.task1:
    df['Empty'] = est['Empty']
    df['Half-full'] = est['Half-full']
    df['Full'] = est['Full']
    df['Filling level'] = est['Filling level']
    num_tasks += 1

  if args.task2:
    df['None'] = est['None']
    df['Pasta'] = est['Pasta']
    df['Rice'] = est['Rice']
    df['Water'] = est['Water']
    df['Filling type'] = est['Filling type']
    num_tasks += 1

  if args.task3:
    if args.mode == 'average':
      cc_avg = np.average(gt['container capacity'].unique())
      df['Container capacity'] = df['Container capacity'].replace(-1,int(cc_avg))
    else:
      df['Container capacity'] = est['Container capacity']
    num_tasks += 1

  if args.task4:
    if args.mode == 'average':
      cm_avg = np.average(gt['container mass'].unique())
      df['Container mass'] = df['Container mass'].replace(-1,int(cm_avg))
    else:
      df['Container mass'] = est['Container mass']
    num_tasks += 1

  if args.task5:
    if args.mode == 'average':
      cwt_avg = np.average(gt['width at the top'].unique())
      df['Width at the top'] = df['Width at the top'].replace(-1,int(cwt_avg))

      cwb_avg = np.average(gt['width at the bottom'].unique())
      df['Width at the bottom'] = df['Width at the bottom'].replace(-1,int(cwb_avg))

      ch_avg = np.average(gt['height'].unique())
      df['Height'] = df['Height'].replace(-1,int(ch_avg))
    else:
      df['Width at the top'] = est['Width at the top']
      df['Width at the bottom'] = est['Width at the bottom']
      df['Height'] = est['Height']
    num_tasks += 1

  if num_tasks > 0:
    df['Execution time'] = est['Execution time']  

  return df


if __name__ == '__main__':

  # Arguments
  parser = argparse.ArgumentParser(description='CORSMAL Challenge evaluation')
  parser.add_argument('--task1', default=False, action='store_true')
  parser.add_argument('--task2', default=False, action='store_true')
  parser.add_argument('--task3', default=False, action='store_true')
  parser.add_argument('--task4', default=False, action='store_true')
  parser.add_argument('--task5', default=False, action='store_true')
  parser.add_argument('--filename', default='teamN.csv', type=str)
  parser.add_argument('--set', default='train', help="Choose the set option:\n--train\n--test_pub\n--test_priv", choices=['train','test_pub','test_priv'])
  parser.add_argument('--mode', default='annotation', help="Choose the set option:\n--annotation\n--random\n--average", choices=['annotation','random','average'])
  args = parser.parse_args()

  if args.set == 'train':
      gt = pd.read_csv('../annotations/ccm_train_annotation.csv', sep=',')
      rnd = pd.read_csv('train_set/random1.csv', sep=',')
      outfilename = 'train_set/' + args.filename
  
  elif args.set == 'test_pub':
      gt = pd.read_csv('../annotations/ccm_test_pub_annotation.csv', sep=',')
      rnd = pd.read_csv('pub_test_set/random1.csv', sep=',')
      outfilename = 'pub_test_set/' + args.filename

  elif args.set == 'test_priv':
      gt = pd.read_csv('../annotations/ccm_test_priv_annotation.csv', sep=',')
      rnd = pd.read_csv('priv_test_set/random1.csv', sep=',')
      outfilename = 'priv_test_set/' + args.filename


  if args.mode == 'annotation':
    df = populateAnnotationEstimations(gt, args)
  elif args.mode == 'random':
    df = populateRandomEstimations(rnd, gt, args)
  elif args.mode == 'average':
    df = populateRandomEstimations(rnd, gt, args)

  df.to_csv(outfilename,index=False)
