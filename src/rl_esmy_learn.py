#s!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 17:46:59 2019

@author: rixhonx
"""


print("General imports")
import numpy as np

import os,sys
from os import system
from datetime import datetime

pylibPath = os.path.abspath("../pylib")    # WARNING ! pwd is where the MAIN file was launched !!!

if pylibPath not in sys.path:
    sys.path.insert(0, pylibPath)

pylibPath = os.path.abspath("../gym-esmy/")    # WARNING ! pwd is where the MAIN file was launched !!!

if pylibPath not in sys.path:
    sys.path.insert(0, pylibPath)

pylibPath = os.path.abspath("../gym-esmy/gym_esmy/envs")    # WARNING ! pwd is where the MAIN file was launched !!!

if pylibPath not in sys.path:
    sys.path.insert(0, pylibPath)

out_dir = os.path.abspath('../out/')
# from fctSaveNN import SaveNeuralNetwork

print("About to import RL modules")
import gym
import tensorflow as tf

import gym_esmy
from stable_baselines.sac.policies import MlpPolicy
from stable_baselines.sac.policies import LnMlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines.common.env_checker import check_env
from stable_baselines import SAC

env = gym.make('esmymo-v0',out_dir=out_dir)

check_env(env)

A = 4


# #---------------- Defining dict -----------------#

# layers_dict = { '16x16'       : [16,16],
#                 '16x16x16'    : [16,16,16],
#                 '32x32'       : [32,32],
#                 '32x32x32'    : [32,32,32],
#                 '64x64'       : [64,64],
#                 '64x64x64'    : [64,64,64], 
#                 '128x128'     : [128,128],
#                 '128x128x128' : [128,128,128]  } 

# policy_dict = { 'Mlp'      : MlpPolicy,
#                 'LnMlp'    : LnMlpPolicy }


# actfun_dict = { 'tanh'     : tf.nn.tanh,
#                 'sigmoid'  : tf.nn.sigmoid,
#                 'softplus' : tf.nn.softplus,
#                 'relu'     : tf.nn.relu       }

# inflow_dict = { 'SYN'      : 'learn_syn',
#                 'BF'       : 'learn_bf'       }


# rundir = datetime.now()
# rundir = rundir.strftime('%Y_%m_%d-%H_%M_%S')


# #--------- Recovering passed arguments ---------#

# if len(sys.argv) > 1:
 
#     try:
#         v = int(sys.argv[1])
#     except:
#         v = 3

#     try:
#         jobid = sys.argv[2]
#         print('Provided job ID - Changing outdir = {} by outdir = {}'.format(rundir,jobid))
#         rundir = jobid
#     except:
#         pass

#     try:
#         flag  = inflow_dict[sys.argv[3]]
#         print('Please, choose one of the following inflows: ', inflow_dict.keys())
#         rundir = jobid
#     except:
#         pass

#     try:
#         policy  = policy_dict[sys.argv[4]]
#     except:
#         print('Please, choose one of the following policies: ', policy_dict.keys())
#         sys.exit(0)
    
#     try: 
#         layers  = layers_dict[sys.argv[5]]
#     except:
#         print('Please, choose one of the following layers configurations: ', layers_dict.keys())
#         sys.exit(0)
    
#     try:
#         act_fun = actfun_dict[sys.argv[6]]
#     except:
#         print('Please, choose one of the following activation functions: ', actfun_dict.keys())
#         sys.exit(0)
   
#     try: 
#         gamma = float(sys.argv[7])
#     except:
#         gamma = 0.3
    
#     try:
#         nS = int(sys.argv[8])
#     except:
#         nS = 16

#     try:
#         nb_done = int(sys.argv[9])
#         print('Starting from batch {}'.format(nb_done))
#     except:
#         nb_done = 0

#     print('Version {}, dir {} - policy = {}, layers = {}, act_fun = {}, gamma = {}, nS = {}'.format(v,rundir,policy,layers,act_fun,gamma,nS))

# else:
#     print('ERROR - No command line arguments given, please provide the following ones:')
#     print('version, directory, policy, layers, act_fun, gamma, nS, nb_done')
#     sys.exit(0)


# #-------- Defining learning variables --------#

# total_timesteps = 10000
# batch_timesteps = 500    

# nbatches = int(np.ceil(total_timesteps/batch_timesteps))
# # FOR BF SLICES !
# ninflows = 10     # Number of possible inflows I have (5 slices x 2 lines))
# inflows  = np.repeat(np.arange(0,ninflows),int(nbatches/ninflows)) 
# np.random.shuffle(inflows)

# ##  
# ##  #------- Defining output directories --------#
# ##   
# out_dir = '../out/learn_v{}/{}/'.format(v,rundir)

# if not os.path.isdir(out_dir):
#     print('Creating out_dir {}'.format(out_dir))
#     system('mkdir -p {}'.format(out_dir))

# #-------- Writing parameters in file --------#

# system('touch ' + out_dir + 'set_up.txt')

# f = open(out_dir + 'set_up.txt', 'r+')
# f.write('Learning with bem-env v{}\n'.format(v))
# f.write('discount factor = {}\n'.format(gamma))
# f.write('layers = {}\n'.format(layers))
# f.write('activation function = {}\n'.format(act_fun))
# f.write('policy = {}\n'.format(policy))
# f.write('number of sectors = {}\n'.format(nS))
# f.write('total #steps for learning = {}\n'.format(total_timesteps))
# f.write('#learning-steps per batch for learning = {}\n'.format(batch_timesteps))
# f.close()

# #----------- Creating environment ----------#

# out_dir_batch = out_dir + 'batch0/'    
# if not os.path.isdir(out_dir_batch):
#     print('Creating out_dir {}'.format(out_dir_batch))
#     system('mkdir -p {}'.format(out_dir_batch))

# it0     = 0
# #flag    = 'learn'
# env     = gym.make('bem-v234', v = v, out_dir = out_dir_batch, flag = flag, it0 = it0, nS = nS)
# env     = DummyVecEnv([lambda:env])
# model   = SAC(policy, env,gamma = gamma, verbose=1, tensorboard_log = '../log', policy_kwargs=dict(act_fun=act_fun, layers=layers))
# mymodel = out_dir_batch+"ipc0"
# model.save(mymodel)

# #--------------- Learning ------------------#

# remain_steps = total_timesteps - nb_done * batch_timesteps
# i = nb_done + 1
# #flag = 'learn_bf'

# while remain_steps > 0:

#     out_dir_batch = out_dir + 'batch{}/'.format(i)    
    
#     if not os.path.isdir(out_dir_batch):
#         print('Creating out_dir {}'.format(out_dir_batch))
#         system('mkdir {}'.format(out_dir_batch))

#     sys.stdout = open(out_dir_batch+'stdout','w')

#     if flag  == 'learn_syn':
#         it0 = total_timesteps - remain_steps
#     elif flag == 'learn_bf':
#         it0 = inflows[i%len(inflows)]
#     env     = gym.make('bem-v234', v = v, out_dir = out_dir_batch, flag = flag, it0 = it0, nS = nS)
#     env     = DummyVecEnv([lambda:env])
#     model   = SAC.load("{}batch{}/ipc{}".format(out_dir,i-1, i-1))
#     mymodel = out_dir_batch+"ipc{}".format(i)
    
#     model.set_env(env)

#     model.learn(batch_timesteps, log_interval=10)
#     model.save(mymodel)
#     SaveNeuralNetwork(model,mymodel+'.dict')

#     i += 1
#     remain_steps -= batch_timesteps

# #-------- Removing batch0 directory ----------#

# out_dir_batch = out_dir + 'batch0/'    
# system('rm -r {}'.format(out_dir_batch))


