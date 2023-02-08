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
    # labels = ['ELECTRICITY', 'COAL', 'GAS', 'LFO','H2', 'METHANOL', 'Incent. RE tech']
    labels = ['Allow some fossil fuels', 'Allow other fossil fuels', 'Incent. RE tech']
    # clip_dict = {1: [0,1], 2:[0,1], 3:[0,1], 4:[0,1], 5:[0,1], 6:[0,1], 7:[0,0.5]}
    clip_dict = {1: [0,1], 2: [0,1], 3:[0,0.5]}
    n_act = len([i for i in list(df_learning) if 'act' in i])
    obs = ['RE_in_mix','Energy_efficiency']
    n_obs = len(obs)
    # clip_obs = [None] * n_obs
    # for j in range(n_obs):
    #     clip_obs[j] = [min(df_learning[obs[j]]),max(df_learning[obs[j]])]
    xticks = [[[0,1]]+[[0,1]]+[[0,0.5]]]
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
                    sns.kdeplot(ax=ax,data = data_step,x='act_{}'.format(j+1), hue ='status_2050', palette=palette, legend=False, clip=xticks[0][j])
                    ax.set_yticks([])
                    ax.set_xticks(xticks[0][j])
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
        elif type_graph == 'obs':
            list_year = ['2020','2025','2030','2035','2040','2045','2050']
            fig, axes = plt.subplots(len(list_year), n_obs, figsize=(15, 15))
            fig.suptitle('States over time and learning')
            unique = data['status_2050'].unique()
            palette = dict(zip(unique, sns.color_palette(n_colors=len(unique))))
            for j in range(n_obs):
                # clip = clip_obs[j]
                for k in df_learning['step'].unique():
                    if k == max(df_learning['step']):
                        m = [k, k+1, k+2]
                    else:
                        m = [k]
                    data_step = data.loc[data['step']==k]
                    for n in m:
                        ax = axes[n,j]
                        # sns.kdeplot(ax=ax,data = data_step,x=obs[j], hue ='status_2050', palette=palette, legend=False, clip = [0,1])
                        sns.histplot(ax=ax,data = data_step,x=obs[j]+'_{}'.format(list_year[n]),multiple="stack", hue ='status_2050',binwidth=0.05, palette=palette, legend=False)
                        # ax.set_xlim(clip)
                        ax.set_xlim([0,1])
                        ax.set_yticks([])
                    # ax.set_xticks([0,1])
                        ax.set(xlabel=obs[j],ylabel=list_year[n])
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

def reward_fig_plus(df_learning, output_path):
    data = df_learning.loc[df_learning['reward'] != 0]
    data_complete = data.loc[data['step'] == 4]

    low = min(data['reward'])
    high = max(data['reward'])

    data['reward_scaled'] = 2.0 * ((data['reward'] - low) / (high-low)) - 1.0

    sns.relplot(data = data, x='cum_gwp',y='cum_cost',hue='status_2050')
    plt.savefig(output_path + '_graphs/gwp_cost_rew_status.png', dpi=300, transparent=False)
    plt.close()
    sns.relplot(data = data, x='episode',y='reward',hue='status_2050')
    plt.ylim(-50, 110)
    plt.savefig(output_path + '_graphs/reward_ep_scat_FC.png', dpi=300, transparent=False)
    plt.close()

    sns.relplot(data = data, x='episode',y='reward_scaled',hue='status_2050')
    plt.savefig(output_path + '_graphs/reward_ep_scat_FC_scaled.png', dpi=300, transparent=False)
    plt.close()

    cum_gwp = list(data['cum_gwp'])
    cum_cost = list(data['cum_cost'])

    cum_gwp_complete = list(data_complete['cum_gwp'])
    cum_cost_complete = list(data_complete['cum_cost'])

    sorted_list = sorted([[cum_gwp[i], cum_cost[i]] for i in range(len(cum_gwp))], reverse = False)
    pareto_front = [sorted_list[0]]

    sorted_list_complete = sorted([[cum_gwp_complete[i], cum_cost_complete[i]] for i in range(len(cum_gwp_complete))], reverse = False)
    pareto_front_complete = [sorted_list_complete[0]]


    for pair in sorted_list[1:]:
        if pair[1] <= pareto_front[-1][1]:
                    pareto_front.append(pair)

    pf_X = [pair[0] for pair in pareto_front]
    pf_Y = [pair[1] for pair in pareto_front]


    for pair_complete in sorted_list_complete[1:]:
        if pair_complete[1] <= pareto_front_complete[-1][1]:
                    pareto_front_complete.append(pair_complete)

    pf_X_complete = [pair_complete[0] for pair_complete in pareto_front_complete]
    pf_Y_complete = [pair_complete[1] for pair_complete in pareto_front_complete]

    fig= plt.figure()
    sns.relplot(data = data,x = 'cum_gwp', y = 'cum_cost', hue = 'step',size='reward')
    # plt.plot(pf_X, pf_Y, color = 'orange',linewidth=5)
    plt.savefig(output_path + '_graphs/gwp_cost_rew_pareto.png', dpi=300, transparent=False)
    plt.close()

    fig= plt.figure()
    sns.relplot(data = data,x = 'cum_gwp', y = 'cum_cost', hue = 'step',size='reward')
    # plt.plot(pf_X, pf_Y, color = 'orange',linewidth=5)
    plt.plot(pf_X_complete, pf_Y_complete, color = 'orange',linewidth=5)
    plt.ylim(0.9*min(pf_Y), 1576611.3990000002)
    plt.savefig(output_path + '_graphs/gwp_cost_rew_pareto_zoom.png', dpi=300, transparent=False)
    plt.close()


def gif(output_path, type_graph, type_distr = 'cum'):
        if type_graph in ['sp','kde']:
            for i in range(5):
                output_dir = output_path + 'step_{}/'.format(i)
                cmd = 'ffmpeg -r 5 -i {} -vcodec mpeg4 -y {}mov_step_'+type_graph+'_{}_{}.mp4'
                cmd = cmd.format(output_dir+'graph_'+type_graph+'_%01d.png',output_path,i,type_distr)
                os.system(cmd)
                shutil.rmtree(output_dir)
        elif type_graph in ['ln_act','pdf_act','pdf_cum_gwp', 'pdf_cum_cost','pdf_obs']:
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
    
