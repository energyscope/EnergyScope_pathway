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

def sp_generator(df_learning, output_path, type_distr = 'cum'):
    dict_year = {0:'2020',1:'2025',2:'2030',3:'2035',4:'2040'}
    palette ={"Failure": "C0", "Success": "C1"}
    for i in df_learning['step'].unique():
        data_1 = df_learning.loc[df_learning['step']==i]
        if not os.path.isdir(output_path + 'step_{}'.format(i)):
                os.makedirs(output_path + 'step_{}'.format(i))
        for j in df_learning['batch'].unique():
            if type_distr == 'cum':
                data = data_1.loc[df_learning['batch']<=j]
            else:
                data = data_1.loc[df_learning['batch']==j]
            g = sns.JointGrid(data = data,x='act_1', y='act_2',xlim=(0,1), ylim=(0,0.5), hue ='status_2050',palette=palette)
            g.plot_joint(sns.scatterplot, s=100, alpha=.5)
            g.plot_marginals(sns.histplot, kde=True)
            g.fig.suptitle('Actions taken in {}'.format(dict_year[i]))
            g.ax_joint.set_xlabel('Allow fossil fuels')
            g.ax_joint.set_ylabel('Incentivize RE tech')
            sns.move_legend(g.ax_joint, "upper right", title='Status episode', frameon=True)
            g.savefig(output_path + 'step_{}/graph_sp_{}.png'.format(i,j))
        


def ln_generator(df_learning, output_path):
    dict_year = {0:'2020',1:'2025',2:'2030',3:'2035',4:'2040'}
    list_year = ['2020','2025','2030','2035','2040']
    palette ={"Failure": "C0", "Success": "C1"}
    for j in df_learning['batch'].unique():
        fig, axes = plt.subplots(2, 1, figsize=(15, 5), sharex=True)
        fig.suptitle('Actions over time and learning')
        data = df_learning.loc[df_learning['batch']<=j]
        sns.lineplot(ax=axes[0],data = data,x='step', y='act_1', markers=True, dashes=False, hue ='status_2050',palette=palette)
        axes[0].set_title('Allow fossil fuels')
        axes[0].get_legend().remove()
        axes[0].set_ylim([0,1])
        axes[0]
        sns.lineplot(ax=axes[1],data = data,x='step', y='act_2',markers=True, dashes=False, hue ='status_2050',palette=palette)
        axes[1].set_title('Incentivize RE tech')
        axes[1].get_legend().remove()
        axes[1].set_ylim([0,0.5])
        fig.legend(['Success','Failure'],loc="upper right")
        plt.subplots_adjust(right=0.9)
        plt.xticks(range(len(list_year)),list_year)
        plt.xlabel('Time of decision making')
        plt.savefig(output_path + 'graph_ln_{}.png'.format(j))
        plt.close()

def pdf_generator(df_learning, output_path):
    list_year = ['2020','2025','2030','2035','2040']
    palette ={"Failure": "C0", "Success": "C1"}
    clip_dict = {1:[0,1], 2:[0,0.5]}
    x_dict = {1:'Allow fossil fuels', 2: 'Incentivize RE tech'}
    for i in df_learning['batch'].unique():
        fig, axes = plt.subplots(5, 2, figsize=(15, 5))
        fig.suptitle('Actions over time and learning')
        data = df_learning.loc[df_learning['batch']<=i]
        for j in range(1,3):
            for k in df_learning['step'].unique():
                data_step = data.loc[data['step']==k]
                ax = axes[k,j-1]
                sns.kdeplot(ax=ax,data = data_step,x='act_{}'.format(j), hue ='status_2050',palette=palette, legend=False, clip=clip_dict[j])
                ax.set_yticks([])
                ax.set(xlabel=x_dict[j],ylabel=list_year[k])
                ax.label_outer()
        plt.figtext(0.5, 0.03, 
            "episodes: {}".format(data_step['episode'].iloc[-1]),
            horizontalalignment ="center",
            wrap = True, fontsize = 10, 
            bbox ={'facecolor':'grey', 
                   'alpha':0.3, 'pad':5})
        fig.legend(['Success','Failure'],loc="upper right")
        plt.subplots_adjust(right=0.9)
        plt.savefig(output_path + 'graph_pdf_{}.png'.format(i))
        plt.close()

def reward_fig(df_learning, output_path):
    n_episode = df_learning['episode'].iloc[-1]
    temp = df_learning.groupby(['episode']).sum()
    reward = temp['reward']
    r_average = reward.rolling(window=int(n_episode/10)).mean()
    plt.figure(figsize=(10, 5))
    plt.plot(reward, 'k-', label="Reward")
    plt.plot(r_average, 'r-', label="Rolling average")
    plt.legend()
    plt.savefig(output_path + '/_graphs/reward.png')
    plt.close()


    
def gif(output_path, type_graph, type_distr = 'cum'):
        if type_graph == 'sp':
            for i in range(5):
                output_dir = output_path + 'step_{}/'.format(i)
                cmd = 'ffmpeg -r 5 -i {} -vcodec mpeg4 -y {}mov_step_'+type_graph+'_{}_{}.mp4'
                cmd = cmd.format(output_dir+'graph_'+type_graph+'_%01d.png',output_path,i,type_distr)
                os.system(cmd)
                shutil.rmtree(output_dir)
        elif type_graph in ['ln','pdf']:
            cmd = 'ffmpeg -r 5 -i {} -vcodec mpeg4 -y {}mov_'+type_graph+'.mp4'
            cmd = cmd.format(output_path+'graph_'+type_graph+'_%01d.png',output_path)
            os.system(cmd)
            system('rm {}*.png'.format(output_path))