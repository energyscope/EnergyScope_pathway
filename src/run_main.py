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

curr_dir = Path(os.path.dirname(__file__))

pymodPath = os.path.abspath(os.path.join(curr_dir.parent,'pylib'))
sys.path.insert(0, pymodPath)

from ampl_object import AmplObject
from ampl_preprocessor import AmplPreProcessor
from ampl_collector import AmplCollector
from ampl_graph import AmplGraph
from ampl_uq_graph import AmplUQGraph
from ampl_uq import AmplUQ


type_of_model = 'MO'
nbr_tds = 12


SMR = False
gwp_budget = True
if gwp_budget:
    budget_iso_lin = False
    
CO2_neutrality_2050 = False

run_opti = False
deterministic = False
UQ = False
graph = True
graph_comp = False

if run_opti:
    if not(deterministic):
        case_study_uq = 'run_2_gwp_budget_isoRL_moret_smr_2_1.5_'+type_of_model


pth_esmy = os.path.join(curr_dir.parent,'ESMY')

if SMR:
    pth_model = os.path.join(pth_esmy,'STEP_2_Pathway_Model_SMR')
else:
    pth_model = os.path.join(pth_esmy,'STEP_2_Pathway_Model')

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
                'presolve=-1'] # Not a good idea to put it to 0 if the model is too big

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

if __name__ == '__main__':
    
    ## Paths
    pth_output_all = os.path.join(curr_dir.parent,'out')
    
    N_year_opti = [30]
    N_year_overlap = [0]

    for m in range(len(N_year_opti)):
        
        # TO DO ONCE AT INITIALISATION OF THE ENVIRONMENT
        i = 0
        n_year_opti = N_year_opti[m]
        n_year_overlap = N_year_overlap[m]
        
        if gwp_budget:
            if SMR:
                if budget_iso_lin:
                    case_study = '{}_{}_{}_gwp_budget_isolin_SMR'.format(type_of_model,n_year_opti,n_year_overlap)
                    expl_text = 'GWP budget_isolin with SMR from 2040 to reach carbon neutrality with {} years of time window and {} years of overlap'.format(n_year_opti,n_year_overlap)
                else:
                    case_study = '{}_{}_{}_gwp_budget_SMR'.format(type_of_model,n_year_opti,n_year_overlap)
                    expl_text = 'GWP budget with SMR from 2040 to reach carbon neutrality with {} years of time window and {} years of overlap'.format(n_year_opti,n_year_overlap)
            else:
                if budget_iso_lin:
                    case_study = '{}_{}_{}_gwp_budget_isolin'.format(type_of_model,n_year_opti,n_year_overlap)
                    expl_text = 'GWP budget_isolin to reach carbon neutrality with {} years of time window and {} years of overlap'.format(n_year_opti,n_year_overlap)
                else:
                    case_study = '{}_{}_{}_gwp_budget'.format(type_of_model,n_year_opti,n_year_overlap)
                    expl_text = 'GWP budget to reach carbon neutrality with {} years of time window and {} years of overlap'.format(n_year_opti,n_year_overlap)
        else:
            if SMR:
                # case_study = '{}_{}_{}_gwp_limit_all_the_way_SMR_unlimited'.format(type_of_model,n_year_opti,n_year_overlap)
                case_study = '{}_{}_{}_gwp_limit_all_the_way_SMR'.format(type_of_model,n_year_opti,n_year_overlap)
                expl_text = 'GWP limit all the way up to 2050 with SMR from 2040, to reach carbon neutrality with {} years of time window and {} years of overlap'.format(n_year_opti,n_year_overlap)
            else:
                case_study = '{}_{}_{}_gwp_limit_all_the_way_PAPER_PATHWAY_no_trajectory'.format(type_of_model,n_year_opti,n_year_overlap)
                expl_text = 'GWP limit all the way up to 2050, to reach carbon neutrality with {} years of time window and {} years of overlap'.format(n_year_opti,n_year_overlap)
        if CO2_neutrality_2050:
            case_study += '_CO2_neutrality_2050'
            expl_text += ', CO2 neutrality by 2050'
        
        # case_study += '_no_efuels_2020_SMR'
        
        case_study = '{}_{}_{}_PAPER_PATHWAY_no_trajectory'.format(type_of_model,n_year_opti,n_year_overlap)
        # case_study = 'TD_30_0_gwp_budget_no_efuels_2020_SMR'
        # case_study = 'TD_30_0_gwp_budget_no_efuels_2020_ROB'
        case_study = 'TD_30_0_gwp_budget_no_efuels_2020_ROB_2'
        # case_study = 'CASE_2_no_SMR_perfect_sto'
        # case_study = 'test'
        # case_study = 'CASE_2_no_SMR'
        # case_study = 'TD_30_0_gwp_budget_no_efuels_2020'
        
        output_folder = os.path.join(pth_output_all,case_study)
        output_file = os.path.join(output_folder,'_Results.pkl')
        ampl_0 = AmplObject(mod_1_path, mod_2_path, dat_path_0, ampl_options, type_model = type_of_model)
        ampl_0.clean_history()
        ampl_pre = AmplPreProcessor(ampl_0, n_year_opti, n_year_overlap)
        ampl_collector = AmplCollector(ampl_pre, output_file, expl_text)
        
        t = time.time()
        
        if run_opti:
        
            for i in range(len(ampl_pre.years_opti)):
            # TO DO AT EVERY STEP OF THE TRANSITION
                t_i = time.time()
                curr_years_wnd = ampl_pre.write_seq_opti(i).copy()
                ampl_pre.remaining_update(i)
                
                ampl = AmplObject(mod_1_path, mod_2_path, dat_path, ampl_options, type_model = type_of_model)
                ampl.ampl.eval("shell 'gurobi -v';")
                
                if gwp_budget:
                    if budget_iso_lin:
                        ampl.set_params('gwp_limit_transition',1991102.29892735)
                    else:
                        ampl.set_params('gwp_limit_transition',1224935.4)
                else:
                    
                    # 1st column: gwp_trajectory for TD_PF with gwp_budget of 1224935.4ktCO2_eq for the transition
                    # 2nd column: linear gwp_trajectory starting in 2020 (Pathway paper). To avoid having H2_RE in the mix in 2020, comment the line related to gwp_limit in YEAR_2020. The TotalGWP in 2020 will be ~123737
                    # 3rd column: linear gwp_trajectory starting in 2015 (GL's thesis)
                    
                    # YEAR_2015 : xxx         xxx    156000
                    # YEAR_2020 : 123713.4258 121250 133715
                    # YEAR_2025 : 63610.12101 101610 111430
                    # YEAR_2030 : 39991.25308 81969 89145
                    # YEAR_2035 : 23792.18604 62328 66860
                    # YEAR_2040 : 23200.18966 42688 44575
                    # YEAR_2045 : 6090.469921 23047 22290
                    # YEAR_2050 : 3406.924541 3406.92 3406.92

                    ampl.set_params('gwp_limit',{('YEAR_2020'):124000}) 
                    # ampl.set_params('gwp_limit',{('YEAR_2025'):103901.1533}) 
                    # ampl.set_params('gwp_limit',{('YEAR_2030'):83802.30667})  
                    # ampl.set_params('gwp_limit',{('YEAR_2035'):63703.46}) 
                    # ampl.set_params('gwp_limit',{('YEAR_2040'):43604.61333}) 
                    # ampl.set_params('gwp_limit',{('YEAR_2045'):23505.76667}) 
                    # ampl.set_params('gwp_limit',{('YEAR_2050'):3406.92})
                    
                if CO2_neutrality_2050:
                    ampl.set_params('gwp_limit',{('YEAR_2050'):3406.92})
                    
                if deterministic: 
                    # ampl.set_params('f_max',{('YEAR_2040','NUCLEAR_SMR'):6})
                    # ampl.set_params('f_max',{('YEAR_2045','NUCLEAR_SMR'):6})
                    # ampl.set_params('f_max',{('YEAR_2050','NUCLEAR_SMR'):6})
                    ampl_uq = AmplUQ(ampl)
                    uncer_param = {'c_op_syn_fuels':1,'industry_eud':1,'param_i_rate':1,'c_op_hydrocarbons':1,
                                   'c_maint_var':1,'c_op_biofuels':1}
                    years_wnd = ['YEAR_2025','YEAR_2030','YEAR_2035','YEAR_2040','YEAR_2045','YEAR_2050']
                    ampl_uq.transcript_uncertainties(uncer_param,years_wnd)
                    solve_result = ampl.run_ampl()
                    ampl.get_results()
                    
                if UQ:
                    case_study_uq += '_no_efuels_2020_full_test'
                    case_study_uq = 'run_2_gwp_budget_isoRL_moret_smr_2_1.5_TD_no_efuels_2020_full'
                    # case_study_uq = 'RL_MO'
                    pol_order = 2
                    dict_uq = {'case':'ES_PATHWAY',
                            'n jobs':                1,
                            'pol order':             pol_order,
                            'objective names':       ['total_transition_cost'],
                            'objective of interest': 'total_transition_cost',
                            'draw pdf cdf':          [True, 1e5],
                            'results dir':           case_study_uq,
                            'ampl_obj':               [mod_1_path, mod_2_path, dat_path, ampl_options, type_of_model],
                            'ampl_collector':       ampl_collector
                            }
                    
                    folder = '/Users/xrixhon/.pyenv/versions/3.7.6/lib/python3.7/site-packages/rheia/RESULTS/ES_PATHWAY/UQ/'
                    # if not(Path(os.path.join(folder,case_study_uq,'samples.csv')).is_file()):
                    # rheia_uq.run_uq(dict_uq, design_space = 'design_space.csv')
                    elapsed = time.time()-t
                    print('Time to solve the whole problem: ',elapsed)
                    
                    # result_dir = ['run_2_gwp_budget_isoRL_moret_smr_2_1.5_MO_full',
                    #               'run_2_gwp_budget_isoRL_moret_smr_2_1.5_TD']
                    result_dir = []
                    ref_case = 'TD_30_0_gwp_budget_no_efuels_2020'
                    smr_case = 'TD_30_0_gwp_budget_no_efuels_2020_SMR'
                    ampl_uq_graph = AmplUQGraph(case_study_uq,ampl_0,ref_case,smr_case,result_dir_comp = result_dir, pol_order=pol_order)
                    # ampl_uq_graph.graph_sobol()
                    # ampl_uq_graph.graph_pdf()
                    # ampl_uq_graph.graph_cdf()
                    ampl_uq_graph.graph_tech_cap()
                    # ampl_uq_graph.graph_layer()
                    # ampl_uq_graph.graph_electrofuels()
                    # ampl_uq_graph.graph_local_RE()
                    
                    # elements = [#'H2_ELECTROLYSIS',
                    #             'CCGT_AMMONIA',
                    #             'SYN_METHANOLATION',
                    #             'METHANE_TO_METHANOL',
                                # 'NUCLEAR_SMR']#,
                    #             'BIOMETHANATION',
                    #             'BIO_HYDROLYSIS']
                    # outputs = ['F'] * len(elements)
                    
                    # elements = ['PV',
                    #             'WIND_ONSHORE',
                    #             'WIND_OFFSHORE']
                    # outputs = ['F'] * len(elements)
                    
                    # elements_2 = [['AMMONIA_RE','AMMONIA'],
                    #             ['GAS_RE','GAS'],
                    #             ['H2_RE','H2'],
                    #             ['METHANOL_RE','METHANOL']]
                    
                    # # elements_2 = [['CAR_FUEL_CELL','MOB_PRIVATE']]
                    
                    # # elements_2 = 5*[['PV','ELECTRICITY'],
                    # #             ['WIND_ONSHORE','ELECTRICITY'],
                    # #             ['WIND_OFFSHORE','ELECTRICITY']]
                    
                    # elements = elements_2
                    
                    # outputs = ['Ft'] * len(elements)
                    
                    # elements += ['NUCLEAR_SMR']
                    
                    # outputs += ['F']

                    
                    # # elements_3 = ['']
                    # # elements += elements_3
                    
                    # # # elements += elements_3
                    
                    # # outputs += ['TotalGwp'] * len(elements_3)
                    
                    # years = ['YEAR_2050'] * len(elements)
                    
                    # years = ['YEAR_2025']*3
                    # years += ['YEAR_2030']*3
                    # years += ['YEAR_2035']*3
                    # years += ['YEAR_2040']*3
                    # years += ['YEAR_2045']*3
                    # # ampl_uq_graph.get_spec_output_test(dict_uq,outputs,elements,years,calc_Sobol=False)
                    # ampl_uq_graph.get_spec_output_test_4(dict_uq,outputs,elements,years,calc_Sobol=True)
                    
                    
                    # break
                
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
                    print('Time to solve the whole problem: ',elapsed)
                    ampl_collector.clean_collector()
                    ampl_collector.pkl()
                    break
        if graph:
            # case_study = 'TD_30_0_gwp_budget_no_efuels_2020_SMR'
            case_study = 'TD_30_0_gwp_budget_no_efuels_2020'
            # case_study = 'CASE_2_no_SMR'
            # case_study = 'CASE_3_80'
            # case_study = 'TD_30_0_gwp_budget_no_efuels_2020'
            # case_study = 'TD_30_0_gwp_budget_no_efuels_2020_ROB_2'
            # case_study = 'TD_30_0_gwp_limit_all_the_way'
            # case_study = 'TD_30_0_gwp_limit_all_the_way_2'
            # case_study = 'TD_10_5_gwp_limit_all_the_way'
            output_file = '/Users/xrixhon/Development/GitKraken/EnergyScope_pathway/out/'+case_study+'/_Results.pkl'
            ampl_graph = AmplGraph(output_file, ampl_0, case_study)
            A = ampl_graph._group_tech_per_eud()
            a_website = "https://www.google.com"
            # webbrowser.open_new(a_website)
            ampl_graph.graph_resource()
            # ampl_graph.graph_cost()
            # ampl_graph.graph_gwp_per_sector()
            # ampl_graph.graph_cost_inv_phase_tech()
            # ampl_graph.graph_cost_return()
            # ampl_graph.graph_cost_op_phase()
            
            # ampl_graph.graph_layer()
            # ampl_graph.graph_gwp()
            # ampl_graph.graph_tech_cap()
            # ampl_graph.graph_total_cost_per_year()
            # ampl_graph.graph_load_factor()
            # df_unused = ampl_graph.graph_load_factor_scaled()
            # ampl_graph.graph_new_old_decom()
            
            # ampl_graph.graph_paper()
            
        if graph_comp:
            # case_study = 'TD_30_0_gwp_budget_no_efuels_2020_SMR'
            # case_study = 'TD_30_0_gwp_limit_all_the_way_2'
            case_study = 'TD_30_0_gwp_budget_no_efuels_2020_ROB2'
            # case_study = 'CASE_2_no_SMR_perfect_sto'
            # case_study = 'CASE_2_no_SMR'
            ampl_graph = AmplGraph(output_file, ampl_0, case_study)
            
            
            # Reference case: TD-Perfect foresight
            if gwp_budget:
                if  SMR or CO2_neutrality_2050:
                    if budget_iso_lin:
                        case_study_1 = '{}_{}_{}_gwp_budget_isolin'.format('TD',30,0)
                    else:
                        case_study_1 = '{}_{}_{}_gwp_budget'.format('TD',30,0)
                else:
                    if budget_iso_lin:
                        case_study_1 = '{}_{}_{}_gwp_budget_isolin'.format('TD',30,0)
                    else:
                        case_study_1 = '{}_{}_{}_gwp_budget'.format('TD',30,0) 
            else:
                case_study_1 = '{}_{}_{}_gwp_limit_all_the_way'.format('TD',30,0)
            
            case_study_1 = 'TD_30_0_gwp_budget_no_efuels_2020'
            # case_study_1 = 'TD_30_0_gwp_budget_no_efuels_2020_SMR'
            # case_study_1 = 'TD_30_0_gwp_budget_no_efuels_2020'

            output_folder_1 = os.path.join(pth_output_all,case_study_1)
            output_file_1 = os.path.join(output_folder_1,'_Results.pkl')
            
            output_folder_2 = output_folder
            output_file_2 = os.path.join(output_folder_2,'_Results.pkl')
            
            
            output_files = [output_file_1,output_file_2]
            
            ampl_graph.graph_comparison(output_files,'C_inv_phase_tech')
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
        
