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

## THIS FUNCTION EXTRACT BOUNDING BOXES OF BORDERED, BORDERLESS TABLES AND CELLS
## FROM THE RESULT RETURNED BY CASCADETABNET PREDICTION
def getBoxes(result, threshold):
  # Get bounding boxes of the detected tables
  res_borderTable = []
  res_borderlessTable = []
  res_cell = []

  ## for tables with borders
  for r in result[0][0]:
    if r[4]>threshold:
      res_borderTable.append(r[:4].astype(int))
        
  ## for cells
  for r in result[0][1]:
    if r[4]>threshold:
      res_cell.append(r[:4].astype(int))

  ## for borderless tables
  for r in result[0][2]:
    if r[4]>threshold:
      res_borderlessTable.append(r[:4].astype(int))
  
  return res_borderTable, res_borderlessTable, res_cell

## THIS FUNCTION RETURNS ONLY CELLS CONTAINED INSIDE THE BBOX considering a left error
def GetBoxCells(bbox, cells, left_error):
  box_cells = []
  for cell in cells:
    # Check if the cell is in the bbox and 
    if (bbox[1] <= cell[1] and cell[1] <= (bbox[3]) and cell[0] <= (bbox[2])):
      box_cells.append(cell)
  return box_cells

## THESE FUNCTIONS ARE USED TO DETECT CELLS CONTAINING NUMERICA VALUES OF INTEREST
## SUCH AS PERCENTAGES AND COSTS

def IsPercentage(st): #should start with - or with a digit
  st = st.strip()
  return re.search('^(\-)?\d+((\,|\.)\d+)?%',st)

def ContainsPercentage(st): #can start with whatever substring
  return re.search('(\-)?\d+((\,|\.)\d+)?%',st)

def IsCost(st):
  # Should be a floating or integer number with ',' or '.' or both, at most 3 alphabetic chars
  # for the unit of measure; check that it is not the header (the detention periods)
  if sum(c.isalpha() for c in st)<=3 and not(re.search(r'\d{2}(/)\d{2}(/)\d{4}',st)):
    return (re.search('\d+((\,|\.)\d+)?',st))
  else: return None

## THIS FUNCTION EXTRACTS THE TEXT FROM A TABLE BY PERFORMING OCR ON EACH DETECTED CELL AND
## TAKING THE CORRECT ORDER BETWEEN CELLS, CONSIDERING THEIR top AND left VALUE 
## --psm=6 OF TESSERACT CONFIGS TREATS THE CELL AS A SINGLE BLOCK OF TEXT
## the enlarge factor is used because often the bounding box crops the text and ocr fails
def ExtractRows(img,bbox,true_cells, table_type, dpi, tess_configs, grayscale, with_contrast, contrast_factor, alignment_factor):
  if table_type == "costs evolution": enlarge_factor = 6 #or 5
  elif table_type == "costs composition": enlarge_factor = 10
  elif table_type == "performance scenarios": enlarge_factor = 7
  
  found = False

  # Initial sorting by top and left to get the right order
  sorted_multi_list = sorted(true_cells, key=lambda x: (x[1],x[0])) #sort by top component and then left cmpt

  # Solve some detection errors
  # We allow for an error of maximum alignment_factor
  for index,elem in enumerate(sorted_multi_list[:-1]):
    if ( (sorted_multi_list[index+1][1]-sorted_multi_list[index][1]<=alignment_factor)) :
      sorted_multi_list[index+1][1]=elem[1]
  
  # Sort again after the error solving
  sorted_cells = sorted(sorted_multi_list, key=lambda x: (x[1],x[0])) #sort by top component
  # Create a distinct row index for each top value
  row_indexes = sorted(set([i[1] for i in sorted_cells]))

  rows = []
  for i in row_indexes:
    row = []
    for cell in sorted_cells:
      if (cell[1]==i):
        # Now extract the text from the cell with OCR pytesseract
        croped_img = img[cell[1]-enlarge_factor:cell[3]+enlarge_factor, cell[0]-enlarge_factor:cell[2]+enlarge_factor]
        
        # To GRAYSCALE
        if grayscale==True:
          np_img = skimage.color.rgb2gray(croped_img) 
        else:
          np_img = croped_img

        # INVERT IMG
        light_spots = np.array((croped_img > 245).nonzero()).T
        dark_spots = np.array((croped_img <= 245).nonzero()).T
        if light_spots.shape[0] < dark_spots.shape[0]: # = light text on darker background
          np_img = 255 - np_img

        # TO PIL (otherwise tesseract gives errors for 2d numpy)
        if grayscale == True:
          pil_img = PIL.Image.fromarray(np.uint8(np_img * 255) , 'L')  
        else:
          pil_img = PIL.Image.fromarray(np_img)
        
        # INCREASE CONTRAST
        if with_contrast==True:
          #image brightness enhancer
          enhancer = ImageEnhance.Contrast(pil_img)
          factor = contrast_factor #increase contrast
          pil_img = enhancer.enhance(factor)
        
        #text = str((pytesseract.image_to_string(croped_img, config='--oem 1 --psm 6 -c preserve_interword_spaces=0 -l ita')))
        text = str((pytesseract.image_to_string(pil_img, lang='eng', config=tess_configs)))
        text = text.replace("\n\x0c", "")
        #print(text)  
        if (table_type == "costs composition"):
          # To speed up the computation we break as soon as we understand that the
          # detected table is not the correct one
          if "costi totali" in text.lower(): return None
          if "stress" in text.lower(): return None
          # This is the table that we want
          elif ("costi una tantum" in text.lower() or "costi correnti" in text.lower() or \
                "oneri accessori" in text.lower()): found = True
          row.append(text)

        elif (table_type == "costs evolution"):
          if "costi di ingresso" in text.lower(): return None
          if "costi di uscita" in text.lower(): return None
          if "stress" in text.lower(): return None
          # This is the table that we want
          elif "costi totali" in text.lower() or ("impatto sul rendimento" and "riy") in text.lower(): found = True
          # We take just riy and cost cells
          if (IsPercentage(text) or IsCost(text)):
            row.append(text)
        
        elif (table_type == "performance scenarios"):
          if "costi totali" in text.lower(): return None
          if "costi di ingresso" in text.lower(): return None
          # This is the table that we want
          elif ("stress" or "sfavorevole" or "moderato" or "favorevole") in text.lower(): found = True
          # Take just costs and %
          if (IsCost(text) or IsPercentage(text)):
            row.append(text)

    if len(row)!=0:
      rows.append(row)

  if found == True: return rows
  else: return None

def ExtractTable(pdf_path, dpi, table_type, model, threshold, tess_configs, grayscale, with_contrast, contrast_factor, alignment_factor):

  start_time = time.time()
  images = convert_from_path(pdf_path, dpi=dpi) #pdf to PIL img 
          
  # Find the correct page idx
  idx = None

  # Some files are encrypted and can not be opened, so we have to check
  try: 
    pdfplumber.open(pdf_path)
  except:
    print("Not able to open the pdf.")
    extracted_rows = []
    return extracted_rows

  with pdfplumber.open(pdf_path) as pdf:
    for page_index in range(len(pdf.pages)):
      full_text = pdf.pages[page_index].extract_text()

      if ( (table_type == "costs composition" and full_text and ("composizione dei costi" in full_text.lower() or \
                        "questa tabella presenta l'impatto sul rendimento" in full_text.lower() or \
                        "scomposizionedeicosti" in full_text.lower() or "costi specifici dell'opzione di investimento" in full_text.lower())) or \
          (table_type == "costs evolution" and full_text and ("andamento dei costi" in full_text.lower() or \
                        "costo nel tempo" in full_text.lower() or \
                        "costi nel tempo" in full_text.lower() or \
                        "costoneltempo" in full_text.lower()))  or \
          (table_type == "performance scenarios" and full_text and ("scenari di performance" in full_text.lower() or \
                          "scenaridiperformance" in full_text.lower() or ("scenari di" and "performance") in full_text.lower()) \
            and ("stress" or "favorevole" or "moderato") in full_text.lower() )):
        # get page index
        idx = page_index
        full_text = ""
        print("Table Page: ", idx)
                
        break

    # IF index is found, get the tables with CascadeTabNet
    if (idx):

      # Predict with CascadeTabNet
      page = images[idx]
      img = np.array(page)
      result = inference_detector(model, img)
      # Get the bounding boxes coordinates of the tables
      res_borderTable, res_borderlessTable, res_cell = getBoxes(result, threshold)
      res_allTable = res_borderlessTable + res_borderTable #consider both border/borderless tables
      print(res_allTable)         
      found_table = False

      for bbox in res_allTable:         
        bbox_cells = GetBoxCells(bbox,res_cell, left_error) #get only cells inside this bbox
        rows = ExtractRows(img, bbox, bbox_cells, table_type, dpi, tess_configs, grayscale, with_contrast, contrast_factor, alignment_factor) #this also checks if it's the correct table

        # If correct table
        if(rows):
            end_time = time.time()
            print("Data extracted in: ",end_time-start_time, " s.")
            found_table=True
            ## Debugging
            print("Tab box: ", bbox)
            print("Tab cells: ", bbox_cells)
            print("Extracted:")
            for row in rows:
              print("row: ", row)
            extracted_rows = rows
                    
        if (found_table==True): 
          break     

      # Case table header in this page but table actually in next page
      if (found_table == False):
        # Check if the table is in the next page
        next_idx = idx+1
        # If there is another page in the pdf
        if(len(pdf.pages)>next_idx):
          page = images[next_idx]
          img = np.array(page)
          # Run inference, find correct box, extract row text with OCR
          result = inference_detector(model, img)
          res_borderTable, res_borderlessTable, res_cell = getBoxes(result, threshold)
          res_allTable = res_borderlessTable + res_borderTable #consider both border/borderless tables
          print(res_allTable)         
          found_table = False

          for bbox in res_allTable:
            bbox_cells = GetBoxCells(bbox,res_cell, left_error) #get only cells inside this bbox
            rows = ExtractRows(img, bbox, bbox_cells, table_type, dpi, tess_configs, grayscale, with_contrast, contrast_factor, alignment_factor) #this also checks if it's the correct table

            # If correct table
            if(rows):
                end_time = time.time()
                print("Data extracted in: ",end_time-start_time, " s.")
                found_table=True
                ## Debugging
                print("Tab box: ", bbox)
                print("Tab cells: ", bbox_cells)
                print("Extracted:")
                for row in rows:
                  print("row: ", row)
                extracted_rows = rows
                    
            if (found_table==True): 
              break

    # Table page not located for some reason
    else:
      found_table = False
                   
    if (found_table==False): 
      extracted_rows = []
      print("row: []")
            
  return extracted_rows

def AdjustRows(rows):
      new_rows = []
      for r in range(len(rows)):
        if IsPercentage(rows[r][0]) and r==0 and r+1<len(rows) and not(IsPercentage(rows[r+1][0])):
          new_rows.append(['-'])
          new_rows.append(rows[r])
        elif IsPercentage(rows[r][0]) and r==0 and r+1<len(rows) and IsPercentage(rows[r+1][0]):
          new_rows.append(['-'])
          new_rows.append(rows[r])
          new_rows.append(['-'])
        elif IsPercentage(rows[r][0]) and r+1<len(rows) and IsPercentage(rows[r+1][0]):
          new_rows.append(rows[r])
          new_rows.append(['-'])
        elif (not(IsPercentage(rows[r][0])) and r+1<len(rows) and not(IsPercentage(rows[r+1][0]))):
          new_rows.append(rows[r])
          new_rows.append(['-'])
        else:
          new_rows.append(rows[r])
      
      while len(new_rows)<8:
        new_rows.append(['-'])
      return new_rows


# mode : ''create' (overwrites the output file), 'append' (appends new rows on output file), 'none' (no storing)
def ProcessRows(new_extr_rows, new_extr_paths, table_type, mode):
    ## THIS IS HOW TO PROCESS EXTRACTED ROWS FROM COSTS EVOLUTION TABLE
  if (table_type == "costs evolution"):
    initial_costs_data = [] 
    intermediate_costs_data = [] 
    final_costs_data = []
    initial_riy_data = []
    intermediate_riy_data = []
    final_riy_data = []

    for rows in new_extr_rows:

      # CASE 1: No numeric info extracted from the table
      if len(rows)==0:
        cost_row = []
        riy_row = []   
      # CASE 2: Both costs and RIY extracted from the table
      elif len(rows)==2:
        cost_row = rows[0]
        riy_row = rows[1] 
      # CASE 3: Only costs extracted or only RIY extracted
      elif len(rows)==1:
        if IsCost(rows[0][0]): 
          cost_row = rows[0]
          riy_row = []
        else: 
          cost_row = []
          riy_row = rows
      # CASE 4: More than 2 rows => there is some error
      else:
        cost_row = []
        riy_row = []
      
      # Assign cost cells to the correct column
      if len(cost_row)==0:
        initial_costs_data.append("-")
        intermediate_costs_data.append("-")
        final_costs_data.append("-")
      # IF n_numeric_cols = 1 THEN add to final_costs 
      elif len(cost_row)==1:  
        initial_costs_data.append("-")
        intermediate_costs_data.append("-")
        final_costs_data.append(cost_row[0])
      # IF n_numeric_cols = 2 THEN add to final_costs and initial_costs
      elif len(cost_row)==2:  
        initial_costs_data.append(cost_row[0])
        intermediate_costs_data.append("-")
        final_costs_data.append(cost_row[1])
      # IF n_numeric_cols = 2 THEN add to final, intermediate and initial_costs
      elif len(cost_row)==3:  
        initial_costs_data.append(cost_row[0])
        intermediate_costs_data.append(cost_row[1])
        final_costs_data.append(cost_row[2])

      # Assign RIY cells to the correct column
      if len(riy_row)==0:
        initial_riy_data.append("-")
        intermediate_riy_data.append("-")
        final_riy_data.append("-")
      # IF n_numeric_cols = 1 THEN add to final_costs 
      elif len(riy_row)==1:  
        initial_riy_data.append("-")
        intermediate_riy_data.append("-")
        final_riy_data.append(riy_row[0])
      # IF n_numeric_cols = 2 THEN add to final_costs and initial_costs
      elif len(riy_row)==2:  
        initial_riy_data.append(riy_row[0])
        intermediate_riy_data.append("-")
        final_riy_data.append(riy_row[1])
      # IF n_numeric_cols = 2 THEN add to final, intermediate and initial_costs
      elif len(riy_row)==3:  
        initial_riy_data.append(riy_row[0])
        intermediate_riy_data.append(riy_row[1])
        final_riy_data.append(riy_row[2]) 
    
    print(len(new_extr_paths), len(initial_costs_data), len(initial_riy_data), len(intermediate_costs_data),
        len(intermediate_riy_data), len(final_costs_data), len(final_riy_data))

  ## THIS IS HOW TO PROCESS EXTRACTED ROWS FROM COSTS COMPOSITION TABLE
  elif (table_type=="costs composition"):
    una_tantum_ingresso_data = ['-']
    una_tantum_uscita_data = ['-']
    correnti_transazioni_data = ['-']
    correnti_altri_data = ['-']
    oneri_accessori_performance_data = ['-']
    oneri_accessori_overperformance_data = ['-']
    count_tab = 0

    for rows in new_extr_rows: #rows is the set of rows representing a single table
      count_tab += 1

      if(rows!=[]):
        for row in rows:
          # If there is at least the second (cost type) and the third col (cost value %)
          if (len(row)>=2):

            # Una tantum ingresso
            if (("ingress" or "iniziali") in row[0].lower() and IsPercentage(row[1])): # "Costi una tantum" not detected
              una_tantum_ingresso_data = [row[1]]
            elif (len(row)>=3 and ("ingress" or "iniziali") in row[1].lower() and IsPercentage(row[2])): # "Costi una tantum detected"
              una_tantum_ingresso_data= [row[2]]
            
            # Una tantum uscita
            elif ("uscita" in row[0].lower() and IsPercentage(row[1])): # "Costi una tantum" not detected
              una_tantum_uscita_data=[row[1]]
            elif (len(row)>=3 and "uscita" in row[1].lower() and IsPercentage(row[2])): # "Costi una tantum detected"
              una_tantum_uscita_data=[row[2]]

            # Correnti transazione
            if ("transazione" in row[0].lower() and IsPercentage(row[1])): # "Costi correnti" not detected
              correnti_transazioni_data=[row[1]]
            elif (len(row)>=3 and "transazione" in row[1].lower() and IsPercentage(row[2])): # "Costi correnti" detected
              correnti_transazioni_data=[row[2]]

            # Correnti altri
            if ("altri" in row[0].lower() and IsPercentage(row[1])): # "Costi correnti" not detected
              correnti_altri_data=[row[1]]
            elif (len(row)>=3 and "altri" in row[1].lower() and IsPercentage(row[2])): # "Costi correnti" detected
              correnti_altri_data=[row[2]]
            
            # Handle the error "Costi Correnti - Oneri Accessori"
            if(len(row)>=3 and "correnti" in row[0].lower() and "oneri" in row[1].lower() and IsPercentage(row[2])):
              correnti_transazioni_data=[row[2]]
              print("Error detected: Costi Correnti Oneri Accessori in ", new_extr_paths[count_tab-1])

            # Oneri accessori performance
            if ("performance" in row[0].lower() and not("overperformance" in row[0].lower()) and IsPercentage(row[1])): # "Oneri accessori" not detected
              oneri_accessori_performance_data=[row[1]]
            elif (len(row)>=3 and "performance" in row[1].lower() and not("overperformance" in row[0].lower()) and IsPercentage(row[2])): # "Oneri accessori" detected
              oneri_accessori_performance_data=[row[2]]
            
            # Oneri accessori overperformance
            if (("overperformance" or "carried interest") in row[0].lower() and IsPercentage(row[1])): # "Oneri accessori" not detected
              oneri_accessori_overperformance_data.append(row[1])
            elif (len(row)>=3 and ("overperformance" or "carried interest") in row[1].lower() and IsPercentage(row[2])): # "Oneri accessori" detected
              oneri_accessori_overperformance_data=[row[2]]

    print(len(una_tantum_ingresso_data), len(una_tantum_uscita_data), len(correnti_transazioni_data),
          len(correnti_altri_data), len(oneri_accessori_performance_data), 
          len(oneri_accessori_overperformance_data), len(new_extr_paths))  

  ## THIS IS HOW TO PROCESS EXTRACTED ROWS FROM PERFORMANCE SCENARIOS TABLE
  elif (table_type=="performance scenarios"):
    # initial performances
    ini_stress_rimborso_data = []
    ini_stress_rendimento_data = []
    ini_sfavorevole_rimborso_data = [] 
    ini_sfavorevole_rendimento_data = []
    ini_moderato_rimborso_data = []
    ini_moderato_rendimento_data = []
    ini_favorevole_rimborso_data = []
    ini_favorevole_rendimento_data = []
    # intermediate performances
    int_stress_rimborso_data = []
    int_stress_rendimento_data = []
    int_sfavorevole_rimborso_data = []
    int_sfavorevole_rendimento_data = []
    int_moderato_rimborso_data = []
    int_moderato_rendimento_data = []
    int_favorevole_rimborso_data = []
    int_favorevole_rendimento_data = []
    # final performances
    fin_stress_rimborso_data = [] 
    fin_stress_rendimento_data = []
    fin_sfavorevole_rimborso_data = []
    fin_sfavorevole_rendimento_data = []
    fin_moderato_rimborso_data = []
    fin_moderato_rendimento_data = []
    fin_favorevole_rimborso_data = []
    fin_favorevole_rendimento_data = []

    for rows in new_extr_rows:
      appended = False
      # No extraction at all
      if len(rows)==0:
        for ls in (ini_stress_rimborso_data, ini_stress_rendimento_data, ini_sfavorevole_rimborso_data,
                  ini_sfavorevole_rendimento_data, ini_moderato_rimborso_data, ini_moderato_rendimento_data,
                  ini_favorevole_rimborso_data, ini_favorevole_rendimento_data, int_stress_rimborso_data,
                  int_stress_rendimento_data, int_sfavorevole_rimborso_data, int_sfavorevole_rendimento_data, 
                  int_moderato_rimborso_data, int_moderato_rendimento_data, int_favorevole_rimborso_data,
                  int_favorevole_rendimento_data, fin_stress_rimborso_data, fin_stress_rendimento_data,
                  fin_sfavorevole_rimborso_data, fin_sfavorevole_rendimento_data, fin_moderato_rimborso_data,
                  fin_moderato_rendimento_data, fin_favorevole_rimborso_data, fin_favorevole_rendimento_data):
          ls.append('-') #append empty symbol to all these lists
        appended = True
      
      new_rows = AdjustRows(rows)
      if len(rows)!=0 and len(new_rows)>=8:
        # Get row with maximum length to understand which rule to apply (the other can have mising data)
        max_length = max(len(x) for x in new_rows)
        if max_length > 3: max_length = 3 #it's an error
        # Missing elements ! => Add '-' to have the same length
        for i in range(len(new_rows)):
          while len(new_rows[i])<max_length:
            new_rows[i].append('-')
        # Assign basing on column rules
        # 1 col => FINAL
        if max_length==1:
          appended = True
          fin_stress_rimborso_data.append(new_rows[0][0])
          ini_stress_rimborso_data.append('-')
          int_stress_rimborso_data.append('-')
          fin_stress_rendimento_data.append(new_rows[1][0])
          ini_stress_rendimento_data.append('-')
          int_stress_rendimento_data.append('-')
          fin_sfavorevole_rimborso_data.append(new_rows[2][0])
          ini_sfavorevole_rimborso_data.append('-')
          int_sfavorevole_rimborso_data.append('-')
          fin_sfavorevole_rendimento_data.append(new_rows[3][0])
          ini_sfavorevole_rendimento_data.append('-')
          int_sfavorevole_rendimento_data.append('-')
          fin_moderato_rimborso_data.append(new_rows[4][0])
          ini_moderato_rimborso_data.append('-')
          int_moderato_rimborso_data.append('-')
          fin_moderato_rendimento_data.append(new_rows[5][0])
          ini_moderato_rendimento_data.append('-')
          int_moderato_rendimento_data.append('-')
          fin_favorevole_rimborso_data.append(new_rows[6][0])
          ini_favorevole_rimborso_data.append('-')
          int_favorevole_rimborso_data.append('-')
          fin_favorevole_rendimento_data.append(new_rows[7][0])
          ini_favorevole_rendimento_data.append('-')
          int_favorevole_rendimento_data.append('-')
        
        # 2 col => INITIAL AND FINAL
        elif max_length==2: 
          appended = True  
          ini_stress_rimborso_data.append(new_rows[0][0])
          int_stress_rimborso_data.append('-')
          fin_stress_rimborso_data.append(new_rows[0][1])
          ini_stress_rendimento_data.append(new_rows[1][0])
          int_stress_rendimento_data.append('-')
          fin_stress_rendimento_data.append(new_rows[1][1])
          ini_sfavorevole_rimborso_data.append(new_rows[2][0])
          int_sfavorevole_rimborso_data.append('-')
          fin_sfavorevole_rimborso_data.append(new_rows[2][1])
          ini_sfavorevole_rendimento_data.append(new_rows[3][0])
          int_sfavorevole_rendimento_data.append('-')
          fin_sfavorevole_rendimento_data.append(new_rows[3][1])
          ini_moderato_rimborso_data.append(new_rows[4][0])
          int_moderato_rimborso_data.append('-')
          fin_moderato_rimborso_data.append(new_rows[4][1])
          ini_moderato_rendimento_data.append(new_rows[5][0])
          int_moderato_rendimento_data.append('-')
          fin_moderato_rendimento_data.append(new_rows[5][1])
          ini_favorevole_rimborso_data.append(new_rows[6][0])
          int_favorevole_rimborso_data.append('-')
          fin_favorevole_rimborso_data.append(new_rows[6][1])
          ini_favorevole_rendimento_data.append(new_rows[7][0])
          int_favorevole_rendimento_data.append('-')
          fin_favorevole_rendimento_data.append(new_rows[7][1])
      
      # 3 col => ALL
        elif max_length==3:   
          appended = True
          ini_stress_rimborso_data.append(new_rows[0][0])
          int_stress_rimborso_data.append(new_rows[0][1])
          fin_stress_rimborso_data.append(new_rows[0][2])
          ini_stress_rendimento_data.append(new_rows[1][0])
          int_stress_rendimento_data.append(new_rows[1][1])
          fin_stress_rendimento_data.append(new_rows[1][2])
          ini_sfavorevole_rimborso_data.append(new_rows[2][0])
          int_sfavorevole_rimborso_data.append(new_rows[2][1])
          fin_sfavorevole_rimborso_data.append(new_rows[2][2])
          ini_sfavorevole_rendimento_data.append(new_rows[3][0])
          int_sfavorevole_rendimento_data.append(new_rows[3][1])
          fin_sfavorevole_rendimento_data.append(new_rows[3][2])
          ini_moderato_rimborso_data.append(new_rows[4][0])
          int_moderato_rimborso_data.append(new_rows[4][1])
          fin_moderato_rimborso_data.append(new_rows[4][2])
          ini_moderato_rendimento_data.append(new_rows[5][0])
          int_moderato_rendimento_data.append(new_rows[5][1])
          fin_moderato_rendimento_data.append(new_rows[5][2])
          ini_favorevole_rimborso_data.append(new_rows[6][0])
          int_favorevole_rimborso_data.append(new_rows[6][1])
          fin_favorevole_rimborso_data.append(new_rows[6][2])
          ini_favorevole_rendimento_data.append(new_rows[7][0])
          int_favorevole_rendimento_data.append(new_rows[7][1])
          fin_favorevole_rendimento_data.append(new_rows[7][2]) 

    print(len(ini_stress_rimborso_data), len(ini_stress_rendimento_data), len(ini_sfavorevole_rimborso_data),
          len(ini_sfavorevole_rendimento_data), len(ini_moderato_rimborso_data), len(ini_moderato_rendimento_data),
          len(ini_favorevole_rimborso_data), len(ini_favorevole_rendimento_data), len(int_stress_rimborso_data),
          len(int_stress_rendimento_data), len(int_sfavorevole_rimborso_data), len(int_sfavorevole_rendimento_data), 
          len(int_moderato_rimborso_data), len(int_moderato_rendimento_data), len(int_favorevole_rimborso_data),
          len(int_favorevole_rendimento_data), len(fin_stress_rimborso_data), len(fin_stress_rendimento_data),
          len(fin_sfavorevole_rimborso_data), len(fin_sfavorevole_rendimento_data), len(fin_moderato_rimborso_data),
          len(fin_moderato_rendimento_data), len(fin_favorevole_rimborso_data), len(fin_favorevole_rendimento_data))

  ## THIS IS HOW TO PROCESS EXTRACTED ROWS FROM COSTS EVOLUTION TABLE
  if (table_type == "costs evolution"):
    # Add data to df and store in csv
    column_names = ["pdf_path", "initial_costs", "intermediate_costs", "final_costs", \
                    "initial_RIY", "intermediate_RIY", "final_RIY"]
    data = {'pdf_path': new_extr_paths,
            'initial_costs': initial_costs_data,
            'intermediate_costs': intermediate_costs_data,
            'final_costs': final_costs_data,
            'initial_riy': initial_riy_data,
            'intermediate_riy': intermediate_riy_data,
            'final_riy': final_riy_data
            }
    output_file = "costs_evolution_extractions.csv"

  elif (table_type == "costs composition"):
    column_names = ["pdf_path", "una_tantum_ingresso", "una_tantum_uscita", \
                    "correnti_transazione", "correnti_altri", \
                    "oneri_accessori_performance", "oner_accessori_overperformance"]
    data = {'pdf_path': new_extr_paths,
            'una_tantum_ingresso': una_tantum_ingresso_data,
            'una_tantum_uscita': una_tantum_uscita_data,
            'correnti_transazioni': correnti_transazioni_data,
            'correnti_altri': correnti_altri_data,
            'oneri_accessori_performance': oneri_accessori_performance_data,
            'oneri_accessori_overperformance': oneri_accessori_overperformance_data
            }
    output_file = "costs_composition_extractions.csv"

  elif (table_type == "performance scenarios"):
    column_names = ["pdf_path", "stress_rimborso_iniziale", "stress_rendimento_iniziale", \
                    "sfavorevole_rimborso_iniziale", "sfavorevole_rendimento_iniziale", \
                    "moderato_rimborso_iniziale", "moderato_rendimento_iniziale", \
                    "favorevole_rimborso_iniziale", "favorevole_rendimento_iniziale", \
                    "stress_rimborso_intermedio", "stress_rendimento_intermedio", \
                    "sfavorevole_rimborso_intermedio", "sfavorevole_rendimento_intermedio", \
                    "moderato_rimborso_intermedio", "moderato_rendimento_intermedio", \
                    "favorevole_rimborso_intermedio", "favorevole_rendimento_intermedio", \
                    "stress_rimborso_finale", "stress_rendimento_finale", \
                    "sfavorevole_rimborso_finale", "sfavorevole_rendimento_finale", \
                    "moderato_rimborso_finale", "moderato_rendimento_finale", \
                    "favorevole_rimborso_finale", "favorevole_rendimento_finale"]
    data = {'pdf_path': new_extr_paths,
            'stress_rimborso_iniziale': ini_stress_rimborso_data,
            'stress_rendimento_iniziale': ini_stress_rendimento_data,
            'sfavorevole_rimborso_iniziale': ini_sfavorevole_rimborso_data,
            'sfavorevole_rendimento_iniziale': ini_sfavorevole_rendimento_data,
            'moderato_rimborso_iniziale': ini_moderato_rimborso_data,
            'moderato_rendimento_iniziale': ini_moderato_rendimento_data,
            'favorevole_rimborso_iniziale': ini_favorevole_rimborso_data,
            'favorevole_rendimento_iniziale': ini_favorevole_rendimento_data,
            'stress_rimborso_intermedio': int_stress_rimborso_data,
            'stress_rendimento_intermedio': int_stress_rendimento_data,
            'sfavorevole_rimborso_intermedio': int_sfavorevole_rimborso_data,
            'sfavorevole_rendimento_intermedio': int_sfavorevole_rendimento_data,
            'moderato_rimborso_intermedio': int_moderato_rimborso_data,
            'moderato_rendimento_intermedio': int_moderato_rendimento_data,
            'favorevole_rimborso_intermedio': int_favorevole_rimborso_data,
            'favorevole_rendimento_intermedio': int_favorevole_rendimento_data,
            'stress_rimborso_finale': fin_stress_rimborso_data,
            'stress_rendimento_finale': fin_stress_rendimento_data,
            'sfavorevole_rimborso_finale': fin_sfavorevole_rimborso_data,
            'sfavorevole_rendimento_finale': fin_sfavorevole_rendimento_data,
            'moderato_rimborso_finale': fin_moderato_rimborso_data,
            'moderato_rendimento_finale': fin_moderato_rendimento_data,
            'favorevole_rimborso_finale': fin_favorevole_rimborso_data,
            'favorevole_rendimento_finale': fin_favorevole_rendimento_data,
            }
    output_file = "performance_extractions.csv"

  df = pd.DataFrame(data)

  # For batch extraction => append
  if mode=='append': df.to_csv(output_file, mode='a',index=False, header=False)
  # else (mode=='none') => do nothing with the csv



