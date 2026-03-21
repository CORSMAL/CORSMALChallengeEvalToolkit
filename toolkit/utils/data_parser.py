#!/usr/bin/env python
#
################################################################################## 
# Author: 
#   - Alessio Xompero: a.xompero@qmul.ac.uk
#         Email: corsmal-challenge@qmul.ac.uk
#
#  Created Date: 2020/09/13
# Modified Date: 2021/11/08
#
################################################################################## 
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


# COMMENT OUT WHAT YOU DO NOT NEED
def ParseFile(containerpath, f):
	## RGB DATA
	for cam_id in range(1,5):
		rgbvideo = containerpath + 'view{:d}/rgb/'.format(cam_id) + f + '.mp4'
		print(rgbvideo)

	## AUDIO DATA
	audiofile = containerpath + 'audio/' + f + '.wav'
	print(audiofile)

	## DEPTH DATA
	for cam_id in range(1,5):
		depthpath = containerpath + 'view{:d}/depth/'.format(cam_id) + f + '/'
		# print(depthpath)

		for dfile in glob.glob(depthpath + '/*.png'):
			print(dfile)

	## IR DATA
	for cam_id in range(1,5):
		videoir1 = containerpath + 'view{:d}/infrared1/'.format(cam_id) + f + '.mp4'
		print(videoir1)

		videoir2 = containerpath + 'view{:d}/infrared2/'.format(cam_id) + f + '.mp4'
		print(videoir2)

	## CALIBRATION DATA
	for cam_id in range(1,5):
		calibfile = containerpath + 'view{:d}/calib/'.format(cam_id) + f + '.pickle'
		print(calibfile)

	## IMU DATAa
	for cam_id in range(3,5):
		accelfile = containerpath + 'view{:d}/accel/'.format(cam_id) + f + '.csv'
		print(accelfile)

		gyrofile = containerpath + 'view{:d}/gyro/'.format(cam_id) + f + '.csv'
		print(gyrofile)


#### TRAIN SET ###
def TrainSetDataParser(args):
	for j in range(0,684):
		ParseFile(args.datapath, '{:06d}'.format(j))

#### PUBLIC TEST SET ###
def PublicTestSetDataParser(args):
	for j in range(0,228):
		ParseFile(args.datapath, '{:06d}'.format(j))

#### PRIVATE TESTING SET ###
def PrivateTestSetDataParser(args):
	for j in range(0,228):
		ParseFile(args.datapath, '{:06d}'.format(j))


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
		TrainSetDataParser(args)
	elif args.set == 'pubtest':
		PublicTestSetDataParser(args)
	elif args.set == 'privtest':
		PrivateTestSetDataParser(args)

	print('Finished!')