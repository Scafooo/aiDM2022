# -*- coding: utf-8 -*-



import pandas as pd
import numpy as np
import re

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


input_file_ce = "costs_evolution_extractions.csv" #costs evolution
input_file_cc = "costs_composition_extractions.csv" #costs composition
input_file_p = "performance_extractions.csv" #performance scenarios

df_ce = pd.read_csv(input_file_ce)
df_cc = pd.read_csv(input_file_cc)
df_p = pd.read_csv(input_file_p)

df_ce = df_ce.replace('-', np.nan)
df_cc = df_cc.replace('-', np.nan)
df_p = df_p.replace('-', np.nan)

print(input_file_ce, df_ce.shape)
numeric_cols = df_ce.columns.to_list()[1:]
df_missing = df_ce[df_ce[numeric_cols].isna().all(axis=1)]
print('Missing:', df_missing.shape[0])
df_ce.head()

print(input_file_cc, df_cc.shape)
numeric_cols = df_cc.columns.to_list()[1:]
df_missing = df_cc[df_cc[numeric_cols].isna().all(axis=1)]
print('Missing:', df_missing.shape[0])
df_cc.head()

print(input_file_p, df_p.shape)
numeric_cols = df_p.columns.to_list()[1:]
df_missing = df_p[df_p[numeric_cols].isna().all(axis=1)]
print('Missing:', df_missing.shape[0])
df_p.head()

"""# Handling OCR mistakes: extra blanks and '/'

Due to OCR mistakes, it often happens that wrong blanks are detected inside costs and percentages, for instance: '*-28, 35%*', '*3.363, 71 CHF*', '*-92 091434391%*', '*68 3802 75896%*'. The blanks may refer to: 
* a punctuation (',' or '.') that the OCR was not able to detect: in this case the spaces should be replaced with the correct punctuation;
* an extra blank added by the ocr due to wrong space consideration, that may be related to particular fonts or templates.

Notice that, not handling these 'internal' blanks would lead to errors in the next phases of the cleaning for wrong regex matches (ex: '98 3802%' is cleaned as '3802%', that is completely different from '98,3802%'). Moreover, it would cause similar troubles when splitting a single (wrongly) multi-line cell into two distinct cells: '10000 EUR\n12, 3%' would be splitted into '10000' and '3%' instead of '12,3%'. 

Another OCR-related error is the interpretation of '7' as '/'. This mistake too may lead to similar troubles discussed above.
"""

def RemoveBlanks(my_str):
  if isinstance(my_str, str):
    string = my_str.strip() 
    string = string.replace(',,', ',')
    # Cases: 'XXX XX', 'XX XXX XX', 'X.XXX XX', 'XX,X XXXX', 'XX X,XX == blanks between digits
    pattern_1 = '(((\d)+(\,|\.))?((\d)+ (\d)+)+)|(\d)+ (\d)+(\,|\.)?(\d)+'
    while (re.search(pattern_1, string)): # use 'while' instead of 'if' to handle cases with multiple spaces (ex: XX XXX XX% => XX,XXXXX )
      match = re.search(pattern_1, string)[0]
      if ',' in match:
        match = match.replace(' ', '') #it's an extra space => remove it
      else:
        match = match.replace(' ', ',') #it's a real space for a missing ','
      # Replace modified match in the string
      string = re.sub(pattern_1, match, string)
      print("\n",my_str, '=>',string)
    
    # Cases: 'XXX, XX', 'XXX. XX', 'XXX,. XX', 'XXX., XX', 'XX .X', 'XX ,X' etc == blanks after/before punctuation and before/after digit
    pattern_2 = '((\d)+(\,|\.|\,.|\.,) (\d)+)|((\d)+ (\,|\.|\,.|\.,)(\d)+)'
    if (re.search(pattern_2, string)):
      match = re.search(pattern_2, string)[0]
      match = match.replace(' ', '') #just remove space
      string = re.sub(pattern_2, match, string)
      print("\n",my_str, "=>", string)
  
    return string
  else: return my_str

def RemoveErrors(my_str):
  # Dates wrongly extracted as they were costs
  pattern_date = '(\d){2}/(\d){2}/(\d){4}'
  if (re.search(pattern_date, my_str)):
    return np.nan
  # Da XX,XX EUR a XX,XX EUR
  if 'da ' in my_str.lower():
    cost_perc_pattern = r'(-)?(\d)+((\.|\,)(\d)+)?(\,|\.)?(\d)+(%)?'
    if re.search(cost_perc_pattern, my_str):
      match_1 = re.search(cost_perc_pattern, my_str)[0]
      substring = my_str.replace(match_1,'')
      if re.search(cost_perc_pattern, substring):
        match_2 = re.search(cost_perc_pattern, substring)[0]
        range_cell = 'da '+match_1+' a '+match_2
      else:
        range_cell = match_1
      print("\n",my_str, "=>", range_cell)
      #now range cell is cleaned
      return range_cell

  else: return my_str
  

def CorrectOcr(my_str):
  if isinstance(my_str, str):
    value = my_str
    number = value.replace(',','')
    number = number.replace('.','')
    number = number.replace('-', ' ')
    number = number.replace('%',' ')
    pattern = r'\d/\d'
    if (re.search(pattern, number)):
      match = re.search(pattern, number)[0]
      string = my_str.replace('/', '7')
      print("\n",my_str, "=>", string)
      return string
    else: return my_str
  else: return my_str

print("\n--Costs Evolution")
for col in df_ce.columns.to_list()[1:]:
  df_ce[col] = df_ce[col].dropna().apply(lambda x: CorrectOcr(RemoveBlanks(RemoveErrors(x))))

print("\n--Costs Composition")
for col in df_cc.columns.to_list()[1:]:
  df_cc[col] = df_cc[col].dropna().apply(lambda x: CorrectOcr(RemoveBlanks(RemoveErrors(x))))

print("\n--Performance scenarios")
for col in df_p.columns.to_list()[1:]:
  df_p[col] = df_p[col].dropna().apply(lambda x: CorrectOcr(RemoveBlanks(RemoveErrors(x))))

"""# Handling CASCADETABNET mistakes: wrong multi-line cells

It often happen that the NN model detects two distinct cells of the same column as a single multi-line cell. It is the case of cells in which the newline symbol appears. It is reasonable to split the two lines into distinct cells and assign the splitted values to the correct dataframe columns. As an example, '*25.914,21 EUR \n 159,14%*' should be splitted into '*25.914,21 EUR*' and '*159,14%*'.
"""

def IsPercentage(st): #should start with - or with a digit
  st = st.strip()
  return re.search('^(\-)?\d+((\,|\.)\d+)?%',st)

def ContainsPercentage(st): #can start with whatever substring
  return re.search('(\-)?\d+((\,|\.)\d+)?%',st)

def GetCostPercentage(my_str):
  # Take the percentage
  percentage = ContainsPercentage(my_str)[0]
  # Take the cost
  cost = my_str.replace(percentage, '') #remove percentage
  chars = ['(', ')','{', '\n'] #remove special characters
  for c in chars:
    cost = cost.replace(c, '')
  return cost, percentage

"""## Splitting costs and percentages in performance table

If we have both a cost and a percentage in a 'rimborso' column, the percentage should be assigned to the 'rendimento' column of the same scenario ('stress', 'sfavorevole', 'moderato', 'favorevole') and period ('iniziale', 'intermedio', 'finale').
"""

# An example, before the splitting
df_p.iloc[384]

def SplitCostPercentage(cell, cell2):
  # If we have a cell containing both cost and percentage for some reason
  cell = str(cell)
  if ('da ' and ' a ') in cell: listy = [cell,cell2] #ignore (already cleaned)
  elif ContainsPercentage(cell) and not (IsPercentage(cell)) and ('\n' or ('(' and ')')) in cell:
    # Take the percentage and cost
    cost, percentage = GetCostPercentage(cell)
    listy = [cost,percentage]   
    print("\nUpdated ", cell, "=>", cost, " and ", percentage)
  else:
    listy = [cell,cell2]
  return pd.Series(listy)

columns = df_p.columns.to_list()[1:]
for idx in range(0,len(columns),2):
  col_rimborso = columns[idx]
  col_rendimento = columns[idx+1]
  df_p[[col_rimborso, col_rendimento]] = df_p.apply(
      lambda x: SplitCostPercentage(x[col_rimborso], x[col_rendimento]) if x[col_rimborso] is not np.nan 
      else pd.Series([x[col_rimborso], x[col_rendimento]]), axis=1)

# An example, after the splitting
df_p.iloc[384]

"""## Splitting costs and percentages in cost evolution table"""

def SplitCostPercentage_shifting(ini_cost, ini_riy, int_cost, int_riy, fin_cost, fin_riy):
  # Initialization 
  ini_cost_new = ini_cost
  ini_riy_new = ini_riy
  int_cost_new = int_cost
  int_riy_new = int_riy
  fin_cost_new = fin_cost
  fin_riy_new = fin_riy

  # If we have INITIAL COST containing both cost and percentage for some reason
  if ini_cost is not np.nan and ContainsPercentage(ini_cost) and not (IsPercentage(ini_cost)) and not (('da ' and ' a ') in ini_cost):
    # Take the percentage and cost
    cost, percentage = GetCostPercentage(ini_cost)
    print(ini_cost, "=>", cost, " and ", percentage)
    ini_cost_new = cost
    # Case 1: Initial riy is empty
    if ini_riy=='-': 
      ini_riy_new = percentage
    # Case 2: Initial riy contains something => initial riy is actually intermediate riy, wrongly assigned
    else: 
      ini_riy_new = percentage
      int_riy_new = ini_riy

  # If we have INTERMEDIATE COST containing both cost and percentage for some reason
  if int_cost is not np.nan and ContainsPercentage(int_cost) and not (IsPercentage(int_cost)) and not (('da ' and ' a ') in int_cost):
    cost, percentage = GetCostPercentage(int_cost)
    print(int_cost, "=>", cost, " and ", percentage)
    # Only possible case is that the intermediate is free
    int_cost_new = cost
    int_riy_new = percentage
  
  # If we have FINAL COST containing both cost and percentage for some reason
  if fin_cost is not np.nan and ContainsPercentage(fin_cost) and not (IsPercentage(fin_cost)) and not (('da ' and ' a ') in fin_cost):
    cost, percentage = GetCostPercentage(fin_cost)
    print(fin_cost, "=>", cost, " and ", percentage)
    fin_cost_new = cost
    # Case 1: final riy is empty
    if fin_riy_new == '-':
      fin_riy_new = percentage     
    # Case 2: final riy is full, initial riy is empty => put old final in initial and perc in final
    elif ini_riy_new =='-':
      ini_riy_new = fin_riy_new 
      fin_riy_new = percentage
    # Case 3: final riy is full, initial riy is full => put old final in intermed and perc in final
    else:
      int_riy_new = fin_riy_new
      fin_riy_new = percentage

  listy = [ini_cost_new, ini_riy_new, int_cost_new, int_riy_new, fin_cost_new, fin_riy_new]
  return pd.Series(listy)

df_ce[['initial_costs', 'initial_riy', 'intermediate_costs', 'intermediate_riy', 'final_costs', 'final_riy']] = df_ce.apply(
      lambda x: SplitCostPercentage_shifting(x.initial_costs, x.initial_riy, x.intermediate_costs, x.intermediate_riy, 
                                     x.final_costs, x.final_riy), axis=1)

"""## Splitting two percentages in Costs Composition table"""

def SplitPercentages(cell, cell2):
  # If we have a cell containing two percentages for some reason (2 cells as a single multi-line)
  if ('da ' and ' a ') in cell: listy = [cell,cell2]
  elif (ContainsPercentage(cell) and '\n' in cell):
    my_str = cell
    # Take the first percentage match
    perc1 = ContainsPercentage(my_str)[0]
    # Remove it from the original string
    perc2 = my_str.replace(perc1, '')
    # Check if there is another percentage in the remaining text
    if (ContainsPercentage(perc2)):
      perc2 = ContainsPercentage(perc2)[0] #take the text
      listy = [perc1,perc2]
      print("\nUpdated ", my_str, "=>", perc1, " and ", perc2)
    else:
      listy = [perc1,cell2]
      print("\nUpdated ", my_str, "=>", perc1)
  else:
    listy = [cell,cell2]
  return pd.Series(listy)


columns = df_cc.columns.to_list()[1:]
for idx in range(0,len(columns),2):
  col_1 = columns[idx]
  col_2 = columns[idx+1]

  df_cc[[col_1, col_2]] = df_cc.apply(
      lambda x: SplitPercentages(x[col_1], x[col_2]) if x[col_1] is not np.nan
      else pd.Series([x[col_1], x[col_2]]), axis=1)

"""# Cleaning cost rows"""

def CleanCost(my_str):

    # Remove spaces at the beginning and the end of the string
    string = my_str.strip()

    # Case "EUR 9.969.,45" => "EUR 9.969,45"
    if (re.search('(\-)?(\d)+(\.,|\,.)(\d)+', string)): 
      string = string.replace('.,', ',')
      string = string.replace(',.', ',')
    # Get just the number and punctuations
    if (re.search('(\-)?\d+((\,|\.)\d+)?((\,|\.)\d+)?',string)):
      string = re.search('(\-)?\d+((\,|\.)\d+)?((\,|\.)\d+)?',string)[0]
    else: 
      print("Error string: ", string)
      return np.nan
    # Case "100.000,11" => "100000,11"
    if (re.search('(\-)?(\d)+(\.)(\d){3}(\,)(\d)+', string)): string = string.replace('.', '')
    # Case "100,000.11" => "100000,11"
    elif (re.search('(\-)?(\d)+(\,)(\d){3}(\.)(\d)+', string)): 
      string = string.replace(',', '')
      string = string.replace('.', ',')
    # Case "122.000" => "122000"
    elif (re.search(r'(\-)?(\d)+(\.)(\d{3}\b$)', string)):
      string = string.replace('.', '')
    # Case "250.00" or "250.63742" => "250,00"
    elif (re.search(r'(\-)?(\d)+(\.)(\d{2}\b$)', string) or re.search(r'^(\-)?(\d)+(\.)(\d{4})', string)):
      string = string.replace('.', ',')
    # None of the above (ex: "122,3451") => DO NOTHING

    if (my_str!=string):
      cleaned.append(string)
      original.append(my_str)
    return string

original = []
cleaned = []

cost_cols_ce = df_ce.columns.to_list()[1:4] # col 1,2,3
cost_cols_p = df_p.columns.to_list()[1::2] # col 1,3,5,...
for col in cost_cols_ce:
  df_ce[col] = df_ce[col].dropna().apply(lambda x: CleanCost(x))
for col in cost_cols_p:
  df_p[col] = df_p[col].dropna().apply(lambda x: CleanCost(x))

updates = pd.DataFrame(data={'original': original, 'cleaned': cleaned})
print(updates.shape)
updates.head(20) #show updates if you want to check correctness

"""# Cleaning percentage rows"""

def CleanPercentage(my_str):

    # Remove spaces at the beginning and the end of the string
    string = my_str.strip()
    
    # Case "9.969.,45%" => "9.969,45%"
    if (re.search('(\-)?(\d)+(\.,|\,.)(\d)+%', string)): 
      string = string.replace('.,', ',')
      string = string.replace(',.', ',')
    # Get just the number and punctuations
    if (re.search('(\-)?\d+((\,|\.)\d+)?((\,|\.)\d+)?%',string)):
      string = re.search('(\-)?\d+((\,|\.)\d+)?((\,|\.)\d+)?%',string)[0]
    else: 
      print("Error string: ", string)
      return np.nan
    # Case "100.000,11%" => "100000,11%"
    if (re.search('(\-)?(\d)+(\.)(\d){3}(\,)(\d)+%', string)): string = string.replace('.', '')
    # Case "100,000.11%" => "100000,11%"
    elif (re.search('(\-)?(\d)+(\,)(\d){3}(\.)(\d)+%', string)): 
      string = string.replace(',', '')
      string = string.replace('.', ',')
    # Case "50.00%" or "50.637%" => "50,00%"
    elif (re.search(r'(\-)?(\d)+(\.)(\d)+%', string)):
      string = string.replace('.', ',')
    # None of the above (ex: "122,3451") => DO NOTHING

    if (my_str!=string):
      cleaned.append(string)
      original.append(my_str)
    return string

perc_cols_ce = df_ce.columns.to_list()[4:] # col 4,5,6
perc_cols_cc = df_cc.columns.to_list()[1:] # col 1,2,3,4,...
perc_cols_p = df_p.columns.to_list()[2::2] # col 2,4,6,...

print("--Costs evolution")
for col in perc_cols_ce:
  df_ce[col] = df_ce[col].dropna().apply(lambda x: CleanPercentage(x))
print("--Performance scenarios")
for col in perc_cols_p:
  df_p[col] = df_p[col].dropna().apply(lambda x: CleanPercentage(x))
print("--Costs composition")
for col in perc_cols_cc:
  df_cc[col] = df_cc[col].dropna().apply(lambda x: CleanPercentage(x))

updates = pd.DataFrame(data={'original': original, 'cleaned': cleaned})
print(updates.shape)
updates.tail(20) #show updates (both from cost and from % cleaning) if you want to check correctness

"""# Write to csv"""
## 02-Dataset [FINE-TUNED MODEL]
output_file_ce = "costs_evolution_extractions_cleaned.csv" #costs evolution
output_file_cc = "costs_composition_extractions_cleaned.csv" #costs composition
output_file_p = "performance_extractions_cleaned.csv" #performance scenarios

df_ce.to_csv(output_file_ce, index=False, header=True)
df_cc.to_csv(output_file_cc, index=False, header=True)
df_p.to_csv(output_file_p, index=False, header=True)
