#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 09:35:22 2021

@author: xrixhon
"""

import pandas as pd
from .dict_color import dict_color as dc
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import plotly.express as px
from plotly.offline import plot


def toPandasDF(matrix):
    headers = matrix.getHeaders()
    columns = {header: list(matrix.getColumn(header)) for header in headers}
    df0 = pd.DataFrame(columns)
    df1 = df0.pivot(index=df0.columns[0], columns=df0.columns[1], values=df0.columns[2])
    df1.index.name = None #To get rid of multilevel index after using pivot table in pandas
    
    return df1

def TDtoYEAR(array_TD,Dict_TDofP):
    l_to_year = np.zeros((8760,1))
    for i in range(365):
        k = i*24+1
        td = Dict_TDofP[k]
        l_to_year[i*24:(i+1)*24] = array_TD[:,int(td-1), None]
    return l_to_year
    

def toPandasDict_Ft(matrix):
    Dict_Ft = {}
    dict_mat = matrix.toDict()
    headers = matrix.getHeaders()
    columns = {header: list(matrix.getColumn(header)) for header in headers}
    
    year = columns['index0']
    tech = columns['index1']
    layer = columns['index2']
    
    for l in set(layer):
        df_ft = pd.DataFrame(index=set(year), columns =set(tech))
        for y in year:
            for t in tech:
                df_ft.at[y,t] = dict_mat[y,t,l]
        df_ft = df_ft.dropna(axis = 1, how = 'all')
        Dict_Ft[l] = df_ft
    
    return Dict_Ft
    

def toPandasDict_H_TD_ofP(Periods, Set):
    Dict_H_TD_ofP = {}
    for i in range(len(Periods)):
        Dict_H_TD_ofP[i+1] = Set[i+1].getValues().toList()[0]
    
    return Dict_H_TD_ofP

def cleanDF(df):
    df = df.dropna(how='all')
    df = df.dropna(axis = 1, how = 'all')
    df = df.fillna(0)
    
    return df

def colorList(ListOfElement,sector):
    color_dict = dc.dict_color(sector)
    color_list = [""]*len(ListOfElement)
    
    for i in range(len(ListOfElement)):
        color_list[i] = color_dict[ListOfElement[i]]
    
    return color_list

def to_pd(amplpy_df):
# function to transform an amplpy df into a pd df
    headers = amplpy_df.getHeaders()
    columns = {header: list(amplpy_df.getColumn(header)) for header in headers}
    df = pd.DataFrame(columns)
    
    return df

def to_pd_pivot(amplpy_df, in_type = 'Def'):
# function to transform an amplpy df into a pd df
    nindices = amplpy_df.getNumIndices()
    headers = amplpy_df.getHeaders()
    columns = {header: list(amplpy_df.getColumn(header)) for header in headers}
    df = pd.DataFrame(columns)
    if nindices==1:
        df = df.set_index(headers[0])
        df.index.name = None # get rid of the name of the index (multilevel)
    elif nindices==2:
        df = df.pivot(index=headers[0], columns=headers[1], values=headers[2])
        df.index.name = None # get rid of the name of the index (multilevel)
    elif nindices==3:
        dic = dict()
        if in_type == 'F_t':
            for i in set(columns[headers[2]]):
                dic[i] = df[df[headers[2]]==i].pivot(index=headers[0], columns=headers[1], values=headers[3])
                dic[i].index.name = None # to get rid of name (multilevel)
        else:
            for i in set(columns[headers[0]]):
                dic[i] = df[df[headers[0]]==i].pivot(index=headers[2], columns=headers[1], values=headers[3])
                dic[i].index.name = None # to get rid of name (multilevel)
        df = dic
    elif nindices==4:
        dic = dict()
        for i in set(columns[headers[0]]):
            dic[i] = dict()
            for j in set(columns[headers[3]]):
                dic[i][int(j)] = df.loc[(df[headers[0]]==i) & (df[headers[3]]==j),:].pivot(index=headers[2], columns=headers[1], values=headers[4])
                dic[i][int(j)].index.name = None # to get rid of name (multilevel)
        df = dic
    
    return df

def scale_marginal_cost(Dict_TDofP,sp):
    L = list(Dict_TDofP.values())
    unique = set(L)
    freq_TD = [0 for i in range(len(unique))]
    for i in unique:
        freq_TD[int(i)-1] = 1/(L.count(i)/24)
    
    
    sp_scaled = (sp*freq_TD)
    return sp_scaled
        
def graph_prod_cons(Tech_Prod_Cons, Plot_list, n_year_opti,n_year_overlap, mode = 'Prod_Cons'):
    
    index = Tech_Prod_Cons.index.names
    
    px.defaults.template = "simple_white"
    
    t = 100
    
    DF_prod = pd.DataFrame(columns=index + ['Value'])
    DF_cons = pd.DataFrame(columns=index + ['Value'])
    
    for l in Plot_list:
        df = Tech_Prod_Cons.loc(axis=0)[slice(None),l,slice(None)]
        
        tresh_prod = df.max()/t
        df_prod = df.loc[(df>tresh_prod).any(axis=1)]
        df_prod = df_prod.reset_index(index)

        fig_prod = px.area(df_prod, x='Year', y='Value', color='Technology', title=l+'_prod_{}_{}'.format(n_year_opti,n_year_overlap),
                           category_orders={'Year': df_prod["Year"]})
        fig_prod.update_traces(mode='none')
        plot(fig_prod)
        
        tresh_cons = df.min()/t
        df_cons = df.loc[(df<tresh_cons).any(axis=1)]
        df_cons = df_cons.reset_index(index)
        
        fig_cons = px.area(df_cons, x='Year', y='Value', color='Technology', title=l+'_cons_{}_{}'.format(n_year_opti,n_year_overlap),
                           category_orders={'Year': df_cons["Year"]})
        fig_cons.update_traces(mode='none')
        plot(fig_cons)
        
        DF_prod = pd.concat([DF_prod, df_prod], ignore_index = True, axis = 0)
        DF_cons = pd.concat([DF_cons, df_cons], ignore_index = True, axis = 0)
    
    
    
    