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

        df_temp = pd.concat([df_obs,df_cost.iloc[:,1:],df_act.iloc[:,2:],df_rew.iloc[:,1:]],axis=1, join='inner')
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

            df_temp = pd.concat([df_obs,df_cost.iloc[:,1:],df_act.iloc[:,2:],df_rew.iloc[:,1:]],axis=1, join='inner')
            df_temp['batch'] = i
            df_temp['episode'] = n_epoch_batch + df_act.iloc[:,0]
            df_temp.columns = df_testing.columns
            if i!=1:
                df_testing = pd.concat([df_testing,df_temp])
            else:
                df_testing = df_temp
            n_epoch_batch += df_act.iloc[-1,0]
    return df_testing


def updated_status_2050(df_learning):
    step = {0:'2030', 1:'2035', 2:'2040', 3:'2045', 4:'2050'}
    ep_success = df_learning['episode'].loc[df_learning['status_2050']=='Success']
    ep_failure = df_learning['episode'].loc[df_learning['status_2050']=='Failure']
    ep_failure_imp = df_learning['episode'].loc[df_learning['status_2050']=='Failure_imp']
    
    final_step_failure = df_learning[['episode','step']].loc[df_learning['status_2050']=='Failure'].copy()
    final_step_failure['step_year'] = final_step_failure['step']
    final_step_failure.replace({"step_year": step},inplace=True)
    final_step_failure['status_ep'] = 'Failure_'+final_step_failure['step_year'].astype(str)
    final_step_failure.drop(columns=['step_year','step'],inplace=True)
    final_step_failure.set_index(['episode'],inplace=True)
    
    final_step_failure_imp = df_learning[['episode','step']].loc[df_learning['status_2050']=='Failure_imp'].copy()
    final_step_failure_imp['step_year'] = final_step_failure_imp['step']
    final_step_failure_imp.replace({"step_year": step},inplace=True)
    final_step_failure_imp['status_ep'] = 'Failure_imp_'+final_step_failure_imp['step_year'].astype(str)
    final_step_failure_imp.drop(columns=['step_year','step'],inplace=True)
    final_step_failure_imp.set_index(['episode'],inplace=True)
    
    df_learning['status_ep'] = ''
    df_learning['status_2050'].loc[df_learning['episode'].isin(ep_success)] = 'Success'
    df_learning['status_ep'].loc[df_learning['episode'].isin(ep_success)] = 'Success'
    df_learning['status_2050'].loc[df_learning['episode'].isin(ep_failure)] = 'Failure'
    df_learning['status_2050'].loc[df_learning['episode'].isin(ep_failure_imp)] = 'Failure_imp'
    
    df_learning = df_learning.dropna(how='all')
    
    df_learning.set_index(['episode'],inplace=True)
    df_learning.update(final_step_failure)
    df_learning.update(final_step_failure_imp)
    df_learning = df_learning.reset_index()
    
    return df_learning