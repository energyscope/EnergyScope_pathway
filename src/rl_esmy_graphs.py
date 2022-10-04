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
import matplotlib.pyplot as plt
import imageio
import shutil
import seaborn as sns

pylibPath = os.path.abspath("../pylib")    # WARNING ! pwd is where the MAIN file was launched !!!

if pylibPath not in sys.path:
    sys.path.insert(0, pylibPath)

def hm_generator(dict_ep, output_path, i, output_type):

    if output_type == 'action':
        for k in dict_ep:
            if not os.path.isdir(output_path + 'step_{}'.format(k)):
                os.makedirs(output_path + 'step_{}'.format(k))
            plt.figure(k)
            plt.imshow(dict_ep[k].T, extent = [0,1,0,0.5], interpolation="quadric")
            plt.savefig(output_path + 'step_{}/graph_hm_{}.png'.format(k,i))
            plt.close()        

def sp_generator(df_learning, output_path):
    # for i in df_learning['batch'].unique():
    # data = df_learning.loc[df_learning['batch']==i]
    # data = df_learning
    # fig, axes = plt.subplots(1,5,figsize=(15,5),sharey=True)
    for i in df_learning['step'].unique():
        data_1 = df_learning.loc[df_learning['step']==i]
        if not os.path.isdir(output_path + 'step_{}'.format(i)):
                os.makedirs(output_path + 'step_{}'.format(i))
        for j in df_learning['batch'].unique():
            data = data_1.loc[df_learning['batch']<=j]
            # g = sns.JointGrid(ax=axes[j],data = data,x='act_1', y='act_2',xlim=(0,1), ylim=(0,0.5), hue ='status_2050')
            g = sns.JointGrid(data = data,x='act_1', y='act_2',xlim=(0,1), ylim=(0,0.5), hue ='status_2050')
            g.plot_joint(sns.scatterplot, s=100, alpha=.5)
            g.plot_marginals(sns.histplot, kde=True)
            g.savefig(output_path + 'step_{}/graph_sp_{}.png'.format(i,j))
        
        
    
def gif(output_path, type_graph, output_type = 'action'):
    if output_type == 'action':
        for i in range(5):
            output_dir = output_path + 'step_{}/'.format(i)
            cmd = 'ffmpeg -r 10 -i {} -vcodec mpeg4 -y {}/mov_step_'+type_graph+'_{}.mp4'
            cmd = cmd.format(output_dir+'graph_'+type_graph+'_%01d.png',output_path,i)
            os.system(cmd)
            shutil.rmtree(output_dir)