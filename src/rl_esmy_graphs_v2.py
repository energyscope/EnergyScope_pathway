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

def pdf_generator(df_learning, output_path, type_graph = 'act'):
    list_year = ['2020','2025','2030','2035','2040']
    labels = ['ELECTRICITY', 'GASOLINE', 'DIESEL', 'LFO', 'GAS', 'COAL', 'URANIUM', 'WASTE', 'H2', 'AMMONIA', 'METHANOL', 'Allow fossils','Incent. RE tech']
    clip_dict = {1: [0,1], 2:[0,1], 3:[0,1], 4:[0,1], 5:[0,1], 6:[0,1], 7:[0,1], 8:[0,1], 9:[0,1], 10:[0,1], 11:[0,1], 12:[0,1], 13:[0,0.5]}
    n_act = len([i for i in list(df_learning) if 'act' in i])
    for i in df_learning['batch'].unique():
        data = df_learning.loc[df_learning['batch']<=i]
        if type_graph == 'act':
            fig, axes = plt.subplots(len(list_year), n_act, figsize=(15, 5))
            fig.suptitle('Actions over time and learning - Limit fossil resources & Incentivise RE techs')
            for j in range(n_act):
                for k in df_learning['step'].unique():
                    data_step = data.loc[data['step']==k]
                    ax = axes[k,j]
                    unique = data['status_2050'].unique()
                    palette = dict(zip(unique, sns.color_palette(n_colors=len(unique))))
                    sns.kdeplot(ax=ax,data = data_step,x='act_{}'.format(j+1), hue ='status_2050', palette=palette, legend=False, clip=clip_dict[j+1])
                    ax.set_yticks([])
                    ax.set(xlabel=labels[j],ylabel=list_year[k])
                    ax.label_outer()
            success_rate = round(100*(data['status_2050']=='Success').sum()/len(data.index),1)
            leg = list(palette.keys())
            fig.legend(leg[::-1],loc="upper right")
            plt.figtext(0.5, 0.03, 
                "episodes: {} & rate of success: {}%".format(data['episode'].iloc[-1],success_rate),
                horizontalalignment ="center",
                wrap = True, fontsize = 10, 
                bbox ={'facecolor':'grey', 
                    'alpha':0.3, 'pad':5})
            plt.subplots_adjust(right=0.9)
            plt.savefig(output_path + 'graph_pdf_{}_{}.png'.format(type_graph,i), dpi=300, transparent=True)
            plt.close()
        elif type_graph in ['cum_gwp', 'cum_cost']:
            palette ={"Failure": "C0", "Success": "C1"}
            fig, axes = plt.subplots(5, 2, figsize=(15, 5),sharex='col')
            suptitle = {'cum_gwp': 'Cumulative gwp', 'cum_cost': 'Cumulative cost'}
            fig.suptitle('{} over time and learning'.format(suptitle[type_graph]))
            for j in range(2):
                if j == 0:
                    status_2050 = 'Success'
                else:
                    status_2050 = 'Failure'
                data_status = data.loc[data['status_2050']==status_2050]
                for k in df_learning['step'].unique():
                    data_step = data_status.loc[data_status['step']==k]
                    ax = axes[k,j]
                    # unique = data['status_2050'].unique()
                    # palette = dict(zip(unique, sns.color_palette(n_colors=len(unique))))
                    sns.histplot(ax=ax,data = data_step,x=type_graph,legend=False,color=palette[status_2050])
                    ax.set_yticks([])
                    ax.set(ylabel=list_year[k])
                    ax.label_outer()
            plt.figtext(0.5, 0.03, 
                "episodes: {} & rate of success: {}%".format(data['episode'].iloc[-1],round(100*(data['status_2050']=='Success').sum()/len(data.index),1)),
                horizontalalignment ="center",
                wrap = True, fontsize = 10, 
                bbox ={'facecolor':'grey', 
                    'alpha':0.3, 'pad':5})
            leg = list(palette.keys())
            fig.legend(leg[::-1],loc="upper right")
            plt.subplots_adjust(right=0.9)
            plt.savefig(output_path + 'graph_pdf_{}_{}.png'.format(type_graph,i), dpi=300, transparent=True)
            plt.close()

def reward_fig(df_learning, output_path):
    n_episode = df_learning['episode'].iloc[-1]
    temp = df_learning.groupby(['episode']).sum()
    reward = temp['reward']
    r_average = reward.rolling(window=int(n_episode/20)).mean()
    plt.figure(figsize=(10, 5))
    plt.plot(reward, 'k-', label="Reward")
    plt.plot(r_average, 'r-', label="Rolling average")
    plt.legend()
    plt.savefig(output_path + '_graphs/reward.png', dpi=300, transparent=True)
    plt.close()

def gif(output_path, type_graph, type_distr = 'cum'):
        if type_graph in ['sp','kde']:
            for i in range(5):
                output_dir = output_path + 'step_{}/'.format(i)
                cmd = 'ffmpeg -r 5 -i {} -vcodec mpeg4 -y {}mov_step_'+type_graph+'_{}_{}.mp4'
                cmd = cmd.format(output_dir+'graph_'+type_graph+'_%01d.png',output_path,i,type_distr)
                os.system(cmd)
                shutil.rmtree(output_dir)
        elif type_graph in ['ln_act','pdf_act','pdf_cum_gwp', 'pdf_cum_cost']:
            cmd = 'ffmpeg -r 5 -i {} -vcodec mpeg4 -y {}mov_'+type_graph+'.mp4'
            cmd = cmd.format(output_path+'graph_'+type_graph+'_%01d.png',output_path)
            os.system(cmd)
            system('rm {}*.png'.format(output_path))

        
def ln_generator(df_learning, output_path, type_graph = 'act'):
    list_year = ['2020','2025','2030','2035','2040']
    sectors = ['ELECTRICITY','HEAT_HIGH_T','HEAT_LOW_T','MOBILITY_PASSENGER','MOBILITY_FREIGHT','NON_ENERGY']
    palette ={"Failure": "C0", "Success": "C1", "Failure_imp": "C2"}
    n_act = len([i for i in list(df_learning) if 'act' in i])
    for j in df_learning['batch'].unique():
        data = df_learning.loc[df_learning['batch']<=j]
        if type_graph == 'act':
            fig, axes = plt.subplots(n_act, 1, figsize=(15, 5), sharex=True)
            fig.suptitle('Actions over time and learning - Limit energy consumption')
            for i in range(n_act):
                sns.lineplot(ax=axes[i],data = data,x='step', y='act_{}'.format(i+1), markers=True, dashes=False, hue ='status_2050',palette=palette)
                axes[i].set_title(sectors[i])
                axes[i].get_legend().remove()
                axes[i].set_ylim([0,1])
                fig.legend(['Failure','Success'],loc="upper right")
                plt.subplots_adjust(right=0.9)
                plt.xticks(range(len(list_year)),list_year)
                plt.xlabel('Time of decision making')
                plt.savefig(output_path + 'graph_ln_act_{}.png'.format(j), dpi=300, transparent=True)
            plt.close()
    
