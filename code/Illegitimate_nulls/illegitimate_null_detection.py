# -*- coding: utf-8 -*-

import pandas as pd
import sklearn 
import numpy as np
from sklearn import preprocessing, cluster, decomposition, neighbors, metrics
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import make_scorer, f1_score

import numpy as np
from numpy import random, where
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
import math
from tqdm import tqdm
import matplotlib.pyplot as plt

pd.options.display.max_columns = 60

df = pd.read_csv('../../dataset/dataset-02.csv')
print(df.shape)
df.head()

"""Testing Costs evolution and performance nulls: Annotation"""

one_year = 365
three_years = 1095

df_1 = df[df['RHP_DAYS']<one_year]
df_2 = df[(df['RHP_DAYS']>=one_year) & (df['RHP_DAYS']<=three_years)]
df_3 = df[df['RHP_DAYS']>three_years]
print(df_1.shape, df_2.shape, df_3.shape)

df_1 = df_1.replace('-',np.nan)
df_2 = df_2.replace('-',np.nan)
df_3 = df_3.replace('-',np.nan)

df_1['ALERT'] = 0
df_2['ALERT'] = 0
df_3['ALERT'] = 0

initial_cols = ['INITIAL_COSTS', 'INITIAL_RIY', 'INTIAL_STRESS_REFUND', 'INITIAL_STRESS_RETURN',
                'INITIAL_UNFAVOURABLE_REFUND', 'INITIAL_UNFAVOURABLE_RETURN',
                'INITIAL_MODERATE_REFUND', 'INITIAL_MODERATE_RETURN',
                'INITIAL_FAVOURABLE_REFUND', 'INITIAL_FAVOURABLE_RETURN',]
intermediate_cols = ['INTERMEDIATE_COSTS', 'INTERMEDIATE_RIY', 'INTERMEDIATE_STRESS_REFUND', 'INTERMEDIATE_STRESS_RETURN',
                    'INTERMEDIATE_UNFAVOURABLE_REFUND', 'INTERMEDIATE_UNFAVOURABLE_RETURN',
                    'INTERMEDIATE_MODERATE_REFUND', 'INTERMEDIATE_MODERATE_RETURN',
                    'INTERMEDIATE_FAVOURABLE_REFUND', 'INTERMEDIATE_FAVOURABLE_RETURN']
final_cols = ['FINAL_COSTS', 'FINAL_RIY','FINAL_STRESS_REFUND', 'FINAL_STRESS_RETURN',
              'FINAL_UNFAVOURABLE_REFUND', 'FINAL_UNFAVOURABLE_RETURN',
              'FINAL_MODERATE_REFUND', 'FINAL_MODERATE_RETURN',
              'FINAL_FAVOURABLE_REFUND', 'FINAL_FAVOURABLE_RETURN']

# Check annotation rules

# RULE 1: In df_1 final can not be null
for col in final_cols:
  condition = df_1[col].isna()
  df_1['ALERT'] = np.where(condition,1,df_1['ALERT']) # Condition, true assign, false assignment
# RULE 2: In df_2 initial and final info can not be null
for col in final_cols+initial_cols:
  condition = df_2[col].isna()
  df_2['ALERT'] = np.where(condition,1,df_2['ALERT'])
# RULE 3: In df_3 initial, intermediate and final info can not be null
for col in final_cols+initial_cols+intermediate_cols:
  condition = df_3[col].isna()
  df_3['ALERT'] = np.where(condition,1,df_3['ALERT'])

print("DF1: %d alert, %d ok." % (df_1['ALERT'].to_list().count(1), df_1['ALERT'].to_list().count(0))) 
print("DF2: %d alert, %d ok." % (df_2['ALERT'].to_list().count(1), df_2['ALERT'].to_list().count(0))) 
print("DF3: %d alert, %d ok." % (df_3['ALERT'].to_list().count(1), df_3['ALERT'].to_list().count(0)))

my_df = df_1.append(df_2).append(df_3)
my_df.shape

"""Vectorization"""

binary_cols = ['FILE_PATH', 'ID', 'ISIN', 'WEBSITE']
categorical_cols = ['PRODUCT_NAME', 'MANUFACTURER', 'TYPE', 'CURRENCY', 'CLASSIFICATION_LEVEL1',
                    'CLASSIFICATION_LEVEL2', 'CLASSIFICATION_LEVEL3']
numeric_cols = ['SYNTHETIC_RISK_INDICATOR', 'RHP_DAYS', 'INITIAL_COSTS', 'INTERMEDIATE_COSTS', 'FINAL_COSTS', 'INITIAL_RIY',
       'INTERMEDIATE_RIY', 'FINAL_RIY', 'ONEOFF_ENTRY_COSTS',
       'ONEOFF_EXIT_COSTS', 'ONGOING_TRANSACTION_COSTS', 'OTHER_ONGOING_COSTS',
       'INCIDENTAL_PERFORMANCE_FEES', 'INCIDENTAL_CARRIED_INTERESTS',
       'INTIAL_STRESS_REFUND', 'INITIAL_STRESS_RETURN',
       'INITIAL_UNFAVOURABLE_REFUND', 'INITIAL_UNFAVOURABLE_RETURN',
       'INITIAL_MODERATE_REFUND', 'INITIAL_MODERATE_RETURN',
       'INITIAL_FAVOURABLE_REFUND', 'INITIAL_FAVOURABLE_RETURN',
       'INTERMEDIATE_STRESS_REFUND', 'INTERMEDIATE_STRESS_RETURN',
       'INTERMEDIATE_UNFAVOURABLE_REFUND', 'INTERMEDIATE_UNFAVOURABLE_RETURN',
       'INTERMEDIATE_MODERATE_REFUND', 'INTERMEDIATE_MODERATE_RETURN',
       'INTERMEDIATE_FAVOURABLE_REFUND', 'INTERMEDIATE_FAVOURABLE_RETURN',
       'FINAL_STRESS_REFUND', 'FINAL_STRESS_RETURN',
       'FINAL_UNFAVOURABLE_REFUND', 'FINAL_UNFAVOURABLE_RETURN',
       'FINAL_MODERATE_REFUND', 'FINAL_MODERATE_RETURN',
       'FINAL_FAVOURABLE_REFUND', 'FINAL_FAVOURABLE_RETURN']
# Remove percentage symbol
for col in my_df.columns:
  my_df[col] = my_df[col].apply(lambda x: x.replace("%","") if isinstance(x, str) else x)

def EncodeBinary(dataframe, columns):
  for col in columns:
    dataframe[col] = dataframe[col].apply(lambda x: 1 if (isinstance(x, str) or not(np.isnan(x))) else np.nan)
  return dataframe

def EncodeCategorical(dataframe, columns):
  for col in columns:
    le = preprocessing.LabelEncoder() #instanciate the Encoder
    df_col = dataframe[[col]] #take just the column
    df_temp = df_col.astype("str").apply(le.fit_transform) #fit and transform
    df_final = df_temp.where(~df_col.isna(), df_col) #apply the encoding without touching the NaNs
    dataframe[col] = df_final[col] #store the encoded features in place of the categories
  return dataframe

def EncodeNumerical(dataframe, columns):
  for col in columns:
    #dataframe[col] = dataframe[col].str.replace(",", ".").astype(float)
    dataframe[col] = dataframe[col].apply(lambda x: str(x).replace(",",".")).astype(float)
  return dataframe

# VECTORIZATION (Feature encoding depending on their types)
my_df = EncodeBinary(my_df, binary_cols)
my_df = EncodeCategorical(my_df, categorical_cols)
my_df = EncodeNumerical(my_df, numeric_cols)
# Cast to float except the label
features = my_df.columns[my_df.columns != 'ALERT']
my_df[features] = my_df[features].astype(float)
print(my_df.shape)
my_df.head()

# Nan Replace
nan_replace = 2*np.amax(my_df[features].max().values) # for each col get max and then get the max of all cols and * 2
my_df = my_df.replace(np.nan, nan_replace)
print("NaN is repesented by ", nan_replace)

scaler = preprocessing.StandardScaler()
X = scaler.fit_transform(my_df[features].to_numpy(copy=True))
y = my_df['ALERT'].to_numpy(copy=True)
print(X.shape, y.shape)
print("Anomalies:",  my_df['ALERT'].to_list().count(1)) # 596

"""Hyperparameter Tuning for DBSCAN: searching for the best model.

The best model is one that:
- is able to distinguish anomalies from normal data in this dataset
- is sensitive to perturbations: not only the present anomalies should be detected, but also the new impurities that we have introduced as test. This should be true on each field to be tested.
"""

# DEFINE HYPERPARAMETERS : 
# min_samples := minimum amount of data points needed to create a cluster (large min_samples => less clusters, possibly more outliers)
# epsilon := maximum distance of a point to its cluster (small epsilon => more dense clusters)
base_min_pts = len(features)
parameters = {'eps':[0.5, 0.8, 1, 1.2, 1.3, 1.6, 1.8, 2, 3, 5, 10, 20, 40, 80, 160, 320], 
              'min_samples':[base_min_pts/10, base_min_pts/8, base_min_pts/5, base_min_pts/3,base_min_pts/2, base_min_pts, 2*base_min_pts, 3*base_min_pts, 
                             4*base_min_pts, 5*base_min_pts],
              'pca':[0,2,3,4,6,8,10,12,14,16,18,20,22,24,26,28,30]}
print(parameters)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)


# This function extracts the outliers from the predicted cluster labels
def get_outliers(clusters_predicted):
  pred_anomalies = []
  for c in clusters_predicted:
    if c==-1: # anomaly
      pred_anomalies.append(1)
    else: # not an anomaly
      pred_anomalies.append(0)
  return np.asarray(pred_anomalies)


def get_best_model(parameters, X_p, y_p):
  precisions = []
  recalls = []
  fscores = []
  weighted_avg_p = []
  weighted_avg_r = []
  weighted_avg_f = []
  eps_vals = []
  minpts_vals = []
  pca_vals = []
  n_anomalies = []
  n_clusters = []

  # APPLY ALL THE HYPERPARAM COMBINATIONS
  for n_comp in parameters['pca']:
    if n_comp==0: # no pca
      my_X = X_p
    else:
      # Apply pca with n_components
      pca = decomposition.PCA(n_components=n_comp).fit(X_p)
      #print(pca.explained_variance_ratio_)
      total_var = pca.explained_variance_ratio_.sum(axis=0)
      my_X = pca.transform(X_p) #nans are ignored
    for eps_val in parameters['eps']:
      for minpts_val in parameters['min_samples']:
        # Run the DBSCAN
        pred = cluster.DBSCAN(eps=eps_val, min_samples=minpts_val).fit_predict(my_X) #with pca
        # Get anomaly labels from cluster labels
        y_pred = get_outliers(pred)
        # Compute performance metrics using predicted and true labels; consider metrics for the anomaly class
        report = metrics.classification_report(y_p, y_pred, output_dict=True, zero_division=True)
        precision = report['1']['precision']
        recall = report['1']['recall']
        fscore = report['1']['f1-score']
        precisions.append(precision)
        recalls.append(recall)
        fscores.append(fscore)
        eps_vals.append(eps_val)
        minpts_vals.append(minpts_val)
        pca_vals.append(n_comp)
        n_anomalies.append(np.count_nonzero(y_pred == 1))
        weighted_avg_p.append(report['weighted avg']['precision'])
        weighted_avg_r.append(report['weighted avg']['recall'])
        weighted_avg_f.append(report['weighted avg']['f1-score'])
        n_clusters.append(len(set(pred)) - (1 if -1 in pred else 0))


  report_df = pd.DataFrame(list(zip(eps_vals, minpts_vals, pca_vals, n_anomalies, n_clusters, precisions, recalls, fscores, weighted_avg_p,
                                    weighted_avg_r, weighted_avg_f, )),
                columns =['epsilon', 'min_samples', 'n_pc','n_anomalies','n_clusters', 'precision_1', 'recall_1', 'f1score_1',
                          'weigh_avg_precision', 'weigh_avg_recall', 'weigh_avg_f1score'])
  report_df = report_df.sort_values(by='f1score_1',ascending=False).head(report_df.shape[0])
  return report_df

report_df = get_best_model(parameters,X, y)
report_df.head()

report_df.head(report_df.shape[0])

print("Best model:")
# Best model
best_idx = 0

best_params = {}
best_params['eps'] = report_df.iloc[best_idx]['epsilon'] 
best_params['min_samples'] = report_df.iloc[best_idx]['min_samples'] 
best_params['pca'] = int(report_df.iloc[best_idx]['n_pc'])
print(best_params)
print(report_df.iloc[0])


"""Test the model performances on Perturbations"""

class MatrixPerturbator:

  # INITIALIZATION
  # feature_matrix is our original matrix of shape (n_data, n_features);
  def __init__(self, feature_matrix):
    self.feature_matrix = feature_matrix
    self.unscaled_matrix = np.zeros(self.feature_matrix.shape) #perturbed not scaled 
    self.scaled_matrix = np.zeros(self.feature_matrix.shape) #perturbed and scaled
  
  # APPLYING ONE-FIELD PERTURBATIONS : what is the effect of perturbing just one feature?
  def one_field_perturbation(self, y_values, n_perturbations,seed, feat_idx):
    y_new = y_values
    np.random.seed(seed)
    updated_matrix = self.feature_matrix
    for p in tqdm(range(n_perturbations)):
      perturbed = False
      while not(perturbed):
        add = 0
        # Generate random sample index
        sample_idx = np.random.randint(0, high=self.feature_matrix.shape[0], size=None)
        sample_idx = sample_idx+add
        if not(updated_matrix[sample_idx][feat_idx]==nan_replace) and y_new[sample_idx]==0:
          # Apply perturbation
          updated_matrix[sample_idx][feat_idx] = nan_replace
          y_new[sample_idx] = 1
          perturbed = True # go to the next perturbation
    self.unscaled_matrix = updated_matrix
    scaler = preprocessing.StandardScaler()
    self.scaled_matrix = scaler.fit_transform(updated_matrix) #nans are ignored
    return y_new


## To test all the features 
pi = 15 #perturbation level (number of anomalies added)
# All the perturbation features
perturbation_feat = [13, 14, 15, 16, 17, 18] # choose which features (idx) you want to perturb
perturbation_feat = perturbation_feat+[i for i in range(25,49)]


# Instanciate DBSCAN with the best parameters
model = cluster.DBSCAN(eps=best_params['eps'], min_samples=best_params['min_samples'])

w_p = [] # weighted precisions
w_r = [] # weighted recalls
w_f = [] # weighted fscores
m_p = [] # macro precisions
m_r = [] # macro recalls
m_f = [] # macro fscores
a_p = [] # anomaly precision
a_r = [] # anomaly recall
a_f = [] # anomaly fscore


# For each feature to be perturbed
for feat_idx in perturbation_feat:
  print("\n\n PERTURBING feature ", features[feat_idx])
  # Take the original data and features
  X = my_df[features].to_numpy(copy=True)
  y = my_df['ALERT'].to_numpy(copy=True)
  # Apply the pi-perturbation
  mp = MatrixPerturbator(X) # initialize
  y_p = mp.one_field_perturbation(y,pi,seed,feat_idx)
  X_p = mp.scaled_matrix
  print("Anomalies present (after perturbation): ", np.count_nonzero(y_p==1))
  # Apply pca if required
  if best_params['pca']!=0:
    pca = decomposition.PCA(n_components=best_params['pca']).fit(X_p)
    X_p = pca.transform(X_p) #nans are ignored
  # else X_p is just the one scaled and perturbed
  # DBSCAN: fit and predict
  pred = model.fit_predict(X_p) # Predict cluster labels
  y_pred = get_outliers(pred) # Get anomaly labels
  # Evaluation
  print(metrics.classification_report(y_p, y_pred, output_dict=False, zero_division=True))
  print(metrics.confusion_matrix(y_p,y_pred, labels=[0,1]))
  rep = metrics.classification_report(y_p, y_pred, output_dict=True, zero_division=True)
  # Append evaluation metrics (useful for the final average)
  w_p.append(rep['weighted avg']['precision'])
  w_r.append(rep['weighted avg']['recall'])
  w_f .append(rep['weighted avg']['f1-score'])
  m_p.append(rep['macro avg']['precision'])
  m_r.append(rep['macro avg']['recall'])
  m_f.append(rep['macro avg']['f1-score'])
  a_p.append(rep['1']['precision'])
  a_r.append(rep['1']['recall'])
  a_f.append(rep['1']['f1-score'])

# Computing averages for each metric
def avg(my_list):
  total = sum(my_list)
  length = len(my_list)
  average = total/length
  return average

print("Average Weighted Precision = ", avg(w_p))
print("Average Weighted Recall = ", avg(w_r))
print("Average Weighted F1-Score = ", avg(w_f))
print("Average Macro Precision = ", avg(m_p))
print("Average Macro Recall = ", avg(m_r))
print("Average Macro F1-Score = ", avg(m_f))
print("Average Anomaly Precision = ", avg(a_p))
print("Average Anomaly Recall = ", avg(a_r))
print("Average Anomaly F1-Score = ", avg(a_f))