# Table Information Extractor

## Requirements
To run this code you need to install the following:

```
!pip install torch==1.4.0+cu100 torchvision==0.5.0+cu100 -f https://download.pytorch.org/whl/torch_stable.html
!pip install -q mmcv terminaltables
!git clone --branch v1.2.0 'https://github.com/open-mmlab/mmdetection.git'
%cd "mmdetection"
!pip install -r "/content/mmdetection/requirements/optional.txt"
!python setup.py install
!python setup.py develop
!pip install -r {"requirements.txt"}
!pip install mmcv==0.4.3
!pip uninstall opencv-python-headless
!pip install opencv-python-headless==4.1.2.30
!pip install pdf2image
!apt-get install poppler-utils #needed for pdf2image package
!pip install pdfplumber
!pip install pytesseract
!sudo apt install tesseract-ocr
!apt-get install tesseract-ocr-ita
!pip install pillow==6.2.1 
```

Also, you need to import the configuration and checkpoint file of the pretrained model from CascadeTabNet:

```
!git clone https://github.com/DevashishPrasad/CascadeTabNet.git 
# Download the pretrained model
!gdown "https://drive.google.com/u/0/uc?id=1-QieHkR1Q7CXuBu4fp3rYrvDG9j26eFT" # ICDAR 19 modern table structure recognition
```

## Instructions
Configure extraction parameters:
- Use ```fine_tuning=True``` if you want to use the fine-tuned model for the extraction,  ```fine_tuning=False``` if you want to use the original model developed by CascadeTabNet authors.
- Choose the type of table that you want to extract (```table_type```), between "costs evolution", "costs composition" and "performance scenarios".

If you want to store the extractions in a csv:
- Create the files "costs_evolution_extractions.csv", "costs_composition_extractions.csv", "performance_extractions.csv"-
- Set ```mode='append'```
