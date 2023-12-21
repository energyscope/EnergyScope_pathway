import rheia.POST_PROCESS.post_process as rheia_pp
import rheia.UQ.uncertainty_quantification as rheia_uq
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd
import plotly.io as pio
import numpy as np
import os, sys
from pathlib import Path
import pickle as pkl
import hashlib

pylibPath = os.path.abspath("../pylib")
if pylibPath not in sys.path:
    sys.path.insert(0, pylibPath)

from ampl_graph import AmplGraph

pio.templates.default = 'simple_white'
pio.kaleido.scope.mathjax = None

pio.renderers.default = 'browser'

class AmplUQGraph:

    """

    The AmplUQGraph class allows to plot the relevant outputs (e.g. installed capacitites, used resources, costs)
    of the different samples of UQ on an optimisation problem.

    Parameters
    ----------
    result_list: list(Pandas.DataFrame)
        Unpickled list where relevant outputs has been stored

    """

    def __init__(self, case_study, ampl_obj,ref_case=None,smr_case=None,result_dir_comp = [], pol_order=2):
        self.result_dir = result_dir_comp
        self.case = 'ES_PATHWAY'
        self.pol_order = pol_order
        self.my_post_process_uq = rheia_pp.PostProcessUQ(self.case,self.pol_order)
        self.case_study = case_study
        self.case_study_dir_path = os.path.join(Path(self.my_post_process_uq.result_path).absolute(),self.case_study)
        
        self.objective = 'total_transition_cost'
        self.threshold = 1
        self.threshold_filter = 0.01

        self.x_axis = [2020, 2025, 2030, 2035, 2040, 2045, 2050]
        # In 2020, 37.41% of electricity in EU-27 was produced from renewables (https://ec.europa.eu/eurostat/databrowser/view/NRG_IND_REN__custom_4442440/default/table?lang=en)
        self.re_share_elec = np.linspace(0.3741,1,len(self.x_axis))
        
        self.gather_results()
        self.ampl_uq_collector = self.unpkl(self)
        self.samples_file = os.path.join(self.case_study_dir_path,'samples.csv')
        samples = pd.read_csv(self.samples_file)
        samples.index.name = 'Sample'
        self.ampl_uq_collector['Samples'] = samples
        self.ampl_obj = ampl_obj
        project_path = Path(__file__).parents[1]
        uq_file = os.path.join(project_path,'uncertainties','uc_final.xlsx')
        uncert_param = pd.read_excel(uq_file,sheet_name='Parameters',engine='openpyxl',index_col=0)
        uncert_param_meaning = uncert_param['Meaning_short']
        self.uncert_param_meaning = dict(uncert_param_meaning)
        
        uncert_range = pd.read_excel(uq_file,sheet_name='YEAR_2025',engine='openpyxl',index_col=0)
        self.uncert_nominal = self.get_nominal(uncert_range)
        
        self.ref_case = ref_case
        self.ref_file = os.path.join(project_path,'out',ref_case,'_Results.pkl')
        ref_results = open(self.ref_file,"rb")
        self.ref_results = pkl.load(ref_results)
        ref_results.close()
        
        self.smr_case = smr_case
        self.smr_file = os.path.join(project_path,'out',smr_case,'_Results.pkl')
        smr_results = open(self.smr_file,"rb")
        self.smr_results = pkl.load(smr_results)
        smr_results.close()
        
        self.color_dict_full = self._dict_color_full()
        
        self.outdir = os.path.join(self.case_study_dir_path,'graphs/')
        if not os.path.exists(Path(self.outdir)):
            Path(self.outdir).mkdir(parents=True,exist_ok=True)

        self.category = self._group_sets()
    
    def get_spec_output(self,dict_uq,output,element,year,focus='High',calc_Sobol=False, flip = True):
        
        labels = [None] * len(output)
        samples_plus = self.ampl_uq_collector['Samples'].copy()
        col_objective = samples_plus.columns.get_loc(self.objective)
        samples_plus = samples_plus.iloc[:,:col_objective+1]
        result_ref_full = dict()
        result_smr_full = dict()
        meaning_output = self.dict_meaning()
        for i in range(len(output)):
            
            nom_values = pd.DataFrame(index=samples_plus.columns,columns=['Nominal'],data=0)
            nom_values.index.name='Parameter'
            nom_values.update(self.uncert_nominal)
            
            nom_values_ref = pd.DataFrame(index=samples_plus.columns,columns=['REF'],data=0)
            nom_values_ref.index.name='Parameter'
            
            nom_values_smr = pd.DataFrame(index=samples_plus.columns,columns=['SMR'],data=0)
            nom_values_smr.index.name='Parameter'
            
            out = output[i]
            if out == 'F':
                el = element[i]
            elif out == 'Ft':
                el = element[i][0]
                layer = element[i][1]
            elif out == 'TotalGwp':
                el = element[i]
            y = year[i]
            label = out+'_'+el+'_'+y
            labels[i] = label
            if out == 'F':
                results = self.ampl_uq_collector['Assets'][['F','Sample']]
                results = results.loc[results.index.get_level_values('Technologies') == el]
                results.rename(columns = {out:label},inplace=True)
                
                result_ref = self.ref_results['Assets']['F']
                result_ref = result_ref.loc[result_ref.index.get_level_values('Technologies') == el]
                
                result_smr = self.smr_results['Assets']['F']
                result_smr = result_smr.loc[result_smr.index.get_level_values('Technologies') == el]
                
            elif out == 'Ft':
                results = self.ampl_uq_collector['Year_balance'][[layer,'Sample']]
                results = results.loc[results.index.get_level_values('Elements') == el]
                results.rename(columns = {layer:label},inplace=True)
                
                result_ref = self.ref_results['Year_balance'][layer]
                result_ref = result_ref.loc[result_ref.index.get_level_values('Elements') == el]
                
                result_smr = self.smr_results['Year_balance'][layer]
                result_smr = result_smr.loc[result_smr.index.get_level_values('Elements') == el]
            
            elif out == 'TotalGwp':
                results = self.ampl_uq_collector['TotalGwp'][['TotalGWP','Sample']]
                results.rename(columns = {'TotalGWP':label},inplace=True)
                result_ref = self.ref_results['TotalGwp']['TotalGWP']
                result_smr = self.smr_results['TotalGwp']['TotalGWP']
                results.index.name = 'Years'
                result_ref.index.name = 'Years'
                result_smr.index.name = 'Years'
                
                
            results = results.loc[results.index.get_level_values('Years') == y]
            result_ref = result_ref.loc[result_ref.index.get_level_values('Years') == y]
            result_smr = result_smr.loc[result_smr.index.get_level_values('Years') == y]
            
            if result_ref.empty:
                result_ref_full[label] = 0
            else:
                result_ref_full[label] = result_ref.values[0]
            
            if result_smr.empty:
                result_smr_full[label] = 0
            else:
                result_smr_full[label] = result_smr.values[0]

            results.reset_index(inplace=True)
            results = results.set_index(['Sample'])
            samples_plus[label] = results[label]
            samples_plus.fillna(0,inplace=True)
        
        samples_plus.to_csv(self.samples_file,index=False)
        dict_uq['objective names'] = dict_uq['objective names'] + labels
        
        samples_plot = samples_plus.copy()
        min_list = dict.fromkeys(samples_plus.columns)
        max_list = dict.fromkeys(samples_plus.columns)
        for i in samples_plus.columns:
            min_temp = min(samples_plot[i])
            min_list[i] = min_temp
            max_temp = max(samples_plot[i])
            max_list[i] = max_temp
            
            if i == self.objective:
                transition_cost_ref = self.get_transition_cost(case_study='ref')
                transition_cost_smr = self.get_transition_cost(case_study='smr')
                nom_values_ref.loc[i] = (transition_cost_ref-min_temp)/(max_temp-min_temp)*1-0
                nom_values_smr.loc[i] = (transition_cost_smr-min_temp)/(max_temp-min_temp)*1-0
            elif i in labels:
                nom_values_ref.loc[i] = (result_ref_full[i]-min_temp)/(max_temp-min_temp)*1-0
                nom_values_smr.loc[i] = (result_smr_full[i]-min_temp)/(max_temp-min_temp)*1-0
                
            samples_plot[i] = (samples_plot[i]-min_temp)/(max_temp-min_temp)*1-0
        
        samples_plot.reset_index(inplace=True)
        samples_plot['Significance'] = 'Neutral'

        dict_uq['draw pdf cdf'] = [False, 1e5]
        
        for i in range(len(output)):
            j = labels[i]
            out = output[i]
            if out == 'F':
                el = element[i]
            elif out == 'Ft':
                el = element[i][0]
            elif out == 'TotalGwp':
                el = 'Total gwp'
            
            output_of_interest = meaning_output[el]
            
            if out == 'F':
                output_of_interest +=' - Capacity'
                output_of_interest += ' [{}; {}] GW'.format(round(min_list[j],1),round(max_list[j],1))
            elif out == 'Ft':
                output_of_interest +=' - Import'
                output_of_interest += ' [{}; {}] TWh'.format(round(min_list[j]/1000,1),round(max_list[j]/1000,1))
            elif out == 'TotalGwp':
                output_of_interest += ' [{}; {}] MtCO2'.format(round(min_list[j]/1000,1),round(max_list[j]/1000,1))
            
            
            if calc_Sobol:
                dict_uq['objective of interest'] = j
                rheia_uq.run_uq(dict_uq,design_space = 'design_space.csv')
            
            x_meaning = self.uncert_param_meaning.copy()
            
            names, sobol = self.my_post_process_uq.get_sobol(self.case_study, j)
            temp_sobol = [x_meaning[names[m]]+' ('+str(round(100*sobol[m]))+ '%)' for m in range(len(names))]
            dict_sobol = dict.fromkeys(names)
            for k,l in enumerate(names):
                dict_sobol[l] = temp_sobol[k]
            dict_sobol[self.objective] = 'Total transition cost'
            dict_sobol[self.objective] += ' [{}; {}] b€'.format(round(min_list[self.objective]/1000),round(max_list[self.objective]/1000))
            dict_sobol[j] = output_of_interest
            n_threshold = len([i for i in sobol if i > 1/len(sobol)])
            param_to_keep = temp_sobol[:min(n_threshold,6)]
            
            smr_in = False
            for p in param_to_keep:
                if 'SMR' in p:
                    smr_in = True
                    dict_ref_smr = {'Parameter':p,'REF':0}
                    dict_smr_smr = {'Parameter':p,'SMR':0.6}
            
            order_x = [dict_sobol[j]] + param_to_keep + [dict_sobol[self.objective]]
            
            nom_values_plot = nom_values.reset_index()
            nom_values_plot = nom_values_plot.replace({"Parameter": dict_sobol})
            nom_values_plot = nom_values_plot.loc[nom_values_plot['Parameter'].isin(param_to_keep)]
            
            nom_values_ref_plot = nom_values_ref.reset_index()
            nom_values_ref_plot = nom_values_ref_plot.replace({"Parameter": dict_sobol})
            nom_values_ref_plot = nom_values_ref_plot.loc[nom_values_ref_plot['Parameter'].isin([dict_sobol[j]] + [dict_sobol[self.objective]])]
            
            nom_values_smr_plot = nom_values_smr.reset_index()
            nom_values_smr_plot = nom_values_smr_plot.replace({"Parameter": dict_sobol})
            nom_values_smr_plot = nom_values_smr_plot.loc[nom_values_smr_plot['Parameter'].isin([dict_sobol[j]] + [dict_sobol[self.objective]])]
            if smr_in:
                nom_values_ref_plot = nom_values_ref_plot.append(dict_ref_smr,ignore_index=True)
                nom_values_smr_plot = nom_values_smr_plot.append(dict_smr_smr,ignore_index=True)

                
                
            
            if focus == 'High':
                share = 20/3
                # temp_high = samples_plot.nlargest(round(len(samples_plot)/(share)),j)
                temp_low = samples_plot.nsmallest(round(len(samples_plot)/(share)),j)
                            
                temp_high = samples_plot.loc[samples_plot[j] >0.1]
                temp_low = samples_plot.loc[samples_plot[j] <0]
                
                # self.get_av_sample(temp_high['Sample'], j+'_'+focus)
                
                s_plot_full = samples_plot.copy()
                
                s_plot_full.drop(labels, axis=1,inplace=True)
                s_plot_full[j] = samples_plot[j]
                
                s_plot_full.loc[s_plot_full['Sample'].isin(temp_high['Sample']),'Significance'] = 'Significant'
                s_plot_full.loc[s_plot_full['Sample'].isin(temp_low['Sample']),'Significance'] = 'Not significant'
                
                s_plot_full = pd.melt(s_plot_full,var_name='x',value_name='value',id_vars=['Significance','Sample'])
                s_plot_full = s_plot_full.replace({"x": dict_sobol})                
                fig = px.strip(s_plot_full,x='x',y='value',color='Significance',
                               color_discrete_map={'Neutral': 'white','Significant':'blue', 'Not significant':'cyan'},
                               stripmode='overlay')
                
                s_plot_sum = s_plot_full.loc[s_plot_full['x'].isin(order_x)]
                
                s_plot_sum.sort_values(by='Significance',inplace=True)
                
                # temp = nom_values_plot.loc[nom_values_plot['Parameter']==output_of_interest,'Nominal'].values[0]
                
                
                if not(flip):
                    fig = px.strip(s_plot_sum,x='x',y='value',color='Significance',
                                    color_discrete_map={'Neutral': 'white','Significant':'blue', 'Not significant':'cyan'},
                                    stripmode='overlay',custom_data=['Sample'])
                    fig.update_layout(xaxis_tickangle=45)
                    fig.add_trace(go.Scatter(x=nom_values_plot["Parameter"], y=nom_values_plot["Nominal"],
                                              mode='markers',
                                              marker=dict(size=15,color='darkorange', symbol='diamond')))
                    fig.add_trace(go.Scatter(x=nom_values_ref_plot["Parameter"], y=nom_values_ref_plot["REF"],
                                              mode='markers',
                                              marker=dict(size=15,color='limegreen', symbol='diamond')))
                    fig.add_trace(go.Scatter(x=nom_values_smr_plot["Parameter"], y=nom_values_smr_plot["SMR"],
                                              mode='markers',
                                              marker=dict(size=15,color='deeppink', symbol='diamond')))
                    
                    xvals=order_x
                    
                    # if temp <= 0.02*max(samples_plot[j]) or temp >= 0.98*max(samples_plot[j]):
                    yvals=[0,1]
                    # else:
                    #     yvals=[0,round(temp,2),1]
                    
                else:
                    fig = px.strip(s_plot_sum,x='value',y='x',color='Significance',
                                    color_discrete_map={'Neutral': 'white','Significant':'blue', 'Not significant':'cyan'},
                                    stripmode='overlay',custom_data=['Sample'])
                    fig.add_trace(go.Scatter(x=nom_values_plot["Nominal"], y=nom_values_plot["Parameter"],
                                              mode='markers',
                                              marker=dict(size=15,color='darkorange', symbol='diamond')))
                    fig.add_trace(go.Scatter(x=nom_values_ref_plot["REF"], y=nom_values_ref_plot["Parameter"],
                                              mode='markers',
                                              marker=dict(size=15,color='limegreen', symbol='diamond')))
                    fig.add_trace(go.Scatter(x=nom_values_smr_plot["SMR"], y=nom_values_smr_plot["Parameter"],
                                              mode='markers',
                                              marker=dict(size=15,color='deeppink', symbol='diamond')))
                    order_x.reverse()
                    
                    # if temp <= 0.02*max(samples_plot[j]) or temp >= 0.98*max(samples_plot[j]):
                    xvals=[0,1]
                    # else:
                    #     xvals=[0,round(temp,2),1]
                        
                    yvals = order_x
                    fig.update_yaxes(categoryorder='array', categoryarray= order_x)
                
                title = None

                self.custom_fig(fig,title,yvals,
                                xvals=xvals,
                                type_graph='strip', flip = flip)
                
                if flip:
                    # if temp <= 0.02*max(samples_plot[j]) or temp >= 0.98*max(samples_plot[j]):
                    xvals = ['Min','Max']
                    fig.update_xaxes(
                        ticktext=xvals,
                        tickvals=[0,1]
                        )
                    # else:
                    #     xvals = ['Min',round(temp,2),'Max']
                    #     fig.update_xaxes(
                    #         ticktext=xvals,
                    #         tickvals=[0,round(temp,2),1]
                    #         )
                else:
                    # if temp <= 0.02*max(samples_plot[j]) or temp >= 0.98*max(samples_plot[j]):
                    yvals = ['Min','Max']
                    fig.update_yaxes(
                        ticktext=yvals,
                        tickvals=list(range(len(yvals)))
                        )
                    # else:
                    #     yvals = ['Min',round(temp,2),'Max']
                    #     fig.update_yaxes(
                    #         ticktext=yvals,
                    #         tickvals=list(range(len(yvals)))
                    #         )
                            
                            
                
                # Define the behavior of the hover tooltip
                fig.update_layout(hovermode='closest')
                if flip:
                    fig.update_traces(hovertemplate='Value: %{x}<br>Sample: %{customdata}')
                else:
                    fig.update_traces(hovertemplate='Value: %{y}<br>Sample: %{customdata}')
                
                pio.show(fig)
                
            if not os.path.exists(Path(self.outdir+"Samples/")):
                Path(self.outdir+"Samples").mkdir(parents=True,exist_ok=True)
            if not os.path.exists(Path(self.outdir+"Samples/_Raw/")):
                Path(self.outdir+"Samples/_Raw").mkdir(parents=True,exist_ok=True)
            
            fig.write_html(self.outdir+"Samples/_Raw/"+j+".html")
            fig.write_image(self.outdir+"Samples/"+j+".pdf", width=1200, height=550)
                
    
                
    
    def get_spec_output_test(self,dict_uq,output,element,year,focus='High',calc_Sobol=False, flip = True):
        
        labels = [None] * len(output)
        samples_plus = self.ampl_uq_collector['Samples'].copy()
        col_objective = samples_plus.columns.get_loc(self.objective)
        samples_plus = samples_plus.iloc[:,:col_objective+1]
        result_ref_full = dict()
        result_smr_full = dict()
        meaning_output = self.dict_meaning()
        for i in range(len(output)):
            
            nom_values = pd.DataFrame(index=samples_plus.columns,columns=['Nominal'],data=0)
            nom_values.index.name='Parameter'
            nom_values.update(self.uncert_nominal)
            
            nom_values_ref = pd.DataFrame(index=samples_plus.columns,columns=['REF'],data=0)
            nom_values_ref.index.name='Parameter'
            
            nom_values_smr = pd.DataFrame(index=samples_plus.columns,columns=['SMR'],data=0)
            nom_values_smr.index.name='Parameter'
            
            out = output[i]
            if out == 'F':
                el = element[i]
            elif out == 'Ft':
                el = element[i][0]
                layer = element[i][1]
            elif out == 'TotalGwp':
                el = element[i]
            y = year[i]
            label = out+'_'+el+'_'+y
            labels[i] = label
            if out == 'F':
                results = self.ampl_uq_collector['Assets'][['F','Sample']]
                results = results.loc[results.index.get_level_values('Technologies') == el]
                results.rename(columns = {out:label},inplace=True)
                
                result_ref = self.ref_results['Assets']['F']
                result_ref = result_ref.loc[result_ref.index.get_level_values('Technologies') == el]
                
                result_smr = self.smr_results['Assets']['F']
                result_smr = result_smr.loc[result_smr.index.get_level_values('Technologies') == el]
                
            elif out == 'Ft':
                results = self.ampl_uq_collector['Year_balance'][[layer,'Sample']]
                results = results.loc[results.index.get_level_values('Elements') == el]
                results.rename(columns = {layer:label},inplace=True)
                
                result_ref = self.ref_results['Year_balance'][layer]
                result_ref = result_ref.loc[result_ref.index.get_level_values('Elements') == el]
                
                result_smr = self.smr_results['Year_balance'][layer]
                result_smr = result_smr.loc[result_smr.index.get_level_values('Elements') == el]
            
            elif out == 'TotalGwp':
                results = self.ampl_uq_collector['TotalGwp'][['TotalGWP','Sample']]
                results.rename(columns = {'TotalGWP':label},inplace=True)
                result_ref = self.ref_results['TotalGwp']['TotalGWP']
                result_smr = self.smr_results['TotalGwp']['TotalGWP']
                results.index.name = 'Years'
                result_ref.index.name = 'Years'
                result_smr.index.name = 'Years'
                
                
            results = results.loc[results.index.get_level_values('Years') == y]
            result_ref = result_ref.loc[result_ref.index.get_level_values('Years') == y]
            result_smr = result_smr.loc[result_smr.index.get_level_values('Years') == y]
            
            if result_ref.empty:
                result_ref_full[label] = 0
            else:
                result_ref_full[label] = result_ref.values[0]
            
            if result_smr.empty:
                result_smr_full[label] = 0
            else:
                result_smr_full[label] = result_smr.values[0]

            results.reset_index(inplace=True)
            results = results.set_index(['Sample'])
            samples_plus[label] = results[label]
            samples_plus.fillna(0,inplace=True)
        
        samples_plus.to_csv(self.samples_file,index=False)
        dict_uq['objective names'] = dict_uq['objective names'] + labels
        
        samples_plot = samples_plus.copy()
        min_list = dict.fromkeys(samples_plus.columns)
        max_list = dict.fromkeys(samples_plus.columns)
        for i in samples_plus.columns:
            min_temp = min(samples_plot[i])
            min_list[i] = min_temp
            max_temp = max(samples_plot[i])
            max_list[i] = max_temp
            
            if i == self.objective:
                transition_cost_ref = self.get_transition_cost(case_study='ref')
                transition_cost_smr = self.get_transition_cost(case_study='smr')
                nom_values_ref.loc[i] = (transition_cost_ref-min_temp)/(max_temp-min_temp)*1-0
                nom_values_smr.loc[i] = (transition_cost_smr-min_temp)/(max_temp-min_temp)*1-0
            elif i in labels:
                nom_values_ref.loc[i] = (result_ref_full[i]-min_temp)/(max_temp-min_temp)*1-0
                nom_values_smr.loc[i] = (result_smr_full[i]-min_temp)/(max_temp-min_temp)*1-0
                
            samples_plot[i] = (samples_plot[i]-min_temp)/(max_temp-min_temp)*1-0
        
        samples_plot.reset_index(inplace=True)
        samples_plot['Significance'] = 'Neutral'

        dict_uq['draw pdf cdf'] = [False, 1e5]
        
        for i in range(len(output)):
            j = labels[i]
            out = output[i]
            if out == 'F':
                el = element[i]
            elif out == 'Ft':
                el = element[i][0]
            elif out == 'TotalGwp':
                el = 'Total gwp'
            
            output_of_interest = meaning_output[el]
            
            if out == 'F':
                output_of_interest +=' - Capacity'
                output_of_interest += ' [{}; {}] GW'.format(round(min_list[j],1),round(max_list[j],1))
            elif out == 'Ft':
                output_of_interest +=' - Import'
                output_of_interest += ' [{}; {}] TWh'.format(round(min_list[j]/1000,1),round(max_list[j]/1000,1))
            elif out == 'TotalGwp':
                output_of_interest += ' [{}; {}] MtCO2'.format(round(min_list[j]/1000,1),round(max_list[j]/1000,1))
            
            
            if calc_Sobol:
                dict_uq['objective of interest'] = j
                rheia_uq.run_uq(dict_uq,design_space = 'design_space.csv')
            
            x_meaning = self.uncert_param_meaning.copy()
            
            names, sobol = self.my_post_process_uq.get_sobol(self.case_study, j)
            temp_sobol = [x_meaning[names[m]]+' ('+str(round(100*sobol[m]))+ '%)' for m in range(len(names))]
            dict_sobol = dict.fromkeys(names)
            for k,l in enumerate(names):
                dict_sobol[l] = temp_sobol[k]
            dict_sobol[self.objective] = 'Total transition cost'
            dict_sobol[self.objective] += ' [{}; {}] b€'.format(round(min_list[self.objective]/1000),round(max_list[self.objective]/1000))
            dict_sobol[j] = output_of_interest
            n_threshold = len([i for i in sobol if i > 1/len(sobol)])
            param_to_keep = temp_sobol[:min(n_threshold,6)]
            
            smr_in = False
            for p in param_to_keep:
                if 'SMR' in p:
                    smr_in = True
                    dict_ref_smr = {'Parameter':p,'REF':0}
                    dict_smr_smr = {'Parameter':p,'SMR':0.6}
            
            order_x = [dict_sobol[j]] + param_to_keep + [dict_sobol[self.objective]]
            
            nom_values_plot = nom_values.reset_index()
            nom_values_plot = nom_values_plot.replace({"Parameter": dict_sobol})
            nom_values_plot = nom_values_plot.loc[nom_values_plot['Parameter'].isin(param_to_keep)]
            
            nom_values_ref_plot = nom_values_ref.reset_index()
            nom_values_ref_plot = nom_values_ref_plot.replace({"Parameter": dict_sobol})
            nom_values_ref_plot = nom_values_ref_plot.loc[nom_values_ref_plot['Parameter'].isin([dict_sobol[j]] + [dict_sobol[self.objective]])]
            
            nom_values_smr_plot = nom_values_smr.reset_index()
            nom_values_smr_plot = nom_values_smr_plot.replace({"Parameter": dict_sobol})
            nom_values_smr_plot = nom_values_smr_plot.loc[nom_values_smr_plot['Parameter'].isin([dict_sobol[j]] + [dict_sobol[self.objective]])]
            if smr_in:
                nom_values_ref_plot = nom_values_ref_plot.append(dict_ref_smr,ignore_index=True)
                nom_values_smr_plot = nom_values_smr_plot.append(dict_smr_smr,ignore_index=True)


                
            s_plot_full = samples_plot.copy()
            
            s_plot_full.drop(labels, axis=1,inplace=True)
            s_plot_full[j] = samples_plot[j]
            
            share = 20/3
            temp_high = samples_plot.nlargest(round(len(samples_plot)/(share)),j)
            temp_low = samples_plot.nsmallest(round(len(samples_plot)/(share)),j)
            
            s_plot_full.loc[s_plot_full['Sample'].isin(temp_high['Sample']),'Significance'] = 'Significant'
            s_plot_full.loc[s_plot_full['Sample'].isin(temp_low['Sample']),'Significance'] = 'Not significant'
            
            for k in s_plot_full.columns:
                if k in dict_sobol.keys():
                    s_plot_full.rename(columns = {k:dict_sobol[k]}, inplace = True)
                elif k == 'Significance':
                    pass
                else:
                    s_plot_full.drop(k, axis=1,inplace=True)
            for k in s_plot_full.columns:
                if not((k in order_x) or (k == 'Significance')):
                    s_plot_full.drop(k, axis=1,inplace=True)
                    
            fig = make_subplots(rows=len(param_to_keep), cols=1,subplot_titles=param_to_keep,
                                shared_xaxes=True)
            
            for k,l in enumerate(param_to_keep):
                fig.add_trace(go.Scatter(x=s_plot_full[dict_sobol[j]], y=s_plot_full[l],mode="markers"),row=k+1, col=1)
            
            fig.update_layout(height=1200, width=550, title_text=dict_sobol[j])
            
            pio.show(fig)
                
            if not os.path.exists(Path(self.outdir+"Samples/TEST/")):
                Path(self.outdir+"Samples/TEST").mkdir(parents=True,exist_ok=True)
            if not os.path.exists(Path(self.outdir+"Samples/TEST/_Raw/")):
                Path(self.outdir+"Samples/TEST/_Raw").mkdir(parents=True,exist_ok=True)
            
            fig.write_html(self.outdir+"Samples/TEST/_Raw/"+j+".html")
            fig.write_image(self.outdir+"Samples/TEST/"+j+".pdf", width=1200, height=550*len(param_to_keep)/2)
    
    def get_spec_output_test_2(self,dict_uq,output,element,year,focus='High',calc_Sobol=False, flip = True):
        
        labels = [None] * len(output)
        samples_plus = self.ampl_uq_collector['Samples'].copy()
        col_objective = samples_plus.columns.get_loc(self.objective)
        samples_plus = samples_plus.iloc[:,:col_objective+1]
        result_ref_full = dict()
        result_smr_full = dict()
        meaning_output = self.dict_meaning()
        for i in range(len(output)):
            
            nom_values = pd.DataFrame(index=samples_plus.columns,columns=['Nominal'],data=0)
            nom_values.index.name='Parameter'
            nom_values.update(self.uncert_nominal)
            
            nom_values_ref = pd.DataFrame(index=samples_plus.columns,columns=['REF'],data=0)
            nom_values_ref.index.name='Parameter'
            
            nom_values_smr = pd.DataFrame(index=samples_plus.columns,columns=['SMR'],data=0)
            nom_values_smr.index.name='Parameter'
            
            out = output[i]
            if out == 'F':
                el = element[i]
            elif out == 'Ft':
                el = element[i][0]
                layer = element[i][1]
            elif out == 'TotalGwp':
                el = element[i]
            y = year[i]
            label = out+'_'+el+'_'+y
            labels[i] = label
            if out == 'F':
                results = self.ampl_uq_collector['Assets'][['F','Sample']]
                results = results.loc[results.index.get_level_values('Technologies') == el]
                results.rename(columns = {out:label},inplace=True)
                
                result_ref = self.ref_results['Assets']['F']
                result_ref = result_ref.loc[result_ref.index.get_level_values('Technologies') == el]
                
                result_smr = self.smr_results['Assets']['F']
                result_smr = result_smr.loc[result_smr.index.get_level_values('Technologies') == el]
                
            elif out == 'Ft':
                results = self.ampl_uq_collector['Year_balance'][[layer,'Sample']]
                results = results.loc[results.index.get_level_values('Elements') == el]
                results.rename(columns = {layer:label},inplace=True)
                
                result_ref = self.ref_results['Year_balance'][layer]
                result_ref = result_ref.loc[result_ref.index.get_level_values('Elements') == el]
                
                result_smr = self.smr_results['Year_balance'][layer]
                result_smr = result_smr.loc[result_smr.index.get_level_values('Elements') == el]
            
            elif out == 'TotalGwp':
                results = self.ampl_uq_collector['TotalGwp'][['TotalGWP','Sample']]
                results.rename(columns = {'TotalGWP':label},inplace=True)
                result_ref = self.ref_results['TotalGwp']['TotalGWP']
                result_smr = self.smr_results['TotalGwp']['TotalGWP']
                results.index.name = 'Years'
                result_ref.index.name = 'Years'
                result_smr.index.name = 'Years'
                
                
            results = results.loc[results.index.get_level_values('Years') == y]
            result_ref = result_ref.loc[result_ref.index.get_level_values('Years') == y]
            result_smr = result_smr.loc[result_smr.index.get_level_values('Years') == y]
            
            if result_ref.empty:
                result_ref_full[label] = 0
            else:
                result_ref_full[label] = result_ref.values[0]
            
            if result_smr.empty:
                result_smr_full[label] = 0
            else:
                result_smr_full[label] = result_smr.values[0]

            results.reset_index(inplace=True)
            results = results.set_index(['Sample'])
            samples_plus[label] = results[label]
            samples_plus.fillna(0,inplace=True)
        
        samples_plus.to_csv(self.samples_file,index=False)
        dict_uq['objective names'] = dict_uq['objective names'] + labels
        
        samples_plot = samples_plus.copy()
        min_list = dict.fromkeys(samples_plus.columns)
        max_list = dict.fromkeys(samples_plus.columns)
        for i in samples_plus.columns:
            min_temp = min(samples_plot[i])
            min_list[i] = min_temp
            max_temp = max(samples_plot[i])
            max_list[i] = max_temp
            
            if i == self.objective:
                transition_cost_ref = self.get_transition_cost(case_study='ref')
                transition_cost_smr = self.get_transition_cost(case_study='smr')
                nom_values_ref.loc[i] = (transition_cost_ref-min_temp)/(max_temp-min_temp)*1-0
                nom_values_smr.loc[i] = (transition_cost_smr-min_temp)/(max_temp-min_temp)*1-0
            elif i in labels:
                nom_values_ref.loc[i] = (result_ref_full[i]-min_temp)/(max_temp-min_temp)*1-0
                nom_values_smr.loc[i] = (result_smr_full[i]-min_temp)/(max_temp-min_temp)*1-0
                
            samples_plot[i] = (samples_plot[i]-min_temp)/(max_temp-min_temp)*1-0
        
        samples_plot.reset_index(inplace=True)
        samples_plot['Significance'] = 'Neutral'

        dict_uq['draw pdf cdf'] = [False, 1e5]
        
        for i in range(len(output)):
            j = labels[i]
            out = output[i]
            if out == 'F':
                el = element[i]
            elif out == 'Ft':
                el = element[i][0]
            elif out == 'TotalGwp':
                el = 'Total gwp'
            
            output_of_interest = meaning_output[el]
            
            if out == 'F':
                output_of_interest +=' - Capacity'
                output_of_interest += ' [{}; {}] GW'.format(round(min_list[j],1),round(max_list[j],1))
            elif out == 'Ft':
                output_of_interest +=' - Import'
                output_of_interest += ' [{}; {}] TWh'.format(round(min_list[j]/1000,1),round(max_list[j]/1000,1))
            elif out == 'TotalGwp':
                output_of_interest += ' [{}; {}] MtCO2'.format(round(min_list[j]/1000,1),round(max_list[j]/1000,1))
            
            
            if calc_Sobol:
                dict_uq['objective of interest'] = j
                rheia_uq.run_uq(dict_uq,design_space = 'design_space.csv')
            
            x_meaning = self.uncert_param_meaning.copy()
            
            names, sobol = self.my_post_process_uq.get_sobol(self.case_study, j)
            temp_sobol = [x_meaning[names[m]]+' ('+str(round(100*sobol[m]))+ '%)' for m in range(len(names))]
            dict_sobol = dict.fromkeys(names)
            for k,l in enumerate(names):
                dict_sobol[l] = temp_sobol[k]
            dict_sobol[self.objective] = 'Total transition cost'
            dict_sobol[self.objective] += ' [{}; {}] b€'.format(round(min_list[self.objective]/1000),round(max_list[self.objective]/1000))
            dict_sobol[j] = output_of_interest
            n_threshold = len([i for i in sobol if i > 1/len(sobol)])
            param_to_keep = temp_sobol[:min(n_threshold,6)]
            
            smr_in = False
            for p in param_to_keep:
                if 'SMR' in p:
                    smr_in = True
                    dict_ref_smr = {'Parameter':p,'REF':0}
                    dict_smr_smr = {'Parameter':p,'SMR':0.6}
            
            order_x = [dict_sobol[j]] + param_to_keep + [dict_sobol[self.objective]]
            
            nom_values_plot = nom_values.reset_index()
            nom_values_plot = nom_values_plot.replace({"Parameter": dict_sobol})
            nom_values_plot = nom_values_plot.loc[nom_values_plot['Parameter'].isin(param_to_keep)]
            
            nom_values_ref_plot = nom_values_ref.reset_index()
            nom_values_ref_plot = nom_values_ref_plot.replace({"Parameter": dict_sobol})
            nom_values_ref_plot = nom_values_ref_plot.loc[nom_values_ref_plot['Parameter'].isin([dict_sobol[j]] + [dict_sobol[self.objective]])]
            
            nom_values_smr_plot = nom_values_smr.reset_index()
            nom_values_smr_plot = nom_values_smr_plot.replace({"Parameter": dict_sobol})
            nom_values_smr_plot = nom_values_smr_plot.loc[nom_values_smr_plot['Parameter'].isin([dict_sobol[j]] + [dict_sobol[self.objective]])]
            if smr_in:
                nom_values_ref_plot = nom_values_ref_plot.append(dict_ref_smr,ignore_index=True)
                nom_values_smr_plot = nom_values_smr_plot.append(dict_smr_smr,ignore_index=True)
                        
                
            s_plot_full = samples_plot.copy()
            
            s_plot_full.drop(labels, axis=1,inplace=True)
            s_plot_full[j] = samples_plot[j]
            
            share = 20/3
            temp_high = samples_plot.nlargest(round(len(samples_plot)/(share)),j)
            temp_low = samples_plot.nsmallest(round(len(samples_plot)/(share)),j)
            
            s_plot_full.loc[s_plot_full['Sample'].isin(temp_high['Sample']),'Significance'] = 'Significant'
            s_plot_full.loc[s_plot_full['Sample'].isin(temp_low['Sample']),'Significance'] = 'Not significant'
            
            s_plot_full = pd.melt(s_plot_full,var_name='x',value_name='value',id_vars=['Significance','Sample',j])
            s_plot_full = s_plot_full.replace({"x": dict_sobol})            
            
            order_x.pop(0)
            order_x.pop()
            
            s_plot_sum = s_plot_full.loc[s_plot_full['x'].isin(order_x)]
            s_plot_sum.rename(columns = {j:dict_sobol[j]}, inplace = True)
            s_plot_sum.sort_values(by='Significance',inplace=True)
            
            
    
            
            
            fig = px.scatter(s_plot_sum,x='value',y=dict_sobol[j],color='x',trendline='rolling',trendline_options=dict(window=int(len(s_plot_sum)/15),center=True,min_periods = 1,win_type='triang'))
            fig.update_traces(visible=False, selector=dict(mode="markers"))
            
            if not os.path.exists(Path(self.outdir+"Samples/TEST_2/")):
                Path(self.outdir+"Samples/TEST_2").mkdir(parents=True,exist_ok=True)
            

            xvals=[0,1]
            yvals=[0,1]
            # # else:
            # #     xvals=[0,round(temp,2),1]
                
            # yvals = order_x
            # fig.update_yaxes(categoryorder='array', categoryarray= order_x)
            
            # A = 4
            
            title = "<b>{}</b><br>Impacting parameters".format(dict_sobol[j])
            title = "<b>{}</b>".format(dict_sobol[j])

            self.custom_fig(fig,title,yvals,
                            xvals=xvals,
                            type_graph='strip', flip = flip)
            
            fig.add_shape(x0=fig.layout.xaxis.tickvals[0],x1=fig.layout.xaxis.tickvals[-1],
                      y0=nom_values_ref.loc[j][0],y1=nom_values_ref.loc[j][0],
                      type='line',layer="above",
                      line=dict(color='rgb(90,90,90)', width=2,dash='dot'),opacity=1)
            
            xvals = ['Min','Max']
            fig.update_xaxes(
                ticktext=xvals,
                tickvals=[0,1]
                )
            
            yvals = [round(min_list[j]/1000,1),round(max_list[j]/1000,1)]
            fig.update_yaxes(
                ticktext=yvals,
                tickvals=[0,1]
                )

            pio.show(fig)
                
            if not os.path.exists(Path(self.outdir+"Samples/TEST_2/")):
                Path(self.outdir+"Samples/TEST_2").mkdir(parents=True,exist_ok=True)
            if not os.path.exists(Path(self.outdir+"Samples/TEST_2/_Raw/")):
                Path(self.outdir+"Samples/TEST_2/_Raw").mkdir(parents=True,exist_ok=True)
            
            fig.write_html(self.outdir+"Samples/TEST_2/_Raw/"+j+".html")
            fig.write_image(self.outdir+"Samples/TEST_2/"+j+".pdf", width=1200, height=550)
     
    
    
    def get_spec_output_test_3(self,dict_uq,output,element,year,focus='High',calc_Sobol=False, flip = True):
        
        labels = [None] * len(output)
        samples_plus = self.ampl_uq_collector['Samples'].copy()
        col_objective = samples_plus.columns.get_loc(self.objective)
        samples_plus = samples_plus.iloc[:,:col_objective+1]
        result_ref_full = dict()
        result_smr_full = dict()
        meaning_output = self.dict_meaning()
        for i in range(len(output)):
            
            nom_values = pd.DataFrame(index=samples_plus.columns,columns=['Nominal'],data=0)
            nom_values.index.name='Parameter'
            nom_values.update(self.uncert_nominal)
            
            nom_values_ref = pd.DataFrame(index=samples_plus.columns,columns=['REF'],data=0)
            nom_values_ref.index.name='Parameter'
            
            nom_values_smr = pd.DataFrame(index=samples_plus.columns,columns=['SMR'],data=0)
            nom_values_smr.index.name='Parameter'
            
            out = output[i]
            if out == 'F':
                el = element[i]
            elif out == 'Ft':
                el = element[i][0]
                layer = element[i][1]
            elif out == 'TotalGwp':
                el = element[i]
            y = year[i]
            label = out+'_'+el+'_'+y
            labels[i] = label
            if out == 'F':
                results = self.ampl_uq_collector['Assets'][['F','Sample']]
                results = results.loc[results.index.get_level_values('Technologies') == el]
                results.rename(columns = {out:label},inplace=True)
                
                result_ref = self.ref_results['Assets']['F']
                result_ref = result_ref.loc[result_ref.index.get_level_values('Technologies') == el]
                
                result_smr = self.smr_results['Assets']['F']
                result_smr = result_smr.loc[result_smr.index.get_level_values('Technologies') == el]
                
            elif out == 'Ft':
                results = self.ampl_uq_collector['Year_balance'][[layer,'Sample']]
                results = results.loc[results.index.get_level_values('Elements') == el]
                results.rename(columns = {layer:label},inplace=True)
                
                result_ref = self.ref_results['Year_balance'][layer]
                result_ref = result_ref.loc[result_ref.index.get_level_values('Elements') == el]
                
                result_smr = self.smr_results['Year_balance'][layer]
                result_smr = result_smr.loc[result_smr.index.get_level_values('Elements') == el]
            
            elif out == 'TotalGwp':
                results = self.ampl_uq_collector['TotalGwp'][['TotalGWP','Sample']]
                results.rename(columns = {'TotalGWP':label},inplace=True)
                result_ref = self.ref_results['TotalGwp']['TotalGWP']
                result_smr = self.smr_results['TotalGwp']['TotalGWP']
                results.index.name = 'Years'
                result_ref.index.name = 'Years'
                result_smr.index.name = 'Years'
                
                
            results = results.loc[results.index.get_level_values('Years') == y]
            result_ref = result_ref.loc[result_ref.index.get_level_values('Years') == y]
            result_smr = result_smr.loc[result_smr.index.get_level_values('Years') == y]
            
            if result_ref.empty:
                result_ref_full[label] = 0
            else:
                result_ref_full[label] = result_ref.values[0]
            
            if result_smr.empty:
                result_smr_full[label] = 0
            else:
                result_smr_full[label] = result_smr.values[0]

            results.reset_index(inplace=True)
            results = results.set_index(['Sample'])
            samples_plus[label] = results[label]
            samples_plus.fillna(0,inplace=True)
        
        samples_plus.to_csv(self.samples_file,index=False)
        dict_uq['objective names'] = dict_uq['objective names'] + labels
        
        samples_plot = samples_plus.copy()
        min_list = dict.fromkeys(samples_plus.columns)
        max_list = dict.fromkeys(samples_plus.columns)
        for i in samples_plus.columns:
            min_temp = min(samples_plot[i])
            min_list[i] = min_temp
            max_temp = max(samples_plot[i])
            max_list[i] = max_temp
            
            if i == self.objective:
                transition_cost_ref = self.get_transition_cost(case_study='ref')
                transition_cost_smr = self.get_transition_cost(case_study='smr')
                nom_values_ref.loc[i] = (transition_cost_ref-min_temp)/(max_temp-min_temp)*1-0
                nom_values_smr.loc[i] = (transition_cost_smr-min_temp)/(max_temp-min_temp)*1-0
            elif i in labels:
                nom_values_ref.loc[i] = (result_ref_full[i]-min_temp)/(max_temp-min_temp)*1-0
                nom_values_smr.loc[i] = (result_smr_full[i]-min_temp)/(max_temp-min_temp)*1-0
                
            samples_plot[i] = (samples_plot[i]-min_temp)/(max_temp-min_temp)*1-0
        
        samples_plot.reset_index(inplace=True)
        samples_plot['Significance'] = 0

        dict_uq['draw pdf cdf'] = [False, 1e5]
        
        for i in range(len(output)):
            j = labels[i]
            out = output[i]
            if out == 'F':
                el = element[i]
            elif out == 'Ft':
                el = element[i][0]
            elif out == 'TotalGwp':
                el = 'Total gwp'
            
            output_of_interest = meaning_output[el]
            
            if out == 'F':
                output_of_interest +=' - Capacity'
                output_of_interest += ' [{}; {}] GW'.format(round(min_list[j],1),round(max_list[j],1))
            elif out == 'Ft':
                output_of_interest +=' - Import'
                output_of_interest += ' [{}; {}] TWh'.format(round(min_list[j]/1000,1),round(max_list[j]/1000,1))
            elif out == 'TotalGwp':
                output_of_interest += ' [{}; {}] MtCO2'.format(round(min_list[j]/1000,1),round(max_list[j]/1000,1))
            
            
            if calc_Sobol:
                dict_uq['objective of interest'] = j
                rheia_uq.run_uq(dict_uq,design_space = 'design_space.csv')
            
            x_meaning = self.uncert_param_meaning.copy()
            
            names, sobol = self.my_post_process_uq.get_sobol(self.case_study, j)
            temp_sobol = [x_meaning[names[m]]+' ('+str(round(100*sobol[m]))+ '%)' for m in range(len(names))]
            dict_sobol = dict.fromkeys(names)
            for k,l in enumerate(names):
                dict_sobol[l] = temp_sobol[k]
            dict_sobol[self.objective] = 'Total transition cost'
            dict_sobol[self.objective] += ' [{}; {}] b€'.format(round(min_list[self.objective]/1000),round(max_list[self.objective]/1000))
            dict_sobol[j] = output_of_interest
            n_threshold = len([i for i in sobol if i > 1/len(sobol)])
            param_to_keep = temp_sobol[:min(n_threshold,6)]
            param_to_keep = temp_sobol[:6]    

                    
            smr_in = False
            for p in param_to_keep:
                if 'SMR' in p:
                    smr_in = True
                    dict_ref_smr = {'Parameter':p,'REF':0}
                    dict_smr_smr = {'Parameter':p,'SMR':0.6}
            
            order_x = [dict_sobol[j]] + param_to_keep + [dict_sobol[self.objective]]
            
            nom_values_plot = nom_values.reset_index()
            nom_values_plot = nom_values_plot.replace({"Parameter": dict_sobol})
            nom_values_plot = nom_values_plot.loc[nom_values_plot['Parameter'].isin(param_to_keep)]
            
            nom_values_ref_plot = nom_values_ref.reset_index()
            nom_values_ref_plot = nom_values_ref_plot.replace({"Parameter": dict_sobol})
            nom_values_ref_plot = nom_values_ref_plot.loc[nom_values_ref_plot['Parameter'].isin([dict_sobol[j]] + [dict_sobol[self.objective]])]
            
            nom_values_smr_plot = nom_values_smr.reset_index()
            nom_values_smr_plot = nom_values_smr_plot.replace({"Parameter": dict_sobol})
            nom_values_smr_plot = nom_values_smr_plot.loc[nom_values_smr_plot['Parameter'].isin([dict_sobol[j]] + [dict_sobol[self.objective]])]
            if smr_in:
                nom_values_ref_plot = nom_values_ref_plot.append(dict_ref_smr,ignore_index=True)
                nom_values_smr_plot = nom_values_smr_plot.append(dict_smr_smr,ignore_index=True)

            share = 20/3
            temp_high = samples_plot.nlargest(round(len(samples_plot)/(share)),j)
            temp_low = samples_plot.nsmallest(round(len(samples_plot)/(share)),j)
            
            # self.get_av_sample(temp_high['Sample'], j+'_'+focus)
            
            s_plot_full = samples_plot.copy()
            
            s_plot_full.drop(labels, axis=1,inplace=True)
            s_plot_full[j] = samples_plot[j]
            
            s_plot_full.loc[s_plot_full['Sample'].isin(temp_high['Sample']),'Significance'] = -1
            s_plot_full.loc[s_plot_full['Sample'].isin(temp_low['Sample']),'Significance'] = 1
            
            s_plot_full = pd.melt(s_plot_full,var_name='x',value_name='value',id_vars=['Significance','Sample'])
            s_plot_full = s_plot_full.replace({"x": dict_sobol})                
            fig = px.strip(s_plot_full,x='x',y='value',color='Significance',
                           color_discrete_map={0: 'white', 1:'blue', -1:'cyan'},
                           stripmode='overlay')
            
            s_plot_sum = s_plot_full.loc[s_plot_full['x'].isin(order_x)]
            
            # s_plot_sum = s_plot_sum.loc[s_plot_sum['Significance'] != 0]
            
            
            n_split = 10
            l = np.linspace(1/n_split,1,n_split)
            mi_temp = pd.MultiIndex.from_product([param_to_keep,l])
            df_av = pd.DataFrame(0,index=mi_temp,columns=['Value'])
            for p in param_to_keep:
                for m,n in enumerate(l):
                    if m==0:
                        inf = 0
                    else:
                        inf = l[m-1]
                    s_plot_sum_temp = s_plot_sum.loc[(s_plot_sum['x']==p) & (s_plot_sum['value'] >= inf) & (s_plot_sum['value'] <= n)]
                    df_av.loc[(p,n),'Value']=np.mean(s_plot_sum_temp['Significance'])
            
            
            df_av.reset_index(inplace=True)
            df_av.level_1=0.1
            
            fig = px.bar(df_av,x='level_1',y='level_0',color='Value',color_continuous_scale='RdBu')
            fig.update_traces(width=0.3)
            # fig.update_coloraxes(showscale=False)
            
            
            order_x.pop()
            order_x.pop(0)
            order_x.reverse()
            
            # if temp <= 0.02*max(samples_plot[j]) or temp >= 0.98*max(samples_plot[j]):
            xvals=[0,1]
            # else:
            #     xvals=[0,round(temp,2),1]
                
            yvals = order_x
            fig.update_yaxes(categoryorder='array', categoryarray= order_x)
            
            A = 4
            
            title = "<b>{}</b><br>Impacting parameters".format(dict_sobol[j])
            title = "<b>{}</b>".format(dict_sobol[j])

            self.custom_fig(fig,title,yvals,
                            xvals=xvals,
                            type_graph='strip', flip = flip)
            
            if flip:
                # if temp <= 0.02*max(samples_plot[j]) or temp >= 0.98*max(samples_plot[j]):
                xvals = ['Min','Max']
                fig.update_xaxes(
                    ticktext=xvals,
                    tickvals=[0,1]
                    )
                # else:
                #     xvals = ['Min',round(temp,2),'Max']
                #     fig.update_xaxes(
                #         ticktext=xvals,
                #         tickvals=[0,round(temp,2),1]
                #         )
            else:
                # if temp <= 0.02*max(samples_plot[j]) or temp >= 0.98*max(samples_plot[j]):
                yvals = ['Min','Max']
                fig.update_yaxes(
                    ticktext=yvals,
                    tickvals=list(range(len(yvals)))
                    )
                # else:
                #     yvals = ['Min',round(temp,2),'Max']
                #     fig.update_yaxes(
                #         ticktext=yvals,
                #         tickvals=list(range(len(yvals)))
                #         )
                        
                        
            
            # Define the behavior of the hover tooltip
            fig.update_layout(hovermode='closest')
            if flip:
                fig.update_traces(hovertemplate='Value: %{x}<br>Sample: %{customdata}')
            else:
                fig.update_traces(hovertemplate='Value: %{y}<br>Sample: %{customdata}')
            
            pio.show(fig)
                
            if not os.path.exists(Path(self.outdir+"Samples/TEST_3/")):
                Path(self.outdir+"Samples/TEST_3").mkdir(parents=True,exist_ok=True)
            if not os.path.exists(Path(self.outdir+"Samples/TEST_3/_Raw/")):
                Path(self.outdir+"Samples/TEST_3/_Raw").mkdir(parents=True,exist_ok=True)
            
            fig.write_html(self.outdir+"Samples/TEST_3/_Raw/"+j+".html")
            fig.write_image(self.outdir+"Samples/TEST_3/"+j+".pdf", width=1200, height=550)
                
    
    def get_spec_output_test_4(self,dict_uq,output,element,year,focus='High',calc_Sobol=False, flip = True):
        
        labels = [None] * len(output)
        samples_plus = self.ampl_uq_collector['Samples'].copy()
        col_objective = samples_plus.columns.get_loc(self.objective)
        samples_plus = samples_plus.iloc[:,:col_objective+1]
        result_ref_full = dict()
        result_smr_full = dict()
        meaning_output = self.dict_meaning()
        for i in range(len(output)):
            
            nom_values = pd.DataFrame(index=samples_plus.columns,columns=['Nominal'],data=0)
            nom_values.index.name='Parameter'
            nom_values.update(self.uncert_nominal)
            
            nom_values_ref = pd.DataFrame(index=samples_plus.columns,columns=['REF'],data=0)
            nom_values_ref.index.name='Parameter'
            
            nom_values_smr = pd.DataFrame(index=samples_plus.columns,columns=['SMR'],data=0)
            nom_values_smr.index.name='Parameter'
            
            out = output[i]
            if out == 'F':
                el = element[i]
            elif out == 'Ft':
                el = element[i][0]
                layer = element[i][1]
            elif out == 'TotalGwp':
                el = element[i]
            y = year[i]
            label = out+'_'+el+'_'+y
            labels[i] = label
            if out == 'F':
                results = self.ampl_uq_collector['Assets'][['F','Sample']]
                results = results.loc[results.index.get_level_values('Technologies') == el]
                results.rename(columns = {out:label},inplace=True)
                
                result_ref = self.ref_results['Assets']['F']
                result_ref = result_ref.loc[result_ref.index.get_level_values('Technologies') == el]
                
                result_smr = self.smr_results['Assets']['F']
                result_smr = result_smr.loc[result_smr.index.get_level_values('Technologies') == el]
                
            elif out == 'Ft':
                results = self.ampl_uq_collector['Year_balance'][[layer,'Sample']]
                results = results.loc[results.index.get_level_values('Elements') == el]
                results.rename(columns = {layer:label},inplace=True)
                
                result_ref = self.ref_results['Year_balance'][layer]
                result_ref = result_ref.loc[result_ref.index.get_level_values('Elements') == el]
                
                result_smr = self.smr_results['Year_balance'][layer]
                result_smr = result_smr.loc[result_smr.index.get_level_values('Elements') == el]
            
            elif out == 'TotalGwp':
                results = self.ampl_uq_collector['TotalGwp'][['TotalGWP','Sample']]
                results.rename(columns = {'TotalGWP':label},inplace=True)
                result_ref = self.ref_results['TotalGwp']['TotalGWP']
                result_smr = self.smr_results['TotalGwp']['TotalGWP']
                results.index.name = 'Years'
                result_ref.index.name = 'Years'
                result_smr.index.name = 'Years'
                
                
            results = results.loc[results.index.get_level_values('Years') == y]
            result_ref = result_ref.loc[result_ref.index.get_level_values('Years') == y]
            result_smr = result_smr.loc[result_smr.index.get_level_values('Years') == y]
            
            if result_ref.empty:
                result_ref_full[label] = 0
            else:
                result_ref_full[label] = result_ref.values[0]
            
            if result_smr.empty:
                result_smr_full[label] = 0
            else:
                result_smr_full[label] = result_smr.values[0]

            results.reset_index(inplace=True)
            results = results.set_index(['Sample'])
            samples_plus[label] = results[label]
            samples_plus.fillna(0,inplace=True)
        
        samples_plus.to_csv(self.samples_file,index=False)
        dict_uq['objective names'] = dict_uq['objective names'] + labels
        
        samples_plot = samples_plus.copy()
        min_list = dict.fromkeys(samples_plus.columns)
        max_list = dict.fromkeys(samples_plus.columns)
        for i in samples_plus.columns:
            min_temp = min(samples_plot[i])
            min_list[i] = min_temp
            max_temp = max(samples_plot[i])
            max_list[i] = max_temp
            
            if i == self.objective:
                transition_cost_ref = self.get_transition_cost(case_study='ref')
                transition_cost_smr = self.get_transition_cost(case_study='smr')
                nom_values_ref.loc[i] = (transition_cost_ref-min_temp)/(max_temp-min_temp)*1-0
                nom_values_smr.loc[i] = (transition_cost_smr-min_temp)/(max_temp-min_temp)*1-0
            elif i in labels:
                nom_values_ref.loc[i] = (result_ref_full[i]-min_temp)/(max_temp-min_temp)*1-0
                nom_values_smr.loc[i] = (result_smr_full[i]-min_temp)/(max_temp-min_temp)*1-0
                
            samples_plot[i] = (samples_plot[i]-min_temp)/(max_temp-min_temp)*1-0
        
        samples_plot.reset_index(inplace=True)
        samples_plot['Significance'] = 0

        dict_uq['draw pdf cdf'] = [False, 1e5]
        
        for i in range(len(output)):
            j = labels[i]
            out = output[i]
            if out == 'F':
                el = element[i]
            elif out == 'Ft':
                el = element[i][0]
            elif out == 'TotalGwp':
                el = 'Total gwp'
            
            output_of_interest = meaning_output[el]
            
            if out == 'F':
                output_of_interest +=' - Capacity'
                output_of_interest += ' [{}; {}] GW'.format(round(min_list[j],1),round(max_list[j],1))
            elif out == 'Ft':
                output_of_interest +=' - Import'
                output_of_interest += ' [{}; {}] TWh'.format(round(min_list[j]/1000,1),round(max_list[j]/1000,1))
            elif out == 'TotalGwp':
                output_of_interest += ' [{}; {}] MtCO2'.format(round(min_list[j]/1000,1),round(max_list[j]/1000,1))
            
            
            if calc_Sobol:
                dict_uq['objective of interest'] = j
                rheia_uq.run_uq(dict_uq,design_space = 'design_space.csv')
            
            x_meaning = self.uncert_param_meaning.copy()
            
            names, sobol = self.my_post_process_uq.get_sobol(self.case_study, j)
            temp_sobol = [x_meaning[names[m]]+' ('+str(round(100*sobol[m]))+ '%)' for m in range(len(names))]
            dict_sobol = dict.fromkeys(names)
            for k,l in enumerate(names):
                dict_sobol[l] = temp_sobol[k]
            dict_sobol[self.objective] = 'Total transition cost'
            dict_sobol[self.objective] += ' [{}; {}] b€'.format(round(min_list[self.objective]/1000),round(max_list[self.objective]/1000))
            dict_sobol[j] = output_of_interest
            n_threshold = len([i for i in sobol if i > 1/len(sobol)])
            param_to_keep = temp_sobol[:min(n_threshold,6)]    

                    
            smr_in = False
            for p in param_to_keep:
                if 'SMR' in p:
                    smr_in = True
                    dict_ref_smr = {'Parameter':p,'REF':0}
                    dict_smr_smr = {'Parameter':p,'SMR':0.6}
            
            order_x = [dict_sobol[j]] + param_to_keep + [dict_sobol[self.objective]]
            
            nom_values_plot = nom_values.reset_index()
            nom_values_plot = nom_values_plot.replace({"Parameter": dict_sobol})
            nom_values_plot = nom_values_plot.loc[nom_values_plot['Parameter'].isin(param_to_keep)]
            
            nom_values_ref_plot = nom_values_ref.reset_index()
            nom_values_ref_plot = nom_values_ref_plot.replace({"Parameter": dict_sobol})
            nom_values_ref_plot = nom_values_ref_plot.loc[nom_values_ref_plot['Parameter'].isin([dict_sobol[j]] + [dict_sobol[self.objective]])]
            
            nom_values_smr_plot = nom_values_smr.reset_index()
            nom_values_smr_plot = nom_values_smr_plot.replace({"Parameter": dict_sobol})
            nom_values_smr_plot = nom_values_smr_plot.loc[nom_values_smr_plot['Parameter'].isin([dict_sobol[j]] + [dict_sobol[self.objective]])]
            if smr_in:
                nom_values_ref_plot = nom_values_ref_plot.append(dict_ref_smr,ignore_index=True)
                nom_values_smr_plot = nom_values_smr_plot.append(dict_smr_smr,ignore_index=True)

            share = 20/3
            temp_high = samples_plot.nlargest(round(len(samples_plot)/(share)),j)
            temp_low = samples_plot.nsmallest(round(len(samples_plot)/(share)),j)
            
            # self.get_av_sample(temp_high['Sample'], j+'_'+focus)
            
            s_plot_full = samples_plot.copy()
            
            s_plot_full.drop(labels, axis=1,inplace=True)
            s_plot_full[j] = samples_plot[j]
            
            s_plot_full.loc[s_plot_full['Sample'].isin(temp_high['Sample']),'Significance'] = -1
            s_plot_full.loc[s_plot_full['Sample'].isin(temp_low['Sample']),'Significance'] = 1
            
            # s_plot_full = pd.melt(s_plot_full,var_name='x',value_name='value',id_vars=['Significance','Sample'])
            # s_plot_full = s_plot_full.replace({"x": dict_sobol})
            s_plot_full.rename(columns=dict_sobol, inplace=True)
            s_plot_sum = s_plot_full[order_x+['Sample']]
            
            order_x.pop()
            order_x.pop(0)
            
            
            fig = go.Figure()
            
            for x in order_x:
                temp = s_plot_sum[[dict_sobol[j],x,'Sample']]
                temp = temp.sort_values(by=x)
                temp_rol = temp[dict_sobol[j]].rolling(window=int(len(temp)/5),center=True,min_periods = 1,win_type='triang').mean()

                fig.add_trace(go.Scatter(x=temp[x],y=temp_rol,line_shape='spline',line=dict(width=2)))

                
                share = 20/3
                temp_high = temp.nlargest(round(len(temp)/(share)),x)
                temp_low = temp.nsmallest(round(len(temp)/(share)),x)
                
                yvals = [0,1]
                xvals = [0,1]
                title = 'Boxplot High - {}'.format(x)
                
                fig_high = px.box(temp_high, y=dict_sobol[j],
                               title=title,notched=True)
                fig_high.update_layout(yaxis_range=yvals)
                
                fig_high.write_image(self.outdir+"Samples/TEST_4/"+j+"_Box_high_{}".format(x)+".pdf", width=1200, height=550)
                fig_high.write_html(self.outdir+"Samples/TEST_4/_Raw/"+j+"_Box_high_{}".format(x)+".html")
                
                title = 'Boxplot Low- {}'.format(x)
                
                fig_low = px.box(temp_low, y=dict_sobol[j],
                               title=title,notched=True)
                fig_low.update_layout(yaxis_range=yvals)
                
                fig_low.write_image(self.outdir+"Samples/TEST_4/"+j+"_Box_low_{}".format(x)+".pdf", width=1200, height=550)
                fig_low.write_html(self.outdir+"Samples/TEST_4/_Raw/"+j+"_Box_low_{}".format(x)+".html")
                

            xvals=[0,1]
            yvals=[0,1]
            # # else:
            # #     xvals=[0,round(temp,2),1]
                
            # yvals = order_x
            # fig.update_yaxes(categoryorder='array', categoryarray= order_x)
            
            # A = 4
            
            title = "<b>{}</b><br>Impacting parameters".format(dict_sobol[j])
            title = "<b>{}</b>".format(dict_sobol[j])

            self.custom_fig(fig,title,yvals,
                            xvals=xvals,
                            type_graph='strip', flip = flip)
            
            fig.add_shape(x0=fig.layout.xaxis.tickvals[0],x1=fig.layout.xaxis.tickvals[-1],
                      y0=nom_values_ref.loc[j][0],y1=nom_values_ref.loc[j][0],
                      type='line',layer="above",
                      line=dict(color='rgb(90,90,90)', width=2,dash='dot'),opacity=1)
            
            xvals = ['Min','Max']
            fig.update_xaxes(
                ticktext=xvals,
                tickvals=[0,1]
                )
            
            yvals = [round(min_list[j]/1000,1),round(result_ref_full[j]/1000,1),round(max_list[j]/1000,1)]
            fig.update_yaxes(
                ticktext=yvals,
                tickvals=[0,nom_values_ref.loc[j][0],1]
                )

            pio.show(fig)
                
            if not os.path.exists(Path(self.outdir+"Samples/TEST_4/")):
                Path(self.outdir+"Samples/TEST_4").mkdir(parents=True,exist_ok=True)
            if not os.path.exists(Path(self.outdir+"Samples/TEST_4/_Raw/")):
                Path(self.outdir+"Samples/TEST_4/_Raw").mkdir(parents=True,exist_ok=True)
            
            fig.write_html(self.outdir+"Samples/TEST_4/_Raw/"+j+".html")
            fig.write_image(self.outdir+"Samples/TEST_4/"+j+".pdf", width=1200, height=550)
        
        
    
    def get_spec_sample(self,sample):
        output_file = os.path.join(Path(self.outdir).parent.absolute(),'Runs/Run{}'.format(sample))
        ampl_0  = self.ampl_obj
        case_study = self.case_study
        ampl_graph = AmplGraph(output_file, ampl_0, case_study)
        ampl_graph.outdir=os.path.join(ampl_graph.outdir,'Run{}/'.format(sample))
        if not os.path.exists(Path(ampl_graph.outdir)):
            Path(ampl_graph.outdir).mkdir(parents=True,exist_ok=True)
        # ampl_graph.graph_resource()
        # ampl_graph.graph_tech_cap()
        ampl_graph.graph_gwp_per_sector()
        ampl_graph.graph_layer()
        ampl_graph.graph_load_factor_scaled()
    
    def get_av_sample(self,sample_list,case):
        uq_collector = self.ampl_uq_collector.copy()
        for key in uq_collector:
            if key != 'Samples':
                temp = uq_collector[key].loc[uq_collector[key]['Sample'].isin(sample_list)]
                if len(temp.index.names) == 1:
                    temp.reset_index(inplace=True)
                    temp = temp.set_index(temp.columns[0])
                temp.drop(['Sample'],axis=1,inplace=True)
                uq_collector[key] = temp.groupby(temp.index.names).mean()
            else:
                uq_collector[key] = uq_collector[key].loc[uq_collector[key].index.get_level_values('Sample').isin(sample_list),:]
        
        pkl_folder = os.path.join(Path(self.outdir).parent.absolute(),'Runs/graphs/{}'.format(case))
        if not os.path.exists(Path(pkl_folder)):
            Path(pkl_folder).mkdir(parents=True,exist_ok=True)
        
        open_file = open(pkl_folder+'/_uq_collector.p',"wb")
        pkl.dump(uq_collector, open_file)
        open_file.close()
        
        output_file = os.path.join(Path(pkl_folder).absolute(),'_uq_collector.p')
        ampl_0  = self.ampl_obj
        case_study = self.case_study
        ampl_graph = AmplGraph(output_file, ampl_0, case_study)
        ampl_graph.outdir=pkl_folder+'/'
        if not os.path.exists(Path(ampl_graph.outdir)):
            Path(ampl_graph.outdir).mkdir(parents=True,exist_ok=True)
        ampl_graph.graph_resource()
        ampl_graph.graph_tech_cap()
        # ampl_graph.graph_gwp_per_sector()
        ampl_graph.graph_layer()
        
        
        
        
    
    def get_transition_cost(self,case_study='ref'):
        ampl_0  = self.ampl_obj
        if case_study == 'ref':
            output_file = self.ref_file
            case_study = self.ref_case
            ampl_graph = AmplGraph(output_file, ampl_0, case_study)
            transition_cost = ampl_graph._compute_transition_cost(self.ref_results)
        elif case_study == 'smr':
            output_file = self.smr_file
            case_study = self.smr_case
            ampl_graph = AmplGraph(output_file, ampl_0, case_study)
            transition_cost = ampl_graph._compute_transition_cost(self.smr_results)
        
        transition_cost_2050 = transition_cost['2050']
        
        return 1000*transition_cost_2050
        
    @staticmethod
    def unpkl(self,case_study = None):
        if case_study == None:
            case_study_dir_path = self.case_study_dir_path
        pkl_file = os.path.join(case_study_dir_path,'_uq_collector.p')
        
        open_file = open(pkl_file,"rb")
        loaded_results = pkl.load(open_file)
        open_file.close()

        return loaded_results
    
    @staticmethod
    def get_nominal(uncert_range):
        uncert_range['Nominal'] = (0-uncert_range['Range_min'])/(uncert_range['Range_max']-uncert_range['Range_min'])*1-0
        if 'f_max_nuclear_smr' in (uncert_range.index):
            uncert_range.loc['f_max_nuclear_smr','Nominal'] = 0
        return pd.DataFrame(uncert_range['Nominal'])
        

    def gather_results(self):
        uq_path = self.case_study_dir_path
        uq_path_runs = uq_path + "/Runs/"
        
        if not(Path(os.path.join(uq_path,'_uq_collector.p')).is_file()):
            uq_collector = {}
            dir = sorted(os.listdir(uq_path_runs))
            for i, file in enumerate(dir):
                if "Run" in file:
                    sample = int(file[3:])
                    open_file = open(uq_path_runs+file,"rb")
                    loaded_results = pkl.load(open_file)
                    if not(uq_collector):
                        for key in loaded_results:
                            loaded_results[key]['Sample'] = sample
                        uq_collector = loaded_results
                    else:
                        for key in uq_collector:
                            loaded_results[key]['Sample'] = sample
                            uq_collector[key] = uq_collector[key].append(loaded_results[key])
            
            open_file = open(uq_path+'/_uq_collector.p',"wb")
            pkl.dump(uq_collector, open_file)
            open_file.close()

    def fill_df_sobol_obj(self):
        result_dir = [self.case_study]+self.result_dir
        df_sobol = pd.DataFrame(columns=['Param','Sobol','Ranking','Case'])
        for i, j in enumerate(result_dir):

            names, sobol = self.my_post_process_uq.get_sobol(j, self.objective)
            df_sobol_temp = pd.DataFrame(columns=df_sobol.columns)
            df_sobol_temp.loc[:,'Param'] = names
            df_sobol_temp.loc[:,'Sobol'] = np.array(sobol)*100
            df_sobol_temp.loc[:,'Ranking'] = list(range(1,len(names)+1))
            df_sobol_temp.loc[:,'Case'] = j
            
            if i!=0:
                df_sobol = pd.concat([df_sobol,df_sobol_temp])
            else:
                df_sobol = df_sobol_temp
            
            self.threshold = min(self.threshold,1/len(names))
        
        self.df_sobol = df_sobol
    
    def fill_df_pdf(self):
        result_dir = [self.case_study]+self.result_dir
        df_pdf = pd.DataFrame(columns=['x_pdf','y_pdf','Case'])

        for i, j in enumerate(result_dir):
            
            x_pdf, y_pdf = self.my_post_process_uq.get_pdf(j, self.objective)
            poly_func = self._polyfit_func(x_pdf, y_pdf)
            y_pdf = poly_func(x_pdf)
            df_pdf_temp = pd.DataFrame(columns=df_pdf.columns)
            df_pdf_temp.loc[:,'x_pdf'] = x_pdf
            df_pdf_temp.loc[:,'y_pdf'] = y_pdf
            df_pdf_temp.loc[:,'Case'] = j 
            
            if i!=0:
                df_pdf = pd.concat([df_pdf,df_pdf_temp])
            else:
                df_pdf = df_pdf_temp
            
        self.df_pdf = df_pdf
    
    def fill_df_cdf(self):
        result_dir = [self.case_study]+self.result_dir
        df_cdf = pd.DataFrame(columns=['x_cdf','y_cdf','Case'])

        for i, j in enumerate(result_dir):
            
            x_cdf, y_cdf = self.my_post_process_uq.get_cdf(j, self.objective)
            df_cdf_temp = pd.DataFrame(columns=df_cdf.columns)
            df_cdf_temp.loc[:,'x_cdf'] = x_cdf
            df_cdf_temp.loc[:,'y_cdf'] = y_cdf
            df_cdf_temp.loc[:,'Case'] = j 
            
            if i!=0:
                df_cdf = pd.concat([df_cdf,df_cdf_temp])
            else:
                df_cdf = df_cdf_temp
            
            self.df_cdf = df_cdf
        
    def filter_df_sobol(self,threshold = 1):
        self.fill_df_sobol_obj()
        threshold_inc = self.threshold*threshold
        param_plot = self.df_sobol.loc[self.df_sobol['Sobol']>=threshold_inc]['Param'].unique()
        self.df_sobol_plot = self.df_sobol.loc[self.df_sobol['Param'].isin(param_plot)]
        
    def graph_sobol(self,threshold=1):
        self.filter_df_sobol(threshold)
        fig = px.bar(self.df_sobol_plot,x='Sobol',y='Param',color='Case',
                      title='Sobol index per case',orientation='h')
        fig.update_layout(barmode='group', xaxis_tickangle=45)
        pio.show(fig)
        fig.write_html(self.outdir+"Sobol_raw.html")
        
        title = "<b>Sobol index per case</b><br>[%]"
        temp = self.df_sobol_plot.copy()
        yvals = [0,max(round(temp['Sobol'],100))]
        yvals = self.df_sobol_plot.Param.unique()
        param_meaning = self.uncert_param_meaning.copy()
        for i,p in enumerate(yvals):
            yvals[i] = param_meaning[p]
        xvals = [0,max(round(temp['Sobol'],1))]
        
        self.custom_fig(fig,title,yvals,xvals=xvals,type_graph='bar')
        fig.write_image(self.outdir+"Sobol.pdf", width=1200, height=550)
        plt.close()
    
    def graph_pdf(self):
        self.fill_df_pdf()
        self.df_pdf['x_pdf'] /= 1e6
        self.df_pdf['y_pdf'] /= max(self.df_pdf['y_pdf'])
        fig = px.line(self.df_pdf,x='x_pdf',y='y_pdf',color='Case',
                      title='PDF per case')
        
        fig.write_html(self.outdir+"PDF_raw.html")
        
        title = "<b>PDF of total transition cost</b><br>[10<sup>3</sup>b€]"
        temp = self.df_pdf.copy()
        yvals = [0,max(temp['y_pdf'])]
        
        mean_cost = 1160748.416529/1e6
        
        nom_cost = 1079.5/1e3
        SMR_cost = nom_cost-36.9/1e3
        xvals = sorted([min(round(temp['x_pdf'],2)),round(nom_cost,2),round(SMR_cost,2),round(mean_cost,2),max(round(temp['x_pdf'],2))])
        
        self.custom_fig(fig,title,yvals,xvals=xvals,flip=True)
        fig.write_image(self.outdir+"PDF.pdf", width=1200, height=550)
        plt.close()
        
    
    def graph_cdf(self):
        self.fill_df_cdf()
        fig = px.line(self.df_cdf,x='x_cdf',y='y_cdf',color='Case',
                      title='CDF per case')
        
        fig.write_html(self.outdir+"CDF_raw.html")
        
        title = "<b>CDF per case</b><br>[k€]"
        temp = self.df_cdf.copy()
        yvals = [0,0.5,round(max(temp['y_cdf']))]
        
        self.custom_fig(fig,title,yvals)
        fig.write_image(self.outdir+"CDF.pdf", width=1200, height=550)
        plt.close()
        
    def graph_tech_cap(self, ampl_uq_collector = None, plot = True):
        
        if ampl_uq_collector == None:
            ampl_uq_collector = self.ampl_uq_collector
            
        results = ampl_uq_collector['Assets'].copy()
        results.reset_index(inplace=True)
        results = results.set_index(['Years','Technologies','Sample'])
        dict_tech = self._group_tech_per_eud()
        df_to_plot_full = pd.DataFrame()
        for sector, tech in dict_tech.items():

            temp = results.loc[results.index.get_level_values('Technologies').isin(tech),'F']
            df_to_plot = pd.DataFrame(index=temp.index,columns=['F'])
            for y in temp.index.get_level_values(0).unique():
                temp_y = temp.loc[temp.index.get_level_values('Years') == y]
                temp_y.dropna(how='all',inplace=True)
                if not temp_y.empty:
                    temp_y = self._remove_low_values(temp_y,threshold=0.05)
                    df_to_plot.update(temp_y)
            df_to_plot.dropna(how='all',inplace=True)
            
            df_to_plot = self._fill_df_to_plot_w_zeros(df_to_plot)
            
            df_to_plot.reset_index(inplace=True)
            df_to_plot['Technologies'] = df_to_plot['Technologies'].astype("str")
            df_to_plot['Years'] = df_to_plot['Years'].str.replace('YEAR_', '')
            
            if plot:
                # if len(df_to_plot.index.get_level_values(0).unique()) <= 1:
                #     fig = px.bar(df_to_plot, x='Years', y = 'F',color='Technologies',
                #                  title=self.case_study + ' - ' + sector+' - Installed capacity',
                #                  color_discrete_map=self.color_dict_full)
                # else:
                    
                fig = px.box(df_to_plot, x='Years', y = 'F',color='Technologies',
                         title= sector+' - Installed capacity',
                         color_discrete_map=self.color_dict_full)
                # fig.for_each_trace(lambda trace: trace.update(fillcolor = trace.line.color))
                # fig.update_traces(mode='none')
                fig.update_xaxes(categoryorder='array', categoryarray= sorted(df_to_plot['Years'].unique()))
                        
                if len(df_to_plot.index.get_level_values(0).unique()) >= 1:
                    pio.show(fig)
                    if not os.path.exists(Path(self.outdir+"Tech_Cap/")):
                        Path(self.outdir+"Tech_Cap").mkdir(parents=True,exist_ok=True)
                    if not os.path.exists(Path(self.outdir+"Tech_Cap/_Raw/")):
                        Path(self.outdir+"Tech_Cap/_Raw").mkdir(parents=True,exist_ok=True)
                    
                    fig.write_html(self.outdir+"Tech_Cap/_Raw/"+sector+"_raw.html")
                    title = "<b>{} - Installed capacities</b><br>[GW]".format(sector)
                    temp = df_to_plot.copy()
                    yvals = [0,round(min(temp['F']),1),round(max(temp['F']),1)]
                    
                    self.custom_fig(fig,title,yvals,xvals=sorted(df_to_plot['Years'].unique()),type_graph='bar')
                        
                    
                    fig.write_image(self.outdir+"Tech_Cap/"+sector+".pdf", width=1200, height=550)
                plt.close()
            
            if len(df_to_plot_full) == 0:
                df_to_plot_full = df_to_plot
            else:
                df_to_plot_full = df_to_plot_full.append(df_to_plot)
            
        return df_to_plot_full
    
    def graph_electrofuels(self, ampl_uq_collector = None, plot = True):
        pio.renderers.default = 'browser'
        
        if ampl_uq_collector == None:
            ampl_uq_collector = self.ampl_uq_collector
        
        col_plot = ['METHANOL_RE','AMMONIA_RE','GAS_RE','H2_RE']
        results = ampl_uq_collector['Resources'].copy()
        results.reset_index(inplace=True)
        results = results.loc[results['Resources'].isin(col_plot),:]
        results['Resources'] = results['Resources'].astype("str")
        results.dropna(how='all',inplace=True)
        results['Res']/=1000
        
        df_to_plot = results.copy()
        df_to_plot = df_to_plot.set_index(['Years','Resources','Sample'])
        df_to_plot.dropna(how='all',inplace=True)
        df_to_plot = self._fill_df_to_plot_w_zeros(df_to_plot)
        df_to_plot.reset_index(inplace=True)
        
        df_to_plot['Years'] = df_to_plot['Years'].str.replace('YEAR_', '')
        
            
        if plot:
            fig = px.box(df_to_plot, x='Years', color='Resources',y='Res',
                           title='Electrofuels [TWh]',
                           color_discrete_map=self.color_dict_full,notched=True)
                
            fig.update_xaxes(categoryorder='array', categoryarray= sorted(df_to_plot['Years'].unique()))
            pio.show(fig)
            
            fig.write_html(self.outdir+"/Electrofuels.html")
        
            title = "<b>Imported renewable electrofuels</b><br>[TWh]"
            yvals = [0,round(max(df_to_plot['Res']))]
            
            self.custom_fig(fig,title,yvals,type_graph='bar')

            fig.write_image(self.outdir+"Electrofuels.pdf", width=1200, height=550)
            plt.close()
    
    def graph_local_RE(self, ampl_uq_collector = None, plot = True):
        pio.renderers.default = 'browser'
        
        if ampl_uq_collector == None:
            ampl_uq_collector = self.ampl_uq_collector
        
        col_plot = ['PV','WIND_ONSHORE','WIND_OFFSHORE']
        results = ampl_uq_collector['Assets'].copy()
        results.reset_index(inplace=True)
        results = results.loc[results['Technologies'].isin(col_plot),:]
        results['Technologies'] = results['Technologies'].astype("str")
        results.dropna(how='all',inplace=True)
        results['F_year']/=1000
        
        df_to_plot = results.copy()
        df_to_plot = df_to_plot.set_index(['Years','Technologies','Sample'])
        df_to_plot.dropna(how='all',inplace=True)
        df_to_plot = self._fill_df_to_plot_w_zeros(df_to_plot)
        df_to_plot.reset_index(inplace=True)
        
        df_to_plot['Years'] = df_to_plot['Years'].str.replace('YEAR_', '')
        
            
        if plot:
            fig = px.box(df_to_plot, x='Years', color='Technologies',y='F',
                           title='Local renewable capacities [GW]',
                           color_discrete_map=self.color_dict_full,notched=True)
                
            fig.update_xaxes(categoryorder='array', categoryarray= sorted(df_to_plot['Years'].unique()))
            pio.show(fig)
            
            fig.write_html(self.outdir+"/Local_Ren_Cap.html")
        
            title = "<b>Local renewables - Capacities</b><br>[GW]"
            yvals = [0,round(max(df_to_plot['F']))]
            
            self.custom_fig(fig,title,yvals,type_graph='bar')

            fig.write_image(self.outdir+"Local_Ren_Cap.pdf", width=1200, height=550)
            plt.close()
            
            fig = px.box(df_to_plot, x='Years', color='Technologies',y='F_year',
                           title='Local renewable production [TWh]',
                           color_discrete_map=self.color_dict_full,notched=True)
                
            fig.update_xaxes(categoryorder='array', categoryarray= sorted(df_to_plot['Years'].unique()))
            pio.show(fig)
            
            fig.write_html(self.outdir+"/Local_Ren_Prod.html")
        
            title = "<b>Local renewables - Production</b><br>[TWh]"
            yvals = [0,round(max(df_to_plot['F_year']))]
            
            self.custom_fig(fig,title,yvals,type_graph='bar')

            fig.write_image(self.outdir+"Local_Ren_Prod.pdf", width=1200, height=550)
            plt.close()
    
    
    
    
    def graph_layer(self, ampl_uq_collector = None, plot = True):
        pio.renderers.default = 'browser'
        
        if ampl_uq_collector == None:
            ampl_uq_collector = self.ampl_uq_collector
        
        col_plot = ['AMMONIA','ELECTRICITY','GAS','H2','WOOD','WET_BIOMASS','HEAT_HIGH_T',
                'HEAT_LOW_T_DECEN','HEAT_LOW_T_DHN','HVC','METHANOL',
                'MOB_FREIGHT_BOAT','MOB_FREIGHT_RAIL','MOB_FREIGHT_ROAD','MOB_PRIVATE',
                'MOB_PUBLIC','Sample']
        results = ampl_uq_collector['Year_balance'].copy()
        results = results[col_plot]
        results.reset_index(inplace=True)
        results = results.set_index(['Years','Elements','Sample'])
        df_to_plot_full = dict.fromkeys(col_plot)
        for k in results.columns:
            df_to_plot = pd.DataFrame(index=results.index,columns=[k])
            temp = results.loc[:,k].dropna(how='all')
            for y in results.index.get_level_values(0).unique():
                temp_y = temp.loc[temp.index.get_level_values('Years') == y,:] 
                if not temp_y.empty:
                    temp_y = self._remove_low_values(temp_y, threshold=0.01)
                    df_to_plot.update(temp_y)
            df_to_plot.dropna(how='all',inplace=True)
            
            
            df_to_plot_prod = df_to_plot.loc[df_to_plot[k]>0]
            df_to_plot_cons = df_to_plot.loc[df_to_plot[k]<0]
            
            df_to_plot_prod = self._fill_df_to_plot_w_zeros(df_to_plot_prod)
            df_to_plot_cons = self._fill_df_to_plot_w_zeros(df_to_plot_cons)
            
            df_to_plot_prod.reset_index(inplace=True)
            df_to_plot_cons.reset_index(inplace=True)
            
            df_to_plot_cons.loc[df_to_plot_cons[k]<0,k] = - df_to_plot_cons.loc[df_to_plot_cons[k]<0,k]
            
            
            df_to_plot_prod['Elements'] = df_to_plot_prod['Elements'].astype("str")
            df_to_plot_prod['Years'] = df_to_plot_prod['Years'].str.replace('YEAR_', '')
            df_to_plot_prod[k] /= 1000
            
            df_to_plot_cons['Elements'] = df_to_plot_cons['Elements'].astype("str")
            df_to_plot_cons['Years'] = df_to_plot_cons['Years'].str.replace('YEAR_', '')
            df_to_plot_cons[k] /= 1000

            
            
            if plot:
                fig_prod = px.box(df_to_plot_prod, x='Years', color='Elements',y=k,
                               title='{} - Production'.format(k),
                               color_discrete_map=self.color_dict_full,notched=True)
                    
                fig_prod.update_xaxes(categoryorder='array', categoryarray= sorted(df_to_plot_prod['Years'].unique()))
                pio.show(fig_prod)
                
                if not os.path.exists(Path(self.outdir+"Layers")):
                    Path(self.outdir+"Layers").mkdir(parents=True,exist_ok=True)
                
                if not os.path.exists(Path(self.outdir+"Layers/_Raw/")):
                    Path(self.outdir+"Layers/_Raw").mkdir(parents=True,exist_ok=True)
                    
                fig_prod.write_html(self.outdir+"Layers/_Raw/"+k+"_Prod.html")
                
                fig_cons = px.box(df_to_plot_cons, x='Years', color='Elements',y=k,
                               title='{} - Consumption'.format(k),
                               color_discrete_map=self.color_dict_full,notched=True)
                    
                fig_cons.update_xaxes(categoryorder='array', categoryarray= sorted(df_to_plot_cons['Years'].unique()))
                pio.show(fig_cons)
                fig_cons.write_html(self.outdir+"Layers/_Raw/"+k+"_Cons.html")
            
                title = "<b>{} - Supply</b><br>[TWh]".format(k)
                yvals = [0,round(max(df_to_plot_prod[k]))]
                
                self.custom_fig(fig_prod,title,yvals,type_graph='bar')

                fig_prod.write_image(self.outdir+"Layers/"+k+" - Production.pdf", width=1200, height=550)
                plt.close()
                
                title = "<b>{} - Consumption</b><br>[TWh]".format(k)
                yvals = [0,round(max(df_to_plot_cons[k]))]
                
                self.custom_fig(fig_cons,title,yvals,type_graph='bar')

                fig_cons.write_image(self.outdir+"Layers/"+k+" - Consumption.pdf", width=1200, height=550)
                plt.close()
                

            df_to_plot_full[k] = df_to_plot
            
        return df_to_plot_full
    
    
    def _fill_df_to_plot_w_zeros(self,df_to_plot):
        index_names = df_to_plot.index.names
        l_ind = [None] * len(index_names)
        for i,j in enumerate(index_names):
            ind = df_to_plot.index.get_level_values(j).unique()
            if j == 'Years' and not('YEAR_2020' in ind):
                ind = ind.union(['YEAR_2020'])
            l_ind[i] = ind
        
        mi_temp = pd.MultiIndex.from_product(l_ind,names=index_names)
        df_temp = pd.DataFrame(0,index=mi_temp,columns=df_to_plot.columns)
        df_temp.update(df_to_plot)
        df_to_plot = df_temp.copy()
        return df_to_plot
        
        
        
    def _polyfit_func(self,x_in, y_in, threshold=0.99999999):
        """
        The function fits a polynomial to the points of x_in and y_in. The
        polynomial starts with order 1. To evaluate its performance, the R-squared
        performance indicator is quantified. If the value for R-squared does
        not reach the defined threshold, the polynomial order is increased and
        the polynomial is fitted again on the points, until the threshold is
        satisfied. Once satisfied, the function returns the polynomial.
    
        Parameters
        ----------
        x_in : ndarray
            The x-coordinates for the sample points.
        y_in : ndarray
            The y-coordinates for the sample points.
        threshold : float, optional
            The threshold for the R-squared parameter. The default is 0.99999999.
    
        Returns
        -------
        poly_func : numpy.poly1d
            A one-dimensional polynomial.
    
        """
        order = 0
        r_squared = 0.
        while r_squared < threshold and order < 15:
            order += 1
    
            # the polynomial
            poly_coeff = np.polyfit(x_in, y_in, order)
            poly_func = np.poly1d(poly_coeff)
    
            # r-squared
            yhat = poly_func(x_in)
            ybar = np.sum(y_in) / len(y_in)
            ssreg = np.sum((yhat - ybar)**2.)
            sstot = np.sum((y_in - ybar)**2.)
            r_squared = ssreg / sstot
    
        return poly_func

    def _remove_low_values(self,df_temp, threshold = None):
        if threshold == None:
            threshold = self.threshold_filter
        max_temp = np.nanmax(df_temp)
        min_temp = np.nanmin(df_temp)
        df_temp = df_temp.loc[(abs(df_temp) > 1e-8) & ((df_temp >= threshold*max_temp) |
                              (df_temp <= threshold*min_temp))]
        return df_temp
    
    def _group_tech_per_eud(self):
        tech_of_end_uses_category = self.ampl_obj.sets['TECHNOLOGIES_OF_END_USES_CATEGORY'].copy()
        del tech_of_end_uses_category["NON_ENERGY"]
        for ned in self.ampl_obj.sets['END_USES_TYPES_OF_CATEGORY']['NON_ENERGY']:
            tech_of_end_uses_category[ned] = self.ampl_obj.sets['TECHNOLOGIES_OF_END_USES_TYPE'][ned]
        df = tech_of_end_uses_category.copy()
        df['INFRASTRUCTURE'] = self.ampl_obj.sets['INFRASTRUCTURE']
        df['STORAGE'] = self.ampl_obj.sets['STORAGE_TECH']
        
        return df
    
    def _group_sets(self):
        categories = self._group_tech_per_eud()
        categories['STORAGE'] = self.ampl_obj.sets['STORAGE_TECH'].copy()
        categories['RE_FUELS'] = self.ampl_obj.sets['RE_RESOURCES'].copy()
        categories['INFRASTRUCTURE'] = self.ampl_obj.sets['INFRASTRUCTURE'].copy()
        re_fuels = self.ampl_obj.sets['RE_RESOURCES'].copy()
        resources = self.ampl_obj.sets['RESOURCES'].copy()
        nre_fuels = [res for res in resources if res not in re_fuels]
        categories['NRE_FUELS'] = nre_fuels
        
        categories_2 = dict()
        
        for k in categories:
            for j in categories[k]:
                if k == 'HEAT_LOW_T':
                    if j in self.ampl_obj.sets['TECHNOLOGIES_OF_END_USES_TYPE']["HEAT_LOW_T_DHN"]:
                        categories_2[j] = 'HEAT_LOW_T_DHN'
                    else:
                        categories_2[j] = 'HEAT_LOW_T_DECEN'
                elif k == 'MOBILITY_PASSENGER':
                    if j in self.ampl_obj.sets['TECHNOLOGIES_OF_END_USES_TYPE']["MOB_PUBLIC"]:
                        categories_2[j] = 'MOB_PUBLIC'
                    else:
                        categories_2[j] = 'MOB_PRIVATE'
                else :
                    categories_2[j] = k
        
        return categories_2
    
    
    def _dict_color_full(self):
        year_balance = self.ampl_uq_collector['Year_balance']
        elements = year_balance.index.get_level_values(1).unique()
        color_dict_full = dict.fromkeys(elements)
        categories = ['Sectors','Electricity','Heat_low_T','Heat_high_T','Mobility','Freight','Ammonia',
                   'Methanol','HVC','Conversion','Storage','Storage','Storage_daily','Resources',
                   'Infrastructure','Years_1','Years_2','Phases']
        for c in categories:
            color_dict_full.update(self.dict_color(c))
        
        color_dict_full['END_USES'] = 'lightsteelblue'
        
        return color_dict_full
    
    @staticmethod
    def dict_color(category):
        color_dict = {}
        
        if category == 'Electricity':
            color_dict = {"NUCLEAR":"deeppink", "NUCLEAR_SMR": "deeppink", "CCGT":"darkorange", "CCGT_AMMONIA":"slateblue", "COAL_US" : "black", "COAL_IGCC" : "dimgray", "PV" : "yellow", "WIND_ONSHORE" : "lawngreen", "WIND_OFFSHORE" : "green", "HYDRO_RIVER" : "blue", "GEOTHERMAL" : "firebrick", "ELECTRICITY" : "dodgerblue"}
        elif category == 'Heat_low_T':
            color_dict = {"DHN_HP_ELEC" : "blue", "DHN_COGEN_GAS" : "orange", "DHN_COGEN_WOOD" : "sandybrown", "DHN_COGEN_WASTE" : "olive", "DHN_COGEN_WET_BIOMASS" : "seagreen", "DHN_COGEN_BIO_HYDROLYSIS" : "springgreen", "DHN_BOILER_GAS" : "darkorange", "DHN_BOILER_WOOD" : "sienna", "DHN_BOILER_OIL" : "blueviolet", "DHN_DEEP_GEO" : "firebrick", "DHN_SOLAR" : "gold", "DEC_HP_ELEC" : "cornflowerblue", "DEC_THHP_GAS" : "lightsalmon", "DEC_COGEN_GAS" : "goldenrod", "DEC_COGEN_OIL" : "mediumpurple", "DEC_ADVCOGEN_GAS" : "burlywood", "DEC_ADVCOGEN_H2" : "violet", "DEC_BOILER_GAS" : "moccasin", "DEC_BOILER_WOOD" : "peru", "DEC_BOILER_OIL" : "darkorchid", "DEC_SOLAR" : "yellow", "DEC_DIRECT_ELEC" : "deepskyblue"}
        elif category == 'Heat_high_T':
            color_dict = {"IND_COGEN_GAS":"orange", "IND_COGEN_WOOD":"peru", "IND_COGEN_WASTE" : "olive", "IND_BOILER_GAS" : "moccasin", "IND_BOILER_WOOD" : "goldenrod", "IND_BOILER_OIL" : "blueviolet", "IND_BOILER_COAL" : "black", "IND_BOILER_WASTE" : "olivedrab", "IND_DIRECT_ELEC" : "royalblue"}
        elif category == 'Mobility':
            color_dict = {"TRAMWAY_TROLLEY" : "dodgerblue", "BUS_COACH_DIESEL" : "dimgrey", "BUS_COACH_HYDIESEL" : "gray", "BUS_COACH_CNG_STOICH" : "orange", "BUS_COACH_FC_HYBRIDH2" : "violet", "TRAIN_PUB" : "blue", "CAR_GASOLINE" : "black", "CAR_DIESEL" : "lightgray", "CAR_NG" : "moccasin", "CAR_METHANOL":"orchid", "CAR_HEV" : "salmon", "CAR_PHEV" : "lightsalmon", "CAR_BEV" : "deepskyblue", "CAR_FUEL_CELL" : "magenta"}
        elif category == 'Freight':
            color_dict = {"TRAIN_FREIGHT" : "royalblue", "BOAT_FREIGHT_DIESEL" : "dimgrey", "BOAT_FREIGHT_NG" : "darkorange", "BOAT_FREIGHT_METHANOL" : "fuchsia", "TRUCK_DIESEL" : "darkgrey", "TRUCK_FUEL_CELL" : "violet", "TRUCK_ELEC" : "dodgerblue", "TRUCK_NG" : "moccasin", "TRUCK_METHANOL" : "orchid"}
        elif category == 'Ammonia':
            color_dict = {"HABER_BOSCH":"tomato", "AMMONIA" : "slateblue", "AMMONIA_RE" : "blue"}
        elif category == 'Methanol':
            color_dict = {"SYN_METHANOLATION":"violet","METHANE_TO_METHANOL":"orange","BIOMASS_TO_METHANOL":"peru", "METHANOL" : "orchid", "METHANOL_RE" : "mediumvioletred"}
        elif category == "HVC":
            color_dict = {"OIL_TO_HVC":"blueviolet", "GAS_TO_HVC":"orange", "BIOMASS_TO_HVC":"peru", "METHANOL_TO_HVC":"orchid"}
        elif category == 'Conversion':
            color_dict = {"H2_ELECTROLYSIS" : "violet", "H2_NG" : "magenta", "H2_BIOMASS" : "orchid", "GASIFICATION_SNG" : "orange", "PYROLYSIS" : "blueviolet", "ATM_CCS" : "black", "INDUSTRY_CCS" : "grey", "SYN_METHANOLATION" : "mediumpurple", "SYN_METHANATION" : "moccasin", "BIOMETHANATION" : "darkorange", "BIO_HYDROLYSIS" : "gold", "METHANE_TO_METHANOL" : "darkmagenta",'SMR':'orange', 'AMMONIA_TO_H2':'fuchsia'}
        elif category == 'Storage':
            color_dict = {"TS_DHN_SEASONAL" : "indianred", "BATT_LI" : "royalblue", "BEV_BATT" : "deepskyblue", "PHEV_BATT" : "lightskyblue", "PHS" : "dodgerblue", "TS_DEC_HP_ELEC" : "blue", "TS_DHN_DAILY" : "lightcoral", "TS_HIGH_TEMP" : "red", "SEASONAL_NG" : "orange", "SEASONAL_H2" : "violet", "SLF_STO" : "blueviolet", "TS_DEC_DIRECT_ELEC":"darkgoldenrod", "TS_DEC_THHP_GAS": "orange", "TS_DEC_COGEN_GAS":"coral", "TS_DEC_COGEN_OIL":"darkviolet", "TS_DEC_ADVCOGEN_GAS":"sandybrown", "TS_DEC_ADVCOGEN_H2": "plum", "TS_DEC_BOILER_GAS": "tan", "TS_DEC_BOILER_WOOD":"peru", "TS_DEC_BOILER_OIL": "darkviolet", "GAS_STORAGE": "orange", "H2_STORAGE": "violet", "CO2_STORAGE": "lightgray", "GASOLINE_STORAGE": "gray", "DIESEL_STORAGE": "silver", "AMMONIA_STORAGE": "slateblue", "LFO_STORAGE": "darkviolet"}
        elif category == 'Storage_daily':
            color_dict = {"BATT_LI" : "royalblue", "BEV_BATT" : "deepskyblue", "PHEV_BATT" : "lightskyblue", "TS_DEC_HP_ELEC" : "blue", "TS_DHN_DAILY" : "lightcoral", "TS_HIGH_TEMP" : "red", "TS_DEC_DIRECT_ELEC":"darkgoldenrod", "TS_DEC_THHP_GAS": "orange", "TS_DEC_COGEN_GAS":"coral", "TS_DEC_COGEN_OIL":"darkviolet", "TS_DEC_ADVCOGEN_GAS":"sandybrown", "TS_DEC_ADVCOGEN_H2": "plum", "TS_DEC_BOILER_GAS": "tan", "TS_DEC_BOILER_WOOD":"peru", "TS_DEC_BOILER_OIL": "darkviolet"}
        elif category == 'Resources':
            color_dict = {"ELECTRICITY" : "deepskyblue", "GASOLINE" : "gray", "DIESEL" : "silver", "BIOETHANOL" : "mediumorchid", "BIODIESEL" : "mediumpurple", "LFO" : "darkviolet", "GAS" : "orange", "GAS_RE" : "gold", "WOOD" : "saddlebrown", "WET_BIOMASS" : "seagreen", "COAL" : "black", "URANIUM" : "deeppink", "WASTE" : "olive", "H2" : "violet", "H2_RE" : "plum", "AMMONIA" : "slateblue", "AMMONIA_RE" : "blue", "METHANOL" : "orchid", "METHANOL_RE" : "mediumvioletred", "CO2_EMISSIONS" : "gainsboro", "RES_WIND" : "limegreen", "RES_SOLAR" : "yellow", "RES_HYDRO" : "blue", "RES_GEO" : "firebrick", "ELEC_EXPORT" : "chartreuse","CO2_ATM": "dimgray", "CO2_INDUSTRY": "darkgrey", "CO2_CAPTURED": "lightslategrey", "RE_FUELS": 'green','NRE_FUELS':'black', 'LOCAL_RE': 'limegreen', 'IMPORTED_ELECTRICITY': 'deepskyblue'}
        elif category == 'Sectors':
            color_dict = {"ELECTRICITY" : "deepskyblue", "HEAT_HIGH_T":"red","HEAT_LOW_T_DECEN":"lightpink", "HEAT_LOW_T_DHN":"indianred", "MOB_PUBLIC":"gold", "MOB_PRIVATE":"goldenrod","MOBILITY_FREIGHT":"darkgoldenrod", "NON_ENERGY": "darkviolet", "INFRASTRUCTURE":"grey","HVC":"cyan",'STORAGE':'chartreuse', 'OTHERS':'gainsboro'}
        elif category == 'Infrastructure':
            color_dict = {'EFFICIENCY': 'lime','DHN': 'orange','GRID': 'gold'}
        elif category == 'Years_1':
            color_dict = {'YEAR_2020': 'blue','YEAR_2025': 'orange','YEAR_2030': 'green', 'YEAR_2035': 'red', 'YEAR_2040': 'purple', 'YEAR_2045': 'brown', 'YEAR_2050':'pink'}
        elif category == 'Years_2':
            color_dict = {'2020': 'blue','2025': 'orange','2030': 'green', '2035': 'red', '2040': 'purple', '2045': 'brown', '2050':'pink'}
        elif category == 'Phases':
                color_dict = {'2015_2020': 'blue','2020_2025': 'orange','2025_2030': 'green', '2030_2035': 'red', '2035_2040': 'purple', '2040_2045': 'brown', '2045_2050':'pink'}
            
        return color_dict
    
    
    def dict_meaning(self):
        meaning_dict = {'H2_RE':'E-hydrogen',
                        'AMMONIA_RE': 'E-ammonia',
                        'METHANOL_RE': 'E-methanol',
                        'GAS_RE': 'E-methane',
                        'H2':'Fossil hydrogen',
                        'AMMONIA': 'Fossil ammonia',
                        'METHANOL': 'Fossil methanol',
                        'GAS': 'Fossil methane',
                        'H2_ELECTROLYSIS': 'Electrolyser',
                        'CCGT_AMMONIA': 'Ammonia CCGT',
                        'SYN_METHANOLATION': 'Methanolation',
                        'METHANE_TO_METHANOL': 'Methane-to-methanol',
                        'NUCLEAR_SMR': 'Nuclear SMR',
                        'BIOMETHANATION': 'Biomethanation',
                        'BIO_HYDROLYSIS': 'Biohydrolysis',
                        'Total gwp' : 'Total gwp',
                        'PV' : 'PV',
                        'WIND_ONSHORE': 'Onshore wind',
                        'WIND_OFFSHORE': 'Offshore wind',
                        'SMR': 'Steam-methane-reforming',
                        'AMMONIA_TO_H2':'Ammonia-to-H2',
                        'CAR_FUEL_CELL':'Fuel cell car'
                        }
        
        return meaning_dict
        
    
    @staticmethod
    def custom_fig(fig,title,yvals,xvals=['2020','2025','2030','2035','2040',
                        '2045','2050'], ftsize=18,annot_text=None,
                   type_graph = None, neg_value = False, flip = False):
    
        def round_repdigit(n, ndigits=0):     
            if n != 0:
                i = int(np.ceil(np.log10(abs(n))))
                x = np.round(n, ndigits-i)
                if i-ndigits >= 0:
                    x = int(x)
                return x     
            else:
                return 0
            
        gray = 'rgb(90,90,90)' 
        color = gray
        
        fig.update_layout(
            xaxis_color=color, yaxis_color=color,
            xaxis_mirror=False, yaxis_mirror=False,
            yaxis_showgrid=False, xaxis_showgrid=False,
            yaxis_linecolor='white', xaxis_linecolor='white',
            xaxis_tickfont_size=ftsize, yaxis_tickfont_size=ftsize,
            showlegend=False,
        )
        
        if title != None:
            fig.update_layout(
                title_text=title,titlefont=dict(family="Raleway",size=ftsize+10)
                )
        
        if type_graph == None:
            fig.update_xaxes(dict(ticks = "inside", ticklen=10))
            fig.update_xaxes(tickangle= 0,tickmode = 'array',tickwidth=2,tickcolor=gray,
                                tickfont=dict(
                                      family="Rawline",
                                      size=ftsize
                                  ))
        fig.update_yaxes(dict(ticks = "inside", ticklen=10))
        if type_graph in ['strip','bar']:
            fig.update_xaxes(dict(ticks = "inside", ticklen=10))
            
        
        if not(flip):
            fig.update_yaxes(tickangle= 0,tickmode = 'array',tickwidth=2,tickcolor=gray,
                                tickfont=dict(
                                      family="Rawline",
                                      size=ftsize
                                  ))
        
        fig.update_layout(
            yaxis = dict(
                tickmode = 'array',
                tickvals = fig.layout.yaxis.tickvals,
                ticktext = list(map(str,yvals))
                ))
        
                
        factor=0.05
        nrepdigit = 0
        
        fig.update_yaxes(tickvals=yvals)
        
        xstring = isinstance(fig.data[0].x[0],str)
        
        if xstring: ## ONLY VALID IF THE FIRST TRACE HAS ALL VALUES
            xvals = xvals
            xmin = 0
            xmax = len(xvals) - 1
        else:
            if not(flip):
                xvals = pd.Series(sum([list(i.x) for i in fig.data],[]))
                xmin = xvals.min()
                xmax = xvals.max()
            else:
                xmin = min(xvals)
                xmax = max(xvals)
            xampl = xmax-xmin
        
        
        if xstring:
            if fig.layout.xaxis.range is None:
                if type_graph in ['bar','strip']:
                    fig.layout.xaxis.range = [xmin-factor*15, xmax+factor*15]
                elif type_graph == 'scatter':
                    fig.layout.xaxis.range = [xmin-factor*6, xmax+factor*6]
                else:
                    fig.layout.xaxis.range = [xmin-factor*3, xmax+factor*3]
            if fig.layout.xaxis.tickvals is None:
                fig.layout.xaxis.tickvals = xvals
        else:
            if fig.layout.xaxis.range is None:
                fig.layout.xaxis.range = [xmin-xampl*factor, xmax+xampl*factor]
            if fig.layout.xaxis.tickvals is None:
                fig.layout.xaxis.tickvals = [round_repdigit(x, nrepdigit) for x in [xmin, xmax]]
        
        if flip:
            fig.update_xaxes(tickvals=xvals)
            
        
        fig.layout.xaxis.tickvals = sorted(fig.layout.xaxis.tickvals)
        fig.layout.xaxis.range = sorted(fig.layout.xaxis.range)
        
        
        yvals = yvals
        
        ystring = isinstance(fig.data[0].y[0],str)
        
        if ystring: ## ONLY VALID IF THE FIRST TRACE HAS ALL VALUES
            ymin = 0
            ymax = len(yvals) - 1
        else:
            ymin = min(yvals)
            ymax = max(yvals)
        yampl = ymax-ymin
        
        if fig.layout.yaxis.range is None:
            fig.layout.yaxis.range = [ymin-yampl*factor, ymax+yampl*factor]
        if fig.layout.yaxis.tickvals is None:
            fig.layout.yaxis.tickvals = [round_repdigit(y, nrepdigit) for y in [ymin, ymax]]
        
        if not(ystring):
            fig.layout.yaxis.tickvals = sorted(fig.layout.yaxis.tickvals)
        fig.layout.yaxis.range = sorted(fig.layout.yaxis.range)
        
        fig.update_layout(xaxis_title=None, yaxis_title=None)
        
        if neg_value:
            if not(flip):
                fig.add_shape(x0=xmin,x1=xmax,
                          y0=0,y1=0,
                          type='line',layer="below",
                          line=dict(color=color,width=1),opacity=0.5)
            else:
                fig.add_shape(x0=0,x1=0,
                          y0=ymin,y1=ymax,
                          type='line',layer="below",
                          line=dict(color=color,width=1),opacity=0.5)
                
        
        fig.add_shape(x0=fig.layout.xaxis.range[0],x1=fig.layout.xaxis.range[0],
                  y0=fig.layout.yaxis.tickvals[0],y1=fig.layout.yaxis.tickvals[-1],
                  type='line',layer="above",
                  line=dict(color=color,width=2),opacity=1)
        
        # if type_graph in [None,'bar']:
        fig.add_shape(x0=xmin,x1=xmax,
                  y0=fig.layout.yaxis.range[0],y1=fig.layout.yaxis.range[0],
                  type='line',layer="above",
                  line=dict(color=color, width=2),opacity=1)
        
        if type_graph in ['scatter']:
            fig.update_layout({ax:{"visible":False, "matches":None} for ax in fig.to_dict()["layout"] if "xaxis" in ax})
        
        if type_graph in ['strip']:
            if not(flip):
                fig.add_shape(x0=0.5,x1=0.5,
                          y0=ymin,y1=ymax,
                          type='line',layer="above",
                          line=dict(color=color,width=2,dash="dot"),opacity=1)
                fig.add_shape(x0=xmax-0.5,x1=xmax-0.5,
                          y0=ymin,y1=ymax,
                          type='line',layer="above",
                          line=dict(color=color,width=2,dash="dot"),opacity=1)
            # else:
                # fig.add_shape(x0=xmin,x1=xmax,
                #           y0=0.5,y1=0.5,
                #           type='line',layer="above",
                #           line=dict(color=color,width=2,dash="dot"),opacity=1)
                # fig.add_shape(x0=xmin,x1=xmax,
                #           y0=ymax-0.5,y1=ymax-0.5,
                #           type='line',layer="above",
                #           line=dict(color=color,width=2,dash="dot"),opacity=1)
        
        fig.update_layout(margin_b = 10, margin_r = 30, margin_l = 30)#,margin_pad = 20)
