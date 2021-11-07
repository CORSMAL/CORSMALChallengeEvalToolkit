#!/usr/bin/env python
#
################################################################################## 
# Author: 
#   - Alessio Xompero: a.xompero@qmul.ac.uk
#         Email: corsmal-challenge@qmul.ac.uk
#
#  Created Date: 2020/09/13
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
#

# System libs
import glob
import sys
import argparse
import os


# Numeric libs
# import cv2
# import numpy as np

# import torch
# import torchvision

# from pdb import set_trace as bp

#
# device = 'cuda' if torch.cuda.is_available() else 'cpu'


fnames_filling =  ['fi0_fu0','fi1_fu1', 'fi1_fu2','fi2_fu1', 'fi2_fu2', 'fi3_fu1', 'fi3_fu2']
fnames_filling2 = ['fi0_fu0','fi1_fu1', 'fi1_fu2','fi2_fu1', 'fi2_fu2']

def populate_filenames(mode):
	list_filenames = []
	for s in range(0,3):
		str_s = 's{:d}_'.format(s)
		
		for b in range(0,2):
			str_b = '_b{:d}_'.format(b)
			
			for l in range(0,2):
				str_l = 'l{:d}'.format(l)

				if mode == 0:
					for f in fnames_filling:
						list_filenames.append(str_s + f + str_b + str_l)
				else:
					for f in fnames_filling2:
						list_filenames.append(str_s + f + str_b + str_l)

	return list_filenames


# COMMENT OUT WHAT YOU DO NOT NEED
def ParseFile(containerpath, f):
	## RGB DATA
	for cam_id in range(1,5):
		rgbvideo = containerpath + '/rgb/' + f + '_c{:d}.mp4'.format(cam_id)
		print(rgbvideo)

	## AUDIO DATA
	audiofile = containerpath + '/audio/' + f + '_audio.wav'
	print(audiofile)

	## DEPTH DATA
	for cam_id in range(1,5):
		depthpath = containerpath + '/depth/' + f + '/c{:d}'.format(cam_id)
		# print(depthpath)

		for dfile in glob.glob(depthpath + '/*.png'):
			print(dfile)


	## IR DATA
	for cam_id in range(1,5):
		videoir1 = containerpath + '/ir/' + f + '_c{:d}_ir1.mp4'.format(cam_id)
		print(videoir1)

		videoir2 = containerpath + '/ir/' + f + '_c{:d}_ir2.mp4'.format(cam_id)
		print(videoir2)

	## CALIBRATION DATA
	for cam_id in range(1,5):
		calibfile = containerpath + '/calib/' + f + '_c{:d}_calib.pickle'.format(cam_id)
		print(calibfile)

	## IMU DATAa
	for cam_id in range(3,5):
		accelfile = containerpath + '/imu/' + f + '_accel_c{:d}.csv'.format(cam_id)
		print(accelfile)

		gyrofile = containerpath + '/imu/' + f + '_gyro_c{:d}.csv'.format(cam_id)
		print(gyrofile)


#### TRAINING DATA ###

def TrainingDataParser(args):
	for objid in range(1,10):
		containerpath = args.datapath + '/{:d}'.format(objid)
		
		if objid < 7:
			list_files = populate_filenames(0)
		else:
			list_files = populate_filenames(1)

		for f in list_files:
			ParseFile(containerpath, f)


#### PUBLIC TESTING SET ###
def PublicTestingDataParser(args):
	for objid in range(10,13):
		containerpath = args.datapath + '/{:d}'.format(objid)
		
		list_files = []
		if objid < 12:
			for j in range(0,84):
				list_files.append('{:04d}'.format(j))
		else:
			for j in range(0,60):
				list_files.append('{:04d}'.format(j))

		for f in list_files:
			ParseFile(containerpath, f)


#### PRIVATE TESTING SET ###
def PrivateTestingDataParser(args):
	for objid in range(13,16):
		containerpath = args.datapath + '/{:d}'.format(objid)
		
		list_files = []
		if objid < 15:
			for j in range(0,84):
				list_files.append('{:04d}'.format(j))
		else:
			for j in range(0,60):
				list_files.append('{:04d}'.format(j))

		for f in list_files:
			ParseFile(containerpath, f)


if __name__ == '__main__':
	# Parse arguments
	parser = argparse.ArgumentParser(prog='ccm_data_parser', usage='%(prog)s --datapath <DATAPATH> --set [train, pubtest, privtest]')
	parser.add_argument('--datapath', type=str)
	parser.add_argument('--set', type=str, default='pubtest', choices=['train','pubtest','privtest'])

	args = parser.parse_args()

	print('Initialising:')
	print('Python {}.{}'.format(sys.version_info[0], sys.version_info[1]))
	# print('OpenCV {}'.format(cv2.__version__))

	# Check if script can run with GPU 
	# if device == 'cuda':
	# 	torch.cuda.set_device(0)
	# print('Using {}'.format(device))
	
	if args.set == 'train':
		TrainingDataParser(args)
	elif args.set == 'pubtest':
		PublicTestingDataParser(args)
	elif args.set == 'privtest':
		PrivateTestingDataParser(args)

	print('Finished!')