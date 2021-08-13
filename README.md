# Medical Image Segmentation
The aim of the medical image segmentation project is to identify and segment internal organs from medical images using convolutional neural networks, a process that is usually done manually by doctors when treating patients for cancer. At this stage, the left lung has been the focus of this project.

## Project Components
The main components of this project are as follows: 
- Data - the data can be accessed upon request, due to licensing limitations. A smaller dataset can be accessed through a python script.
- iPython Notebook for resampling data - after the data access, the data needs to be run through the resampling code to ensure uniformity of the data
- iPython Notebook for training 2D model and calculating the surface dice score - the 2D_segmentation_model iPython notebook allows for the training of the 2D model
- iPython Notebook for training 3D model - this notebook allows for the training of the 3D model
- A python script containing the code for the calculation of the surface dice metrics

## Setup and Usage
1. Clone the repository to your local machine and run the project using the dockerfile:
	`cd` into the directory with the dockerfile and type the command `docker build .` 
afterwards type the command `docker images` and copy the image id. Paste the image id 
in the following command where it says img-id:
`docker run -it -p 8888:8888 img-id`
2. Instead of using the dockerfile, you can also run these iPython notebooks in the following order:
    - Install all packages: `pip install -r requirements.txt`
    - Download the data via python script
    - Data is split into three folders: train, test, val - 70%, 20%, 10%
You may choose to resplit the data into different percentages
    - Run these three folders in the iPython notebook labeled data_resampling
For 2D training, run the ‘convert_nrrd_to_png()’ function at the bottom of this notebook, in the helpers section
    - Training:
      - 2D training - run the resulting data from step c into the iPython notebook segmentation_model_2d.ipynb
      - 3D training - run the resulting data from step c into the iPython notebook segmentation_model_3d.ipynb
    - Use the python script found in the helper_functions folder labeled surface_dice.py to calculate the surface dice score of your model

NOTE ABOUT TRAINING: depending on the amount of data used in the training process, the user might need to set up a virtual server with powerful computing capabilities for 2D training. 3D training requires such a server in order to work.

## Requesting data
If you would like to request access to the complete dataset, you will need to complete a data usage agreement with NCTN/NCORP Data Archive.  
 
Fun visualization of the true mask and predicted mask shown on top of the CT scans for a patient.
![](lung_patient_results.gif)
​​
