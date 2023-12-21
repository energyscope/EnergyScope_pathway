# -*- coding: utf-8 -*-
"""
Created on Mon May 17 10:21 2021

@author: Xavier Rixhon
"""

import os, sys
from os import system
from pathlib import Path
import webbrowser
import time
import rheia.UQ.uncertainty_quantification as rheia_uq
import multiprocessing as mp
import pickle as pkl
import pandas as pd

curr_dir = Path(os.path.dirname(__file__))

pymodPath = os.path.abspath(os.path.join(curr_dir.parent,'pylib'))
sys.path.insert(0, pymodPath)

from ampl_object import AmplObject
from ampl_preprocessor import AmplPreProcessor
from ampl_collector import AmplCollector
from ampl_graph import AmplGraph
from ampl_uncert_graph import AmplUncertGraph
from ampl_uq import AmplUQ
from ampl_pca import AmplPCA
from rheia.CASES.determine_stoch_des_space import StochasticDesignSpace
import rheia.UQ.pce as uq


type_of_model = 'TD'
nbr_tds = 12
case_to_study = [#'CASE_REF',
                 # 'CASE_2',
                    # 'CASE_ROB'] #,
                    'CASE_PCA']
                  # 'CASE_3_50',
                  # 'CASE_3_80',
                  # 'CASE_4_50',
                  # 'CASE_4_80']


SMR = False
gwp_budget = False
if gwp_budget:
    budget_iso_lin = False
    
CO2_neutrality_2050 = False

run_opti = False
check_status = False
graph = False
run_pca = True
graph_comp = False

pth_esmy = os.path.join(curr_dir.parent,'ESMY')
pth_model = os.path.join(pth_esmy,'STEP_2_Pathway_Model')

pth_output_all = os.path.join(curr_dir.parent,'out')

base_case_dict={'CASE_REF':'TD_30_0_gwp_budget_no_efuels_2020',
                'CASE_2':'TD_30_0_gwp_budget_no_efuels_2020_SMR',
                'CASE_ROB': 'TD_30_0_gwp_budget_no_efuels_2020_ROB',
                'CASE_ROB_2': 'TD_30_0_gwp_budget_no_efuels_2020_ROB_2',
                'CASE_PCA': 'CASE_4_80',
                'CASE_PCA_MO': 'CASE_3_80',
                'CASE_3_50':'CASE_3_50',
                'CASE_3_80':'CASE_3_80',
                'CASE_4_50':'CASE_4_50',
                'CASE_4_80':'CASE_4_80'}

#%% UQ settings
uq_dict = {'case' : 'ES_PATHWAY',
                    'eval_type' : 'UQ',
                    'design_space' : 'design_space.csv',
                    'sampling method': 'SOBOL'}

space_obj = StochasticDesignSpace(uq_dict['eval_type'],uq_dict['case'],uq_dict['design_space'])
my_data = uq.Data(uq_dict, space_obj)
my_data.read_stoch_parameters()
uq_experiment = uq.RandomExperiment(my_data, 0)
uq_experiment.create_distributions()

#%% AMPL files for problem + options



if type_of_model == 'MO':
    mod_1_path = [os.path.join(pth_model,'PESMO_model.mod'),
                os.path.join(pth_model,'PESMO_store_variables.mod'),
                os.path.join(pth_model,'PESMO_RL/PESMO_RL_v7.mod'),
                os.path.join(pth_model,'PES_store_variables.mod')]
    mod_2_path = [os.path.join(pth_model,'PESMO_initialise_2020.mod'),
                  os.path.join(pth_model,'fix.mod')]
    dat_path = [os.path.join(pth_model,'PESMO_data_all_years.dat')]
else:
    mod_1_path = [os.path.join(pth_model,'PESTD_model.mod'),
            os.path.join(pth_model,'PESTD_store_variables.mod'),
            os.path.join(pth_model,'PESTD_RL/PESTD_RL_v8.mod'),
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

## Options for ampl and gurobi
gurobi_options = ['predual=-1',
                'method = 2', # 2 is for barrier method
                'crossover=0', #-1 let gurobi decides
                'prepasses = 3',
                'barconvtol=1e-6',
                'dualreductions=0',
                'presolve=-1'] # Not a good idea to put it to 0 if the model is too big

gurobi_options_str = ' '.join(gurobi_options)

ampl_options = {'show_stats': 1,
                'log_file': os.path.join(pth_model,'log.txt'),
                'presolve': 10,
                'presolve_eps': 1e-4,
                'presolve_fixeps': 1e-4,
                'show_boundtol': 0,
                'gurobi_options': gurobi_options_str,
                '_log_input_only': False}

###############################################################################
''' main script '''
###############################################################################




#%% Actual script
if __name__ == '__main__':
        
    # TO DO ONCE AT INITIALISATION OF THE ENVIRONMENT
    
    
    n_year_opti = 10
    n_year_overlap = 5
    
    
    
    for cs in case_to_study:
        skip = 123454
        n_test = 50
    
        case_study = cs
        output_folder_cs = os.path.join(pth_output_all,case_study,type_of_model)
        output_folder_runs = os.path.join(output_folder_cs,'Runs')
        
        status_df = pd.DataFrame(columns=['Case','Test','Step','solve_result','solve_result_num'])
        status_file = os.path.join(output_folder_runs,'_Status.pkl')
    
        base_case = base_case_dict[case_study] #bc
        output_folder_bc = os.path.join(pth_output_all,base_case)
        output_file_bc = os.path.join(output_folder_bc,'_Results.pkl')
        output_file_bc = open(output_file_bc,"rb")
        results_bc = pkl.load(output_file_bc)
        output_file_bc.close()
        assets_bc = results_bc['Assets']['F']
        
        ampl_0 = AmplObject(mod_1_path, mod_2_path, dat_path_0, ampl_options, type_model = type_of_model)
        
        if run_opti:
        
            for j in range(n_test):
                i = 0
                
                output_file_run = os.path.join(output_folder_runs,'Run{}'.format(j))
                
                ampl_0 = AmplObject(mod_1_path, mod_2_path, dat_path_0, ampl_options, type_model = type_of_model)
                ampl_pre = AmplPreProcessor(ampl_0, n_year_opti, n_year_overlap)

                ampl_0.clean_history()
                
                
                ampl_uq = AmplUQ(ampl_0)
                sample = ampl_uq.generate_one_sample(uq_exp = uq_experiment, skip=skip)
                ampl_collector = AmplCollector(ampl_pre, output_file_run)
                
                t = time.time()
            
            
                for i in range(len(ampl_pre.years_opti)):
                # TO DO AT EVERY STEP OF THE TRANSITION
                    t_i = time.time()
                    curr_years_wnd = ampl_pre.write_seq_opti(i).copy()
                    ampl_pre.remaining_update(i)
                    
                    ampl = AmplObject(mod_1_path, mod_2_path, dat_path, ampl_options, type_model = type_of_model)
                    
                    ampl.set_params('gwp_limit_transition',1224935.4)
                    
                    ampl_uq = AmplUQ(ampl)
                    
                    years_wnd=['YEAR_2025','YEAR_2030','YEAR_2035','YEAR_2040','YEAR_2045','YEAR_2050']
                    ampl_uq.transcript_uncertainties(sample,years_wnd)
                    
                    ampl.set_f_min(assets_bc)
                    
                    solve_result, solve_result_num = ampl.run_ampl()
                    
                    new_row = {'Case':cs,'Test':j,'Step':i,'solve_result':solve_result,'solve_result_num':solve_result_num}  
                    status_df = status_df.append(new_row,ignore_index=True)
                    
                    if (solve_result != 'solved') and (solve_result != 'solved?'):
                        break
                    
                    ampl.get_results()
                    
                    if i==0: 
                        ampl_collector.init_storage(ampl)
                    
                    
                    if i > 0:
                        curr_years_wnd.remove(ampl_pre.year_to_rm)
                    
                    ampl_collector.update_storage(ampl,curr_years_wnd,i)
                    
                    ampl.set_init_sol()
                    
                    elapsed_i = time.time()-t_i
                    print('Time to solve the window #'+str(i+1)+': ',elapsed_i)
                    
                    
                    if i == len(ampl_pre.years_opti)-1:
                        elapsed = time.time()-t
                        print('Time to solve the whole problem #{}: '.format(j),elapsed)
                        ampl_collector.clean_collector()
                        ampl_collector.pkl()
                        break
                skip += 1
        

            status_file_pkl = open(status_file,"wb")
            pkl.dump(status_df,status_file_pkl)
            status_file_pkl.close()
        
        if check_status:
            status_file_upkl = open(status_file,"rb")
            loaded_results = pkl.load(status_file_upkl)
            A = loaded_results.loc[loaded_results['solve_result'].isin(['unbounded','infeasible'])]
            B = 4
        
        if run_pca :
            ampl_pca = AmplPCA(ampl_0,cs)
            # ampl_pca.pkl_PCA()
            
            output_folder_cs = []
            for cs in case_to_study:
                output_folder_cs += [os.path.join(pth_output_all,cs,type_of_model)]
                
            ampl_pca.graph_PC_projection(case_to_study,output_folder_cs)
            
            break
            
            # ampl_pca.graph_score_plot()
            # A = 4
            # ampl_pca.graph_PC_j(1,'Assets')
            # ampl_pca.graph_PC_j(1,'Assets_eud')
            # ampl_pca.graph_PC_j(2,'Assets_eud')
            # ampl_pca.graph_PC_j(3,'Assets_eud')
            # ampl_pca.graph_PC_j(1,'Assets_eud',True_val = True)
            # ampl_pca.graph_PC_j(2,'Assets_eud',True_val = True)
            # ampl_pca.graph_PC_j(3,'Assets_eud',True_val = True)
            # ampl_pca.graph_PC_j(4,'Assets_eud',True_val = True)
            # ampl_pca.graph_PC_j(1,'Prod')
            # ampl_pca.graph_PC_j(1,'Cons')
            # A = ampl_pca.var_share_PC
            # B = 4
            # ampl_pca.graph_PC_j(j=2)
            # ampl_pca.graph_PC_top_tech()

        
            
        if graph:
            ampl_uncert_graph = AmplUncertGraph(case_study,base_case,ampl_0,output_folder_cs)
            
            output_folder_cs = []
            output_folder_bc = []
            for cs in case_to_study:
                output_folder_cs += [os.path.join(pth_output_all,cs,type_of_model)]
                output_folder_bc += [os.path.join(pth_output_all,base_case_dict[cs])]
                
            
            
            # ampl_uncert_graph.graph_comp_tech_cap(base_case_dict,output_folder_bc) 
            # ampl_uncert_graph.graph_comp_c_inv_2050(base_case_dict,output_folder_bc,ampl_0)
            # ampl_uncert_graph.graph_comp_c_inv_phase(base_case_dict,output_folder_bc,ampl_0)
            # ampl_uncert_graph.graph_comp_c_op_phase(base_case_dict,output_folder_bc,ampl_0)
            # ampl_uncert_graph.graph_transition_cost(case_to_study,output_folder_cs,output_folder_bc)
            # ampl_uncert_graph.graph_tot_capex_cost(case_to_study,output_folder_cs,output_folder_bc)
            # ampl_uncert_graph.graph_tot_opex_cost(case_to_study,output_folder_cs,output_folder_bc)
            ampl_uncert_graph.graph_tech_cap()
            
            # break
           
            # ampl_uncert_graph.graph_electrofuels()
        
                