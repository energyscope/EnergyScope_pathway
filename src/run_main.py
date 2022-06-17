# -*- coding: utf-8 -*-
"""
Created on Mon May 17 10:21 2021

@author: Xavier Rixhon
"""

import os, sys
from pathlib import Path
import time

curr_dir = Path(os.path.dirname(__file__))

pymodPath = os.path.abspath(os.path.join(curr_dir.parent,'pylib'))
sys.path.insert(0, pymodPath)

from ampl_object import AmplObject
from ampl_preprocessor import AmplPreProcessor
from ampl_collector import AmplCollector

pth_esmy = os.path.join(curr_dir.parent,'ESMY')
pth_model = os.path.join(pth_esmy,'STEP_2_Pathway_Model')

mod_1_path = [os.path.join(pth_model,'PESTD_model.mod'),
            os.path.join(pth_model,'store_variables.mod')]

mod_2_path = [os.path.join(pth_model,'PESTD_initialise_2015.mod'),
              os.path.join(pth_model,'fix.mod')]

dat_path = [os.path.join(pth_model,'seq_opti.dat'),
             os.path.join(pth_model,'PESTD_data_year_related.dat'),
             os.path.join(pth_model,'PESTD_data_efficiencies.dat'),
             os.path.join(pth_model,'PESTD_12TD.dat'),
             os.path.join(pth_model,'PESTD_data_set_AGE.dat'),
             os.path.join(pth_model,'PESTD_data_remaining_wnd.dat'),
             os.path.join(pth_model,'PESTD_data_all_years.dat'),
             os.path.join(pth_model,'PESTD_data_decom_allowed.dat')]

## Options for ampl and gurobi
gurobi_options = ['predual=-1',
                'method = 2', # 2 is for barrier method
                'crossover=0',
                'prepasses = 3',
                'barconvtol=1e-6',                
                'presolve=-1'] # Not a good idea to put it to 0 if the model is too big

gurobi_options_str = ' '.join(gurobi_options)

ampl_options = {'show_stats': 1,
                'log_file': os.path.join(pth_model,'log.txt'),
                'presolve': 10,
                'presolve_eps': 1e-7,
                'presolve_fixeps': 1e-7,
                'times': 0,
                'gentimes': 1,
                'show_boundtol': 0,
                'gurobi_options': gurobi_options_str,
                '_log_input_only': False}

###############################################################################
''' main script '''
###############################################################################

if __name__ == '__main__':
    
    ## Paths
    pth_output_all = os.path.join(curr_dir.parent,'out')
    
    
    N_year_opti = [10]
    N_year_overlap = [5]


    
    for m in range(len(N_year_opti)):
        
        # TO DO ONCE AT INITIALISATION OF THE ENVIRONMENT

        n_year_opti = N_year_opti[m]
        n_year_overlap = N_year_overlap[m]
        
        case_study = 'pickle_{}_{}_gwp_only_2050'.format(n_year_opti,n_year_overlap)
        expl_text = 'No gwp limit for any year except 2050, to reach carbon neutrality'
        
        output_folder = os.path.join(pth_output_all,case_study)
        output_file = os.path.join(output_folder,'_Results.pkl')
        
        ampl_0 = AmplObject(mod_1_path, mod_2_path, dat_path, ampl_options)
        ampl_0.clean_history()
        ampl_pre = AmplPreProcessor(ampl_0, n_year_opti, n_year_overlap)
        ampl_collector = AmplCollector(ampl_0, output_file, expl_text)
        
        t = time.time()
        
        for i in range(len(ampl_pre.years_opti)):
        # TO DO AT EVERY STEP OF THE TRANSITION
            t_i = time.time()
            curr_years_wnd = ampl_pre.write_seq_opti(i)
            ampl_pre.remaining_update(i)
            
            ampl = AmplObject(mod_1_path, mod_2_path, dat_path, ampl_options)
            
            ampl.set_params('gwp_limit',{('YEAR_2015'):1e6})
            ampl.set_params('gwp_limit',{('YEAR_2020'):1e6})
            ampl.set_params('gwp_limit',{('YEAR_2025'):1e6})
            ampl.set_params('gwp_limit',{('YEAR_2030'):1e6})
            ampl.set_params('gwp_limit',{('YEAR_2035'):1e6})
            ampl.set_params('gwp_limit',{('YEAR_2040'):1e6})
            ampl.set_params('gwp_limit',{('YEAR_2045'):1e6})
            
            ampl.run_ampl()

            ampl.get_outputs()
            
            if i > 0:
                curr_years_wnd.remove(ampl_pre.year_to_rm)
            
            ampl_collector.update_storage(ampl.outputs,curr_years_wnd)
            
            ampl.set_init_sol()
            
            elapsed_i = time.time()-t_i
            print('Time to solve the window #'+str(i+1)+': ',elapsed_i)
            
            
            if i == len(ampl_pre.years_opti)-1:
                ampl_collector.pkl()
                break
        
        elapsed = time.time()-t
        print('Time to solve the whole problem: ',elapsed)
                
        
        # if PostProcess:
            
        #     RES = loaded_list['Resources'].T
        #     Tech_Prod_Cons = loaded_list['Tech_Prod_Cons']
        #     Tech_Cap = loaded_list['Tech_Cap'].T
        #     Shadow_prices = loaded_list['Shadow_prices']
        #     EUD = loaded_list['EUD']
        #     C_INV = loaded_list['C_INV'].T
        #     C_OP_MAINT = loaded_list['C_OP_MAINT'].T
            
        #     no_plot = ['GASOLINE', 'DIESEL', 'LFO', 'WOOD', 'WET_BIOMASS',
        #                'COAL','URANIUM','WASTE','RES_WIND','RES_SOLAR',
        #                'RES_GEO','RES_HYDRO','CO2_ATM','CO2_INDUSTRY',
        #                'CO2_CAPTURED']
            
        #     Plot_list = [x for x in Layers if x not in no_plot]
        #     # Plot_list = ['ELECTRICITY', 'HEAT_HIGH_T']
            
        #     Plot_Layer = pd.concat([EUD,Tech_Prod_Cons])
            
        #     postp.graph_prod_cons(Plot_Layer,Plot_list, n_year_opti, n_year_overlap)
            
            
        #     # Tech_Prod_layer = dict.fromkeys(EUD_demands)
        #     # Tech_Cons_layer = dict.fromkeys(EUD_demands)
            
        #     # for l in EUD_demands:
        #     #     Tech_Prod_layer[l] = pd.DataFrame(0,index = Tech_minus_sto,columns = Years)
        #     #     for y in Years:
        #     #         Tech_Prod_layer[l][:,y] = Tech_Prod_Cons[y].loc[l,:]    
            
        # if DrawGraphs:
            
        #     # for k in ['ELECTRICITY']:#Shadow_prices_year:
        #     #     for y in Years:
        #     #         NBR_BINS = postp.freedman_diaconis(Shadow_prices_year[k][y], returnas="bins")
        #     #         plt.figure
        #     #         # plt.boxplot(Shadow_prices_year[k][y])
        #     #         density, bins = np.histogram(Shadow_prices_year[k][y], bins=NBR_BINS, density=1)
        #     #         centers = [(a + b) / 2 for a, b in zip(bins[::1], bins[1::1])]
        #     #         plt.plot(centers,density)
                    
        #     #     #     plt.plot(Shadow_prices_year[k][y])
        #     #     # plt.legend(Years)
        #     #     # plt.title(k)
        #     #     # plt.show()
            
            
        #     # plt.figure()
        #     # year_plt = [2015, 2020, 2025, 2030, 2035, 2040, 2045, 2050]
        #     # # short_list = ['ELECTRICITY', 'HEAT_HIGH_T', 'HEAT_LOW_T_DHN', 'HEAT_LOW_T_DECEN']
        #     # # short_list = ['MOB_PUBLIC', 'MOB_PRIVATE']
        #     # short_list = ['MOB_FREIGHT_RAIL', 'MOB_FREIGHT_BOAT','MOB_FREIGHT_ROAD']
        #     # # short_list = ['AMMONIA', 'HVC', 'METHANOL']
        #     # for k in short_list:
        #     #     plt.plot(year_plt,Shadow_prices_av_year[k].values())
        #     # plt.legend(short_list)
        #     # plt.title('Averaged shadow prices/marginal costs')
            
            
        #     # for y in Years:
        #     #     Shadow_prices_av_year['GWP'][y] = - Shadow_prices_av_year['GWP'][y]
        #     # plt.figure()
        #     # plt.plot(year_plt,Shadow_prices_av_year['GWP'].values())
        #     # plt.title('CO2 marginal cost')
            
            
        #     resol = 8.53e-10
            
        #     RES = RES[RES > resol]
        #     RES = postp.cleanDF(RES)
        #     RES[RES < 1e-3] = 0
        #     RES.pop("CO2_EMISSIONS")
        #     RES.pop("CO2_ATM")
        #     plt.figure()
        #     RES.plot.bar(stacked=True)
    
        #     # RES.pop("ELEC_EXPORT")
        #     color_list = postp.colorList(RES.columns, 'Resources')
            
        #     px.defaults.template = "simple_white"
        #     fig = px.area(RES)
        #     plot(fig)
        #     # ax = RES.plot.area(color = color_list)
        #     # ax.legend(title='Resources', bbox_to_anchor=(1.05, 1), loc='upper center')
            
        #     # x = ['2015','2020','2025','2030','2035','2040','2045','2050']
        #     # RES['year'] = x
        #     # plt.figure(figsize=(12,4))
        #     # plt.stackplot(RES['year'].values,RES.drop('year',axis=1).T,colors = color_list)
            
            
        #     # TECH_ELEC_PROD = TECH_ELEC[TECH_ELEC > resol]
        #     # TECH_ELEC_PROD = postp.cleanDF(TECH_ELEC_PROD)
        #     # ax1 = TECH_ELEC_PROD.plot.area()
        #     # ax1.legend(title='Prod Elec', bbox_to_anchor=(1.05, 1), loc='upper center')
            
        #     # TECH_ELEC_CONS = TECH_ELEC[TECH_ELEC < -resol]
        #     # TECH_ELEC_CONS = postp.cleanDF(TECH_ELEC_CONS)
        #     # ax2 = TECH_ELEC_CONS.plot.area()
        #     # ax2.legend(title='Cons Elec', bbox_to_anchor=(1.05, 1), loc='upper center')
                    
        # # else:
        # #     ampl.close()
                
        ###############################################################################
        ''' main script ends here '''
        ###############################################################################
        
