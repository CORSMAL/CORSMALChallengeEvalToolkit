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

# from pdb import set_trace as bp

# fLev = [0,50,90]


def populateFile(id_con, n_seq, task1, task2, task3, myfile):

  for x in range(0,n_seq):
    e1 = -1
    e2 = -1
    e3 = -1
    
    if task1 == True:
      e1 = random.randint(0,3)
    
    if task2 == True:
      # y = random.randint(0,2)
      # e2 = fLev[y]
      e2 = random.randint(0,2)

    if task3 == True:
      e3 = round(3950*random.random() + 50)
    
    # print('[{:d}, {:d}, {:d}, {:d}, {:d}]'.format(id_con, x, e1, e2, e3))
    myfile.write('{:d},{:d},{:d},{:d},{:d}\n'.format(id_con, x, e1, e2, e3))
    

if __name__ == '__main__':

  # Arguments
  parser = argparse.ArgumentParser(description='CORSMAL Challenge evaluation')
  parser.add_argument('--task1', default=False, action='store_true')
  parser.add_argument('--task2', default=False, action='store_true')
  parser.add_argument('--task3', default=False, action='store_true')
  parser.add_argument('--filename', default='teamN.csv', type=str)
  args = parser.parse_args()


  myfile = open(args.filename, "w")
  myfile.write('Container ID,Sequence,Filling type,Filling level,Container Capacity\n')

  populateFile(1,84, args.task1, args.task2, args.task3, myfile)
  populateFile(2,84, args.task1, args.task2, args.task3, myfile)
  populateFile(3,84, args.task1, args.task2, args.task3, myfile)
  populateFile(4,84, args.task1, args.task2, args.task3, myfile)
  populateFile(5,84, args.task1, args.task2, args.task3, myfile)
  populateFile(6,84, args.task1, args.task2, args.task3, myfile)
  populateFile(7,60, args.task1, args.task2, args.task3, myfile)
  populateFile(8,60, args.task1, args.task2, args.task3, myfile)
  populateFile(9,60, args.task1, args.task2, args.task3, myfile)

  myfile.close()