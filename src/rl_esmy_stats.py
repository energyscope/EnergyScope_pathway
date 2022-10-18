#s!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  26 2022

@author: rixhonx
"""


print("General imports")
import numpy as np
from numpy import pi
import os,sys
from os import system
import pandas as pd

pylibPath = os.path.abspath("../pylib")    # WARNING ! pwd is where the MAIN file was launched !!!

if pylibPath not in sys.path:
    sys.path.insert(0, pylibPath)

def fill_df(output_dir, df_learning, nb_batch):
    df_temp = pd.DataFrame(columns=df_learning.columns)
    for i in range(1,nb_batch+1):
        df_obs = pd.read_csv(output_dir+'batch{}/observation.txt'.format(i), header = None, sep = ' ').reset_index(drop=True)
        df_act = pd.read_csv(output_dir+'batch{}/action.txt'.format(i), header = None, sep = ' ').reset_index(drop=True)
        df_rew = pd.read_csv(output_dir+'batch{}/reward.txt'.format(i), header = None, sep = ' ').reset_index(drop=True)

        df_temp = pd.concat([df_obs,df_act.iloc[:,1:],df_rew.iloc[:,1:]],axis=1, join='inner')
        df_temp['batch'] = i
        df_temp['episode'] = 0
        df_temp.columns = df_learning.columns
        if i!=1:
            df_learning = pd.concat([df_learning,df_temp])
        else:
            df_learning = df_temp
    return df_learning

def updated_status_2050(df_learning):
    idx_success = list(df_learning.index[df_learning['status_2050']=='Success'])
    idx_failure = list(df_learning.index[df_learning['status_2050']=='Failure'])
    df_learning.loc[[j-i for j in idx_success for i in range(1,5)],'status_2050'] = 'Success'
    df_learning.loc[[j-i for j in idx_failure for i in range(1,5)],'status_2050'] = 'Failure'
    df_learning.loc[df_learning['status_2050']=='','status_2050'] = 'Failure_imp'

    
    # if output_type == 'action':
    #     for i in dict_ep:
    #         if j == 1:
    #             dict_ep[i]= df_temp.loc[df_temp[0] == i].iloc[:,1:]
    #         else:
    #             dict_ep[i] = dict_ep[i].append(df_temp.loc[df_temp[0] == i].iloc[:,1:])
    # elif output_type == 'observation':
    #     if j == 1:
    #         dict_ep = df_temp.iloc[:,1:]
    #     else:
    #         dict_ep = dict_ep.append(df_temp.iloc[:,1:])
