#s!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  26 2022

@author: rixhonx
"""


print("General imports")
import numpy as np
import os,sys
from os import system
import pandas as pd

pylibPath = os.path.abspath("../pylib")    # WARNING ! pwd is where the MAIN file was launched !!!

if pylibPath not in sys.path:
    sys.path.insert(0, pylibPath)

def fill_df_learning(output_dir, df_learning, nb_batch):
    df_temp = pd.DataFrame(columns=df_learning.columns)
    n_epoch_batch = 0
    for i in range(1,nb_batch+1):
        df_obs = pd.read_csv(output_dir+'batch{}/observation.txt'.format(i), header = None, sep = ' ').reset_index(drop=True)
        df_act = pd.read_csv(output_dir+'batch{}/action.txt'.format(i), header = None, sep = ' ').reset_index(drop=True)
        df_rew = pd.read_csv(output_dir+'batch{}/reward.txt'.format(i), header = None, sep = ' ').reset_index(drop=True)
        df_cost = pd.read_csv(output_dir+'batch{}/cost.txt'.format(i), header = None, sep = ' ').reset_index(drop=True)
        df_binding = pd.read_csv(output_dir+'batch{}/binding.txt'.format(i), header = None, sep = ' ').reset_index(drop=True)

        df_temp = pd.concat([df_obs,df_cost.iloc[:,1:],df_act.iloc[:,2:],df_binding.iloc[:,2:],df_rew.iloc[:,1:]],axis=1, join='inner')
        df_temp['batch'] = i
        df_temp['episode'] = n_epoch_batch + df_act.iloc[:,0]
        df_temp.columns = df_learning.columns
        if i!=1:
            df_learning = pd.concat([df_learning,df_temp])
        else:
            df_learning = df_temp
        n_epoch_batch += df_act.iloc[-1,0]
    return df_learning

def fill_df_testing(output_dir, df_testing, nb_batch,nb_test):
    df_temp = pd.DataFrame(columns=df_testing.columns)
    n_epoch_batch = 0
    for i in range(1,nb_batch+1):
        for j in range(1,nb_test+1):
            df_obs = pd.read_csv(output_dir+'batch{}/test{}/observation.txt'.format(i,j), header = None, sep = ' ').reset_index(drop=True)
            df_act = pd.read_csv(output_dir+'batch{}/test{}/action.txt'.format(i,j), header = None, sep = ' ').reset_index(drop=True)
            df_rew = pd.read_csv(output_dir+'batch{}/test{}/reward.txt'.format(i,j), header = None, sep = ' ').reset_index(drop=True)
            df_cost = pd.read_csv(output_dir+'batch{}/test{}/cost.txt'.format(i,j), header = None, sep = ' ').reset_index(drop=True)
            df_binding = pd.read_csv(output_dir+'batch{}/test{}/binding.txt'.format(i,j), header = None, sep = ' ').reset_index(drop=True)
            
            df_temp = pd.concat([df_obs,df_cost.iloc[:,1:],df_act.iloc[:,2:],df_binding.iloc[:,2:],df_rew.iloc[:,1:]],axis=1, join='inner')
            df_temp['batch'] = i
            df_temp['episode'] = j
            df_temp.columns = df_testing.columns
            if i==1 and j==1 :
                df_testing = df_temp
            else:
                df_testing = pd.concat([df_testing,df_temp])
            n_epoch_batch += df_act.iloc[-1,0]
    return df_testing


def updated_status_2050_learning(df_learning):
    step = {0:'2030', 1:'2035', 2:'2040', 3:'2045', 4:'2050'}
    
    status_full = df_learning['status_2050'].unique()
    
    status_full = [x for x in status_full if str(x) != "nan"]
    status_failure = [x for x in status_full if "Failure" in str(x)]
    
    dict_ep = dict.fromkeys(status_full)
    final_step_failure = dict.fromkeys(status_failure)
    
    df_learning['status_ep'] = 'Success'
    
    
    for i,j in enumerate(status_full):
        dict_ep[j] = df_learning['episode'].loc[df_learning['status_2050']==j]
        if j in status_failure:
            temp = df_learning[['episode','step']].loc[df_learning['status_2050']==j].copy()
            temp['step_year'] = temp['step']
            temp.replace({"step_year": step},inplace=True)
            temp['status_ep'] = 'Failure_'+temp['step_year'].astype(str)
            temp.drop(columns=['step_year','step'],inplace=True)
            temp.set_index(['episode'],inplace=True)
            final_step_failure[j] = temp.copy()
        
        df_learning['status_2050'].loc[df_learning['episode'].isin(dict_ep[j])] = j
        
    df_learning = df_learning.dropna()
    
    df_learning.set_index(['episode'],inplace=True)
    
    for i,j in enumerate(status_failure):
        df_learning.update(final_step_failure[j])
    

    
    df_learning = df_learning.reset_index()
        
    return df_learning

def updated_status_2050_testing(df_testing):
    step = {0:'2030', 1:'2035', 2:'2040', 3:'2045', 4:'2050'}
    
    status_full = df_testing['status_2050'].unique()
    
    status_full = [x for x in status_full if str(x) != "nan"]
    status_failure = [x for x in status_full if "Failure" in str(x)]
    
    dict_ep = dict.fromkeys(status_full)
    final_step_failure = dict.fromkeys(status_failure)
    
    df_testing['status_ep'] = 'Success'
    
    
    for i,j in enumerate(status_full):
        dict_ep[j] = df_testing['episode'].loc[df_testing['status_2050']==j]
        if j in status_failure:
            temp = df_testing[['episode','step']].loc[df_testing['status_2050']==j].copy()
            temp['step_year'] = temp['step']
            temp.replace({"step_year": step},inplace=True)
            temp['status_ep'] = 'Failure_'+temp['step_year'].astype(str)
            temp.drop(columns=['step_year','step'],inplace=True)
            temp.set_index(['episode'],inplace=True)
            final_step_failure[j] = temp.copy()
        
        df_testing['status_2050'].loc[df_testing['episode'].isin(dict_ep[j])] = j
        
    df_testing = df_testing.dropna()
    
    df_testing.set_index(['episode'],inplace=True)
    
    for i,j in enumerate(status_failure):
        df_testing.update(final_step_failure[j])
    
    df_testing = df_testing.reset_index()
        
    return df_testing