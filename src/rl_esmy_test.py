#s!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 17:46:59 2019

@author: coqueletm
"""

print("General imports")
import numpy as np
import os,sys
from os import system

print("Adding pymodules directory to path")
import classNN as NN

pylibPath = os.path.abspath("../pylib")    # WARNING ! pwd is where the MAIN file was launched !!!
if pylibPath not in sys.path:
    sys.path.insert(0, pylibPath)

pylibPath = os.path.abspath("../gym-esmy/")    # WARNING ! pwd is where the MAIN file was launched !!!
if pylibPath not in sys.path:
    sys.path.insert(0, pylibPath)

pylibPath = os.path.abspath("../gym-esmy/gym_esmy/envs")    # WARNING ! pwd is where the MAIN file was launched !!!
if pylibPath not in sys.path:
    sys.path.insert(0, pylibPath)

import ESMY_MO_env_v0 as esmy_mo_env
import gym
from stable_baselines3.sac import SAC



#-------- Defining learning and testing variables --------#

nb_done = 0
v = 0
rundir = '2022_10_04-10_40_23'

learn_dir = '../out/learn_v{}/{}/'.format(v,rundir)


bf = len(next(os.walk(learn_dir))[1])-1
# bf = 20
b0 = nb_done + 1 
print('There are {} batches to test, starting at batch {}'.format(bf,b0))

nit    = 6
ntests = 1

nobs = 2
nact = 2

#------------------ // testing -----------------------#


for batch in range(b0,bf+1):
    out_dir_batch = learn_dir + 'batch{}/'.format(batch)    
    out_dir_test  = '../out/test_v{}/{}/'.format(v,rundir)    
    if not os.path.isdir(out_dir_test):
        os.makedirs(out_dir_test)
    for j in range(ntests):

        out_dir_test_batch = out_dir_test + 'batch{}/test{}/'.format(batch,j+1)    
        
        print('out_dir_test_batch = {}'.format(out_dir_test_batch))
    
        if not os.path.isdir(out_dir_test_batch):
            print('Creating out_dir {}'.format(out_dir_test_batch))
            os.makedirs(out_dir_test_batch)
    
        sys.stdout = open(out_dir_test_batch+'stdout','w')
    
        #---------- Loading model        
        system('cp {}test{}.zip {}'.format(out_dir_batch,batch,out_dir_test_batch))

        env   = gym.make('esmymo-v0',out_dir=out_dir_test_batch)
        model_2 = SAC.load("{}test{}.zip".format(out_dir_test_batch,batch))
    
        #--------- Testing model
        obs      = np.zeros((nit,nobs), dtype=np.float32)
        obs[0,:] = env.reset()
        action   = np.zeros((nit,nact),dtype=np.float32)
        reward   = np.zeros((nit))
    
        for it in range(1,nit):
    
            print('Iteration {}/{}'.format(it,nit))
            action, _states = model_2.predict(obs[it-1,:], deterministic=True)
            print('action = ', action, 'action.shape = ',action.shape)
    
            obs[it,:],reward[it],_,_ = env.step(action)
            print('reward = ', reward[it], 'reward.shape = ',reward[it].shape)

