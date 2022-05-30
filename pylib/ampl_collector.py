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

    def __init__(self, ampl_obj, PKL_list):

        self.ampl_obj = ampl_obj
        self.PKL_dict = dict.fromkeys(PKL_list)
    

    def init_storage(self):
        s = self.ampl_obj.sets['STORE_RESULTS']
        vars = self.ampl_obj.ampl.getVariables()
        
