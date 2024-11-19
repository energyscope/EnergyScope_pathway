# -*- coding: utf-8 -*-
"""
Created on Mon May 17 10:21 2021

@author: Xavier Rixhon
"""

#%% Import Python packages and paths creation
import os, sys
from pathlib import Path

import time # To print the time needed for one optimisation
import rheia.UQ.uncertainty_quantification as rheia_uq

curr_dir = Path(os.path.dirname(__file__)) # Current directory
pth_esmy = os.path.join(curr_dir.parent,'ESMY') # Directory with ES files
pth_model = os.path.join(pth_esmy,'STEP_2_Pathway_Model') # Directory with
                                                          # Step-2 files
pth_output_all = os.path.join(curr_dir.parent,'out') # Directory to store
                                                     # outputs

pymodPath = os.path.abspath(os.path.join(curr_dir.parent,'pylib'))
sys.path.insert(0, pymodPath)

#%% Linked objects

from ampl_object import AmplObject
from ampl_preprocessor import AmplPreProcessor
from ampl_collector import AmplCollector
from ampl_graph import AmplGraph


#%% Options of this run_main.py

type_of_model = 'TD' # Define the time resolution of the model. 'TD' for hourly
                     # model and 'MO' for monthly model

nbr_tds = 12 # Number of typical days per year to consider. Can choose between
             # 2, 4, 6, 8, 10, 12 and 20. Per Limpens et al. (2019), 12 seemed 
             # the best trade-off between accuracy and computational time.

gwp_budget = True # True if limiting the overall GWP of the whole transition
gwp_budget_val = 1224935.4 # GWP budget for the whole transition [ktCO2,eq]
CO2_neutrality_2050 = False # True if setting the GWP of 2050 to carbon-
                            # neutrality
CO2_neutrality_2050_val = 3406.92 # Value equivalent to CO2-neutrality in 2050
                                  # [ktCO2,eq]
                                  
run_opti = False # True to run optimisation
graph = False # True to plot graphs for deterministic run
graph_comp = False # True to plot comparative graphs between two deterministic
                   # runs

case_study = 'test_test' # Give here the name of the case study for 
                    # deterministic run
expl_text = 'test_text' # Give here explanation text to describe the
                        # case study
        
#%% Join the .dat and .mod files depending on the type of model (MO or TD).
# ! The order of the files in the list is important !

if type_of_model == 'MO':
    mod_1_path = [os.path.join(pth_model,'PESMO_model.mod'),
                os.path.join(pth_model,'PESMO_store_variables.mod'),
                os.path.join(pth_model,'PES_store_variables.mod')]
    mod_2_path = [os.path.join(pth_model,'PESMO_initialise_2020.mod'),
                  os.path.join(pth_model,'fix.mod')]
    dat_path = [os.path.join(pth_model,'PESMO_data_all_years.dat')]
else:
    mod_1_path = [os.path.join(pth_model,'PESTD_model.mod'),
            os.path.join(pth_model,'PESTD_store_variables.mod'),
            os.path.join(pth_model,'PES_store_variables.mod')]
    mod_2_path = [os.path.join(pth_model,'PESTD_initialise_2020.mod'),
              os.path.join(pth_model,'fix.mod')]
    dat_path = [os.path.join(pth_model,'PESTD_data_all_years.dat'),
                os.path.join(pth_model,'PESTD_{}TD.dat'.format(nbr_tds))]

dat_path += [os.path.join(pth_model,'PES_data_all_years.dat'),
             os.path.join(pth_model,'PES_seq_opti.dat'),
             os.path.join(pth_model,'PES_data_year_related.dat'),
             os.path.join(pth_model,'PES_data_efficiencies.dat'),
             os.path.join(pth_model,'PES_data_set_AGE_2020.dat')]
dat_path_0 = dat_path + [os.path.join(pth_model,'PES_data_remaining.dat'),
             os.path.join(pth_model,'PES_data_decom_allowed_2020.dat')]

dat_path += [os.path.join(pth_model,'PES_data_remaining_wnd.dat'),
             os.path.join(pth_model,'PES_data_decom_allowed_2020.dat')]

#%% Options for ampl and gurobi
gurobi_options = ['predual=-1',
                'method = 2', # 2 is for barrier method
                'crossover=0', #-1 let gurobi decides
                'prepasses = 3',
                'barconvtol=1e-6',
                'presolve=-1'] # Not a good idea to put it to 0 if the model is
                               # too big

gurobi_options_str = ' '.join(gurobi_options)

ampl_options = {'show_stats': 1,
                'log_file': os.path.join(pth_model,'log.txt'),
                'presolve': 10,
                'presolve_eps': 1e-6,
                'presolve_fixeps': 1e-6,
                'show_boundtol': 0,
                'gurobi_options': gurobi_options_str,
                '_log_input_only': False}

###############################################################################
''' main script '''
###############################################################################

#%% Actual script part
if __name__ == '__main__':
    
    N_year_opti = 25 # Duration of the time window to optimise. Must be a
                     # multiple of 5, between 5 and 25.
    N_year_overlap = 0 # Duration of the overlap between two consecutives
                       # time windows. Must be a multiple of 5 and smaller 
                       # than the duration of the time window
        
    # To do once at initialisation of the environment
    i = 0
    
    output_folder = os.path.join(pth_output_all,case_study)
    output_file = os.path.join(output_folder,'_Results.pkl')
    
    # Creation of Ampl object to instantiate pre-processor and collector
    ampl_0 = AmplObject(mod_1_path, mod_2_path, dat_path_0, ampl_options,
                        type_model = type_of_model)
    ampl_0.clean_history()
    ampl_pre = AmplPreProcessor(ampl_0, N_year_opti, N_year_overlap)
    ampl_collector = AmplCollector(ampl_pre, output_file, expl_text)
    
    # To keep track of the time needed to run a whole-horizon optimisation
    t = time.time()

    #%% Run optimisation
    if run_opti:
        
        # For-loop for every time window of the transition
        for i in range(len(ampl_pre.years_opti)):

            t_i = time.time()
            
            # Update sets of EnergyScope depending on the time window
            curr_years_wnd = ampl_pre.write_seq_opti(i).copy()
            ampl_pre.remaining_update(i)
            
            # Ampl object created for each time window
            ampl = AmplObject(mod_1_path, mod_2_path, dat_path, 
                              ampl_options, type_model = type_of_model)
            ampl.ampl.eval("shell 'gurobi -v';")
            
            # Set the actual gwp limit in 2020
            ampl.set_params('gwp_limit',{('YEAR_2025'):124000})
            
            if gwp_budget:
                ampl.set_params('gwp_limit_transition',gwp_budget_val)
                
            if CO2_neutrality_2050:
                ampl.set_params('gwp_limit',{('YEAR_2050'):
                                             CO2_neutrality_2050_val})

            #%% Run deterministic optimisation and collect results
            solve_result = ampl.run_ampl()
            ampl.get_results()
            
            # Initialisation of the collector
            if i==0: 
                ampl_collector.init_storage(ampl)
            else:
                curr_years_wnd.remove(ampl_pre.year_to_rm)
            
            # Filling in the collector with new results
            ampl_collector.update_storage(ampl,curr_years_wnd,i)
            
            # Set initial conditions for the start of the next time window
            ampl.set_init_sol()
            
            elapsed_i = time.time()-t_i
            print('Time to solve the window #'+str(i+1)+': ',elapsed_i)
            
            # When reaching the end of the transition, clean and pickle the 
            # collector of results
            if i == len(ampl_pre.years_opti)-1:
                elapsed = time.time()-t
                print('Time to solve the whole problem: ',elapsed)
                
                ampl_collector.clean_collector()
                ampl_collector.pkl()
                break
            
    #%% Plot graphs for deterministic runs
    if graph:
        case_study = 'case_study'
        
        output_file = pth_output_all + '/' + case_study + '/_Results.pkl'
        ampl_graph = AmplGraph(output_file, ampl_0, case_study)
        # ampl_graph.graph_resource() # Primary energy mix
        # ampl_graph.graph_cost() # Total annual system cost 
        # ampl_graph.graph_gwp_per_sector() # GWP per energy sector
        # ampl_graph.graph_cost_inv_phase_tech() # Cumulative investment costs
        # ampl_graph.graph_cost_op_phase() # Cumulative operational costs
        # ampl_graph.graph_cost_return() # Salvage value

        
        # ampl_graph.graph_layer() # Prod-Cons graph per layer
        # ampl_graph.graph_tech_cap() # Installed capapcities per sector
        # ampl_graph.graph_load_factor() # Load factor per sector
        # df_unused,_ = ampl_graph.graph_load_factor_scaled() # Scaled load factor
        
    #%% Plot graphs to compare two different deterministic runs:
      # case_study: the studied case study
      # case_study_1: the reference case study
      # Graphs present the absolute difference: case_study - case_study_1
    if graph_comp:
        case_study = 'case_study'
        output_file = pth_output_all + '/' + case_study + '/_Results.pkl'
        ampl_graph = AmplGraph(output_file, ampl_0, case_study)
        output_folder_2 = os.path.join(pth_output_all,case_study)
        output_file_2 = os.path.join(output_folder_2,'_Results.pkl')
        
        # Reference case: TD-Perfect foresight
        case_study_1 = 'case_ref'
        output_folder_1 = os.path.join(pth_output_all,case_study_1)
        output_file_1 = os.path.join(output_folder_1,'_Results.pkl')
        

        output_files = [output_file_1,output_file_2]
        
        # ampl_graph.graph_comparison(output_files,'C_inv_phase_tech')
        # ampl_graph.graph_comparison(output_files,'C_op_phase')
        # ampl_graph.graph_comparison(output_files,'Resources')
        # ampl_graph.graph_comparison(output_files,'Cost_return')
        # ampl_graph.graph_comparison(output_files,'Total_trans_cost')
        # ampl_graph.graph_comparison(output_files,'Total_system_cost')
        # ampl_graph.graph_comparison(output_files,'Tech_cap')
        # ampl_graph.graph_comparison(output_files,'Layer')
        # ampl_graph.graph_comparison(output_files,'GWP_per_sector')
        # ampl_graph.graph_comparison(output_files,'Load_factor')

        
    ###############################################################################
    ''' main script ends here '''
    ###############################################################################
        
