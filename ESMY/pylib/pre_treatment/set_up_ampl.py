#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 11 09:56:37 2021

@author: xrixhon
"""

import os

def set_up_ampl(ampl_obj, pth_model, ampl_options):
    
    ## AMPL .mod and .dat
    
    ampl_obj.read(os.path.join(pth_model,'PESTD_model.mod'))
    ampl_obj.read(os.path.join(pth_model,'store_variables.mod'))
    
    ampl_obj.readData(os.path.join(pth_model,'seq_opti.dat'))
    ampl_obj.readData(os.path.join(pth_model,'PESTD_data_year_related.dat'))
    ampl_obj.readData(os.path.join(pth_model,'PESTD_data_efficiencies.dat'))
    ampl_obj.readData(os.path.join(pth_model,'PESTD_12TD.dat'))
    ampl_obj.readData(os.path.join(pth_model,'PESTD_data_set_AGE.dat'))
    ampl_obj.readData(os.path.join(pth_model,'PESTD_data_remaining_wnd.dat'))
    ampl_obj.readData(os.path.join(pth_model,'PESTD_data_all_years.dat'))
    ampl_obj.readData(os.path.join(pth_model,'PESTD_data_decom_allowed.dat'))
    
    ampl_obj.read(os.path.join(pth_model,'PESTD_initialise_2015.mod'))
    ampl_obj.read(os.path.join(pth_model,'fix_2.mod'))

    ## AMPL OPTIONS
    ampl_obj.setOption("solver", "cplex")
    
    for o in ampl_options:
        ampl_obj.setOption(o, ampl_options[o])
    
    # ampl_obj.setOption("log_file", os.path.join(pth_model,'log.txt')) #write the log in a .txt file. Create the file before running
    # ampl_obj.setOption("presolve", "0")
    # ampl_obj.setOption("times", "0") # show time
    # ampl_obj.setOption("gentimes", "0") # show time

    # ampl_obj.setOption("cplex_options","baropt predual=-1 crossover=0 barstart= 4")
    # # ampl_obj.setOption("presolve_eps", "8.53e-10")
    # ampl_obj.setOption("cplex_options","bardisplay=0")
    # ampl_obj.setOption("cplex_options","prestats=0")
    # ampl_obj.setOption("cplex_options","display=0")
    # ampl_obj.setOption("cplex_options","timelimit=64800")
    
    # ampl_obj.setOption("show_boundtol", "0") # To suppress messages about abs_boundtol and rel_boundtol, since the dual variables are not crucial to the analysis of the results
        