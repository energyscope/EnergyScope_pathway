#s!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""

@author: rixhonx
"""

print("General imports")
import numpy as np
import os,sys
from os import system
import pandas as pd
import pickle as pkl
import time

pylibPath = os.path.abspath("../pylib")    # WARNING ! pwd is where the MAIN file was launched !!!
if pylibPath not in sys.path:
    sys.path.insert(0, pylibPath)

pylibPath = os.path.abspath("../gym-esmy/")    # WARNING ! pwd is where the MAIN file was launched !!!
if pylibPath not in sys.path:
    sys.path.insert(0, pylibPath)

pylibPath = os.path.abspath("../gym-esmy/gym_esmy/envs")    # WARNING ! pwd is where the MAIN file was launched !!!
if pylibPath not in sys.path:
    sys.path.insert(0, pylibPath)

import gym
import gym_esmy
from stable_baselines3.sac import SAC
import rl_esmy_stats
import seaborn as sns




#-------- Defining learning and testing variables --------#


v = '10'
type_of_model = 'MO'
rundir = '2023_09_06-11_54_49'
out_dir_test  = '../out/test_v{}/{}/{}/'.format(v,rundir,type_of_model)


if not os.path.isdir(out_dir_test):
    os.makedirs(out_dir_test)

learn_dir = '../out/learn_v{}/{}/_batchs/'.format(v,rundir)


bf = len(next(os.walk(learn_dir))[1])-1
# bf = 2
nb_done = 0
b0 = nb_done + 1 
print('There are {} batches to test, starting at batch {}'.format(bf,b0))

nit    = 1
ntests = 10

lst_files = os.listdir(out_dir_test)
txt_files = [x for x in lst_files if x.endswith('.txt')]
if 'set_up.txt' in txt_files:
    txt_files.remove('set_up.txt')
if 'READ_ME.txt' in txt_files:
    txt_files.remove('READ_ME.txt')
for f in txt_files:
    system('rm {}{}'.format(out_dir_test,f))

test = False
fill_df = True
graph = True

#------------------ // testing -----------------------#


if test:

    for batch in range(b0,bf+1):
        out_dir_batch = learn_dir + 'batch{}/'.format(batch)    
        for j in range(ntests):
            t = time.time()
    
            out_dir_test_batch = out_dir_test + 'batch{}/test{}/'.format(batch,j+1)    
            
            print('out_dir_test_batch = {}'.format(out_dir_test_batch))
        
            if not os.path.isdir(out_dir_test_batch):
                print('Creating out_dir {}'.format(out_dir_test_batch))
                os.makedirs(out_dir_test_batch)
        
            sys.stdout = open(out_dir_test_batch+'stdout','w')
        
            #---------- Loading model        
            system('cp {}test{}.zip {}'.format(out_dir_batch,batch,out_dir_test_batch))
            
            env = gym.make('esmy-v{}'.format(v),out_dir=out_dir_test_batch, v=v,type_of_model=type_of_model, nb_done=j, new_step_api=False)
            model = SAC.load("{}test{}".format(out_dir_test_batch,batch))
        
            #--------- Testing model
            obs = env.reset()
            
            episode_over = False
            i = 1
            while not episode_over:
                t_i = time.time()-t
                action, _states = model.predict(obs, deterministic=True)
                obs,reward,episode_over,_ = env.step(action)
                elapsed_i = time.time()-t_i
                print('Time to test the {}th steps: '.format(i),elapsed_i)
                i += 1
            elapsed = time.time()-t
            print('Time to test the whole problem (after {} steps): '.format(i),elapsed)
    
    if not os.path.isdir(out_dir_test+ '_batchs'):
        os.makedirs(out_dir_test+ '_batchs')
    system('cp -R {}batch* {}'.format(out_dir_test,out_dir_test+'_batchs'))
    system('rm -R {}batch*'.format(out_dir_test))

if fill_df:
    env = gym.make('esmy-v{}'.format(v),out_dir=out_dir_test, v=v,type_of_model=type_of_model, new_step_api=False)
    lst_files = os.listdir(out_dir_test)
    txt_files = [x for x in lst_files if x.endswith('.txt')]
    for f in txt_files:
        system('rm {}{}'.format(out_dir_test,f))
        
    nb_batch = len(next(os.walk(out_dir_test+'_batchs'))[1])
    # nb_test = len(next(os.walk(out_dir_test+'_batchs/'+'batch1'))[1])
    nb_test = ntests
    
    nb_act = env.action_space.shape[0]
    lst_act = ['act_{}'.format(i) for i in range(1,nb_act+1)]
    lst_binding = ['binding_{}'.format(i) for i in range(1,nb_act+1)]
    columns = ['step']
    columns += ['cum_gwp','gwp_2020','gwp_2025','gwp_2030','gwp_2035','gwp_2040','gwp_2045','gwp_2050']
    columns += ['RE_in_mix_2020', 'RE_in_mix_2025', 'RE_in_mix_2030', 'RE_in_mix_2035', 'RE_in_mix_2040', 'RE_in_mix_2045', 'RE_in_mix_2050']
    columns += ['Energy_efficiency_2020', 'Energy_efficiency_2025', 'Energy_efficiency_2030', 'Energy_efficiency_2035', 'Energy_efficiency_2040', 'Energy_efficiency_2045', 'Energy_efficiency_2050']
    columns += ['cum_cost','cost_2020','cost_2025','cost_2030','cost_2035','cost_2040','cost_2045','cost_2050']
    columns += lst_act
    columns += lst_binding
    columns += ['reward','status_2050','batch', 'episode']
    df_testing = pd.DataFrame(columns=columns)
    df_testing = rl_esmy_stats.fill_df_testing(out_dir_test+'_batchs/', df_testing, nb_batch,nb_test)
    df_testing = df_testing.reset_index().iloc[:,1:]
    # df_testing = rl_esmy_stats.updated_status_2050_testing(df_testing)
    open_file = open(out_dir_test+'df_testing_pkl',"wb")
    pkl.dump(df_testing, open_file)
    open_file.close()

if graph:
    env = gym.make('esmy-v{}'.format(v),out_dir=out_dir_test, v=v,type_of_model=type_of_model, new_step_api=False)
    lst_files = os.listdir(out_dir_test)
    txt_files = [x for x in lst_files if x.endswith('.txt')]
    for f in txt_files:
        system('rm {}{}'.format(out_dir_test,f))
    
    df_testing = open(out_dir_test+'df_testing_pkl','rb')
    df_testing = pkl.load(df_testing)
    
    finish = df_testing.loc[df_testing['reward'] !=0]
    finish_success = finish.loc[finish['status_2050'] == 'Success']
    
    best_policy = df_testing.loc[df_testing['episode']==df_testing.loc[df_testing['reward']==max(df_testing['reward'])]['episode'].iloc[0]]
    final_best = best_policy.loc[best_policy['reward'] != 0]
    
    sns.scatterplot(finish_success,x='cum_cost',y='cum_gwp',hue='episode')
    sns.scatterplot(finish,x='cum_cost',y='cum_gwp',hue='episode')
    
    # sns.scatterplot(finish_success,x='episode',y='reward')
    
    
    A = 4



