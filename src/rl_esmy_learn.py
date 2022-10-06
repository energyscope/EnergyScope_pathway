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
from fctSaveNN import SaveNeuralNetwork

print("About to import RL modules")
import gym
import gym_esmy
import torch
import pandas as pd
import pickle as pkl
import shutil

import rl_esmy_stats
import rl_esmy_graphs
from stable_baselines3.sac.policies import SACPolicy
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.sac import SAC

# from stable_baselines.common.env_checker import check_env
# rundir = datetime.now()
# rundir = rundir.strftime('%Y_%m_%d-%H_%M_%S')
# v = 0
# out_dir = '../out/learn_v{}/{}/'.format(v,rundir)
# if not os.path.isdir(out_dir):
#     print('Creating out_dir {}'.format(out_dir))
#     system('mkdir -p {}'.format(out_dir))
# env = gym.make('esmymo-v0',out_dir=out_dir)
# check_env(env)



#---------------- Defining dict -----------------#


# #--------- Recovering passed arguments ---------#

v = 0
policy = 'MlpPolicy'
gamma = 0.3
act_fun = torch.nn.modules.activation.ReLU
layers = [16,16]
nb_done = 0

# #-------- Defining learning variables --------#

total_timesteps = 10000
batch_timesteps = 500

rundir = '2022_10_06-12_12_13'
out_dir = '../out/learn_v{}/{}/'.format(v,rundir)

learning = False
fill_df = True
plot = True

df_learning = pd.DataFrame(columns=['step', 'cum_gwp','gwp_2020','gwp_2025','gwp_2030','gwp_2035','gwp_2040','gwp_2045','gwp_2050','act_1','act_2','reward','status_2050','batch', 'episode'])

if learning:
    rundir = datetime.now()
    rundir = rundir.strftime('%Y_%m_%d-%H_%M_%S')

    nbatches = int(np.ceil(total_timesteps/batch_timesteps))
    
    # ##  
    # ##  #------- Defining output directories --------#
    # ##   
    out_dir = '../out/learn_v{}/{}/'.format(v,rundir)
    
    if not os.path.isdir(out_dir):
        print('Creating out_dir {}'.format(out_dir))
        system('mkdir -p {}'.format(out_dir))
    
    #-------- Writing parameters in file --------#
    
    system('touch ' + out_dir + 'set_up.txt')
    
    f = open(out_dir + 'set_up.txt', 'r+')
    f.write('Learning with esmymo v{}\n'.format(v))
    f.write('discount factor = {}\n'.format(gamma))
    f.write('nlayers = {}\n'.format(layers))
    f.write('activation function = {}\n'.format(act_fun))
    f.write('policy = {}\n'.format(policy))
    f.write('total #steps for learning = {}\n'.format(total_timesteps))
    f.write('#learning-steps per batch for learning = {}\n'.format(batch_timesteps))
    f.close()
    
    # #----------- Creating environment ----------#
    
    out_dir_batch = out_dir + 'batch0/'    
    if not os.path.isdir(out_dir_batch):
        print('Creating out_dir {}'.format(out_dir_batch))
        system('mkdir -p {}'.format(out_dir_batch))
    
    env = gym.make('esmymo-v0',out_dir=out_dir)
    env     = DummyVecEnv([lambda:env])
    model   = SAC(policy, env,gamma = gamma, verbose=1, tensorboard_log = '../log', policy_kwargs=dict(activation_fn=act_fun, net_arch=dict(pi=layers, qf=layers)), learning_starts=100)
    mymodel = out_dir_batch+"test0"
    model.save(mymodel)
    # SaveNeuralNetwork(model,mymodel+'.dict')
    
    # #--------------- Learning ------------------#
    
    remain_steps = total_timesteps - nb_done * batch_timesteps
    i = nb_done + 1
    
    while remain_steps > 0:
    
        out_dir_batch = out_dir + 'batch{}/'.format(i)    
        
        if not os.path.isdir(out_dir_batch):
            print('Creating out_dir {}'.format(out_dir_batch))
            system('mkdir {}'.format(out_dir_batch))
    
        sys.stdout = open(out_dir_batch+'stdout','w')
    
        it0 = total_timesteps - remain_steps
        env = gym.make('esmymo-v0',out_dir=out_dir)
        env     = DummyVecEnv([lambda:env])
        
        model.set_env(env)
    
        model.learn(batch_timesteps, log_interval=10, reset_num_timesteps = True)
        
        mymodel = out_dir_batch+"test{}".format(i)
        model.save(mymodel)
    
    
        i += 1
        remain_steps -= batch_timesteps
        system('cp {}{}.txt {}'.format(out_dir,'action',out_dir_batch))
        system('cp {}{}.txt {}'.format(out_dir,'observation',out_dir_batch))
        system('cp {}{}.txt {}'.format(out_dir,'reward',out_dir_batch))
    
    
    system('rm {}{}.txt'.format(out_dir,'action'))
    system('rm {}{}.txt'.format(out_dir,'observation'))
    system('rm {}{}.txt'.format(out_dir,'reward'))
    
    if not os.path.isdir(out_dir+ '_batchs'):
        os.makedirs(out_dir+ '_batchs')
    system('cp -R {}batch* {}'.format(out_dir,out_dir+'_batchs'))
    system('rm -R {}batch*'.format(out_dir))

if fill_df:
    nb_batch = len(next(os.walk(out_dir+'_batchs'))[1])-1
    df_learning = rl_esmy_stats.fill_df(out_dir+'_batchs/', df_learning,nb_batch)
    df_learning = df_learning.reset_index().iloc[:,1:]
    df_learning['episode'] = df_learning.index//5+1
    rl_esmy_stats.updated_status_2050(df_learning)
    open_file = open(out_dir+'df_learning_pkl',"wb")
    pkl.dump(df_learning, open_file)
    open_file.close()

if plot:
    
    df_learning = open(out_dir+'df_learning_pkl','rb')
    df_learning = pkl.load(df_learning)
    
    rl_esmy_graphs.pdf_generator(df_learning,out_dir)   
    rl_esmy_graphs.gif(out_dir,'pdf')
    # rl_esmy_graphs.ln_generator(df_learning, out_dir)
    # rl_esmy_graphs.gif(out_dir,'ln')
    
    # rl_esmy_graphs.sp_generator(df_learning, out_dir)
    # rl_esmy_graphs.gif(out_dir,'sp')
    # rl_esmy_graphs.sp_generator(df_learning, out_dir,'stat')
    # rl_esmy_graphs.gif(out_dir,'sp',type_distr='stat')
    
    # rl_esmy_graphs.reward_fig(df_learning,out_dir)
    
    if not os.path.isdir(out_dir+ '_graphs'):
        os.makedirs(out_dir+ '_graphs')
    system('cp {}*.mp4 {}'.format(out_dir,out_dir+'_graphs'))
    system('rm {}*.mp4'.format(out_dir))

# #-------- Removing batch0 directory ----------#

# out_dir_batch = out_dir + 'batch0/'    
# system('rm -r {}'.format(out_dir_batch))


