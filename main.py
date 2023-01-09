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


def check_length_arrays(array1, array2):
    if len(array1) != len(array2):
        raise Exception(
                "Number of predictions does not equal number of ground truths.")

###############################################################################
class CorsmalEvaluationToolkit():
    def __init__(self):
        
        reset_all_scores()


    def reset_all_scores(self):
        # Vision scores
        self.width_top = 0               # in mm
        self.width_bottom = 0            # in mm
        self.height = 0                  # in mm  
        self.mass = 0                    # in g (cup + filling)
        self.fullness = 0                # in %

        # Robot scores
        self.mass_robot = 0              # in mm
        self.hand_pose = 0               # in mm, degrees
        self.end_effector = 0            # in mm, degrees

        # Task scores
        self.delivery_location = 0       # in mm
        self.delivery_mass_filling = 0   # in grams
        self.time_human_maneuvering = 0  # in mm
        self.time_handover = 0           # in mm
        self.time_robot_maneuvering = 0  # in mm

        # Group scores
        self.vision_score = 0
        self.robot_score = 0
        self.task_score = 0
        
        self.benchmark_score = 0


    # Sigma functions
    def compute_score_type_1(self, a, b):
        if a == 0 and b == 0:
            return 1
        
        diff_a_b = np.abs(a-b)
        if diff_a_b >= b:
            return 0
        
        return 1 - ( diff_a_b / b)    

    def compute_score_type_2(self, a, eta):
        if a < eta:
            return 1 - (a/eta)
        else:
            return 0

    def compute_score_type_3(self, P, P_hat, epsilon):
        # NOTE: I do not know the exact dimensions of P - therefore I left it 
        # as a TODO for the moment
        return 0


    def compute_width_top(self, preds, gts):
        check_length_preds_gts(preds, gts)
        
        width_top = 0
        for pred, gt in zip(preds, gts):
            width_top += sigma_1(pred, gt)
        
        self.width_top = width_top / len(preds)


    def compute_width_bottom(self, preds, gts):
        check_length_preds_gts(preds, gts)
        
        width_bottom = 0
        for pred, gt in zip(preds, gts):
            width_bottom += sigma_1(pred, gt)
        
        self.width_bottom = width_bottom / len(preds)


    def compute_height(self, pred, gts):
        check_length_preds_gts(preds, gts)
        
        height = 0
        for pred, gt in zip(preds, gts):
            height += sigma_1(pred, gt)
        
        self.height = height / len(preds)


    def compute_mass_vision(self, preds, gts):
        check_length_preds_gts(preds, gts)
        
        mass = 0
        for pred, gt in zip(preds, gts):
            mass += sigma_1(pred, gt)
        
        self.mass = mass / len(preds)


    def compute_fullness(self, preds, gts):
        check_length_preds_gts(preds, gts)
        
        fullness = 0
        for pred, gt in zip(preds, gts):
            fullness += (1 - (np.abs(pred - gt) / 100))
        
        self.fullness = fullness / len(preds)


    def compute_vision_score(self):
        vision_score =  self.width_top / 9
                        + self.width_bottom / 9
                        + self.height / 9
                        + self.mass / 3
                        + self.fullness /3

        self.vision_score = vision_score


    def compute_mass_robot(self, preds, gts):
        check_length_preds_gts(preds, gts)
        
        mass = 0
        for pred, gt in zip(preds, gts):
            mass += sigma_1(pred, gt)
        
        self.mass_robot = mass / len(preds)

    def compute_human_hand_pose_prediction(self, preds, gts, epsilon):
        hand_pose = compute_score_type_3(preds, gts. epsilon)
        self.hand_pose = hand_pose

    def compute_end_effector(self, preds, gts, epsilon):
        end_effector = compute_score_type_3(preds, gts. epsilon)
        self.end_effector = end_effector


     def compute_robot_score(self):
        robot_score =  self.mass_robot + self.hand_pose + self.end_effector
        self.robot_score = robot_score / 3

    
    def compute_benchmark_score(self):
        benchmark_score = self.vision_score 
                        + self.robot_score 
                        + self.task_score
        
        benchmark_score /= 3
        self.benchmark_score = benchmark_score
    

    def get_vision_score(self):
        return self.vision_score

    def get_robot_score(self):
        return self.robot_score

    def get_task_score(self):
        return self.task_score

    def get_benchmark_score(self):
        return self.benchmark_score



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


# GETTERS
def get_gt_fullnesses(fillings, cups, GTs):
    gt_fullnesses = []
    for i in range(0, 288):
        current_filling = fillings[i]
        current_cup = cups[i]
        current_volume = GTs["volume"]["cup{}".format(current_cup)]
        gt_fullness = current_filling / current_volume * 100
        gt_fullnesses.append(gt_fullness)
    return gt_fullnesses



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
        predicted_wis_mm = df.loc[:, "w^i (mm)"]        # width at top
        predicted_wibs = df.loc[:, "w^i_b (mm)"]        # width at bottom
        predicted_his = df.loc[:, "h^i (mm)"]           # height
        predicted_mivs = df.loc[:, "m^i_v (grams)"]     # mass - vision
        predicted_fis = df.loc[:, "f^i (%)"]            # fullness
        predicted_mirs = df.loc[:, "m^i_r (grams)"]     # mass - robot
        predicted_dis = df.loc[:, "d^i (mm)"]           # delivery location
        predicted_wis_g = df.loc[:, "w^i (grams)"]      # mass of delivered filling
        predicted_tihms1 = df.loc[:, "t^i_{hm} (ms)"]   # human maneuvering time
        predicted_tihms2 = df.loc[:, "t^i_{ho} (ms)"]   # handover time
        predicted_tirms = df.loc[:, "t^i_{rm} (ms)"]    # robot maneuvering time

        #print("Predicted WIS:\n", predicted_wis_mm.to_numpy())

        print("\nComputed scores")
        # s1
        cup1_18 = np.repeat(GTs["width_at_the_top"]["cup1"], 18)
        cup2_18 = np.repeat(GTs["width_at_the_top"]["cup2"], 18)
        cup3_18 = np.repeat(GTs["width_at_the_top"]["cup3"], 18)
        cup4_18 = np.repeat(GTs["width_at_the_top"]["cup4"], 18)
        cups_all = np.concatenate([cup1_18, cup2_18, cup3_18, cup4_18])
        cups_preds = np.tile(cups_all, 4)
        s1 = s1_s2_s3_s4_s6_s10(predicted_wis_mm, cups_preds)
        print("s1 :", s1)

        # s2
        cup1_18 = np.repeat(GTs["width_at_the_bottom"]["cup1"], 18)
        cup2_18 = np.repeat(GTs["width_at_the_bottom"]["cup2"], 18)
        cup3_18 = np.repeat(GTs["width_at_the_bottom"]["cup3"], 18)
        cup4_18 = np.repeat(GTs["width_at_the_bottom"]["cup4"], 18)
        cups_all = np.concatenate([cup1_18, cup2_18, cup3_18, cup4_18])
        cups_preds = np.tile(cups_all, 4)
        s2 = s1_s2_s3_s4_s6_s10(predicted_wibs, cups_preds)
        print("s2 :", s2)

        # s3
        cup1_18 = np.repeat(GTs["height"]["cup1"], 18)
        cup2_18 = np.repeat(GTs["height"]["cup2"], 18)
        cup3_18 = np.repeat(GTs["height"]["cup3"], 18)
        cup4_18 = np.repeat(GTs["height"]["cup4"], 18)
        cups_all = np.concatenate([cup1_18, cup2_18, cup3_18, cup4_18])
        cups_preds = np.tile(cups_all, 4)
        s3 = s1_s2_s3_s4_s6_s10(predicted_wibs, cups_preds)
        print("s3 :", s3)
        
        # s4 - NOTE: I'm not sure how to compute the mass of the filling
        print("s4 : not implemented yet.")

        # s5 
        gt_fullnesses = get_gt_fullnesses(fillings, cups, GTs)
        s5 = compute_s5(gt_fullnesses, predicted_fis)
        print("s5 :", s5)
        
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