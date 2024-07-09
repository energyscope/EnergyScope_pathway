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
import pandas as pd

pylibPath = os.path.abspath("../pylib")    # WARNING ! pwd is where the MAIN file was launched !!!

if pylibPath not in sys.path:
    sys.path.insert(0, pylibPath)     

def pdf_generator(df_learning, output_path, env, type_graph = 'act'):
    list_year = ['2020','2025','2030','2035','2040']
    # labels = ['Gwp limit for 5 years later', 'Gwp limit for 10 years later', 'Gas limit','LFO limit','Coal limit']
    labels = ['Gwp limit for 10 years later', 'Gas limit','LFO limit','Coal limit','GWP tax']
    n_act = len(labels)
    obs = ['RE_in_mix','Energy_efficiency']
    n_obs = len(obs)
    xticks = list(zip(env.action_space.low,env.action_space.high))
    for i in df_learning['batch'].unique():
        data = df_learning.loc[df_learning['batch']<=i]
        # data = df_learning.loc[df_learning['batch']==i]
        if type_graph == 'act':
            unique = sorted(df_learning['status_2050'].unique())
            palette_full = dict(zip(unique, sns.color_palette(n_colors=len(unique))))
            fig, axes = plt.subplots(len(list_year), n_act, figsize=(15, 5),sharex='col')
            fig.suptitle('Actions over time and learning')
            for j in range(n_act):
                for k in df_learning['step'].unique():
                    data_step = data.loc[data['step']==k]
                    ax = axes[k,j]
                    # unique = data['status_2050'].unique()
                    unique = sorted(data['status_ep'].unique())
                    # palette = dict(zip(unique, sns.color_palette(n_colors=len(unique))))
                    palette = {key: value for key, value in palette_full.items() if key in unique}
                    # sns.kdeplot(ax=ax,data = data_step,x='act_{}'.format(j+1), hue ='status_2050', palette=palette, legend=False, clip=xticks[j],multiple='stack')
                    sns.kdeplot(ax=ax,data = data_step,x='act_{}'.format(j+1), hue ='status_2050', palette=palette_full, legend=False, clip=xticks[j],multiple='stack')
                    ax.set_yticks([])
                    ax.set_xticks(xticks[j])
                    ax.set(xlabel=labels[j],ylabel=list_year[k])
                    ax.label_outer()
            success_rate = round(100*(data['status_2050']=='Success').sum()/len(data.index),1)
            # leg = list(palette.keys())
            # fig.legend(leg[::-1],loc="upper right")
            markers = [plt.Line2D([0,0],[0,0],color=color, marker='o', linestyle='') for color in palette_full.values()]
            fig.legend(markers, palette_full.keys(), numpoints=1,loc='upper right')
            # fig.legend(handles_leg, labels_leg, loc='upper right')
            plt.figtext(0.5, 0.91, 
                "batch: {} & rate of success: {}%".format(i,success_rate),
                horizontalalignment ="center",
                wrap = True, fontsize = 10, 
                bbox ={'facecolor':'grey', 
                    'alpha':0.3, 'pad':5})
            plt.subplots_adjust(right=0.9)
            plt.savefig(output_path + 'graph_pdf_{}_{}.png'.format(type_graph,i), dpi=300, transparent=True)
            plt.close()
        elif type_graph == 'act_plus':
            unique = sorted(df_learning['status_ep'].unique())
            palette_full = dict(zip(unique, sns.color_palette(n_colors=len(unique))))
            fig, axes = plt.subplots(len(list_year), n_act, figsize=(15, 5),sharex='col')
            fig.suptitle('Actions over time and learning')
            for j in range(n_act):
                for k in df_learning['step'].unique():
                    data_step = data.loc[data['step']==k]
                    ax = axes[k,j]
                    # unique = data['status_2050'].unique()
                    unique = sorted(data['status_ep'].unique())
                    # palette = dict(zip(unique, sns.color_palette(n_colors=len(unique))))
                    palette = {key: value for key, value in palette_full.items() if key in unique}
                    # sns.kdeplot(ax=ax,data = data_step,x='act_{}'.format(j+1), hue ='status_2050', palette=palette, legend=False, clip=xticks[j],multiple='stack')
                    sns.kdeplot(ax=ax,data = data_step,x='act_{}'.format(j+1), hue ='status_ep', palette=palette_full, legend=False, clip=xticks[j],multiple='stack')
                    ax.set_yticks([])
                    ax.set_xticks(xticks[j])
                    ax.set(xlabel=labels[j],ylabel=list_year[k])
                    ax.label_outer()
            success_rate = round(100*(data['status_2050']=='Success').sum()/len(data.index),1)
            # leg = list(palette.keys())
            # fig.legend(leg[::-1],loc="upper right")
            markers = [plt.Line2D([0,0],[0,0],color=color, marker='o', linestyle='') for color in palette_full.values()]
            fig.legend(markers, palette_full.keys(), numpoints=1,loc='upper right')
            # fig.legend(handles_leg, labels_leg, loc='upper right')
            plt.figtext(0.5, 0.91, 
                "batch: {} & rate of success: {}%".format(i,success_rate),
                horizontalalignment ="center",
                wrap = True, fontsize = 10, 
                bbox ={'facecolor':'grey', 
                    'alpha':0.3, 'pad':5})
            plt.subplots_adjust(right=0.9)
            plt.savefig(output_path + 'graph_pdf_{}_{}.png'.format(type_graph,i), dpi=300, transparent=True)
            plt.close()
        elif type_graph in ['cum_gwp', 'cum_cost']:
            list_year = ['2030','2035','2040','2045','2050']
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
            success_rate = round(100*(data['status_2050']=='Success').sum()/len(data.index),1)
            plt.figtext(0.5, 0.91, 
                "batch: {} & rate of success: {}%".format(i,success_rate),
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
            fig, axes = plt.subplots(len(list_year), n_obs, figsize=(15, 15),sharex='col')
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
            plt.figtext(0.5, 0.91, 
                "batch: {} & rate of success: {}%".format(i,success_rate),
                horizontalalignment ="center",
                wrap = True, fontsize = 10, 
                bbox ={'facecolor':'grey', 
                    'alpha':0.3, 'pad':5})
            plt.subplots_adjust(right=0.9)
            plt.savefig(output_path + 'graph_pdf_{}_{}.png'.format(type_graph,i), dpi=300, transparent=True)
            plt.close()
        elif type_graph == 'act_binding':
            unique = sorted(df_learning['binding_1'].unique())
            palette_full = dict(zip(unique, sns.color_palette(n_colors=len(unique))))
            fig, axes = plt.subplots(len(list_year), n_act-1, figsize=(15, 5),sharex='col')
            fig.suptitle('Actions over time and learning')
            for j in [0,1,2,3]:
                for k in df_learning['step'].unique():
                    data_step = data.loc[(data['step']==k) & (data['status_2050']=='Success')]
                    ax = axes[k,j]
                    # unique = data['status_2050'].unique()
                    unique = sorted(data['status_ep'].unique())
                    # palette = dict(zip(unique, sns.color_palette(n_colors=len(unique))))
                    palette = {key: value for key, value in palette_full.items() if key in unique}
                    # sns.kdeplot(ax=ax,data = data_step,x='act_{}'.format(j+1), hue ='status_2050', palette=palette, legend=False, clip=xticks[j],multiple='stack')
                    sns.kdeplot(ax=ax,data = data_step,x='act_{}'.format(j+1), hue ='binding_{}'.format(j+1), palette=palette_full, legend=False, clip=xticks[j],multiple='stack')
                    ax.set_yticks([])
                    ax.set_xticks(xticks[j])
                    ax.set(xlabel=labels[j],ylabel=list_year[k])
                    ax.label_outer()
            success_rate = round(100*(data['status_2050']=='Success').sum()/len(data.index),1)
            # leg = list(palette.keys())
            # fig.legend(leg[::-1],loc="upper right")
            markers = [plt.Line2D([0,0],[0,0],color=color, marker='o', linestyle='') for color in palette_full.values()]
            fig.legend(markers, palette_full.keys(), numpoints=1,loc='upper right')
            # fig.legend(handles_leg, labels_leg, loc='upper right')
            plt.figtext(0.5, 0.91, 
                "batch: {} & rate of success: {}%".format(i,success_rate),
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
    # plt.plot(reward, 'k-', label="Reward")
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
    # plt.ylim(-40, 20)
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


def reward_plus_plus(df_learning, output_path, env, type_graph = 'act'):
    
    n_act = len([i for i in list(df_learning) if 'act' in i])
    xticks = list(zip(env.action_space.low,env.action_space.high))
    data_finish = df_learning.loc[df_learning['reward'] != 0]
    data_updated = df_learning.loc[:]
    for i in data_finish['episode'].unique():
        data_updated.loc[data_updated['episode']== i,'reward'] = data_finish.loc[data_finish['episode'] == i,'reward'].iloc[0]
    if type_graph == 'act':
        labels = ['Gwp limit for 10 years later', 'Gas limit','LFO limit','Coal limit']
        list_year = ['2020','2025','2030','2035','2040']
        for i in data_updated['batch'].unique():
            data = data_updated.loc[df_learning['batch']<=i]
            fig, axes = plt.subplots(len(list_year), n_act, figsize=(15, 5),sharex='col')
            fig.suptitle('End-of-episode reward of successfull transition')
            for j in range(n_act):
                for k in data['step'].unique():
                    data_step = data.loc[data['step'] == k]
                    data_success = data_step.loc[data_step['status_2050']=='Success']

                    data_rew_av = pd.DataFrame(columns=['act_{}'.format(j+1),'reward','batch','episode','status_2050'])
                    for a,b  in enumerate(data_step['batch'].unique()):
                        for c, d in enumerate(['Success','Failure']):
                            data_to_av = data_step.loc[data_step['status_2050']==d]
                            data_rew = data_to_av.loc[:,['act_{}'.format(j+1),'reward','batch','episode','status_2050']]
                            data_batch = data_rew.loc[data_rew['batch'] == b]
                            data_rew_av.loc[2*a+c,'act_{}'.format(j+1)] = np.average(data_batch['act_{}'.format(j+1)])
                            data_rew_av.loc[2*a+c,'reward'] = np.average(data_batch['reward'])
                            data_rew_av.loc[2*a+c,'batch'] = b
                            data_rew_av.loc[2*a+c,'episode'] = len(data_batch['episode'].unique())
                            data_rew_av.loc[2*a+c,'status_2050'] = c
                    ax = axes[k,j]
                    sns.scatterplot(ax=ax,data=data_rew_av, x="act_{}".format(j+1), y="reward",hue="batch",size='episode',palette='coolwarm',style='status_2050',legend=False)
                    ax.set_yticks([])
                    ax.set_xticks(xticks[j])
                    ax.set_xlim(xticks[j])
                    ax.set(xlabel=labels[j],ylabel=list_year[k])
                    ax.label_outer()
            success_rate = round(100*(data['status_2050']=='Success').sum()/len(data.index),1)
            plt.figtext(0.5, 0.91, 
                "batch: {} & rate of success: {}%".format(i,success_rate),
                horizontalalignment ="center",
                wrap = True, fontsize = 10, 
                bbox ={'facecolor':'grey', 
                    'alpha':0.3, 'pad':5})
            plt.subplots_adjust(right=0.9)
            plt.savefig(output_path + 'graph_pdf_rew_act_{}.png'.format(i), dpi=300, transparent=True)
            plt.close()
    else:
        labels = ['Cumulative cost', 'Cumulative emissions']
        x_to_plot = ['cum_cost','cum_gwp']
        list_year = ['2030','2035','2040','2045','2050']
        min_cum_cost = min(df_learning.loc[df_learning['status_2050']=='Success','cum_cost'])
        max_cum_cost = max(df_learning.loc[df_learning['status_2050']=='Success','cum_cost'])
        min_cum_gwp = min(df_learning.loc[df_learning['status_2050']=='Success','cum_gwp'])
        max_cum_gwp = max(df_learning.loc[df_learning['status_2050']=='Success','cum_gwp'])
        xticks = [[[min_cum_cost,max_cum_cost]]+[[min_cum_gwp,max_cum_gwp]]]
        # xticks = [[[]]+[[0.75*max_cum_gwp,max_cum_gwp]]]
        for i in data_updated['batch'].unique():
            data = data_updated.loc[df_learning['batch']<=i]
            fig, axes = plt.subplots(len(list_year), len(x_to_plot), figsize=(15, 5),sharex='col')
            fig.suptitle('End-of-episode reward of successfull transition')
            for j,l in enumerate(x_to_plot):
                for k in data['step'].unique():
                    data_step = data.loc[data['step'] == k]
                    data_success = data_step.loc[data_step['status_2050']=='Success']
                    data_rew = data_success.loc[:,['act_{}'.format(j+1),'cum_cost','cum_gwp','reward','batch','episode']]
                    data_rew_av = pd.DataFrame(columns=data_rew.columns)
                    for a,b  in enumerate(data_rew['batch'].unique()):
                        data_batch = data_rew.loc[data_rew['batch'] == b]
                        data_rew_av.loc[a,'cum_cost'] = np.average(data_batch['cum_cost'])
                        data_rew_av.loc[a,'cum_gwp'] = np.average(data_batch['cum_gwp'])
                        data_rew_av.loc[a,'reward'] = np.average(data_batch['reward'])
                        data_rew_av.loc[a,'batch'] = b
                        data_rew_av.loc[a,'episode'] = len(data_batch['episode'].unique())

                    ax = axes[k,j]
                    sns.scatterplot(ax=ax,data=data_rew_av, x=l, y="reward",hue="batch",size='episode',palette='coolwarm',legend=False)
                    ax.set_yticks([])
                    # ax.set_xticks([])
                    ax.set_xticks(xticks[0][j])
                    ax.set(xlabel=labels[j],ylabel=list_year[k])
                    ax.label_outer()
            success_rate = round(100*(data['status_2050']=='Success').sum()/len(data.index),1)
            plt.figtext(0.5, 0.91, 
                "batch: {} & rate of success: {}%".format(i,success_rate),
                horizontalalignment ="center",
                wrap = True, fontsize = 10, 
                bbox ={'facecolor':'grey', 
                    'alpha':0.3, 'pad':5})
            plt.subplots_adjust(right=0.9)
            plt.savefig(output_path + 'graph_pdf_rew_cost_gwp_{}.png'.format(i), dpi=300, transparent=True)
            plt.close()

def gif(output_path, type_graph, type_distr = 'cum'):
        if type_graph in ['sp','kde']:
            for i in range(5):
                output_dir = output_path + 'step_{}/'.format(i)
                cmd = 'ffmpeg -r 5 -i {} -vcodec mpeg4 -y {}mov_step_'+type_graph+'_{}_{}.mp4'
                cmd = cmd.format(output_dir+'graph_'+type_graph+'_%01d.png',output_path,i,type_distr)
                os.system(cmd)
                shutil.rmtree(output_dir)
        elif type_graph in ['ln_act','pdf_act','pdf_act_binding','pdf_act_plus','pdf_cum_gwp', 'pdf_cum_cost','pdf_obs','pdf_rew_act','pdf_rew_cost_gwp']:
            cmd = 'ffmpeg -r 3 -i {} -vcodec mpeg4 -y {}mov_'+type_graph+'.mp4'
            cmd = cmd.format(output_path+'graph_'+type_graph+'_%01d.png',output_path)
            os.system(cmd)
            system('rm {}*.png'.format(output_path))
    
