# -*- coding: utf-8 -*-
"""
Created on Mon May 17 10:21 2021

@author: Xavier Rixhon
"""

import os

import matplotlib.pyplot as plt
import plotly.express as px
from plotly.offline import plot


import time
import pandas as pd

from amplpy import AMPL, Environment

from pylib.pre_treatment import Pathway_window as wnd
from pylib.pre_treatment import set_up_ampl as sua
from pylib.post_treatment import post_processing as postp

import pylib.opti_probl as op

import numpy as np


import pickle

from copy import deepcopy        

###############################################################################
''' main script '''
###############################################################################

if __name__ == '__main__':	
    
    # Different actions
    CleanHistory = True
    InitStorage = True
    RunMyopicOpti = True
    GoNextWindow = True
    PostProcess = False
    DrawGraphs = False
    
    
    ## Pickled results: preparation
    PKL_list = ['Resources','Tech_Prod_Cons','Tech_Cap','Shadow_prices']
    PKL_dict = dict.fromkeys(PKL_list)
    
    
    ## Paths
    pth_model = os.path.join(os.getcwd(),'STEP_2_Pathway_Model')
    pth_ampl = '/Users/xrixhon/Documents/Software/AMPL'
    pth_output = os.path.join(os.getcwd(),'outputs')
    
    ## Options for ampl and cplex
    cplex_options = ['baropt',
                 'predual=-1',
                 'barstart=4',
                 'timelimit 64800',
                 'crossover=0',
                 'bardisplay=0',
                 'prestats=0',
                 'presolve=0', # Not a good idea to put it to 0 if the model is too big
                 'display=0']
    cplex_options_str = ' '.join(cplex_options)
    ampl_options = {'show_stats': 3,
                    'log_file': os.path.join(pth_model,'log.txt'),
                    'presolve': 10,
                    'presolve_eps': 1e-3,
                    'presolve_fixeps': 1e-3,
                    'times': 0,
                    'gentimes': 0,
                    # 'show_boundtol': 0,
                    'cplex_options': cplex_options_str}
    
    
    N_year_opti = [10] # HERE
    N_year_overlap = [5]
    
    # N_year_opti = [10]
    # N_year_overlap = [5]
    
    for m in range(len(N_year_opti)):    
        n_year_opti = N_year_opti[m]
        n_year_overlap = N_year_overlap[m]
        # n_year_opti = 10
        # n_year_overlap = 5
    
    
        file_name = os.path.join(pth_output,'pickle_{}_{}.pkl'.format(n_year_opti,n_year_overlap))
    
        [years_wnd, phases_wnd, years_up_to, phases_up_to] = wnd.pathway_window(n_year_opti,n_year_overlap)
            
        if CleanHistory:
            open(os.path.join(pth_model,'fix_2.mod'), 'w').close()
            open(os.path.join(pth_model,'PESTD_data_remaining_wnd.dat'), 'w').close()
            open(os.path.join(pth_model,'seq_opti.dat'), 'w').close()
            
        if InitStorage:
            
            ampl0 = AMPL(Environment(pth_ampl))
            # ampl0 = AMPL(Environment(pth_ampl,'ampldev'))
            # ampl0 = op.OptiProbl(pth_model, pth_model, pth_ampl, ampl_options)
            
            
            
            sua.set_up_ampl(ampl0, pth_model, ampl_options)
            
            S = ampl0.getSets()
            V = ampl0.getVariables()
            P = ampl0.getParameters()
            
            Res = S['RESOURCES'].getValues().toList()
            Tech = S['TECHNOLOGIES'].getValues().toList()
            Layers = S['LAYERS'].getValues().toList()
            
            Tech_EUD = S['TECHNOLOGIES_OF_END_USES_TYPE']
            Years = S['YEARS'].getValues().toList()
            Phase = S['PHASE'].getValues().toList()
            
            EUD_cat = S['END_USES_CATEGORIES'].getValues().toList()
            EUD_type = S['END_USES_TYPES_OF_CATEGORY']
            EUD_demands = []
            for i in EUD_cat:
                EUD_demands += EUD_type[i].getValues().toList()
            
            SP_LIST = ['GWP','Layer','EUD']
            
            Shadow_prices = dict.fromkeys(SP_LIST)
            
            Shadow_prices['GWP'] = dict.fromkeys(Years)
            Shadow_prices['Layer'] = dict.fromkeys(EUD_demands)
            Shadow_prices['EUD'] = dict.fromkeys(EUD_demands)
            
            for i in Shadow_prices['Layer']:
                Shadow_prices['Layer'][i] = dict.fromkeys(Years)
            for i in Shadow_prices['EUD']:
                Shadow_prices['EUD'][i] = dict.fromkeys(Years)
                
                
            
            Periods = S['PERIODS'].getValues().toList()
            Hour = S['HOURS'].getValues().toList()
            TD = S['TYPICAL_DAYS'].getValues().toList()
            
            Hour_of_period = S['HOUR_OF_PERIOD']
            Dict_HofP = postp.toPandasDict_H_TD_ofP(Periods, Hour_of_period)
            
            TDofP = S['TYPICAL_DAY_OF_PERIOD']
            Dict_TDofP = postp.toPandasDict_H_TD_ofP(Periods, TDofP)
            
            Tech_Prod_Cons = dict.fromkeys(Years)
            
            RES = pd.DataFrame(0,index = Years,columns = Res)
            Tech_Cap = pd.DataFrame(0,index = Years,columns = Tech)
            
        
        t0 = time.time()
        if RunMyopicOpti:
            
            year_one = ''
            
            for i in range(len(years_wnd)):
                curr_window_years = years_wnd[i]
                curr_window_phases = phases_wnd[i]
                curr_years_up_to = years_up_to[i]
                curr_phases_up_to = phases_up_to[i]
                
                wnd.write_seq_opti(curr_window_years, curr_window_phases,\
                                   curr_years_up_to, curr_phases_up_to, pth_model, year_one, i, n_year_overlap)
                wnd.remaining_update("PESTD_data_remaining.dat",pth_model,curr_window_phases)
                
                ampl = AMPL(Environment(pth_ampl))
                
                sua.set_up_ampl(ampl, pth_model, ampl_options)
                
                ampl._startRecording('session.log')
                ampl.setOption('_log_input_only', False)
                
                t = time.time()
                if i==0:
                    ampl.getConstraint('total_capex_no_2015').drop()
                    ampl.getConstraint('Opex_tot_cost_calculation_no_2015').drop()
                else:
                    ampl.getConstraint('total_capex_2015').drop()
                    ampl.getConstraint('Opex_tot_cost_calculation_2015').drop()

                ampl.solve()
                elapsed = time.time()-t
                print('Time to solve the window #'+str(i+1)+': ',elapsed)
                
                
                curr_wnd_y = deepcopy(curr_window_years)
                if i>0:
                    curr_wnd_y.remove(year_one)
                
                # Shadow price of CO2 and EUDs
                t_x = time.time()
                for y in curr_wnd_y:
                    Shadow_prices['GWP'][y] = ampl.getConstraint('minimum_GWP_reduction')[y].dual()
                    for l in EUD_demands:
                        temp_layer = np.zeros((len(Hour),len(TD)))
                        temp_EUD = np.zeros((len(Hour),len(TD)))
                        for h in Hour:
                            for td in TD:
                                h_i = int(h-1)
                                td_i = int(td-1)
                                temp_layer[h_i,td_i] = ampl.getConstraint('layer_balance')[y,l,h,td].dual()
                                temp_EUD[h_i,td_i] = ampl.getConstraint('end_uses_t')[y,l,h,td].dual()
                        Shadow_prices['Layer'][l][y] = deepcopy(temp_layer)
                        Shadow_prices['EUD'][l][y] = deepcopy(temp_EUD)
                elapsed_x = time.time()-t_x
                print('Time to extract shadow prices:',elapsed_x)
                
                
                # F
                F_up_to = ampl.getVariable('F_up_to')
                
                # F_new
                F_new_up_to = ampl.getVariable('F_new_up_to')
                
                # F_old
                F_old_up_to = ampl.getVariable('F_old_up_to')
                
                # F_decom
                F_decom_up_to = ampl.getVariable('F_decom_up_to')
                
                #Delta_change
                Delta_change_up_to = ampl.getVariable('Delta_change_up_to')
                
                
                # Resources
                Res_wnd = ampl.getVariable('Res_wnd').getValues()
                df_temp_res = postp.to_pd_pivot(Res_wnd)
                RES.update(df_temp_res)
    
                # Tech
                F_wnd = ampl.getVariable('F_wnd').getValues()
                df_temp_F = postp.to_pd_pivot(F_wnd)
                Tech_Cap.update(df_temp_F)
                
                Tech_wnd = ampl.getVariable('Tech_wnd').getValues()
                Tech_dict = postp.to_pd_pivot(Tech_wnd, 'F_t')
                Tech_df = postp.to_pd(Tech_wnd)
                # Tech_df = Tech_df.loc[Tech_df['Tech_wnd.val'] !=0]
                Tech_df = Tech_df.set_index(['index0','index1','index2'])
                
                for y in curr_window_years:
                    Tech_Prod_Cons[y] = Tech_df.loc[y]
                
                if i == len(years_wnd)-1:
                    elapsed0 = time.time()-t0
                    print('Time to solve the whole problem:',elapsed0)
                    
                    PKL_dict['Resources'] = RES
                    PKL_dict['Tech_Prod_Cons'] = Tech_Prod_Cons
                    PKL_dict['Tech_Cap'] = Tech_Cap
                    PKL_dict['Shadow_prices'] = Shadow_prices
                    
                    open_file = open(file_name,"wb")
                    pickle.dump(PKL_dict,open_file)
                    open_file.close()
                    break
                
                if GoNextWindow:
                    fix = os.path.join(pth_model,'fix.mod')
                    fix_2 = os.path.join(pth_model,'fix_2.mod')
                    
                    with open(fix,'w+', encoding='utf-8') as fp:
                        for index, variable in F_up_to:
                            print('fix {}:={};'.format(variable.name(),round(variable.value(),3)), file = fp)
                        print("\n", file = fp)
                        for index, variable in F_new_up_to:
                            print('fix {}:={};'.format(variable.name(),round(variable.value(),3)), file = fp)
                        print("\n", file = fp)
                        for index, variable in F_old_up_to:
                            print('fix {}:={};'.format(variable.name(),round(variable.value(),3)), file = fp)
                        print("\n", file = fp)
                        for index, variable in F_decom_up_to:
                            print('fix {}:={};'.format(variable.name(),round(variable.value(),3)), file = fp)
                        for index, variable in Delta_change_up_to:
                            print('fix {}:={};'.format(variable.name(),variable.value()), file = fp)
                    
                    with open(fix) as fin, open(fix_2,'w+', encoding='utf-8') as fout:
                        for line in fin:
                            line = line.replace("_up_to","")
                            fout.write(line)
                    
                    year_one = years_wnd[i+1][0]
                    
                
        
        if PostProcess:
            
            open_file = open(file_name,"rb")
            loaded_list = pickle.load(open_file)
            open_file.close()
            
            RES = loaded_list['Resources']
            Tech_Prod_Cons = loaded_list['Tech_Prod_Cons']
            Tech_Cap = loaded_list['Tech_Cap']
            Shadow_prices = loaded_list['Shadow_prices']
            
            tyo = time.time()
            Shadow_prices_year = deepcopy(Shadow_prices)
            for y in Years:
                for l in EUD_demands:
                    Shadow_prices_year['Layer'][l][y] = postp.TDtoYEAR(Shadow_prices['Layer'][l][y], Dict_TDofP)
                    Shadow_prices_year['EUD'][l][y] = postp.TDtoYEAR(Shadow_prices['EUD'][l][y], Dict_TDofP)
            
            Shadow_prices_av_year = deepcopy(Shadow_prices)
            for l in Shadow_prices_av_year:
                for y in Years:
                    Shadow_prices_av_year['Layer'][l][y] = np.average(Shadow_prices_year['Layer'][l][y])
                    Shadow_prices_av_year['EUD'][l][y] = np.average(Shadow_prices_year['EUD'][l][y])
            
            elapsedyo = time.time()-tyo
            print('Time to get all shadow prices from TD to year:',elapsedyo)
            
        if DrawGraphs:
            
            for k in ['ELECTRICITY']:#Shadow_prices_year:
                for y in Years:
                    NBR_BINS = postp.freedman_diaconis(Shadow_prices_year[k][y], returnas="bins")
                    plt.figure
                    # plt.boxplot(Shadow_prices_year[k][y])
                    density, bins = np.histogram(Shadow_prices_year[k][y], bins=NBR_BINS, density=1)
                    centers = [(a + b) / 2 for a, b in zip(bins[::1], bins[1::1])]
                    plt.plot(centers,density)
                    
                #     plt.plot(Shadow_prices_year[k][y])
                # plt.legend(Years)
                # plt.title(k)
                # plt.show()
            
            
            plt.figure()
            year_plt = [2015, 2020, 2025, 2030, 2035, 2040, 2045, 2050]
            # short_list = ['ELECTRICITY', 'HEAT_HIGH_T', 'HEAT_LOW_T_DHN', 'HEAT_LOW_T_DECEN']
            # short_list = ['MOB_PUBLIC', 'MOB_PRIVATE']
            short_list = ['MOB_FREIGHT_RAIL', 'MOB_FREIGHT_BOAT','MOB_FREIGHT_ROAD']
            # short_list = ['AMMONIA', 'HVC', 'METHANOL']
            for k in short_list:
                plt.plot(year_plt,Shadow_prices_av_year[k].values())
            plt.legend(short_list)
            plt.title('Averaged shadow prices/marginal costs')
            
            
            for y in Years:
                Shadow_prices_av_year['GWP'][y] = - Shadow_prices_av_year['GWP'][y]
            plt.figure()
            plt.plot(year_plt,Shadow_prices_av_year['GWP'].values())
            plt.title('CO2 marginal cost')
            
            
            resol = 8.53e-10
            
            RES = RES[RES > resol]
            RES = postp.cleanDF(RES)
            RES.pop("CO2_EMISSIONS")
            plt.figure()
            RES.plot.bar(stacked=True)
    
            # RES.pop("ELEC_EXPORT")
            color_list = postp.colorList(RES.columns, 'Resources')
            
            px.defaults.template = "simple_white"
            fig = px.area(RES)
            plot(fig)
            # ax = RES.plot.area(color = color_list)
            # ax.legend(title='Resources', bbox_to_anchor=(1.05, 1), loc='upper center')
            
            # x = ['2015','2020','2025','2030','2035','2040','2045','2050']
            # RES['year'] = x
            # plt.figure(figsize=(12,4))
            # plt.stackplot(RES['year'].values,RES.drop('year',axis=1).T,colors = color_list)
            
            
            # TECH_ELEC_PROD = TECH_ELEC[TECH_ELEC > resol]
            # TECH_ELEC_PROD = postp.cleanDF(TECH_ELEC_PROD)
            # ax1 = TECH_ELEC_PROD.plot.area()
            # ax1.legend(title='Prod Elec', bbox_to_anchor=(1.05, 1), loc='upper center')
            
            # TECH_ELEC_CONS = TECH_ELEC[TECH_ELEC < -resol]
            # TECH_ELEC_CONS = postp.cleanDF(TECH_ELEC_CONS)
            # ax2 = TECH_ELEC_CONS.plot.area()
            # ax2.legend(title='Cons Elec', bbox_to_anchor=(1.05, 1), loc='upper center')
                    
        # else:
        #     ampl.close()
                
        ###############################################################################
        ''' main script ends here '''
        ###############################################################################
        
