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
import tensorflow as tf

import gym_esmy
from stable_baselines.sac.policies import MlpPolicy
from stable_baselines.sac.policies import LnMlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import SAC

# from stable_baselines.common.env_checker import check_env
# check_env(env)



#---------------- Defining dict -----------------#

layers_dict = { '16x16'       : [16,16],
                '16x16x16'    : [16,16,16],
                '32x32'       : [32,32],
                '32x32x32'    : [32,32,32],
                '64x64'       : [64,64],
                '64x64x64'    : [64,64,64], 
                '128x128'     : [128,128],
                '128x128x128' : [128,128,128]  } 

policy_dict = { 'Mlp'      : MlpPolicy,
                'LnMlp'    : LnMlpPolicy }


actfun_dict = { 'tanh'     : tf.nn.tanh,
                'sigmoid'  : tf.nn.sigmoid,
                'softplus' : tf.nn.softplus,
                'relu'     : tf.nn.relu       }

rundir = datetime.now()
rundir = rundir.strftime('%Y_%m_%d-%H_%M_%S')


# #--------- Recovering passed arguments ---------#

v = 0
policy = LnMlpPolicy
gamma = 0.3
act_fun = tf.nn.relu
layers = [16,16]
nb_done = 0

if len(sys.argv) > 1:
 
    try:
        v = int(sys.argv[1])
    except:
        v = 0


# #-------- Defining learning variables --------#

total_timesteps = 10000
batch_timesteps = 500    

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
f.write('layers = {}\n'.format(layers))
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

# it0     = 0
# #flag    = 'learn'
# env     = gym.make('bem-v234', v = v, out_dir = out_dir_batch, flag = flag, it0 = it0, nS = nS)
env = gym.make('esmymo-v0',out_dir=out_dir)
env     = DummyVecEnv([lambda:env])
model   = SAC(policy, env,gamma = gamma, verbose=1, tensorboard_log = '../log', policy_kwargs=dict(act_fun=act_fun, layers=layers))
mymodel = out_dir_batch+"test0"
model.save(mymodel)

# #--------------- Learning ------------------#

remain_steps = total_timesteps - nb_done * batch_timesteps
i = nb_done + 1
#flag = 'learn_bf'

while remain_steps > 0:

    out_dir_batch = out_dir + 'batch{}/'.format(i)    
    
    if not os.path.isdir(out_dir_batch):
        print('Creating out_dir {}'.format(out_dir_batch))
        system('mkdir {}'.format(out_dir_batch))

    sys.stdout = open(out_dir_batch+'stdout','w')

    it0 = total_timesteps - remain_steps
    env = gym.make('esmymo-v0',out_dir=out_dir)
    env     = DummyVecEnv([lambda:env])
    model   = SAC.load("{}batch{}/test{}".format(out_dir,i-1, i-1))
    mymodel = out_dir_batch+"test{}".format(i)
    
    model.set_env(env)

    model.learn(batch_timesteps, log_interval=10)
    model.save(mymodel)
    SaveNeuralNetwork(model,mymodel+'.dict')

    i += 1
    remain_steps -= batch_timesteps

# #-------- Removing batch0 directory ----------#

# out_dir_batch = out_dir + 'batch0/'    
# system('rm -r {}'.format(out_dir_batch))


