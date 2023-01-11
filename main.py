#!/usr/bin/env python
#
# Evaluation script for the CORSMAL Benchmark
#
################################################################################## 
# Authors: 
# - Alessio Xompero
# - Xavier Weber
# 
# Email: corsmal-challenge@qmul.ac.uk
#
#  Created Date: 2020/08/25
# Modified Date: 2023/01/09
#
# MIT License

# Copyright (c) 2023 CORSMAL

# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.
#----------------------------------------------------------------------------
"""

Written by Xavier Weber

Refer to: https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=8968407

TODO:
 - [ ] implement sigma_3()
 - [ ] implement s7_s8()
 - [ ] add functions from the 'challenge' script
 - [ ] read .xlsx file and compute the scores

NOTE:
- I don't know how to compute the mass of the filling. We only have the filling amount in millilitre, but to compute mass,
  you need to convert it to grams. So you need to know how much the filling per ml weighs in grams. The ground-truths were done in white rice,
  which is about 0.81g per 1ml. But the predictions could have used different rice, which could have a different weighing factor.

"""

import argparse
import pandas as pd
import json
import numpy as np

##################################################################################
def create_new_pandaframe_submission_form():
    """
    Let's create a better form for the submission_form_test.xlsx
    """
    df = pd.DataFrame()
    
    cups = [1]*18 + [2]*18 + [3]*18 + [4]*18
    cups = cups*4

    filling_ml = [0]*9 + [125]*9 + [0]*9 + [400]*9 + [0]*9 + [450]*9 + [0]*9 + [300]*9
    filling_ml = filling_ml*4

    grasp_types = [1]*3 + [2]*3 + [3]*3 
    grasp_types = grasp_types * 32

    handover_location = [1,2,3] * 96

    subjects = [1]*72 + [2]*72 + [3]*72 + [4]*72

    # configuration
    df["configuration"] = list(range(1, 289))
    df["cup"] = cups
    df["filling (ml)"] = filling_ml
    df["grasp type"] = grasp_types
    df["handover location"] = handover_location
    df["subject"] = subjects
    df["w^i (mm)"] = [-1] * 288
    df["w^i_b (mm)"] = [-1] * 288
    df["h^i (mm)"] = [-1] * 288 
    df["m^i_v (grams)"] = [-1] * 288
    df["f^i (%)"] = [-1] * 288
    df["m^i_r (grams)"] = [-1] * 288
    df["d^i (mm)"] = [-1] * 288
    df["w^i (grams)"] = [-1] * 288
    df["t^i_{hm} (ms)"] = [-1] * 288
    df["t^i_{ho} (ms)"] = [-1] * 288
    df["t^i_{rm} (ms)"] = [-1] * 288
    
    df.to_csv("./Submission_form.csv")


# Group: Task
def s9_s11_s12_s13(preds, thr):
    running_scores = 0
    for pred in preds:
        running_scores += sigma_2(pred, thr)
    return running_scores / len(preds)

def Sg(lambdas, s9, s11, s12, s13):
    return lambdas[8] * s9 + lambdas[10] * s11 + lambdas[11] * s12 + lambdas[12] * s13



def GetParser():
    parser = argparse.ArgumentParser(
        description='CORSMAL Evaluation Toolkit',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--challenge', action='store_true')
        parser.add_argument('--benchmark', action='store_true')
        parser.add_argument('--submission_csv', default='random.csv', type=str)
        #parser.add_argument('--submission_xlsx', default='Submission_form.xlsx', type=str)
    
    return parser



if __name__ == '__main__':
    
    print('Initialising:')
    print('Python {}.{}'.format(sys.version_info[0], sys.version_info[1]))
    # print('OpenCV {}'.format(cv2.__version__))

    # Arguments
    parser = GetParser()
    args = parser.parse_args()

    #create_new_pandaframe_submission_form()
    
    if args.benchmark:
        
        # Read .json dictionary containing the ground-truths
        f = open('benchmark_groundtruths.json')
        GTs = json.load(f)

        # Read .xlsx file containing the predictions
        #PREDs_df = pd.read_excel(args.submission_xlsx, 'Measures')
        df = pd.read_csv(args.submission_csv)
        print(df)

        # Get the configuration data from the dataframe
        configurations = df.loc[:, "configuration"]
        cups = df.loc[:, "cup"]
        fillings = df.loc[:, "filling (ml)"]
        grasp_types = df.loc[:, "grasp type"]
        handover_locations = df.loc[:, "handover location"]
        subjects = df.loc[:, "subject"]
        
        # Get the predictions from the column from the dataframe    
        predicted_mirs = df.loc[:, "m^i_r (grams)"]     # mass - robot
        predicted_dis = df.loc[:, "d^i (mm)"]           # delivery location
        predicted_wis_g = df.loc[:, "w^i (grams)"]      # mass of delivered filling
        predicted_tihms1 = df.loc[:, "t^i_{hm} (ms)"]   # human maneuvering time
        predicted_tihms2 = df.loc[:, "t^i_{ho} (ms)"]   # handover time
        predicted_tirms = df.loc[:, "t^i_{rm} (ms)"]    # robot maneuvering time

        #print("Predicted WIS:\n", predicted_wis_mm.to_numpy())

        print("\nComputed scores")
        print("s1 :", s1)
        
        # s4 - NOTE: I'm not sure how to compute the mass of the filling
        print("s4 : not implemented yet.")
        
        # s6 - NOTE: same as note for s4: I don't know how to compute the mass of the filling
        print("s6 : not implemented yet.")
        
        # s7
        print("s7 : not implemented yet.")

        # s8
        print("s8 : not implemented yet.")

        # s9
        thr = 50
        s9 = s9_s11_s12_s13(predicted_dis, thr)
        print("s9 :", s9, "| Note: this was with a threshold of {}".format(thr))

        # s10
        s10 = s1_s2_s3_s4_s6_s10(predicted_wis_g, fillings)
        print("s10:", s10)
        
        # s11
        s11 = s9_s11_s12_s13(predicted_tihms1, thr)
        print("s11:", s11, "| Note: this was with a threshold of {}".format(thr))
        
        # s12
        s12 = s9_s11_s12_s13(predicted_tihms2, thr)
        print("s12:", s12, "| Note: this was with a threshold of {}".format(thr))

        # s13
        s13 = s9_s11_s12_s13(predicted_tirms, thr)
        print("s13:", s13, "| Note: this was with a threshold of {}".format(thr))

        # TODO: save the scores
        

    print("\nRan succesfully!\n")


# predicted_wibs = PREDs_df.iloc[3:, 7]     # s2  : width at bottom
# predicted_his = PREDs_df.iloc[3:, 8]      # s3  : height
# predicted_mivs = PREDs_df.iloc[3:, 9]     # s4  : mass (cup+filling) - vision
# predicted_fis = PREDs_df.iloc[3:, 10]     # s5  : fullness
# predicted_mirs = PREDs_df.iloc[3:, 11     # s6  : mass (cup+filling) - robot
# predicted_dis = PREDs_df.iloc[3:, 12]     # s9  : delivery location
# predicted_wis = PREDs_df.iloc[3:, 13]     # s10 : mass of the delivered filling
# predicted_tihms1 = PREDs_df.iloc[3:, 14]  # s11 : human maneuvering time
# predicted_tihms2 = PREDs_df.iloc[3:, 15]  # s12 : handover
# predicted_tirms = PREDs_df.iloc[3:, 16]   # s13 : robot maneuvering