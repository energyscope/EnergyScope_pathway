#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 08 2022

@author: rixhonx
"""

from pathlib import Path

import os,sys
from copy import deepcopy
import re

pylibPath = os.path.abspath("../pylib")
if pylibPath not in sys.path:
    sys.path.insert(0, pylibPath)

class AmplPostProcessor:

    """

    The AmplPostProcessor class allows to transfer solutions from one optimisation window to
    the other and save the relevant outputs on the way 

    Parameters
    ----------
    mod_path : pathlib.Path
        Path towards the files of the model
    list_year : list(string)
        List specifying the whole set of YEARS
    list_phase : list(string)
        List specifying the whole set of PHASE
    n_years_wnd : int
        Duration in years of the time windows. To avoid overshooting the end of the time horizon,
        the last window of optimisation might be shorter than n_years_wnd
    n_years_overlap : int
        Duration in years of the overlap between two windows of optimisation
    t_phase : int
        Duration in years of a phase

    """

    def __init__(self, ampl_obj, out_path, PKL_list):

        self.ampl_obj = ampl_obj
        self.mod_path = ampl_obj.dir
        self.variables = ampl_obj.ampl.getVariables()
        self.out_path = out_path
        self.PKL_dict = dict.fromkeys(PKL_list)
    

    
    def set_init_sol(self):
    
        fix_0 = os.path.join(self.mod_path,'fix_0.mod')
        fix = os.path.join(self.mod_path,'fix.mod')

        with open(fix_0,'w+', encoding='utf-8') as fp:
            for k in self.ampl_obj.sets['SET_INIT_SOL']:
                for i, v in self.variables[k]:
                    print('fix {}:={};'.format(v.name(),v.value()), file = fp)
                print("\n", file = fp)
                    
        with open(fix_0) as fin, open(fix,'w+', encoding='utf-8') as fout:
            for line in fin:
                line = line.replace("_up_to","")
                line = line.replace("_next","")
                fout.write(line)
        
        os.remove(fix_0)
        
