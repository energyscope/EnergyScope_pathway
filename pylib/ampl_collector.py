#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 08 2022

@author: rixhonx
"""

from pathlib import Path

import os,sys
from copy import deepcopy
import pickle
import pandas as pd

pylibPath = os.path.abspath("../pylib")
if pylibPath not in sys.path:
    sys.path.insert(0, pylibPath)

class AmplCollector:

    """

    The AmplCollector class allows to store interesting results/outputs along the
    different time windows

    Parameters
    ----------
    ampl_obj : AmplObject object of ampl_object module
        Ampl object containing the optimisation problem and its attributes
    n_years_wnd : int
        Duration in years of the time windows. To avoid overshooting the end of the time horizon,
        the last window of optimisation might be shorter than n_years_wnd
    n_years_overlap : int
        Duration in years of the overlap between two windows of optimisation
    t_phase : int
        Duration in years of a phase

    """

    def __init__(self, ampl_obj, output_file):

        self.ampl_obj = ampl_obj
        self.PKL_save = dict.fromkeys(ampl_obj.sets['STORE_RESULTS'])
        self.init_storage()
        self.output_file = output_file
    
    def init_storage(self):
            
        Res = self.ampl_obj.sets['RESOURCES']
        Tech = self.ampl_obj.sets['TECHNOLOGIES']
        Storage = self.ampl_obj.sets['STORAGE_TECH']
        Tech_minus_sto = [x for x in Tech if x not in Storage]
        Tech_plus_res = Tech_minus_sto + Res

        Eut = self.ampl_obj.sets['END_USES_TYPES']
        
        Layers = self.ampl_obj.sets['LAYERS']
        
        Years = self.ampl_obj.sets['YEARS']
        
        index_Tech_Prod_Cons = pd.MultiIndex.from_product([Years, Layers, Tech_plus_res],names = ['Year','Layer','Technology'])
        index_RES = pd.MultiIndex.from_product([Years, Res],names = ['Year','Resource'])
        index_Tech_Cap = pd.MultiIndex.from_product([Years, Tech],names = ['Year','Technology'])
        index_EUD = pd.MultiIndex.from_product([Years, Layers],names = ['Year','Layer'])
        index_C_INV = pd.MultiIndex.from_product([Years, Tech],names = ['Year','Technology'])
        index_C_OP_MAINT = pd.MultiIndex.from_product([Years, Res + Tech],names = ['Year','Resource_Technology'])
        index_eud = pd.MultiIndex.from_product([Years, Layers, ['EUD']],names = ['Year','Layer','Technology'])
        
        RES = pd.DataFrame(0,index=index_RES, columns=['Value'])
        Tech_Cap = pd.DataFrame(0,index=index_Tech_Cap, columns=['Value'])
        Tech_Prod_Cons = pd.DataFrame(0, index=index_Tech_Prod_Cons, columns=['Value'])
        EUD = pd.DataFrame(0, index=index_EUD, columns=['Value'])
        C_INV = pd.DataFrame(0,index=index_C_INV, columns=['Value'])
        C_OP_MAINT = pd.DataFrame(0,index=index_C_OP_MAINT, columns=['Value'])

        self.PKL_save['Res_wnd'] = RES
        self.PKL_save['Tech_wnd'] = Tech_Prod_Cons
        self.PKL_save['F_wnd'] = Tech_Cap
        self.PKL_save['EUD_wnd'] = EUD
        self.PKL_save['C_inv_wnd'] = C_INV
        self.PKL_save['C_op_maint_wnd'] = C_OP_MAINT

    def update_storage(self, dict_outputs, curr_years_wnd):
        for k in self.PKL_save:
            df_output = dict_outputs[k]
            temp = df_output.reset_index()
            if temp.shape[1] == 3:
                self.PKL_save[k].loc[(curr_years_wnd,slice(None))] = df_output.loc[(curr_years_wnd,slice(None))]
            else:
                self.PKL_save[k].loc[(curr_years_wnd,slice(None),slice(None))] = df_output.loc[(curr_years_wnd,slice(None),slice(None))]
    
    def pkl(self):
        open_file = open(self.output_file,"wb")
        pickle.dump(self.PKL_save,open_file)
        open_file.close()

