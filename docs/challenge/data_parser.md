# DataParser for CORSMAL Containers Manipulation

Python script for parsing the CORSMAL Containers Manipulation dataset, including
train set, public test set, and private test set. The script includes
Numpy, OpenCV, and PyTorch libraries for testing and starting the development
of solutions to solve different tasks on the dataset. To simply test the parsing
of the dataset, libraries can be commented out.

[Dataset](http://corsmal.eecs.qmul.ac.uk/containers_manip.html)


## Tested on
* Python 3.8.5
* Server machine with CentOS Linux release 7.7.1908

## Installation
Download or clone the repository.
```
git clone https://github.com/CORSMAL/CCM-DataParser.git
```

## How to run
Use the following command and modify the options accordingly:
```
python ccm_data_parser.py --datapath <DATAPATH> --set [train, pubtest, privtest]
```

## Starting kit
If you wish to integrate your software directly into the current script, we 
suggest the following libraries (already tested):
* OpenCV 4.4.0
* PyTorch 1.6.0
* TorchVision 0.7.0
* NVIDIA CUDA 10.1
* Anaconda3 (4.7.12)
* Numpy 19.1.1

You can find some commands in the script that are commented to start integrating
the software in the script.

To overcome root privilege issues and favour reproducibility across machine with
different compatibilities, we recommend to create virtual environments and we
suggest Anaconda/Miniconda. See the following tutorial for more infor on how to
install miniconda: 
[Miniconda tutorial](https://docs.conda.io/en/latest/miniconda.html)

```
conda create -n CCM
source activate CCM

conda install scipy numpy
conda install -c conda-forge opencv
conda install -c pytorch torchvision
pip install pickle5
```

Pickle library is necessary for reading calibration files.

The script will output Python and OpenCV versions and if GPU is enabled.


## Enquiries, Question and Comments

If you have any further enquiries, question, or comments, please contact 
corsmal-challenge@qmul.ac.uk If you would like to 
file a bug report or a feature request, use the Github issue tracker. 

## Licence
This work is licensed under the MIT License. To view a copy of this license, 
see [LICENSE](../LICENSE).

