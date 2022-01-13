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

# From http://www.jtrive.com/determining-histogram-bin-width-using-the-freedman-diaconis-rule.html
def freedman_diaconis(data, returnas="width"):
    """
    Use Freedman Diaconis rule to compute optimal histogram bin width. 
    ``returnas`` can be one of "width" or "bins", indicating whether
    the bin width or number of bins should be returned respectively. 


    Parameters
    ----------
    data: np.ndarray
        One-dimensional array.

    returnas: {"width", "bins"}
        If "width", return the estimated width for each histogram bin. 
        If "bins", return the number of bins suggested by rule.
    """
    data = np.asarray(data, dtype=np.float_)
    IQR  = stats.iqr(data, rng=(25, 75), scale="raw", nan_policy="omit")
    N    = data.size
    bw   = (2 * IQR) / np.power(N, 1/3)

    if returnas=="width":
        result = bw
    else:
        datmin, datmax = data.min(), data.max()
        datrng = datmax - datmin
        result = int((datrng / bw) + 1)
    return(result)
        
    
    
    
    