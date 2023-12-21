#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 11:47:54 2023

@author: xrixhon
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
import plotly.figure_factory as ff
from scipy import stats

import math
import pickle as pkl
import os


class AmplPCA:
    
    def __init__(self, ampl_obj,case_study):
        self.ampl_obj = ampl_obj
        self.color_dict_full = self._dict_color_full()
        self.case_study = case_study
        
        self.folder_name = os.path.join(Path(os.getcwd()).parent,'out',case_study)#'/Users/xrixhon/Development/GitKraken/EnergyScope_pathway/out/'+case_study+'/'
        self.case_name = 'TD'
        file_name = os.path.join(self.folder_name,self.case_name,'_uncert_collector.p')
        file_name = open(file_name,"rb")
        self.collector = pkl.load(file_name)
        file_name.close()
        
        self.assets = self.collector['Assets']
        self.resources = self.collector['Resources']
        
        # self._scaling_factor_sector() # Scaling versus EUD
        self._scaling_factor_sector_2() # Scaling versus commodity production
        
        # self._get_import_efuels()
        # self._get_elec_heat()
        
        self.assets_scaled=self._scale_per_sector()
        
        
        # self.assets_scaled_eud=self._scale_per_sector_eud() # Scaling versus EUD
        self.assets_scaled_eud=self._scale_per_sector_eud_2() # Scaling versus commodity production
        
        # self.layers = self.layer_collector()
        # self.layers_scaled = self._scale_per_layer()
        
        self.var_share_PC_assets = pd.DataFrame(columns=['Case','Years','PC','Var_share'])
        self.var_PC_assets = pd.DataFrame(columns=['Case','Years','PC','Var'])
        self.var_share_PC_prod = pd.DataFrame(columns=['Case','Years','PC','Var_share'])
        self.var_share_PC_cons = pd.DataFrame(columns=['Case','Years','PC','Var_share'])
        
        
        # self.df_pca_full_transition = self._pca_assets_transition()
        # self.df_pca_full_assets = self._pca_assets_year(self.assets_scaled)
        self.df_pca_full_assets_eud = self._pca_assets_year(self.assets_scaled_eud)
        
        self._most_different_PC()
        self._PC_transition()
        
        A = 4
        
        # self.df_pca_full_prod = self._pca_layer('Prod')
        # self.df_pca_full_cons = self._pca_layer('Cons')
    
    def graph_PC_j(self,j,quantity,True_val = False):
        if quantity == 'Assets': 
            df_pca = self.df_pca_full_assets.loc[self.df_pca_full_assets['PC']=='PC_{}'.format(j)]
        elif quantity == 'Assets_eud': 
            df_pca = self.df_pca_full_assets_eud.loc[self.df_pca_full_assets_eud['PC']=='PC_{}'.format(j)]
        elif quantity == 'Prod':
            df_pca = self.df_pca_full_prod.loc[self.df_pca_full_prod['PC']=='PC_{}'.format(j)]
        elif quantity == 'Cons':
            df_pca = self.df_pca_full_cons.loc[self.df_pca_full_cons['PC']=='PC_{}'.format(j)]
        df_to_plot = pd.DataFrame(columns=df_pca.columns)
        
        for y in df_pca.Years.unique():
            temp = df_pca.loc[df_pca['Years']==y]
            temp = temp.nlargest(5, 'Value')
            df_to_plot = df_to_plot.append(temp)
        
        if quantity in ['Assets','Assets_eud']:
            if True_val:
                fig = px.line(df_to_plot,x='Years',y='True_value',color='Technologies',color_discrete_map=self.color_dict_full,markers=True)        
            else:
                fig = px.bar(df_to_plot,x='Years',y='Value',color='Technologies',color_discrete_map=self.color_dict_full)        
        else:
            fig = px.bar(df_to_plot,x='Years',y='Value',color='Elements',color_discrete_map=self.color_dict_full)
        fig.update_xaxes(categoryorder='array', categoryarray= sorted(df_to_plot['Years'].unique()))
        title = 'Top-5 components of PC_{}_{}_{}'.format(j,quantity,self.case_study)
        if True_val:
            self.custom_fig(fig,title=title,yvals = [round(min(df_to_plot.True_value),2),0,round(max(df_to_plot.True_value),2)],xvals=['2025','2030','2035','2040','2045','2050'],neg_value=True)
        else:
            self.custom_fig(fig,title=title,yvals = [0,round(max(df_to_plot.groupby(by=['Years']).sum().Value),2)],xvals=['2025','2030','2035','2040','2045','2050'],type_graph = 'bar')
        pio.show(fig)
        
    
    def graph_PC_top_tech(self):
        df_pca = self.df_pca_full_assets.copy()
        
        df_to_plot = pd.DataFrame(columns=['Years','Technologies','W_value'])
        
        top_5_tech = []
        
        for y in df_pca.Years.unique():
            temp = df_pca.loc[df_pca['Years']==y]
            temp = temp.groupby(['Technologies']).sum()
            temp.reset_index(inplace=True)
            temp.drop('Value',axis='columns', inplace=True)
            temp['Years'] = y
            
            tech = temp.nlargest(3, 'W_value')['Technologies']
            
            top_5_tech += list(tech)
            
            df_to_plot = df_to_plot.append(temp)
        
        top_5_tech = list(set(top_5_tech))
        
        df_to_plot = df_to_plot.loc[df_to_plot['Technologies'].isin(top_5_tech)]
        
        fig = px.line(df_to_plot,x='Years',y='W_value',color='Technologies',color_discrete_map=self.color_dict_full)
        
        title = 'Main drivers accounting for all PC_{}'.format(self.case_study)
        self.custom_fig(fig,title=title,yvals = [0,round(max(df_to_plot['W_value']),2)],xvals=['2025','2030','2035','2040','2045','2050'],type_graph = 'line')
        pio.show(fig)
    
    def layer_collector(self):
        # col_plot = ['AMMONIA','ELECTRICITY','GAS','H2','WOOD','WET_BIOMASS','HEAT_HIGH_T',
        #         'HEAT_LOW_T_DECEN','HEAT_LOW_T_DHN','HVC','METHANOL',
        #         'MOB_FREIGHT_BOAT','MOB_FREIGHT_RAIL','MOB_FREIGHT_ROAD','MOB_PRIVATE',
        #         'MOB_PUBLIC','Sample']
        col_plot = ['AMMONIA','ELECTRICITY','HEAT_HIGH_T',
                'HEAT_LOW_T_DECEN','HEAT_LOW_T_DHN','HVC','METHANOL',
                'MOB_FREIGHT_BOAT','MOB_FREIGHT_RAIL','MOB_FREIGHT_ROAD','MOB_PRIVATE',
                'MOB_PUBLIC','Sample']
        results = self.collector['Year_balance'].copy()
        results = results[col_plot]
        results.reset_index(inplace=True)
        results = results.set_index(['Years','Elements','Sample'])
        df_to_plot_full = dict.fromkeys(col_plot)
        for k in results.columns:
            df_to_plot = pd.DataFrame(index=results.index,columns=[k])
            temp = results.loc[:,k].dropna(how='all')
            for y in results.index.get_level_values(0).unique():
                temp_y = temp.loc[temp.index.get_level_values('Years') == y,:] 
                if not temp_y.empty:
                    # temp_y = self._remove_low_values(temp_y, threshold=0.01)
                    df_to_plot.update(temp_y)
            df_to_plot.dropna(how='all',inplace=True)
            
            
            df_to_plot_prod = df_to_plot.loc[df_to_plot[k]>0]
            df_to_plot_cons = df_to_plot.loc[df_to_plot[k]<0]
            
            df_to_plot_prod = self._fill_df_to_plot_w_zeros(df_to_plot_prod)
            df_to_plot_cons = self._fill_df_to_plot_w_zeros(df_to_plot_cons)
            
            df_to_plot_prod.reset_index(inplace=True)
            df_to_plot_cons.reset_index(inplace=True)
            
            df_to_plot_cons.loc[df_to_plot_cons[k]<0,k] = - df_to_plot_cons.loc[df_to_plot_cons[k]<0,k]
            
            df_to_plot_prod['Elements'] = df_to_plot_prod['Elements'].astype("str")
            df_to_plot_prod[k] /= 1000
            
            df_to_plot_cons['Elements'] = df_to_plot_cons['Elements'].astype("str")
            df_to_plot_cons[k] /= 1000
            
            df_to_plot_prod['Type'] = 'Production'
            df_to_plot_cons['Type'] = 'Consumption'

            df_to_plot_full[k] = df_to_plot_prod.append(df_to_plot_cons)
        
        return df_to_plot_full
        

    def _scale_per_sector(self):
        dict_tech = self._group_tech_per_eud()
        
        assets_scaled = self.assets.copy().loc[:,['F','Sample']]
        assets_scaled.reset_index(inplace=True)
        assets_scaled = assets_scaled.set_index(['Years','Technologies','Sample'])
        
        self._fill_df_to_plot_w_zeros(assets_scaled)
        
        years = self.assets.index.get_level_values('Years').unique()
        
        for y in years:
            temp_y = self.assets.loc[self.assets.index.get_level_values('Years')==y,['F','Sample']]
        
            for sector, tech in dict_tech.items():
                temp_s = temp_y.loc[temp_y.index.get_level_values('Technologies').isin(tech)]
                if temp_s['F'].empty:
                    continue
                temp_s['F'] /= max(temp_s['F'])
                temp_s.reset_index(inplace=True)
                temp_s = temp_s.set_index(['Years','Technologies','Sample'])
                assets_scaled.update(temp_s)
        
        return assets_scaled

    def _scale_per_sector_eud(self):
        dict_tech = self._group_tech_per_eud()
        
        inf_sto = dict_tech['INFRASTRUCTURE']+dict_tech['STORAGE']
        
        eud = self.scaling_factor_sector
        
        assets_scaled = self.assets.copy().loc[:,['F','Sample']]
        assets_scaled = assets_scaled.loc[~assets_scaled.index.get_level_values('Technologies').isin(inf_sto)]
        assets_scaled.reset_index(inplace=True)
        assets_scaled_eud = assets_scaled.set_index(['Years','Technologies','Sample'])
        
        self._fill_df_to_plot_w_zeros(assets_scaled_eud)
        
        years = self.assets.index.get_level_values('Years').unique()
        
        for y in years:
            temp_y = self.assets.loc[self.assets.index.get_level_values('Years')==y,['F','Sample']]
        
            for sector, tech in dict_tech.items():
                if sector in ['INFRASTRUCTURE','STORAGE']:
                    continue
                else:
                    if sector == 'ELECTRICITY':
                        share_eud = eud.loc[y,'LIGHTING']['Share_eud']+eud.loc[y,'ELECTRICITY']['Share_eud']
                    elif sector == 'HEAT_LOW_T':
                        share_eud = eud.loc[y,'HEAT_LOW_T_SH']['Share_eud']+eud.loc[y,'HEAT_LOW_T_HW']['Share_eud'] 
                    else:
                        share_eud = eud.loc[y,sector]['Share_eud']
                temp_s = temp_y.loc[temp_y.index.get_level_values('Technologies').isin(tech)]
                if temp_s['F'].empty:
                    continue
                temp_s['F'] /= (max(temp_s['F'])/share_eud)
                temp_s.reset_index(inplace=True)
                temp_s = temp_s.set_index(['Years','Technologies','Sample'])
                assets_scaled_eud.update(temp_s)
        
        return assets_scaled_eud

    def _scale_per_sector_eud_2(self, eud = None, assets = None):
        dict_tech = self._group_tech_per_eud()
        
        inf_sto = dict_tech['INFRASTRUCTURE']+dict_tech['STORAGE']
        
        if eud is None:    
            eud = self.scaling_factor_sector
        else:
            eud = eud
        
        if assets is None:
            assets = self.assets.copy()
        else:
            assets = assets.copy()
            
        
        assets_scaled = assets.loc[:,['F','Sample']]
        assets_scaled = assets_scaled.loc[~assets_scaled.index.get_level_values('Technologies').isin(inf_sto)]
        assets_scaled.reset_index(inplace=True)
        assets_scaled_eud = assets_scaled.set_index(['Years','Technologies','Sample'])
        
        self._fill_df_to_plot_w_zeros(assets_scaled_eud)
        
        years = assets.index.get_level_values('Years').unique()
        
        for y in years:
            temp_y = assets.loc[assets.index.get_level_values('Years')==y,['F','Sample']]
        
            for sector, tech in dict_tech.items():
                if sector in ['INFRASTRUCTURE','STORAGE']:
                    continue
                else:
                    share_eud = eud.loc[y,sector]['Share_eud']
                temp_s = temp_y.loc[temp_y.index.get_level_values('Technologies').isin(tech)]
                if temp_s['F'].empty:
                    continue
                temp_s['F'] /= (max(temp_s['F'])/share_eud)
                temp_s.reset_index(inplace=True)
                temp_s = temp_s.set_index(['Years','Technologies','Sample'])
                assets_scaled_eud.update(temp_s)
        
        return assets_scaled_eud
    
    def _scaling_factor_sector(self):
        dict_tech = self._group_tech_per_eud()
        
        eud = self.ampl_obj.get_elem('end_uses_demand_year',type_of_elem='Param')
        eud = eud.groupby(['Years','End_uses_input']).sum()
        eud_ned = eud.reset_index()
        eud_ned = eud_ned.loc[eud_ned['End_uses_input'] == 'NON_ENERGY']
        eud_ned = eud_ned.set_index(['Years'])
        share_ned = self.ampl_obj.get_elem('share_ned',type_of_elem='Param')
        share_ned = share_ned.reset_index().set_index(['Years'])
        
        share_ned['eud'] = share_ned['share_ned'].mul(eud_ned['end_uses_demand_year'])
        col_share_ned = share_ned.columns
        share_ned.rename(columns={col_share_ned[0]:'End_uses_input','eud':'end_uses_demand_year'},inplace=True)
        share_ned = pd.DataFrame(share_ned.reset_index().set_index(['Years','End_uses_input'])['end_uses_demand_year'])
        
        eud = eud.append(share_ned)
        eud = eud.loc[eud.index.get_level_values('End_uses_input')!='NON_ENERGY']
        
        file = '/Users/xrixhon/Development/GitKraken/EnergyScope_pathway/out/TD_30_0_gwp_budget_no_efuels_2020/_Results.pkl'
        file_name = open(file,"rb")
        collector = pkl.load(file_name)
        file_name.close()
        
        yb = collector['Year_balance']
        
        yb_mob_pass = yb.loc[yb.index.get_level_values('Elements').isin(dict_tech['MOBILITY_PASSENGER'])]
        yb_mob_freight = yb.loc[yb.index.get_level_values('Elements').isin(dict_tech['MOBILITY_FREIGHT'])]
        
        yb_mob_pass = yb_mob_pass.dropna(axis=1,how='all')
        yb_mob_pass_cons = yb_mob_pass.drop(['MOB_PRIVATE','MOB_PUBLIC'],axis=1)
        yb_mob_pass_cons = pd.DataFrame(yb_mob_pass_cons.groupby('Years').sum().sum(axis=1)*-1)
        yb_mob_pass_cons = yb_mob_pass_cons.rename(columns={0:'end_uses_demand_year'})
        yb_mob_pass_cons['End_uses_input'] = 'MOBILITY_PASSENGER'
        yb_mob_pass_cons = yb_mob_pass_cons.reset_index().set_index(['Years','End_uses_input'])
        
        yb_mob_freight = yb_mob_freight.dropna(axis=1,how='all')
        yb_mob_freight_cons = yb_mob_freight.drop(['MOB_FREIGHT_BOAT','MOB_FREIGHT_ROAD','MOB_FREIGHT_RAIL'],axis=1)
        yb_mob_freight_cons = pd.DataFrame(yb_mob_freight_cons.groupby('Years').sum().sum(axis=1)*-1)
        yb_mob_freight_cons = yb_mob_freight_cons.rename(columns={0:'end_uses_demand_year'})
        yb_mob_freight_cons['End_uses_input'] = 'MOBILITY_FREIGHT'
        yb_mob_freight_cons = yb_mob_freight_cons.reset_index().set_index(['Years','End_uses_input'])
        
        eud.update(yb_mob_pass_cons)
        eud.update(yb_mob_freight_cons)
        
        eud_y = eud.groupby(['Years']).sum()
        
        eud = eud.reset_index().set_index(['Years'])
        
        eud.sort_values(by=['Years'],inplace=True)
        
        eud['Share_eud'] = eud['end_uses_demand_year'].div(eud_y['end_uses_demand_year'])
        
        eud = eud.reset_index().set_index(['Years','End_uses_input'])
        
        self.scaling_factor_sector = eud
    
    def _scaling_factor_sector_2(self):
        
        dict_layer = {'ELECTRICITY':['ELECTRICITY'],
                      'AMMONIA':['AMMONIA'],
                      'HVC':['HVC'],
                      'METHANOL':['METHANOL'],
                      'HEAT_LOW_T':['HEAT_LOW_T_DHN','HEAT_LOW_T_DECEN'],
                      'HEAT_HIGH_T':['HEAT_HIGH_T']}
        
        file = '/Users/xrixhon/Development/GitKraken/EnergyScope_pathway/out/TD_30_0_gwp_budget_no_efuels_2020/_Results.pkl'
        file_name = open(file,"rb")
        collector = pkl.load(file_name)
        file_name.close()
        
        yb = collector['Year_balance']
        
        df = pd.DataFrame(index=['Years','End_uses_input'],columns=['end_uses_demand_year','Share_eud'])
        
        for i,sector in enumerate(dict_layer):
            layers = dict_layer[sector]
            yb_s = yb[layers]
            yb_s.dropna(how='all',inplace=True)
            yb_s = pd.DataFrame(yb_s.sum(axis=1))
            yb_s = yb_s.loc[yb_s[0]>0]
            yb_s = pd.DataFrame(yb_s.groupby('Years').sum())
            yb_s.rename(columns={0:'end_uses_demand_year'},inplace=True)
            yb_s['End_uses_input'] = sector
            yb_s['Share_eud'] = 0
            yb_s = yb_s.reset_index().set_index(['Years','End_uses_input'])
            
            if i == 0:
                df = yb_s
            else:
                df = df.append(yb_s)
        
        dict_tech = self._group_tech_per_eud()

        
        yb_mob_pass = yb.loc[yb.index.get_level_values('Elements').isin(dict_tech['MOBILITY_PASSENGER'])]
        yb_mob_freight = yb.loc[yb.index.get_level_values('Elements').isin(dict_tech['MOBILITY_FREIGHT'])]
        
        yb_mob_pass = yb_mob_pass.dropna(axis=1,how='all')
        yb_mob_pass_cons = yb_mob_pass.drop(['MOB_PRIVATE','MOB_PUBLIC'],axis=1)
        yb_mob_pass_cons = pd.DataFrame(yb_mob_pass_cons.groupby('Years').sum().sum(axis=1)*-1)
        yb_mob_pass_cons = yb_mob_pass_cons.rename(columns={0:'end_uses_demand_year'})
        yb_mob_pass_cons['End_uses_input'] = 'MOBILITY_PASSENGER'
        yb_mob_pass_cons = yb_mob_pass_cons.reset_index().set_index(['Years','End_uses_input'])
        yb_mob_pass_cons['Share_eud'] = 0
        
        yb_mob_freight = yb_mob_freight.dropna(axis=1,how='all')
        yb_mob_freight_cons = yb_mob_freight.drop(['MOB_FREIGHT_BOAT','MOB_FREIGHT_ROAD','MOB_FREIGHT_RAIL'],axis=1)
        yb_mob_freight_cons = pd.DataFrame(yb_mob_freight_cons.groupby('Years').sum().sum(axis=1)*-1)
        yb_mob_freight_cons = yb_mob_freight_cons.rename(columns={0:'end_uses_demand_year'})
        yb_mob_freight_cons['End_uses_input'] = 'MOBILITY_FREIGHT'
        yb_mob_freight_cons = yb_mob_freight_cons.reset_index().set_index(['Years','End_uses_input'])
        yb_mob_freight_cons['Share_eud'] = 0
        
        df = df.append(yb_mob_pass_cons)
        df = df.append(yb_mob_freight_cons)
        
        df_y = df.groupby(['Years']).sum()
        
        df = df.reset_index().set_index(['Years'])
        
        df.sort_values(by=['Years'],inplace=True)
        
        df['Share_eud'] = df['end_uses_demand_year'].div(df_y['end_uses_demand_year'])
        
        df = df.reset_index().set_index(['Years','End_uses_input'])
        
        self.scaling_factor_sector = df
    
    def _scale_per_layer(self):
        dict_tech = self._group_tech_per_eud()
        
        dict_layer = {'ELECTRICITY':'ELECTRICITY',
                      'AMMONIA':'AMMONIA',
                      'HVC':'HVC',
                      'METHANOL':'METHANOL',
                      'HEAT_LOW_T_DHN':'HEAT_LOW_T',
                      'HEAT_LOW_T_DECEN':'HEAT_LOW_T',
                      'HEAT_HIGH_T':'HEAT_HIGH_T',
                      'MOB_FREIGHT_BOAT':'MOBILITY_FREIGHT',
                      'MOB_FREIGHT_ROAD':'MOBILITY_FREIGHT',
                      'MOB_FREIGHT_RAIL':'MOBILITY_FREIGHT',
                      'MOB_PRIVATE':'MOBILITY_PASSENGER',
                      'MOB_PUBLIC':'MOBILITY_PASSENGER'
                      }
        
        layers = self.layers.copy()
        
        eud = self.scaling_factor_sector
        
        layers_scaled = pd.DataFrame(columns=['Years','Elements','Sample','Value',
                                              'Type','Layer'])
        
        for l in layers:
            if not (layers[l] is None):
                temp_l = layers[l].copy()
                years = temp_l['Years'].unique()
                for y in years:
                    temp_y = temp_l.loc[temp_l['Years']==y]
    
                    temp_y_prod = temp_y.loc[temp_y['Type'] == 'Production']
                    temp_y_prod [l] /= max(temp_y_prod[l])
                    temp_y_prod ['Layer'] = l
                    temp_y_prod.rename(columns={l: "Value"},inplace=True)
                    layers_scaled = layers_scaled.append(temp_y_prod)
                    
                    temp_y_cons = temp_y.loc[temp_y['Type'] == 'Consumption']
                    temp_y_cons = temp_y_cons.loc[temp_y_cons['Elements'] != 'END_USES']
                    if (temp_y_cons.empty) or (max(temp_y_cons[l])==0):
                        continue
                    temp_y_cons[l] /= max(temp_y_cons[l])
                    temp_y_cons['Layer'] = l
                    temp_y_cons.rename(columns={l: "Value"},inplace=True)
                    layers_scaled = layers_scaled.append(temp_y_cons)
         
        layers_scaled = layers_scaled.set_index(['Years','Elements','Sample'])

        
        return layers_scaled                 
            
    def _pca_assets_year(self,assets):
        
        years = ['YEAR_2025','YEAR_2030','YEAR_2035','YEAR_2040','YEAR_2045','YEAR_2050']
        assets_scaled = assets
        
        df_pca_full = pd.DataFrame(columns=['Years','PC','Technologies','Value','True_value','W_value'])
        df_pca_PC = pd.DataFrame(columns=['Years','PC','Expl_Var','Expl_Var_Ratio'])
        df_pca_features = pd.DataFrame(columns=['Years','PC','Technologies','Value','True_value'])
        
        for y in years:
            assets_scaled_y = assets_scaled.loc[assets_scaled.index.get_level_values('Years')==y]
            assets_scaled_y.reset_index(inplace=True)
            assets_scaled_y = assets_scaled_y.pivot(columns='Technologies',index='Sample',values='F')
            assets_scaled_y = assets_scaled_y.fillna(0)
            
            assets_scaled_y = self._remove_outliers(assets_scaled_y)
            
            # pca = PCA(n_components=n_components)
            # pca = PCA(0.85)
            pca = PCA(0.90)
        
            x_transformed = pca.fit_transform(assets_scaled_y)
            # for j in range(n_components):
            for j in range(pca.n_components_):

                temp = zip(assets_scaled_y.columns.values,abs(pca.components_[j,:]),pca.components_[j,:],abs(pca.components_[j,:])*pca.explained_variance_ratio_[j])
                temp_2 = zip(assets_scaled_y.columns.values,pca.components_[j,:])
                
                new_row = {'Case':self.case_study,'Years':y,'PC':'PC_{}'.format(j+1),'Var_share':pca.explained_variance_ratio_[j]}
                self.var_share_PC_assets = self.var_share_PC_assets.append(new_row,ignore_index=True)
                new_row = {'Case':self.case_study,'Years':y[-4:],'PC':'PC_{}'.format(j+1),'Var':pca.explained_variance_[j]}
                self.var_PC_assets = self.var_PC_assets.append(new_row,ignore_index=True)
                
                temp = pd.DataFrame(temp)
                temp.columns = ['Technologies','Value','True_value','W_value']
                temp['Years'] = y[-4:]
                temp['PC'] = 'PC_{}'.format(j+1)
                
                temp_2 = pd.DataFrame(temp_2)
                temp_2.columns = ['Technologies','Value']
                temp_2['Years'] = y[-4:]
                temp_2['PC'] = 'PC_{}'.format(j+1)

                
                temp = temp[['Years','PC','Technologies','Value','True_value','W_value']]
                temp_2 = temp_2[['Years','PC','Technologies','Value']]
                
                df_pca_full = df_pca_full.append(temp)
                
                new_row = {'Years':y,'PC':'PC_{}'.format(j+1),'Expl_Var':pca.explained_variance_[j],'Expl_Var_Ratio':pca.explained_variance_ratio_[j]}
                df_pca_PC = df_pca_PC.append(new_row,ignore_index=True)
                df_pca_features = df_pca_features.append(temp_2,ignore_index=True)
        
        file_name = os.path.join(self.folder_name,self.case_name,'_PCA.p')
        file_name = open(file_name,"wb")
        pkl_dict = {'df_pca_PC':df_pca_PC,
                    'df_pca_features':df_pca_features}
        
        pkl.dump(pkl_dict,file_name)
        file_name.close()
        
        
        return df_pca_full
    
    def graph_PC_projection(self,case_studies,output_folder_cs):
        
        file = '/Users/xrixhon/Development/GitKraken/EnergyScope_pathway/out/CASE_PCA/PCA_ref.pkl'
        file_name = open(file,"rb")
        PCA_ref = pkl.load(file_name)
        file_name.close()
        
        scaling_factor = PCA_ref['Scaling']
        PC_transition = PCA_ref['PC_transition']
        
        years = ['YEAR_2025','YEAR_2030','YEAR_2035','YEAR_2040','YEAR_2045','YEAR_2050']
        
        for PC in PC_transition.PC_tran.unique():
            PC_temp = PC_transition.loc[PC_transition['PC_tran'] == PC]
            
            df_to_plot = pd.DataFrame(columns=['Case',PC])
            hist_data = []
            group_labels = []
            
            for i, cs in enumerate(case_studies):
                output_folder = output_folder_cs[i]
                file = os.path.join(output_folder,'_uncert_collector.p')
                file_name = open(file,"rb")
                ampl_uncert_collector = pkl.load(file_name)
                file_name.close()
                
                assets = ampl_uncert_collector['Assets'].copy()
                
                assets_scaled = self._scale_per_sector_eud_2(eud = scaling_factor, assets = assets)
                
                assets_scaled = self._fill_df_to_plot_w_zeros(assets_scaled)
                assets_scaled = assets_scaled.loc[assets_scaled.index.get_level_values('Years').isin(years)]
                
                assets_scaled.reset_index(inplace=True)
                assets_scaled = assets_scaled.pivot(columns='Technologies',index=['Sample','Years'],values='F')
                assets_scaled = assets_scaled.fillna(0)
                assets_scaled.reset_index(inplace=True)
                assets_scaled.drop(columns=['Sample','Years'],inplace=True)
                
                assets_scaled = assets_scaled[PC_temp.Technologies.unique()]
                
                PC_temp_2 = PC_temp.set_index('Technologies').Val.to_frame().T
                
                temp = assets_scaled.values * PC_temp_2.values[:, None]
                temp = temp[0,:,:]
                temp = pd.DataFrame(temp.sum(axis=1)).rename(columns={0:PC})
                temp['Case'] = cs
                
                hist_data += [np.array(temp[PC])]
                group_labels += [cs]
                
                if i == 0:
                    df_to_plot = temp
                else:
                    df_to_plot = df_to_plot.append(temp)
                    
                ## Computation of 95% confidence
                self._confidence_interval(temp[PC],0.95,cs,PC)
                
            
            fig_test = ff.create_distplot(hist_data,group_labels,show_hist = False,show_rug=False)
            fig_test.update_layout(title_text=PC,titlefont=dict(family="Raleway",size=28))
            pio.show(fig_test)
                    
                                
    def _confidence_interval(self,data,confidence_level,cs,PC):
        mean = np.mean(data)
        sem = stats.sem(data)

        # Set the confidence level (e.g., 95%)
        confidence_level = confidence_level

        # Calculate the margin of error
        margin_of_error = sem * stats.t.ppf((1 + confidence_level) / 2, len(data) - 1)

        # Calculate the confidence interval
        confidence_interval = (mean - margin_of_error, mean + margin_of_error)
        range_interval = confidence_interval[1]-confidence_interval[0]
        
        print('-----------')
        print('For {}, and {}'.format(cs,PC))
        print(f"Mean: {mean}")
        print(f"Margin of Error: {margin_of_error}")
        print(f"95% Confidence Interval: {confidence_interval}")
        print('Range of the confidence interval: {}'.format(range_interval))
        
    
    def pkl_PCA(self):
        struct_pkl = {'Scaling':self.scaling_factor_sector,
                      'PC_transition':self.PC_transition}
        file_name = os.path.join(self.folder_name,'PCA_ref.pkl')
        
        open_file = open(file_name,"wb")
        
        pkl.dump(struct_pkl,open_file)
        open_file.close()
    
    def _pca_assets_transition(self):
        
        years = ['YEAR_2025','YEAR_2030','YEAR_2035','YEAR_2040','YEAR_2045','YEAR_2050']
        assets_scaled = self.assets_scaled.copy()
        
        assets_scaled = assets_scaled.loc[assets_scaled.index.get_level_values('Years').isin(years)]
        
        assets_scaled = self._fill_df_to_plot_w_zeros(assets_scaled)
        assets_scaled.reset_index(inplace=True)
        assets_scaled = assets_scaled.pivot(columns='Technologies',index=['Sample','Years'],values='F')
        assets_scaled = assets_scaled.fillna(0)
        assets_scaled = self._remove_outliers(assets_scaled)
        assets_scaled.reset_index(inplace=True)
        assets_scaled.drop(columns=['Sample','Years'],inplace=True)
        
        df_pca_full = pd.DataFrame(columns=['PC','Technologies','Value','W_value'])
        
        pca = PCA(0.90)
    
        x_transformed = pca.fit_transform(assets_scaled)
        for j in range(pca.n_components_):

            temp = zip(assets_scaled.columns.values,abs(pca.components_[j,:]),abs(pca.components_[j,:])*pca.explained_variance_[j])
            temp_2 = zip(assets_scaled.columns.values,pca.components_[j,:])
            
            temp = pd.DataFrame(temp)
            temp.columns = ['Technologies','Value','W_value']
            temp['PC'] = 'PC_{}'.format(j+1)
            
            temp_2 = pd.DataFrame(temp_2)
            temp_2.columns = ['Technologies','Value']
            temp_2['PC'] = 'PC_{}'.format(j+1)

            
            temp = temp[['PC','Technologies','Value','W_value']]
            temp_2 = temp_2[['PC','Technologies','Value']]
            
            df_pca_full = df_pca_full.append(temp)
        
        A = df_pca_full.groupby(['Technologies']).sum()
        A.sort_values(by=['W_value'],ascending=False,inplace=True)
        B = A.nlargest(10,'W_value')
        B.reset_index(inplace=True)
        title = 'Top-10 features over the transition for {}'.format(self.case_study)
        fig = px.bar(B,x='Technologies',y='W_value')
        fig.update_layout(title=title)

        pio.show(fig)

        
        return df_pca_full
    
    def _pca_layer(self,part_of_layer):
        
        years = ['YEAR_2025','YEAR_2030','YEAR_2035','YEAR_2040','YEAR_2045','YEAR_2050']
        layers_prod = self.layers_scaled.copy()
        
        if part_of_layer == 'Prod':        
            layers_prod = layers_prod.loc[layers_prod['Type']=='Production']
        else:
            layers_prod = layers_prod.loc[layers_prod['Type']=='Consumption']
        
        df_pca_full = pd.DataFrame(columns=['Years','PC','Elements','Value','W_value'])
        
        n_components = 4
        
        for y in years:
            layers_prod_y = layers_prod.loc[layers_prod.index.get_level_values('Years')==y]
            layers_prod_y.reset_index(inplace=True)
            layers_prod_y = layers_prod_y.groupby(['Years','Elements','Sample']).sum()
            layers_prod_y.reset_index(inplace=True)
            layers_prod_y = layers_prod_y.pivot(columns='Elements',index='Sample',values='Value')
            layers_prod_y = layers_prod_y.fillna(0)
            
            layers_prod_y = self._remove_outliers(layers_prod_y)
            
            pca = PCA(n_components=n_components)
        
            x_transformed = pca.fit_transform(layers_prod_y)
        
            for j in range(n_components):

                temp = zip(layers_prod_y.columns.values,abs(pca.components_[j,:]),abs(pca.components_[j,:])*pca.explained_variance_ratio_[j])
                
                new_row = {'Case':self.case_study,'Years':y,'PC':'PC_{}'.format(j+1),'Var_share':pca.explained_variance_ratio_[j]}
                if part_of_layer == 'Prod':
                    self.var_share_PC_prod = self.var_share_PC_prod.append(new_row,ignore_index=True)
                else:
                    self.var_share_PC_cons = self.var_share_PC_cons.append(new_row,ignore_index=True)
                
                temp = pd.DataFrame(temp)
                temp.columns = ['Elements','Value','W_value']
                temp['Years'] = y[-4:]
                temp['PC'] = 'PC_{}'.format(j+1)
                
                temp = temp[['Years','PC','Elements','Value','W_value']]
                
                df_pca_full = df_pca_full.append(temp)
        
        return df_pca_full
    
    def _get_elec_heat(self):
        dict_tech = self._group_tech_per_eud()
        
        eff = self.ampl_obj.get_elem('layers_in_out',type_of_elem='Param')
        eff.reset_index(inplace=True)
        eff = eff.loc[eff['Years'] == 'YEAR_2020']
        eff = eff.pivot(columns='\n  layers',index='Resources union technologies diff storage_tech',values='layers_in_out')
        eff.reset_index(inplace=True)
        ELEC_LT = eff.loc[(eff['ELECTRICITY'] < 0) & ((eff['HEAT_LOW_T_DHN'] == 1) | (eff['HEAT_LOW_T_DECEN'] == 1))]['Resources union technologies diff storage_tech']
        ELEC_HT = eff.loc[(eff['ELECTRICITY'] < 0) & (eff['HEAT_HIGH_T'] == 1)]['Resources union technologies diff storage_tech']
        
        yb = self.collector['Year_balance']
        yb_lt = yb.loc[(yb['HEAT_LOW_T_DHN'] > 0) |  (yb['HEAT_LOW_T_DECEN'] > 0)][['HEAT_LOW_T_DHN','HEAT_LOW_T_DECEN','Sample']]
        yb_lt = yb_lt.reset_index().set_index(['Years','Elements','Sample'])
        yb_lt = self._fill_df_to_plot_w_zeros(yb_lt)
        yb_lt['HEAT_LOW_T'] = yb_lt['HEAT_LOW_T_DHN']+yb_lt['HEAT_LOW_T_DECEN']
        yb_lt = yb_lt[['HEAT_LOW_T']]
        
        yb_ht = yb.loc[yb['HEAT_HIGH_T'] > 0][['HEAT_HIGH_T','Sample']]
        yb_ht = yb_ht.reset_index().set_index(['Years','Elements','Sample'])
        yb_ht = self._fill_df_to_plot_w_zeros(yb_ht)
        
        yb_lt_y_s = yb_lt.groupby(['Years','Sample']).sum()
        yb_ht_y_s = yb_ht.groupby(['Years','Sample']).sum()
        
        yb_lt_elec = yb_lt.loc[yb_lt.index.get_level_values('Elements').isin(ELEC_LT)].groupby(['Years','Sample']).sum()
        yb_ht_elec = yb_ht.loc[yb_ht.index.get_level_values('Elements').isin(ELEC_HT)].groupby(['Years','Sample']).sum()
        
        yb_lt_elec_share = yb_lt_elec.div(yb_lt_y_s)
        yb_ht_elec_share = yb_ht_elec.div(yb_ht_y_s)
        
        output = yb_lt_elec_share
        output[yb_ht_elec_share.columns] = yb_ht_elec_share
        
        fig = px.box(yb_lt_elec_share.reset_index(),x='Years',y='HEAT_LOW_T',notched=True)
        title = 'Electrification LOW_T_HEAT - {}'.format(self.case_study)
        fig.update_layout(title=title)
        pio.show(fig)
        
        fig = px.box(yb_ht_elec_share.reset_index(),x='Years',y='HEAT_HIGH_T',notched=True)
        title = 'Electrification HIGH_T_HEAT - {}'.format(self.case_study)
        fig.update_layout(title=title)
        pio.show(fig)
        
        return output
    
    def _get_import_efuels(self):
        efuels = ['AMMONIA_RE','GAS_RE','H2_RE','METHANOL_RE']
        energy_mix = [x for x in self.ampl_obj.sets['RESOURCES'] if x not in ['ELEC_EXPORT','CO2_EMISSIONS','CO2_ATM','CO2_INDUSTRY','CO2_CAPTURED']]
        
        res = self.collector['Resources']
        
        efuels = res.loc[res.index.get_level_values('Resources').isin(efuels)]
        efuels = efuels.reset_index().set_index(['Years','Resources','Sample'])
        efuels = self._fill_df_to_plot_w_zeros(efuels)
        
        energy_mix = res.loc[res.index.get_level_values('Resources').isin(energy_mix)]
        energy_mix = energy_mix.reset_index().set_index(['Years','Resources','Sample'])
        energy_mix = self._fill_df_to_plot_w_zeros(energy_mix)
        
        efuels_y_s = efuels.groupby(['Years','Sample']).sum()
        energy_mix_y_s = energy_mix.groupby(['Years','Sample']).sum()
        
        efuels_share = efuels_y_s.div(energy_mix_y_s)
        fig = px.box(efuels_share.reset_index(),x='Years',y='Res',notched=True)
        title = 'Share of efuels in energy mix - {}'.format(self.case_study)
        fig.update_layout(title=title)
        pio.show(fig)
        
    def _most_different_PC(self):
        
        df_pca = self.df_pca_full_assets_eud[['Years','PC','Technologies','True_value']].copy()
        df_pca = df_pca.pivot(index=['Years','PC'],columns='Technologies',values='True_value')
        df_pca.fillna(0,inplace=True)
        
        var_PC_assets = self.var_PC_assets.copy()[['Years','PC','Var']]
        var_PC_assets = var_PC_assets.set_index(['Years','PC'])
        var_PC_assets = var_PC_assets.sort_values('Var',ascending=False)
        
        df_pca = pd.concat([df_pca,var_PC_assets],axis=1)
        df_pca = df_pca.sort_values('Var',ascending=False)
        df_pca.drop(columns='Var',inplace=True)
        
        # # Convert the list of vectors to a NumPy array
        # vectors_array = np.array(vectors)
        
        # Calculate the cosine similarity matrix
        similarity_matrix = cosine_similarity(df_pca)
        
        # Set the diagonal elements to zero to exclude self-similarity
        np.fill_diagonal(similarity_matrix, 0)
        
        PC_dict = dict()
        
        sum_var = var_PC_assets.sum()[0]
        
        counter = 0
        
        threshold_counter = 0.9
        
        threshold_similarity = 0.8
        
        i = 0
        
        while counter <= threshold_counter * sum_var:
            temp = [0]
            ind_sim = np.where(similarity_matrix[:,0] >= threshold_similarity)
            temp += list(ind_sim[0])
            PC_dict[i] = var_PC_assets.index[temp]
            counter += var_PC_assets.iloc[temp].sum()[0]
            df_pca = df_pca.drop(index=var_PC_assets.index[temp])
            var_PC_assets = var_PC_assets.drop(index=var_PC_assets.index[temp])
            similarity_matrix = cosine_similarity(df_pca)
            np.fill_diagonal(similarity_matrix, 0)
            i += 1
        
        self.PC_transition_dict = PC_dict
    
    def _PC_transition(self):
        PC_transition_dict = self.PC_transition_dict.copy()
        
        df_pca = self.df_pca_full_assets_eud[['Years','PC','Technologies','True_value']].copy()
        df_pca = df_pca.pivot(index=['Years','PC'],columns='Technologies',values='True_value')
        df_pca.fillna(0,inplace=True)
        
        PC_transition = pd.DataFrame(columns=['PC_tran','Technologies','Val'])
        
        for i in PC_transition_dict:
            df_pca_temp = df_pca.loc[PC_transition_dict[i]]
            df_pca_temp = pd.DataFrame(df_pca_temp.mean())
            norm = np.sqrt(np.square(df_pca_temp).sum())
            df_pca_temp /= norm
            
            df_pca_temp['PC_tran'] = 'PC_{}'.format(i+1)            
            df_pca_temp.rename(columns={0:'Val'},inplace=True)
            
            df_pca_temp.reset_index(inplace=True)
            
            PC_transition =  PC_transition.append(df_pca_temp[['PC_tran','Technologies','Val']])
        
        PC_transition['Abs_value'] = abs(PC_transition['Val'])
        
        self.PC_transition = PC_transition
        
    def graph_PC_transition(self):
        
        PC_transition = self.PC_transition.copy()
        
        df_to_plot = pd.DataFrame(columns=PC_transition.columns)
        
        y_pos = 0
        y_neg = 0
        
        
        for PC in PC_transition.PC_tran.unique():
            temp = PC_transition.loc[PC_transition['PC_tran']==PC]
            temp = temp.nlargest(5, 'Abs_value')
            df_to_plot = df_to_plot.append(temp)
            
            y_neg = max(y_neg,abs(temp.loc[temp['Val'] < 0].Val.sum()))
            y_pos = max(y_pos,abs(temp.loc[temp['Val'] > 0].Val.sum()))
        
        y = max(y_neg,y_pos)
        
        fig = px.bar(df_to_plot,x='PC_tran',y='Abs_value',color='Technologies',
                     color_discrete_map=self.color_dict_full)
        title = 'PCs of the transition - {}'.format(self.case_study)
        self.custom_fig(fig,title=title,yvals = [0,round(max(df_to_plot.groupby(by=['PC_tran']).sum().Abs_value),2)],xvals=df_to_plot.PC_tran.unique(),type_graph = 'bar')
        pio.show(fig)
        
        fig = px.bar(df_to_plot,x='PC_tran',y='Val',color='Technologies',
                     color_discrete_map=self.color_dict_full,barmode='relative')
        title = 'PCs of the transition - {}'.format(self.case_study)
        self.custom_fig(fig,title=title,yvals = [round(-y,2),0,round(y,2)],xvals=df_to_plot.PC_tran.unique(),type_graph = 'bar',neg_value=True)
        pio.show(fig)
    
    
    def _remove_outliers(self,df):
        
        for column in df.columns:
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            Q2 = df[column].quantile(0.5)
            IQR = Q3 - Q1
            
            threshold = 1.5
            outliers = df[(df[column] < Q1 - threshold * IQR) | (df[column] > Q3 + threshold * IQR)]
            
            if not(outliers.empty):
                df.loc[outliers.index, column] = Q2
            
        return df
    
    def _fill_df_to_plot_w_zeros(self,df_to_plot):
        
        index_names = df_to_plot.index.names
        l_ind = [None] * len(index_names)
        for i,j in enumerate(index_names):
            ind = df_to_plot.index.get_level_values(j).unique()
            if j == 'Years' and not('YEAR_2020' in ind):
                ind = ind.union(['YEAR_2020'])
            l_ind[i] = ind
        
        mi_temp = pd.MultiIndex.from_product(l_ind,names=index_names)
        df_temp = pd.DataFrame(0,index=mi_temp,columns=df_to_plot.columns)
        df_temp.update(df_to_plot)
        df_to_plot = df_temp.copy()
        
        return df_to_plot
    
    def _group_tech_per_eud(self):
        tech_of_end_uses_category = self.ampl_obj.sets['TECHNOLOGIES_OF_END_USES_CATEGORY'].copy()
        del tech_of_end_uses_category["NON_ENERGY"]
        for ned in self.ampl_obj.sets['END_USES_TYPES_OF_CATEGORY']['NON_ENERGY']:
            tech_of_end_uses_category[ned] = self.ampl_obj.sets['TECHNOLOGIES_OF_END_USES_TYPE'][ned]
        df = tech_of_end_uses_category.copy()
        df['INFRASTRUCTURE'] = self.ampl_obj.sets['INFRASTRUCTURE']
        df['STORAGE'] = self.ampl_obj.sets['STORAGE_TECH']
        
        return df
    
    
    def _dict_color_full(self):
        year_balance = self.ampl_obj.get_elem('layers_in_out',type_of_elem='Param')
        elements = list(year_balance.index.unique('Resources union technologies diff storage_tech'))
        elements += self.ampl_obj.sets['STORAGE_TECH']
        elements = year_balance.index.get_level_values(1).unique()
        color_dict_full = dict.fromkeys(elements)
        categories = ['Sectors','Electricity','Heat_low_T','Heat_high_T','Mobility','Freight','Ammonia',
                   'Methanol','HVC','Conversion','Storage','Storage','Storage_daily','Resources',
                   'Infrastructure','Years_1','Years_2','Phases']
        for c in categories:
            color_dict_full.update(self.dict_color(c))
        
        color_dict_full['END_USES'] = 'lightsteelblue'
        
        return color_dict_full
    
    @staticmethod
    def dict_color(category):
        color_dict = {}
        
        if category == 'Electricity':
            color_dict = {"NUCLEAR":"deeppink", "NUCLEAR_SMR": "deeppink", "CCGT":"darkorange", "CCGT_AMMONIA":"slateblue", "COAL_US" : "black", "COAL_IGCC" : "dimgray", "PV" : "yellow", "WIND_ONSHORE" : "lawngreen", "WIND_OFFSHORE" : "green", "HYDRO_RIVER" : "blue", "GEOTHERMAL" : "firebrick", "ELECTRICITY" : "dodgerblue"}
        elif category == 'Heat_low_T':
            color_dict = {"DHN_HP_ELEC" : "blue", "DHN_COGEN_GAS" : "orange", "DHN_COGEN_WOOD" : "sandybrown", "DHN_COGEN_WASTE" : "olive", "DHN_COGEN_WET_BIOMASS" : "seagreen", "DHN_COGEN_BIO_HYDROLYSIS" : "springgreen", "DHN_BOILER_GAS" : "darkorange", "DHN_BOILER_WOOD" : "sienna", "DHN_BOILER_OIL" : "blueviolet", "DHN_DEEP_GEO" : "firebrick", "DHN_SOLAR" : "gold", "DEC_HP_ELEC" : "cornflowerblue", "DEC_THHP_GAS" : "lightsalmon", "DEC_COGEN_GAS" : "goldenrod", "DEC_COGEN_OIL" : "mediumpurple", "DEC_ADVCOGEN_GAS" : "burlywood", "DEC_ADVCOGEN_H2" : "violet", "DEC_BOILER_GAS" : "moccasin", "DEC_BOILER_WOOD" : "peru", "DEC_BOILER_OIL" : "darkorchid", "DEC_SOLAR" : "yellow", "DEC_DIRECT_ELEC" : "deepskyblue"}
        elif category == 'Heat_high_T':
            color_dict = {"IND_COGEN_GAS":"orange", "IND_COGEN_WOOD":"peru", "IND_COGEN_WASTE" : "olive", "IND_BOILER_GAS" : "moccasin", "IND_BOILER_WOOD" : "goldenrod", "IND_BOILER_OIL" : "blueviolet", "IND_BOILER_COAL" : "black", "IND_BOILER_WASTE" : "olivedrab", "IND_DIRECT_ELEC" : "royalblue"}
        elif category == 'Mobility':
            color_dict = {"TRAMWAY_TROLLEY" : "dodgerblue", "BUS_COACH_DIESEL" : "dimgrey", "BUS_COACH_HYDIESEL" : "gray", "BUS_COACH_CNG_STOICH" : "orange", "BUS_COACH_FC_HYBRIDH2" : "violet", "TRAIN_PUB" : "blue", "CAR_GASOLINE" : "black", "CAR_DIESEL" : "lightgray", "CAR_NG" : "moccasin", "CAR_METHANOL":"orchid", "CAR_HEV" : "salmon", "CAR_PHEV" : "lightsalmon", "CAR_BEV" : "deepskyblue", "CAR_FUEL_CELL" : "magenta"}
        elif category == 'Freight':
            color_dict = {"TRAIN_FREIGHT" : "royalblue", "BOAT_FREIGHT_DIESEL" : "dimgrey", "BOAT_FREIGHT_NG" : "darkorange", "BOAT_FREIGHT_METHANOL" : "fuchsia", "TRUCK_DIESEL" : "darkgrey", "TRUCK_FUEL_CELL" : "violet", "TRUCK_ELEC" : "dodgerblue", "TRUCK_NG" : "moccasin", "TRUCK_METHANOL" : "orchid"}
        elif category == 'Ammonia':
            color_dict = {"HABER_BOSCH":"tomato", "AMMONIA" : "slateblue", "AMMONIA_RE" : "blue"}
        elif category == 'Methanol':
            color_dict = {"SYN_METHANOLATION":"violet","METHANE_TO_METHANOL":"orange","BIOMASS_TO_METHANOL":"peru", "METHANOL" : "orchid", "METHANOL_RE" : "mediumvioletred"}
        elif category == "HVC":
            color_dict = {"OIL_TO_HVC":"blueviolet", "GAS_TO_HVC":"orange", "BIOMASS_TO_HVC":"peru", "METHANOL_TO_HVC":"orchid"}
        elif category == 'Conversion':
            color_dict = {"H2_ELECTROLYSIS" : "violet", "H2_NG" : "magenta", "H2_BIOMASS" : "orchid", "GASIFICATION_SNG" : "orange", "PYROLYSIS" : "blueviolet", "ATM_CCS" : "black", "INDUSTRY_CCS" : "grey", "SYN_METHANOLATION" : "mediumpurple", "SYN_METHANATION" : "moccasin", "BIOMETHANATION" : "darkorange", "BIO_HYDROLYSIS" : "gold", "METHANE_TO_METHANOL" : "darkmagenta",'SMR':'orange'}
        elif category == 'Storage':
            color_dict = {"TS_DHN_SEASONAL" : "indianred", "BATT_LI" : "royalblue", "BEV_BATT" : "deepskyblue", "PHEV_BATT" : "lightskyblue", "PHS" : "dodgerblue", "TS_DEC_HP_ELEC" : "blue", "TS_DHN_DAILY" : "lightcoral", "TS_HIGH_TEMP" : "red", "SEASONAL_NG" : "orange", "SEASONAL_H2" : "violet", "SLF_STO" : "blueviolet", "TS_DEC_DIRECT_ELEC":"darkgoldenrod", "TS_DEC_THHP_GAS": "orange", "TS_DEC_COGEN_GAS":"coral", "TS_DEC_COGEN_OIL":"darkviolet", "TS_DEC_ADVCOGEN_GAS":"sandybrown", "TS_DEC_ADVCOGEN_H2": "plum", "TS_DEC_BOILER_GAS": "tan", "TS_DEC_BOILER_WOOD":"peru", "TS_DEC_BOILER_OIL": "darkviolet", "GAS_STORAGE": "orange", "H2_STORAGE": "violet", "CO2_STORAGE": "lightgray", "GASOLINE_STORAGE": "gray", "DIESEL_STORAGE": "silver", "AMMONIA_STORAGE": "slateblue", "LFO_STORAGE": "darkviolet"}
        elif category == 'Storage_daily':
            color_dict = {"BATT_LI" : "royalblue", "BEV_BATT" : "deepskyblue", "PHEV_BATT" : "lightskyblue", "TS_DEC_HP_ELEC" : "blue", "TS_DHN_DAILY" : "lightcoral", "TS_HIGH_TEMP" : "red", "TS_DEC_DIRECT_ELEC":"darkgoldenrod", "TS_DEC_THHP_GAS": "orange", "TS_DEC_COGEN_GAS":"coral", "TS_DEC_COGEN_OIL":"darkviolet", "TS_DEC_ADVCOGEN_GAS":"sandybrown", "TS_DEC_ADVCOGEN_H2": "plum", "TS_DEC_BOILER_GAS": "tan", "TS_DEC_BOILER_WOOD":"peru", "TS_DEC_BOILER_OIL": "darkviolet"}
        elif category == 'Resources':
            color_dict = {"ELECTRICITY" : "deepskyblue", "GASOLINE" : "gray", "DIESEL" : "silver", "BIOETHANOL" : "mediumorchid", "BIODIESEL" : "mediumpurple", "LFO" : "darkviolet", "GAS" : "orange", "GAS_RE" : "gold", "WOOD" : "saddlebrown", "WET_BIOMASS" : "seagreen", "COAL" : "black", "URANIUM" : "deeppink", "WASTE" : "olive", "H2" : "violet", "H2_RE" : "plum", "AMMONIA" : "slateblue", "AMMONIA_RE" : "blue", "METHANOL" : "orchid", "METHANOL_RE" : "mediumvioletred", "CO2_EMISSIONS" : "gainsboro", "RES_WIND" : "limegreen", "RES_SOLAR" : "yellow", "RES_HYDRO" : "blue", "RES_GEO" : "firebrick", "ELEC_EXPORT" : "chartreuse","CO2_ATM": "dimgray", "CO2_INDUSTRY": "darkgrey", "CO2_CAPTURED": "lightslategrey", "RE_FUELS": 'green','NRE_FUELS':'black', 'LOCAL_RE': 'limegreen', 'IMPORTED_ELECTRICITY': 'deepskyblue'}
        elif category == 'Sectors':
            color_dict = {"ELECTRICITY" : "deepskyblue", "HEAT_HIGH_T":"red","HEAT_LOW_T_DECEN":"lightpink", "HEAT_LOW_T_DHN":"indianred", "MOB_PUBLIC":"gold", "MOB_PRIVATE":"goldenrod","MOBILITY_FREIGHT":"darkgoldenrod", "NON_ENERGY": "darkviolet", "INFRASTRUCTURE":"grey","HVC":"cyan",'STORAGE':'chartreuse', 'OTHERS':'gainsboro'}
        elif category == 'Infrastructure':
            color_dict = {'EFFICIENCY': 'lime','DHN': 'orange','GRID': 'gold'}
        elif category == 'Years_1':
            color_dict = {'YEAR_2020': 'blue','YEAR_2025': 'orange','YEAR_2030': 'green', 'YEAR_2035': 'red', 'YEAR_2040': 'purple', 'YEAR_2045': 'brown', 'YEAR_2050':'pink'}
        elif category == 'Years_2':
            color_dict = {'2020': 'blue','2025': 'orange','2030': 'green', '2035': 'red', '2040': 'purple', '2045': 'brown', '2050':'pink'}
        elif category == 'Phases':
                color_dict = {'2015_2020': 'blue','2020_2025': 'orange','2025_2030': 'green', '2030_2035': 'red', '2035_2040': 'purple', '2040_2045': 'brown', '2045_2050':'pink'}
            
        return color_dict
    
    @staticmethod
    def custom_fig(fig,title,yvals,xvals=['2020','2025','2030','2035','2040',
                        '2045','2050'], ftsize=18,annot_text=None,
                   type_graph = None, neg_value = False, flip = False):
    
        def round_repdigit(n, ndigits=0):     
            if n != 0:
                i = int(np.ceil(np.log10(abs(n))))
                x = np.round(n, ndigits-i)
                if i-ndigits >= 0:
                    x = int(x)
                return x     
            else:
                return 0
            
        gray = 'rgb(90,90,90)' 
        color = gray
        
        fig.update_layout(
            xaxis_color=color, yaxis_color=color,
            xaxis_mirror=False, yaxis_mirror=False,
            yaxis_showgrid=False, xaxis_showgrid=False,
            yaxis_linecolor='white', xaxis_linecolor='white',
            xaxis_tickfont_size=ftsize, yaxis_tickfont_size=ftsize,
            showlegend=False,
        )
        
        if title != None:
            fig.update_layout(
                title_text=title,titlefont=dict(family="Raleway",size=ftsize+10)
                )
        
        if type_graph == None:
            fig.update_xaxes(dict(ticks = "inside", ticklen=10))
            fig.update_xaxes(tickangle= 0,tickmode = 'array',tickwidth=2,tickcolor=gray,
                                tickfont=dict(
                                      family="Rawline",
                                      size=ftsize
                                  ))
        fig.update_yaxes(dict(ticks = "inside", ticklen=10))
        if type_graph in ['strip','bar']:
            fig.update_xaxes(dict(ticks = "inside", ticklen=10))
            
        
        if not(flip):
            fig.update_yaxes(tickangle= 0,tickmode = 'array',tickwidth=2,tickcolor=gray,
                                tickfont=dict(
                                      family="Rawline",
                                      size=ftsize
                                  ))
        
        fig.update_layout(
            yaxis = dict(
                tickmode = 'array',
                tickvals = fig.layout.yaxis.tickvals,
                ticktext = list(map(str,yvals))
                ))
        
                
        factor=0.05
        nrepdigit = 0
        
        fig.update_yaxes(tickvals=yvals)
        
        xstring = isinstance(fig.data[0].x[0],str)
        
        if xstring: ## ONLY VALID IF THE FIRST TRACE HAS ALL VALUES
            xvals = xvals
            xmin = 0
            xmax = len(xvals) - 1
        else:
            if not(flip):
                xvals = pd.Series(sum([list(i.x) for i in fig.data],[]))
                xmin = xvals.min()
                xmax = xvals.max()
            else:
                xmin = min(xvals)
                xmax = max(xvals)
            xampl = xmax-xmin
        
        
        if xstring:
            if fig.layout.xaxis.range is None:
                if type_graph in ['bar','strip']:
                    fig.layout.xaxis.range = [xmin-factor*15, xmax+factor*15]
                elif type_graph == 'scatter':
                    fig.layout.xaxis.range = [xmin-factor*6, xmax+factor*6]
                else:
                    fig.layout.xaxis.range = [xmin-factor*3, xmax+factor*3]
            if fig.layout.xaxis.tickvals is None:
                fig.layout.xaxis.tickvals = xvals
        else:
            if fig.layout.xaxis.range is None:
                fig.layout.xaxis.range = [xmin-xampl*factor, xmax+xampl*factor]
            if fig.layout.xaxis.tickvals is None:
                fig.layout.xaxis.tickvals = [round_repdigit(x, nrepdigit) for x in [xmin, xmax]]
        
        if flip:
            fig.update_xaxes(tickvals=xvals)
            
        
        fig.layout.xaxis.tickvals = sorted(fig.layout.xaxis.tickvals)
        fig.layout.xaxis.range = sorted(fig.layout.xaxis.range)
        
        
        yvals = yvals
        
        ystring = isinstance(fig.data[0].y[0],str)
        
        if ystring: ## ONLY VALID IF THE FIRST TRACE HAS ALL VALUES
            ymin = 0
            ymax = len(yvals) - 1
        else:
            ymin = min(yvals)
            ymax = max(yvals)
        yampl = ymax-ymin
        
        if fig.layout.yaxis.range is None:
            fig.layout.yaxis.range = [ymin-yampl*factor, ymax+yampl*factor]
        if fig.layout.yaxis.tickvals is None:
            fig.layout.yaxis.tickvals = [round_repdigit(y, nrepdigit) for y in [ymin, ymax]]
        
        if not(ystring):
            fig.layout.yaxis.tickvals = sorted(fig.layout.yaxis.tickvals)
        fig.layout.yaxis.range = sorted(fig.layout.yaxis.range)
        
        fig.update_layout(xaxis_title=None, yaxis_title=None)
        
        if neg_value:
            if not(flip):
                fig.add_shape(x0=xmin,x1=xmax,
                          y0=0,y1=0,
                          type='line',layer="below",
                          line=dict(color=color,width=1),opacity=0.5)
            else:
                fig.add_shape(x0=0,x1=0,
                          y0=ymin,y1=ymax,
                          type='line',layer="below",
                          line=dict(color=color,width=1),opacity=0.5)
                
        
        fig.add_shape(x0=fig.layout.xaxis.range[0],x1=fig.layout.xaxis.range[0],
                  y0=fig.layout.yaxis.tickvals[0],y1=fig.layout.yaxis.tickvals[-1],
                  type='line',layer="above",
                  line=dict(color=color,width=2),opacity=1)
        
        # if type_graph in [None,'bar']:
        fig.add_shape(x0=xmin,x1=xmax,
                  y0=fig.layout.yaxis.range[0],y1=fig.layout.yaxis.range[0],
                  type='line',layer="above",
                  line=dict(color=color, width=2),opacity=1)
        
        if type_graph in ['scatter']:
            fig.update_layout({ax:{"visible":False, "matches":None} for ax in fig.to_dict()["layout"] if "xaxis" in ax})
        
        if type_graph in ['strip']:
            if not(flip):
                fig.add_shape(x0=0.5,x1=0.5,
                          y0=ymin,y1=ymax,
                          type='line',layer="above",
                          line=dict(color=color,width=2,dash="dot"),opacity=1)
                fig.add_shape(x0=xmax-0.5,x1=xmax-0.5,
                          y0=ymin,y1=ymax,
                          type='line',layer="above",
                          line=dict(color=color,width=2,dash="dot"),opacity=1)
            # else:
                # fig.add_shape(x0=xmin,x1=xmax,
                #           y0=0.5,y1=0.5,
                #           type='line',layer="above",
                #           line=dict(color=color,width=2,dash="dot"),opacity=1)
                # fig.add_shape(x0=xmin,x1=xmax,
                #           y0=ymax-0.5,y1=ymax-0.5,
                #           type='line',layer="above",
                #           line=dict(color=color,width=2,dash="dot"),opacity=1)
        
        fig.update_layout(margin_b = 10, margin_r = 30, margin_l = 30)#,margin_pad = 20)

    