# Requirements
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
