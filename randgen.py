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


# Each row corresponds to the respective configuration, the second column is the estimated capacity of the container in millilitres, 
# the third column is the mass of the empty container in grams, the fourth column is the mass of the filling in grams, 
# the fifth, sixth, seventh, and eight columns are the probabilities for each filling type (none, water, pasta or rice), 
# the ninth, tenth, and eleventh columns are the probabilities of the estimated filling level (0%, 50% or 90%), 
# the twelfth, thirteenth, and fourteenth columns are the width at the top, width at the bottom, and the height in millimetres, 
# the fifteenth column is the measured object safety in the simulator, the sixteenth and seventeenth columns are the distance 
# in millimetres and angle difference in degrees measured in the simulator, and the eighteenth column provides the execution time in milliseconds.


# s1: filling level
# s2: filling type
# s3: container capacity
# s4: container mass
# s5: width at the top
# s6: width at the bottom
# s7: height
# s8: filling mass
# s9: object safety
# s10: delivery accuracy

def populateFile(n_conf, t1, t2, t3, t4, t5, myfile):

  for x in range(0,n_conf):
    c01 = x  # configuration id
    c02 = -1      # estimated capacity of the container in millilitres
    c03 = -1      # estimated mass of the empty container in grams
    c04 = -1      # estimated mass of the filling in grams
    c05 = -1      # filling type: none (probability [0,1])
    c06 = -1      # filling type: pasta (probability [0,1])
    c07 = -1      # filling type: rice (probability [0,1])
    c08 = -1      # filling type: water (probability [0,1])
    c09 = -1      # filling type [0,1,2,3]
    c10 = -1      # filling level: empty (probability [0,1])
    c11 = -1      # filling level: half-full (probability [0,1])
    c12 = -1      # filling level: full (probability [0,1])
    c13 = -1      # filling level: [0,1,2]
    c14 = -1      # estimated width at the top in millimetres
    c15 = -1      # estimated width at the bottom in millimetres
    c16 = -1      # estimated height in millimetres
    c17 = -1      # measured object safety
    c18 = -1      # distance from the target location in millimetres measured in the simulator
    c19 = -1      # angle difference in degrees measured in the simulator
    c20 = -1      # estimated execution time in milliseconds
    
    if t1 == True:
      c10 = random.randint(0,100)
      c11 = random.randint(0,100)
      c12 = random.randint(0,100)
      tot = c10 + c11 + c12
      c10 = c10 / tot
      c11 = c11 / tot
      c12 = c12 / tot
      filling_level = [c10,c11,c12]
      c13 = filling_level.index(max(filling_level))
    
    if t2 == True:
      c05 = random.randint(0,100)
      c06 = random.randint(0,100)
      c07 = random.randint(0,100)
      c08 = random.randint(0,100)
      
      tot = c05 + c06 + c07 + c08
      
      c05 = c05 / tot
      c06 = c06 / tot
      c07 = c07 / tot
      c08 = c08 / tot

      filling_type = [c05,c06,c07,c08]
      c09 = filling_type.index(max(filling_type))

    if t3 == True:
      c02 = round(3950*random.random() + 50)

    if t4 == True:
      c03 = round(350*random.random() + 1)

    if t5 == True:
      c14 = round(300*random.random() + 50)
      c15 = round(350*random.random() + 30)
      c16 = round(350*random.random() + 20)
    
    c20 = round(5000*random.random() + 20)
    # print('[{:d}; {:d}; {:d}; {:d}; {:d}]'.format(id_con, x, e1, e2, e3))
    myfile.write('{:d},{:d},{:d},{:d},{:.2f},{:.2f},{:.2f},{:.2f},{:d},{:.2f},{:.2f},{:.2f},{:d},{:d},{:d},{:d},{:d},{:d},{:d},{:d}\n'.format(c01,c02,c03,c04,c05,c06,c07,c08,c09,c10,c11,c12,c13,c14,c15,c16,c17,c18,c19,c20))
    

if __name__ == '__main__':

  # Arguments
  parser = argparse.ArgumentParser(description='CORSMAL Challenge evaluation')
  parser.add_argument('--task1', default=False, action='store_true')
  parser.add_argument('--task2', default=False, action='store_true')
  parser.add_argument('--task3', default=False, action='store_true')
  parser.add_argument('--task4', default=False, action='store_true')
  parser.add_argument('--task5', default=False, action='store_true')
  parser.add_argument('--filename', default='teamN.csv', type=str)
  parser.add_argument('--num_configs', default=684, type=int)
  args = parser.parse_args()


  myfile = open(args.filename, "w")
  myfile.write('Configuration ID,Container capacity,Container mass,Filling mass,None,Pasta,Rice,Water,Filling type,Empty,Half-full,Full,Filling level,Width at the top,Width at the bottom,Height,Object safety,Distance,Angle difference,Execution time\n')

  populateFile(args.num_configs, args.task1, args.task2, args.task3,args.task4,args.task5, myfile)

  myfile.close()