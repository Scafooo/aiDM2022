from functions import getBoxes, GetBoxCells, IsPercentage, ContainsPercentage, IsCost, ExtractRows, ExtractTable, AdjustRows, ProcessRows


"""# Configure Model"""

# Apply Fine Tuning or use the model directly?
# Possible values: True, False
fine_tuning = True

# Import all needed packages
import requests
from pdf2image import convert_from_path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pytesseract
from pytesseract import Output
import PIL
import skimage
import torch
from mmdet.apis import init_detector, inference_detector, show_result_pyplot
import mmcv
import os
import pandas as pd
import re
import pdfplumber
import numpy as np
import csv
from PIL import Image, ImageEnhance
import warnings
import time

warnings.filterwarnings('ignore')

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print("Using ",device)

# Load the model [gpu]
config_file = 'CascadeTabNet/Config/cascade_mask_rcnn_hrnetv2p_w32_20e.py'
if fine_tuning==False:
  checkpoint_file = 'epoch_36.pth'
else: # Load my configs and the fine-tuned model
  checkpoint_file = 'epoch_10.pth'
model = init_detector(config_file, checkpoint_file, device=device)
print("Configured gpu model.")


"""# Set extraction hyperparameters and additional configurations
Change settings according to your needs
"""

# Table/Table-Structure detector threshold configuration
threshold = 0.6

# What data you want to extract ?
# Possible values: "costs evolution", "costs composition", "performance scenarios"
table_type = "performance scenarios"


# Which directory/directories contains folders with kids?
dataset = 2 

paths = ['../../../aiDM2022/dataset/dataset-2']

# Extract from all paths or filter paths? (filter_paths should be a list)
filter = False
filter_paths = []

# Tolerance factor to consider bounding boxes of cells belonging to the same row
if table_type=='costs evolution': alignment_factor = 6
else: alignment_factor=20

# Dot per inch (image resolution)
dpi = 400 

# Image preprocessing settings (don't modify this)
if table_type=='costs composition' or table_type=='costs evolution':
  grayscale = False #True/False
  with_contrast = False
  contrast_factor = 1
elif table_type=='performance scenarios':
  grayscale = True 
  with_contrast = True
  contrast_factor = 4.5

# Tesseract-ocr configurations
tess_configs = '--oem 1 --psm 6 -c preserve_interword_spaces=0 -l eng+ita --dpi 400 '

# Start from the first available kid or skip some?
start_from = 0

# Storing modality: 'create'(overwrite csv) / 'append'(append data) / 'none'(no storing) 
mode = 'none'


for i in range(len(paths)):
  directory = paths[0]

  left_error = 70
  count = 0 
  n_files = 7736 #CAMBIARE

  for j in os.listdir(directory):
     
    if  os.path.isdir(directory+'/'+j): #check if it's a path
      for k in os.listdir(directory+'/'+j): #take every folder of the path
        new_extr_paths = []
        new_extr_rows = []
        if re.match('.*.(pdf|PDF)',k) :
          
          pdf_path = directory+'/'+j+'/'+k
          count += 1
          
          # IF you want to do batch extraction
          if count < start_from: break  
                
          # If you want to run the computation just on a subset of paths
          if (filter==True and j+'/'+k in filter_paths) or (filter==False):

            print("\n",count, "-")
            print("FILE PATH:", j+'/'+k)

            new_extr_paths.append(j+'/'+k)

            pdf_rows = ExtractTable(pdf_path, dpi, table_type, model, threshold, 
                                    tess_configs, grayscale, with_contrast, contrast_factor,alignment_factor)
            new_extr_rows.append(pdf_rows)

            # After the extraction, process and store rows         
            ProcessRows(new_extr_rows, new_extr_paths, table_type, mode)




