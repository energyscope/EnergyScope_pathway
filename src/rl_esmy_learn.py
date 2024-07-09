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

print("About to import RL modules")
import gym
import gym_esmy
import torch
import pandas as pd
import pickle as pkl
import shutil
import sobol

import rl_esmy_stats
import rl_esmy_graphs_v0
import rl_esmy_graphs_v01
import rl_esmy_graphs_v1
import rl_esmy_graphs_v2
import rl_esmy_graphs_v21
import rl_esmy_graphs_v3
import rl_esmy_graphs_v31
import rl_esmy_graphs_v32
import rl_esmy_graphs_v4
import rl_esmy_graphs_v41
import rl_esmy_graphs_v5
import rl_esmy_graphs_v6
import rl_esmy_graphs_v7
import rl_esmy_graphs_v8
import rl_esmy_graphs_v9
import rl_esmy_graphs_v10
import rl_esmy_graphs_v10_ses
import rl_esmy_graphs_v11
import rl_esmy_graphs_v12
import rl_esmy_graphs_v14
from stable_baselines3.sac.policies import SACPolicy
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.sac import SAC

#---------------- Defining dict -----------------#


# #--------- Recovering passed arguments ---------#

v = '14'
policy = 'MlpPolicy'

gamma = 1
act_fun = torch.nn.modules.activation.ReLU
# layers = [16,16]
layers = [128,128,128]

# #-------- Defining learning variables --------#

total_timesteps = 500
batch_timesteps = 500

# rundir = '2024_03_12-15_45_05'

type_of_model = 'MO'
rundir = '2024_04_10-15_15_54'

# V14
type_of_model = 'MO'
rundir = '2024_05_01-19_52_38'

# type_of_model = 'TD'
# rundir = '2024_03_25-17_04_35'
out_dir = '../out/learn_v{}/{}_{}/'.format(v,rundir,type_of_model)

learning_from_scratch = False
keep_on_learning = False
fill_df = True
plot = True
gater_results_ES = False

if learning_from_scratch:
    nb_done = 0
    rundir = datetime.now()
    rundir = rundir.strftime('%Y_%m_%d-%H_%M_%S')

    nbatches = int(np.ceil(total_timesteps/batch_timesteps))
    
    # ##  
    # ##  #------- Defining output directories --------#
    # ##   
    out_dir = '../out/learn_v{}/{}_{}/'.format(v,rundir,type_of_model)
    
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
    
    env = gym.make('esmy-v{}'.format(v),out_dir=out_dir, v=v, type_of_model=type_of_model, nb_done=nb_done,out_dir_batch=out_dir_batch, new_step_api=False)
    env     = DummyVecEnv([lambda:env])
    model   = SAC(policy, env,gamma = gamma, verbose=1, tensorboard_log = '../log', policy_kwargs=dict(activation_fn=act_fun, net_arch=dict(pi=layers, qf=layers)), learning_starts=100)
    mymodel = out_dir_batch+"test0"
    model.save(mymodel)
    # SaveNeuralNetwork(model,mymodel+'.dict')
    
    # #--------------- Learning ------------------#
    
    remain_steps = total_timesteps - nb_done * batch_timesteps
    i = nb_done + 1
    
    txt_files = []
    while remain_steps > 0:
    
        out_dir_batch = out_dir + 'batch{}/'.format(i)    
        
        if not os.path.isdir(out_dir_batch):
            print('Creating out_dir {}'.format(out_dir_batch))
            system('mkdir {}'.format(out_dir_batch))
    
        sys.stdout = open(out_dir_batch+'stdout','w')
    
        it0 = total_timesteps - remain_steps

        env = gym.make('esmy-v{}'.format(v),out_dir=out_dir, v=v, type_of_model=type_of_model,nb_done=nb_done,out_dir_batch=out_dir_batch, new_step_api=False)
        
        env = DummyVecEnv([lambda:env])
        
        model.set_env(env)
    
        model.learn(batch_timesteps, log_interval=10, reset_num_timesteps = True, tb_log_name='SAC_v{}_{}'.format(v,rundir))
        
        mymodel = out_dir_batch+"test{}".format(i)
        model.save(mymodel)
    
    
        i += 1
        remain_steps -= batch_timesteps
        lst_files = os.listdir(out_dir)
        txt_files = [x for x in lst_files if x.endswith('.txt')]
        txt_files.remove('set_up.txt')
        if 'READ_ME.txt' in txt_files:
            txt_files.remove('READ_ME.txt')
        for f in txt_files:
            system('cp {}{} {}'.format(out_dir,f,out_dir_batch))
        system('cp {}{}.txt {}'.format(out_dir,'action',out_dir_batch))
        system('cp {}{}.txt {}'.format(out_dir,'observation',out_dir_batch))
        system('cp {}{}.txt {}'.format(out_dir,'reward',out_dir_batch))
        
        nb_done+=1
    
    
    for f in txt_files:
        system('rm {}{}'.format(out_dir,f))
    
    if not os.path.isdir(out_dir+ '_batchs'):
        os.makedirs(out_dir+ '_batchs')
    system('cp -R {}batch* {}'.format(out_dir,out_dir+'_batchs'))
    system('rm -R {}batch*'.format(out_dir))


if keep_on_learning:
    
    batches_dir = out_dir+'_batchs/'
    err_msg = 'There are no batches yet'
    assert os.path.isdir(batches_dir), err_msg

    nb_done = len(next(os.walk(batches_dir))[1])-1
    
    remain_steps = total_timesteps
    i = nb_done + 1
    
    out_dir_batch = out_dir + 'batch{}/'.format(i)
    
    mymodel = batches_dir+'batch{}/test{}'.format(nb_done,nb_done)
    
    # env = gym.make('esmymo-v{}'.format(v),out_dir=out_dir, v=v, new_step_api=False)
    env = gym.make('esmy-v{}'.format(v),out_dir=out_dir, v=v,type_of_model=type_of_model,nb_done=nb_done,out_dir_batch=out_dir_batch,new_step_api=False)
    # env     = DummyVecEnv([lambda:env])
    model   = SAC(policy, env,gamma = gamma, verbose=1, tensorboard_log = '../log', policy_kwargs=dict(activation_fn=act_fun, net_arch=dict(pi=layers, qf=layers)), learning_starts=100)
    # model = SAC.load(mymodel, env=env)
    model.load(mymodel, env=env)
    
    txt_files = []
    while remain_steps > 0:
    
        out_dir_batch = out_dir + 'batch{}/'.format(i)    
        
        if not os.path.isdir(out_dir_batch):
            print('Creating out_dir {}'.format(out_dir_batch))
            system('mkdir {}'.format(out_dir_batch))
    
        sys.stdout = open(out_dir_batch+'stdout','w')
    
        it0 = total_timesteps - remain_steps
        # env = gym.make('esmymo-v{}'.format(v),out_dir=out_dir, v=v, new_step_api=False)
        env = gym.make('esmy-v{}'.format(v),out_dir=out_dir, v=v,type_of_model=type_of_model,nb_done=nb_done,out_dir_batch=out_dir_batch, new_step_api=False)
        
        env     = DummyVecEnv([lambda:env])
        
        model.set_env(env)
    
        model.learn(batch_timesteps, log_interval=10, reset_num_timesteps = True)
        
        mymodel = out_dir_batch+"test{}".format(i)
        model.save(mymodel)
    
    
        i += 1
        remain_steps -= batch_timesteps
        lst_files = os.listdir(out_dir)
        txt_files = [x for x in lst_files if x.endswith('.txt')]
        txt_files.remove('set_up.txt')
        if 'READ_ME.txt' in txt_files:
            txt_files.remove('READ_ME.txt')
        for f in txt_files:
            system('cp {}{} {}'.format(out_dir,f,out_dir_batch))
        system('cp {}{}.txt {}'.format(out_dir,'action',out_dir_batch))
        system('cp {}{}.txt {}'.format(out_dir,'observation',out_dir_batch))
        system('cp {}{}.txt {}'.format(out_dir,'reward',out_dir_batch))
    
        nb_done += 1
    for f in txt_files:
        system('rm {}{}'.format(out_dir,f))
    
    if not os.path.isdir(out_dir+ '_batchs'):
        os.makedirs(out_dir+ '_batchs')
    system('cp -R {}batch* {}'.format(out_dir,batches_dir))
    system('rm -R {}batch*'.format(out_dir))
    

if fill_df:
    env = gym.make('esmy-v{}'.format(v),out_dir=out_dir, v=v,type_of_model=type_of_model, new_step_api=False)
    # lst_files = os.listdir(out_dir)
    # txt_files = [x for x in lst_files if x.endswith('.txt')]
    # txt_files.remove('set_up.txt')
    # if 'READ_ME.txt' in txt_files:
    #     txt_files.remove('READ_ME.txt')
    # for f in txt_files:
    #     system('rm {}{}'.format(out_dir,f))
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
    df_learning = pd.DataFrame(columns=columns)
    nb_batch = len(next(os.walk(out_dir+'_batchs'))[1])-1
    df_learning = rl_esmy_stats.fill_df_learning(out_dir+'_batchs/', df_learning, nb_batch)
    df_learning = df_learning.reset_index().iloc[:,1:]
    df_learning = rl_esmy_stats.updated_status_2050_learning(df_learning)
    open_file = open(out_dir+'df_learning_pkl',"wb")
    pkl.dump(df_learning, open_file)
    open_file.close()

if plot:
    env = gym.make('esmy-v{}'.format(v),out_dir=out_dir, v=v,type_of_model=type_of_model,new_step_api=False)
    # lst_files = os.listdir(out_dir)
    # txt_files = [x for x in lst_files if x.endswith('.txt')]
    # txt_files.remove('set_up.txt')
    # if 'READ_ME.txt' in txt_files:
    #     txt_files.remove('READ_ME.txt')
    # for f in txt_files:
    #     system('rm {}{}'.format(out_dir,f))
    
    df_learning = open(out_dir+'df_learning_pkl','rb')
    df_learning = pkl.load(df_learning)
    
    switcher = {'0':rl_esmy_graphs_v0,
                '01':rl_esmy_graphs_v01,
                '1':rl_esmy_graphs_v1,
                '2':rl_esmy_graphs_v2,
                '21':rl_esmy_graphs_v21,
                '3':rl_esmy_graphs_v3,
                '31':rl_esmy_graphs_v31,
                '32':rl_esmy_graphs_v32,
                '4':rl_esmy_graphs_v4,
                '41':rl_esmy_graphs_v41,
                '5':rl_esmy_graphs_v5,
                '6':rl_esmy_graphs_v6,
                '7':rl_esmy_graphs_v7,
                '8':rl_esmy_graphs_v8,
                '9':rl_esmy_graphs_v9,
                '10':rl_esmy_graphs_v10,
                '10_ses':rl_esmy_graphs_v10_ses,
                '11':rl_esmy_graphs_v11,
                '12':rl_esmy_graphs_v12,
                '14':rl_esmy_graphs_v14}
    v = '11'
    grph_mth = switcher.get(str(v))
    
    if not os.path.isdir(out_dir+ '_graphs'):
        os.makedirs(out_dir+ '_graphs')
    
    
    # grph_mth.reward_plus_plus(df_learning,out_dir,env,type_graph='act')
    # grph_mth.gif(out_dir, type_graph='pdf_rew_act')
    
    # grph_mth.reward_plus_plus(df_learning,out_dir,env,type_graph='cost_gwp')
    # grph_mth.gif(out_dir, type_graph='pdf_rew_cost_gwp') 
    
    grph_mth.pdf_generator(df_learning,out_dir, env, type_graph='act')
    # grph_mth.gif(out_dir, type_graph='pdf_act')
    
    grph_mth.pdf_generator(df_learning,out_dir, env, type_graph='act_binding')
    # grph_mth.gif(out_dir, type_graph='pdf_act_binding')
    
    # grph_mth.pdf_generator(df_learning,out_dir, env, type_graph='act_plus')
    # grph_mth.gif(out_dir, type_graph='pdf_act_plus')    
    
    # grph_mth.pdf_generator(df_learning,out_dir, env, type_graph='cum_gwp')
    # grph_mth.gif(out_dir,'pdf_cum_gwp')

    # grph_mth.pdf_generator(df_learning,out_dir, env, type_graph='cum_cost')
    # grph_mth.gif(out_dir,'pdf_cum_cost')
    
    grph_mth.pdf_generator(df_learning,out_dir,env, type_graph='obs')
    # grph_mth.gif(out_dir,'pdf_obs')
    
    grph_mth.pdf_generator(df_learning,out_dir,env, type_graph='cost_gwp')
    # grph_mth.gif(out_dir,'pdf_cost_gwp')
    
    # grph_mth.reward_fig_plus(df_learning,out_dir)
    
    # grph_mth.reward_fig(df_learning,out_dir)
    
    # rl_esmy_graphs.sp_generator(df_learning, out_dir)
    # rl_esmy_graphs.gif(out_dir,'sp')
    
    # rl_esmy_graphs.sp_generator(df_learning, out_dir,'stat')
    # rl_esmy_graphs.gif(out_dir,'sp',type_distr='stat')
    
    # rl_esmy_graphs.kde_generator(df_learning, out_dir)
    # rl_esmy_graphs.gif(out_dir,'kde')
    
    
    system('cp {}*.mp4 {}'.format(out_dir,out_dir+'_graphs'))
    system('rm {}*.mp4'.format(out_dir))

# #-------- Removing batch0 directory ----------#

# out_dir_batch = out_dir + 'batch0/'    
# system('rm -r {}'.format(out_dir_batch))

if gater_results_ES:
    rl_esmy_stats.gather_results_ES(out_dir)
    


