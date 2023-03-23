#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 08 2022

@author: rixhonx
"""

from pathlib import Path

import os,sys
import csv
import pickle
import pandas as pd
from datetime import datetime
from time import time

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
    output_file : pathlib.Path
        Path towards the output file where to pickle the results
    expl_text : String
        Small description of the case study

    """

    def __init__(self, ampl_pre, output_file, expl_text):

        self.ampl_pre = ampl_pre
        self.pth_output_all = Path(output_file).parent.parent
        self.output_file = output_file
        self.expl_text = expl_text
    
    def init_storage(self,ampl_obj):
        
        Years = ampl_obj.sets['YEARS'].copy()
        if 'YEAR_2015' in Years:
            Years.remove('YEAR_2015')
        
        Phases = ampl_obj.sets['PHASE'].copy()

        self.results = dict.fromkeys(list(ampl_obj.results.keys()))

        for k in self.results:
            result = ampl_obj.results[k]
            if k in ['TotalCost','TotalGwp']:
                self.results[k] = pd.DataFrame(index=Years,columns=result.columns)
            elif k == 'Cost_return':
                index_elem = result.index.get_level_values(1).unique()
                last_year_wnd = [years[-1] for years in self.ampl_pre.years_opti]
                multi_ind = pd.MultiIndex.from_product([last_year_wnd,index_elem],names = result.index.names)
                self.results[k] = pd.DataFrame(index=multi_ind,columns=result.columns)
            elif k in ['New_old_decom','C_inv_phase_tech','C_op_phase_tech','C_op_phase_res']:
                index_elem = result.index.get_level_values(1).unique()
                multi_ind = pd.MultiIndex.from_product([Phases,index_elem],names = result.index.names)
                self.results[k] = pd.DataFrame(index=multi_ind,columns=result.columns)
            elif k in ['F_decom']:
                index_elem = result.index.get_level_values(2).unique()
                multi_ind = pd.MultiIndex.from_product([Phases,Phases,index_elem],names = result.index.names)
                self.results[k] = pd.DataFrame(index=multi_ind,columns=result.columns)
            elif k in ['C_inv_phase']:
                self.results[k] = pd.DataFrame(index=Phases,columns=result.columns)
            else:
                index_elem = result.index.get_level_values(1).unique()
                multi_ind = pd.MultiIndex.from_product([Years,index_elem],names = result.index.names)
                self.results[k] = pd.DataFrame(index=multi_ind,columns=result.columns)
    
    def update_storage(self, ampl_obj,curr_years_wnd,i):
        for k in self.results:
            results = ampl_obj.results[k]
            if k in ['New_old_decom','F_decom','C_inv_phase','C_inv_phase_tech','C_op_phase_tech','C_op_phase_res']:
                phases_up_to = ['2015_2020'] + self.ampl_pre.phases_up_to[i]
                temp_res = results.loc[results.index.get_level_values('Phases').isin(phases_up_to),:]
            else:
                temp_res = results.loc[results.index.get_level_values('Years').isin(curr_years_wnd),:]
            temp = [self.results[k],temp_res]
            temp = pd.concat(temp)
            self.results[k] = temp.loc[~temp.index.duplicated(keep='last')]
            self.results[k] = self.results[k].sort_index()
    
    def clean_collector(self):
        for k in self.results:
            self.results[k].dropna(how='all',inplace=True)

    def pkl(self):

        case_name = os.path.basename(os.path.normpath(Path(self.output_file).parent))
        recap_file = os.path.join(self.pth_output_all,'_Recap.csv')
        t = datetime.fromtimestamp(time())
        if not os.path.exists(Path(recap_file)):
            Path(recap_file).parent.mkdir(parents=True,exist_ok=True)
            with open(recap_file,'w+') as f:
                writer = csv.writer(f)
                writer.writerow(['Case_study','Comment','Date_Time'])
        df = pd.read_csv(recap_file)
        if case_name in df.Case_study.values:
            df.loc[df['Case_study'] == case_name,'Comment'] = self.expl_text
            df.loc[df['Case_study'] == case_name,'Date_Time'] = t
            df.to_csv(recap_file, index=False)                                              
        else:
            with open(recap_file, 'a') as f:
                writer = csv.writer(f)
                writer.writerow([case_name,self.expl_text,t])
                
        if not os.path.exists(Path(self.output_file).parent):
            os.makedirs(Path(self.output_file).parent)
        
        open_file = open(self.output_file,"wb")
        pickle.dump(self.results,open_file)
        open_file.close()
