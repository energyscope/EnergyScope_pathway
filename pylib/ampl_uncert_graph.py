import rheia.POST_PROCESS.post_process as rheia_pp
import rheia.UQ.uncertainty_quantification as rheia_uq
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd
import plotly.io as pio
import plotly.figure_factory as ff
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

class AmplUncertGraph:

    """

    The AmplUQGraph class allows to plot the relevant outputs (e.g. installed capacitites, used resources, costs)
    of the different samples of UQ on an optimisation problem.

    Parameters
    ----------
    result_list: list(Pandas.DataFrame)
        Unpickled list where relevant outputs has been stored

    """

    def __init__(self, case_study,base_case,ampl_obj,output_folder_cs):
        project_path = Path(__file__).parents[1]
        
        self.case_study = case_study
        self.output_folder_cs = output_folder_cs
        
        self.base_case = base_case
        self.output_folder_bc = os.path.join(project_path,'out',self.base_case)
        
        bc_pkl_file = os.path.join(self.output_folder_bc,'_Results.pkl')
        bc_open_file = open(bc_pkl_file,"rb")
        self.bc_results = pkl.load(bc_open_file)
        bc_open_file.close()
        
        self.threshold = 1
        self.threshold_filter = 0.01

        self.x_axis = [2020, 2025, 2030, 2035, 2040, 2045, 2050]
        # In 2020, 37.41% of electricity in EU-27 was produced from renewables (https://ec.europa.eu/eurostat/databrowser/view/NRG_IND_REN__custom_4442440/default/table?lang=en)
        self.re_share_elec = np.linspace(0.3741,1,len(self.x_axis))
        
        self.gather_results()
        self.ampl_uncert_collector = self.unpkl(self)
        # self.samples_file = os.path.join(self.output_folder_cs,'samples.csv')
        # samples = pd.read_csv(self.samples_file)
        # samples.index.name = 'Sample'
        # self.ampl_uncert_collector['Samples'] = samples
        self.ampl_obj = ampl_obj

        # uq_file = os.path.join(project_path,'uncertainties','uc_final.xlsx')
        # uncert_param = pd.read_excel(uq_file,sheet_name='Parameters',engine='openpyxl',index_col=0)
        # uncert_param_meaning = uncert_param['Meaning_short']
        # self.uncert_param_meaning = dict(uncert_param_meaning)
        
        # uncert_range = pd.read_excel(uq_file,sheet_name='YEAR_2025',engine='openpyxl',index_col=0)
        # self.uncert_nominal = self.get_nominal(uncert_range)
        
        # self.ref_case = ref_case
        # self.ref_file = os.path.join(project_path,'out',ref_case,'_Results.pkl')
        # ref_results = open(self.ref_file,"rb")
        # self.ref_results = pkl.load(ref_results)
        # ref_results.close()
        
        # self.smr_case = smr_case
        # self.smr_file = os.path.join(project_path,'out',smr_case,'_Results.pkl')
        # smr_results = open(self.smr_file,"rb")
        # self.smr_results = pkl.load(smr_results)
        # smr_results.close()
        
        self.color_dict_full = self._dict_color_full()
        
        self.outdir = os.path.join(self.output_folder_cs,'graphs/')
        if not os.path.exists(Path(self.outdir)):
            Path(self.outdir).mkdir(parents=True,exist_ok=True)

        self.category = self._group_sets()
        
    
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
        uq_collector = self.ampl_uncert_collector.copy()
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
    def unpkl(self,case_study = None, output_folder_cs = None):
        if case_study == None:
            output_folder_cs = self.output_folder_cs
        else:
            output_folder_cs = output_folder_cs
        pkl_file = os.path.join(output_folder_cs,'_uncert_collector.p')
        
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
        

    def gather_results(self,output_folder_cs = None):
        if output_folder_cs == None:
            uncert_path = self.output_folder_cs
        else:
            uncert_path = output_folder_cs
        uncert_path_runs = uncert_path + "/Runs/"
        
        if not(Path(os.path.join(uncert_path,'_uncert_collector.p')).is_file()):
            uncert_collector = {}
            dir = sorted(os.listdir(uncert_path_runs))
            for i, file in enumerate(dir):
                if "Run" in file:
                    sample = int(file[3:])
                    open_file = open(uncert_path_runs+file,"rb")
                    loaded_results = pkl.load(open_file)
                    if not(uncert_collector):
                        for key in loaded_results:
                            loaded_results[key]['Sample'] = sample
                        uncert_collector = loaded_results
                    else:
                        for key in uncert_collector:
                            loaded_results[key]['Sample'] = sample
                            uncert_collector[key] = uncert_collector[key].append(loaded_results[key])
    
            open_file = open(uncert_path+'/_uncert_collector.p',"wb")
            pkl.dump(uncert_collector, open_file)
            open_file.close()
    
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
        
    def graph_tech_cap(self, ampl_uncert_collector = None, plot = True):
        
        if ampl_uncert_collector == None:
            ampl_uncert_collector = self.ampl_uncert_collector
        
        results = ampl_uncert_collector['Assets'].copy()
        results.reset_index(inplace=True)
        results = results.set_index(['Years','Technologies','Sample'])
        
        results_bc = self.bc_results['Assets'].copy()
        
        
        dict_tech = self._group_tech_per_eud()
        df_to_plot_full = pd.DataFrame()
        for sector, tech in dict_tech.items():

            temp = results.loc[results.index.get_level_values('Technologies').isin(tech),'F']
            temp_bc = results_bc.loc[results_bc.index.get_level_values('Technologies').isin(tech),'F']
            df_to_plot = pd.DataFrame(index=temp.index,columns=['F'])
            df_to_plot_bc = pd.DataFrame(index=temp_bc.index,columns=['F'])
            for y in temp.index.get_level_values(0).unique():
                temp_y = temp.loc[temp.index.get_level_values('Years') == y]
                temp_y_bc = temp_bc.loc[temp_bc.index.get_level_values('Years') == y]
                # temp_y.dropna(how='all',inplace=True)
                # temp_y_bc.dropna(how='all',inplace=True)
                if not temp_y.empty:
                    temp_y = self._remove_low_values(temp_y,threshold=0.0)
                    df_to_plot.update(temp_y)
                if not temp_y_bc.empty:
                    temp_y_bc = self._remove_low_values(temp_y_bc,threshold=0.0)
                    df_to_plot_bc.update(temp_y_bc)
            df_to_plot.dropna(how='all',inplace=True)
            df_to_plot_bc.dropna(how='all',inplace=True)
            
            df_to_plot = self._fill_df_to_plot_w_zeros(df_to_plot)
            df_to_plot_bc = self._fill_df_to_plot_w_zeros(df_to_plot_bc)
            
            df_to_plot['Delta'] = df_to_plot['F'].sub(df_to_plot_bc['F'],fill_value=0.0)
            
            df_to_plot.reset_index(inplace=True)
            df_to_plot['Technologies'] = df_to_plot['Technologies'].astype("str")
            df_to_plot['Years'] = df_to_plot['Years'].str.replace('YEAR_', '')
            
            df_to_plot_bc.reset_index(inplace=True)
            df_to_plot_bc['Technologies'] = df_to_plot_bc['Technologies'].astype("str")
            df_to_plot_bc['Years'] = df_to_plot_bc['Years'].str.replace('YEAR_', '')
            
            
            
            if plot:
                fig = px.box(df_to_plot, x='Years', y = 'Delta',color='Technologies',
                         title= sector+' - Installed capacity',
                         color_discrete_map=self.color_dict_full)

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
                    yvals = sorted([0,round(min(temp['Delta']),1),round(max(temp['Delta']),1)])
                    
                    self.custom_fig(fig,title,yvals,xvals=sorted(df_to_plot['Years'].unique()),type_graph='bar',neg_value=True)
                        
                    
                    fig.write_image(self.outdir+"Tech_Cap/"+sector+".pdf", width=1200, height=550)
                plt.close()
            
            if len(df_to_plot_full) == 0:
                df_to_plot_full = df_to_plot
            else:
                df_to_plot_full = df_to_plot_full.append(df_to_plot)
            
        return df_to_plot_full
    
    def graph_electrofuels(self, ampl_uncert_collector = None, plot = True):
        pio.renderers.default = 'browser'
        
        if ampl_uncert_collector == None:
            ampl_uncert_collector = self.ampl_uncert_collector
        
        col_plot = ['METHANOL_RE','AMMONIA_RE','GAS_RE','H2_RE']
        results = ampl_uncert_collector['Resources'].copy()
        results.reset_index(inplace=True)
        results = results.loc[results['Resources'].isin(col_plot),:]
        results['Resources'] = results['Resources'].astype("str")
        results.dropna(how='all',inplace=True)
        results['Res']/=1000
        
        results_bc = self.bc_results['Resources'].copy()
        results_bc.reset_index(inplace=True)
        results_bc = results_bc.loc[results_bc['Resources'].isin(col_plot),:]
        results_bc['Resources'] = results_bc['Resources'].astype("str")
        results_bc.dropna(how='all',inplace=True)
        results_bc['Res']/=1000
        

        df_to_plot = results.set_index(['Years','Resources','Sample'])
        df_to_plot.dropna(how='all',inplace=True)
        df_to_plot = self._fill_df_to_plot_w_zeros(df_to_plot)
        
        
        df_to_plot_bc = results_bc.set_index(['Years','Resources'])
        df_to_plot_bc.dropna(how='all',inplace=True)
        
        df_to_plot['Delta'] = df_to_plot['Res']-df_to_plot_bc['Res']
        
        df_to_plot.reset_index(inplace=True)
        
        df_to_plot['Years'] = df_to_plot['Years'].str.replace('YEAR_', '')
        
            
        if plot:
            fig = px.box(df_to_plot, x='Years', color='Resources',y='Delta',
                           title='Electrofuels [TWh]',
                           color_discrete_map=self.color_dict_full,notched=False)
                
            fig.update_xaxes(categoryorder='array', categoryarray= sorted(df_to_plot['Years'].unique()))
            pio.show(fig)
            
            fig.write_html(self.outdir+"/Electrofuels.html")
        
            title = "<b>Imported renewable electrofuels</b><br>[TWh]"
            df_to_plot.dropna(how='any',inplace=True)
            yvals = [round(min(df_to_plot['Delta'])),0,round(max(df_to_plot['Delta']))]
            
            self.custom_fig(fig,title,yvals,type_graph='bar',neg_value=True)

            fig.write_image(self.outdir+"Electrofuels.pdf", width=1200, height=550)
            plt.close()
            
    def graph_transition_cost(self,case_studies,output_folder_cs,output_folder_bc, ampl_uncert_collector = None, plot = True):
        pio.renderers.default = 'browser'
        
        if ampl_uncert_collector == None:
            ampl_uncert_collector = self.ampl_uncert_collector
        
        hist_data = []
        group_labels = []
        bc_res = []
        
        df_to_plot_full = pd.DataFrame()
        
        for i, cs in enumerate(case_studies):
            output_folder = output_folder_cs[i]            
            self.gather_results(output_folder)
            ampl_uncert_collector = self.unpkl(self,cs,output_folder)
            
            results = ampl_uncert_collector['Transition_cost'].copy()
            results.reset_index(inplace=True)
            results = results.loc[results['index'].isin(['YEAR_2050']),:]
            results.dropna(how='all',inplace=True)
            results['Transition_cost']/=1000
            
            output_folder_bc_i = output_folder_bc[i]
            bc_pkl_file = os.path.join(output_folder_bc_i,'_Results.pkl')
            bc_open_file = open(bc_pkl_file,"rb")
            bc_results = pkl.load(bc_open_file)
            bc_open_file.close()
            
            results_bc = bc_results['Transition_cost'].copy()
            results_bc.reset_index(inplace=True)
            results_bc = results_bc.loc[results_bc['index'].isin(['YEAR_2050']),:]
            results_bc.dropna(how='all',inplace=True)
            results_bc['Transition_cost']/=1000
            bc_res += [results_bc.Transition_cost[0]]

            df_to_plot = results.set_index(['index','Sample'])
            df_to_plot.dropna(how='all',inplace=True)
            df_to_plot.reset_index(inplace=True)
            df_to_plot['index'] = df_to_plot['index'].str.replace('YEAR_', '')
            df_to_plot['Case'] = cs
            
            if i==0:
                df_to_plot_full = df_to_plot
            else:
                df_to_plot_full = df_to_plot_full.append(df_to_plot)
                
            
            hist_data += [np.array(df_to_plot.Transition_cost)]
            group_labels += [cs]
            
                
            if plot:
                fig_temp = px.ecdf(df_to_plot, x="Transition_cost")
                
                x = fig_temp.data[0].x
                y = fig_temp.data[0].y
                
                poly_func  = self.polyfit_func(x,y)
                
                x_smooth = np.linspace(min(x),max(x),num=int(1e5))
                y_smooth = poly_func(x_smooth)
                
                if i==0:
                    # fig = px.scatter(x = x_smooth,y = y_smooth)
                    fig = px.line(x = x,y = y)
                else:
                    # fig.add_trace(go.Scatter(x = x_smooth,y = y_smooth))
                    fig.add_trace(go.Scatter(x = x,y = y))
        
        
        
        fig.add_shape(x0=min(fig.data[0].x),x1=max(fig.data[0].x),
                  y0=0.5,y1=0.5,
                  type='line',layer="below",
                  line=dict(color='rgb(90,90,90)',width=1),opacity=0.5)     
        pio.show(fig)
        
        fig_test = ff.create_distplot(hist_data,group_labels,show_hist = False,show_rug=False)
        fig_test.update_layout(title_text='Total transition cost [b€]',titlefont=dict(family="Raleway",size=28))
        y1 = 0
        for k,bc_r in enumerate(bc_res):
            y1 = max(y1,max(fig_test.data[k].y))
        for bc_r in bc_res:
            fig_test.add_shape(x0=bc_r,x1=bc_r,
                      y0=min(fig_test.data[0].y),y1=y1,
                      type='line',layer="below",
                      line=dict(color='rgb(90,90,90)',width=1),opacity=0.5)
            
        pio.show(fig_test)
        save_dir = str(Path(self.outdir).parent.parent.parent)+'/_Graphs_comp'
        fig_test.write_html(save_dir+"/Total_transition_cost.html")
        
        fig_hist = px.histogram(df_to_plot_full, x = 'Transition_cost',facet_row='Case')
        # pio.show(fig_hist)
    
    def graph_tot_opex_cost(self,case_studies,output_folder_cs,output_folder_bc, ampl_uncert_collector = None, plot = True):
        pio.renderers.default = 'browser'
        
        if ampl_uncert_collector == None:
            ampl_uncert_collector = self.ampl_uncert_collector
        
        hist_data = []
        group_labels = []
        bc_res = []
        
        df_to_plot_full = pd.DataFrame()
        
        for i, cs in enumerate(case_studies):
            output_folder = output_folder_cs[i]
            self.gather_results(output_folder)
            ampl_uncert_collector = self.unpkl(self,cs,output_folder)
            
            results = ampl_uncert_collector['C_tot_opex'].copy()
            results.reset_index(inplace=True)
            results = results.loc[results['index'].isin(['YEAR_2050']),:]
            results.dropna(how='all',inplace=True)
            results['C_tot_opex']/=1000

            df_to_plot = results.set_index(['index','Sample'])
            df_to_plot.dropna(how='all',inplace=True)
            df_to_plot.reset_index(inplace=True)
            df_to_plot['index'] = df_to_plot['index'].str.replace('YEAR_', '')
            df_to_plot['Case'] = cs
            
            output_folder_bc_i = output_folder_bc[i]
            bc_pkl_file = os.path.join(output_folder_bc_i,'_Results.pkl')
            bc_open_file = open(bc_pkl_file,"rb")
            bc_results = pkl.load(bc_open_file)
            bc_open_file.close()
            
            results_bc = bc_results['C_tot_opex'].copy()
            results_bc.reset_index(inplace=True)
            results_bc = results_bc.loc[results_bc['index'].isin(['YEAR_2050']),:]
            results_bc.dropna(how='all',inplace=True)
            results_bc['C_tot_opex']/=1000
            bc_res += [results_bc.C_tot_opex[0]]
            
            if i==0:
                df_to_plot_full = df_to_plot
            else:
                df_to_plot_full = df_to_plot_full.append(df_to_plot)
                
            
            hist_data += [np.array(df_to_plot.C_tot_opex)]
            group_labels += [cs]
            
                
            if plot:
                fig_temp = px.ecdf(df_to_plot, x="C_tot_opex")
                
                x = fig_temp.data[0].x
                y = fig_temp.data[0].y
                
                poly_func  = self.polyfit_func(x,y)
                
                x_smooth = np.linspace(min(x),max(x),num=int(1e5))
                y_smooth = poly_func(x_smooth)
                
                if i==0:
                    fig = px.scatter(x = x_smooth,y = y_smooth)
                else:
                    fig.add_trace(go.Scatter(x = x_smooth,y = y_smooth))
        
                
        # pio.show(fig)
        
        fig_test = ff.create_distplot(hist_data,group_labels,show_hist = False,show_rug=False)
        fig_test.update_layout(title_text='Total operational cost [b€]',titlefont=dict(family="Raleway",size=28))
        
        y1 = 0
        for k,bc_r in enumerate(bc_res):
            y1 = max(y1,max(fig_test.data[k].y))
        for bc_r in bc_res:
            fig_test.add_shape(x0=bc_r,x1=bc_r,
                      y0=min(fig_test.data[0].y),y1=y1,
                      type='line',layer="below",
                      line=dict(color='rgb(90,90,90)',width=1),opacity=0.5)
        pio.show(fig_test)
        save_dir = str(Path(self.outdir).parent.parent.parent)+'/_Graphs_comp'
        fig_test.write_html(save_dir+"/Total_operational_cost.html")
        
        # fig_hist = px.histogram(df_to_plot_full, x = 'C_tot_opex',facet_row='Case')
        # pio.show(fig_hist)
    
    def graph_tot_capex_cost(self,case_studies,output_folder_cs,output_folder_bc, ampl_uncert_collector = None, plot = True):
        pio.renderers.default = 'browser'
        
        if ampl_uncert_collector == None:
            ampl_uncert_collector = self.ampl_uncert_collector
        
        hist_data = []
        group_labels = []
        bc_res = []
        
        df_to_plot_full = pd.DataFrame()
        
        for i, cs in enumerate(case_studies):
            output_folder = output_folder_cs[i]
            self.gather_results(output_folder)
            ampl_uncert_collector = self.unpkl(self,cs,output_folder)
            
            results = ampl_uncert_collector['C_tot_capex'].copy()
            results.reset_index(inplace=True)
            results = results.loc[results['index'].isin(['YEAR_2050']),:]
            results.dropna(how='all',inplace=True)
            results['C_tot_capex']/=1000

            df_to_plot = results.set_index(['index','Sample'])
            df_to_plot.dropna(how='all',inplace=True)
            df_to_plot.reset_index(inplace=True)
            df_to_plot['index'] = df_to_plot['index'].str.replace('YEAR_', '')
            df_to_plot['Case'] = cs
            
            output_folder_bc_i = output_folder_bc[i]
            bc_pkl_file = os.path.join(output_folder_bc_i,'_Results.pkl')
            bc_open_file = open(bc_pkl_file,"rb")
            bc_results = pkl.load(bc_open_file)
            bc_open_file.close()
            
            results_bc = bc_results['C_tot_capex'].copy()
            results_bc.reset_index(inplace=True)
            results_bc = results_bc.loc[results_bc['index'].isin(['YEAR_2050']),:]
            results_bc.dropna(how='all',inplace=True)
            results_bc['C_tot_capex']/=1000
            bc_res += [results_bc.C_tot_capex[0]]
            
            if i==0:
                df_to_plot_full = df_to_plot
            else:
                df_to_plot_full = df_to_plot_full.append(df_to_plot)
                
            
            hist_data += [np.array(df_to_plot.C_tot_capex)]
            group_labels += [cs]
            
                
            if plot:
                fig_temp = px.ecdf(df_to_plot, x="C_tot_capex")
                
                x = fig_temp.data[0].x
                y = fig_temp.data[0].y
                
                poly_func  = self.polyfit_func(x,y)
                
                x_smooth = np.linspace(min(x),max(x),num=int(1e5))
                y_smooth = poly_func(x_smooth)
                
                if i==0:
                    fig = px.scatter(x = x_smooth,y = y_smooth)
                else:
                    fig.add_trace(go.Scatter(x = x_smooth,y = y_smooth))
        
                
        # pio.show(fig)
        
        fig_test = ff.create_distplot(hist_data,group_labels,show_hist = False,show_rug=False)
        fig_test.update_layout(title_text='Total capital cost [b€]',titlefont=dict(family="Raleway",size=28))
        y1 = 0
        for k,bc_r in enumerate(bc_res):
            y1 = max(y1,max(fig_test.data[k].y))
        for bc_r in bc_res:
            fig_test.add_shape(x0=bc_r,x1=bc_r,
                      y0=min(fig_test.data[0].y),y1=y1,
                      type='line',layer="below",
                      line=dict(color='rgb(90,90,90)',width=1),opacity=0.5)
        pio.show(fig_test)
        save_dir = str(Path(self.outdir).parent.parent.parent)+'/_Graphs_comp'
        fig_test.write_html(save_dir+"/Total_capital_cost.html")
        
        # fig_hist = px.histogram(df_to_plot_full, x = 'C_tot_capex',facet_row='Case',title='Total capital cost [b€]')
        # pio.show(fig_hist)
    
    
    def graph_comp_tech_cap(self,case_studies,output_folder_bc, ampl_uncert_collector = None, plot = True):
        pio.renderers.default = 'browser'
        
        if ampl_uncert_collector == None:
            ampl_uncert_collector = self.ampl_uncert_collector
        
        df_to_plot_full = pd.DataFrame()
        
        for i, cs in enumerate(case_studies):
            
            pkl_file = os.path.join(output_folder_bc[i],'_Results.pkl')
            
            open_file = open(pkl_file,"rb")
            collector = pkl.load(open_file)
            open_file.close()
            
            results = pd.DataFrame(collector['Assets'].copy()['F'])
            results = results.loc[results['F'] > 1e-1]
            results.reset_index(inplace=True)

            df_to_plot = results.copy()
            df_to_plot['Years'] = df_to_plot['Years'].str.replace('YEAR_', '')
            df_to_plot['Case'] = cs
            
            if i==0:
                df_to_plot_full = df_to_plot
            else:
                df_to_plot_full = df_to_plot_full.append(df_to_plot)
                
            
        dict_tech = self._group_tech_per_eud()
        for sector, tech in dict_tech.items():

            temp = df_to_plot_full.loc[df_to_plot_full['Technologies'].isin(tech)]
            df_to_plot = temp.copy()
            df_to_plot['Technologies'] = df_to_plot['Technologies'].astype("str")
            
            for t in tech:
                df_to_plot_2 = df_to_plot.loc[df_to_plot['Technologies'] == t]
            
                if plot:
                    
                    fig = px.bar(df_to_plot_2, x='Years', y = 'F',color='Case',barmode='group')
    
                    fig.update_xaxes(categoryorder='array', categoryarray= sorted(df_to_plot['Years'].unique()))
                    
                    fig.update_layout(title_text=t+' [GW]',titlefont=dict(family="Raleway",size=28))
            
            
            
                save_dir = str(Path(self.outdir).parent.parent.parent)+'/_Graphs_comp'
                
                if not os.path.exists(Path(save_dir+"/Tech_Cap/"+sector)):
                    Path(save_dir+"/Tech_Cap/"+sector).mkdir(parents=True,exist_ok=True)
                
                fig.write_html(save_dir+"/Tech_Cap/"+sector+"/"+t+".html")
        
        # fig_hist = px.histogram(df_to_plot_full, x = 'Transition_cost',facet_row='Case')
        # pio.show(fig_hist)
    
    
    def graph_comp_c_inv_2050(self,case_studies,output_folder_bc, ampl_obj, ampl_uncert_collector = None, plot = True):
        pio.renderers.default = 'browser'
        
        if ampl_uncert_collector == None:
            ampl_uncert_collector = self.ampl_uncert_collector
        
        df_to_plot_full = pd.DataFrame()
        
        for i, cs in enumerate(case_studies):
            
            pkl_file = os.path.join(output_folder_bc[i],'_Results.pkl')
            
            ampl_graph = AmplGraph(pkl_file, ampl_obj, cs)
            temp = ampl_graph.graph_cost_inv_phase_tech(plot=False)
            temp_return = ampl_graph.graph_cost_return(plot=False)
            
            
            results = temp.loc[temp['Years']=='2050']
            results_return = temp_return.loc[temp_return['Years']=='2050']
            
            results = results.set_index(['Years','Category'])
            results_return = results_return.set_index(['Years','Category'])
            results['Diff_Return'] = results['cumsum']-results_return['Cost_return']
            
            df_to_plot = results.copy()
            df_to_plot['Case'] = cs
            
            df_to_plot.reset_index(inplace=True)
            
            if i==0:
                df_to_plot_full = df_to_plot
            else:
                df_to_plot_full = df_to_plot_full.append(df_to_plot)

        
        if plot:
            
            fig = px.bar(df_to_plot_full, x='Category', y = 'cumsum',color='Case',barmode='group')
            fig_2 = px.bar(df_to_plot_full, x='Case', y = 'cumsum',color='Category',color_discrete_map=self.color_dict_full)
            
            fig_3 = px.bar(df_to_plot_full, x='Category', y = 'Diff_Return',color='Case',barmode='group')
            fig_4 = px.bar(df_to_plot_full, x='Case', y = 'Diff_Return',color='Category',color_discrete_map=self.color_dict_full)
            
            save_dir = str(Path(self.outdir).parent.parent.parent)+'/_Graphs_comp'
            
            # fig.write_html(save_dir+"/Cum_cost_inv_2050.html")
    
        A  = 4
        
    
    def graph_comp_c_inv_phase(self,case_studies,output_folder_bc, ampl_obj, ampl_uncert_collector = None, plot = True):
        pio.renderers.default = 'browser'
        
        if ampl_uncert_collector == None:
            ampl_uncert_collector = self.ampl_uncert_collector
        
        df_to_plot_full = pd.DataFrame()
        
        for i, cs in enumerate(case_studies):
            
            pkl_file = os.path.join(output_folder_bc[i],'_Results.pkl')
            
            ampl_graph = AmplGraph(pkl_file, ampl_obj, cs)
            temp = ampl_graph.graph_cost_inv_phase_tech(plot=False)
            temp_return = ampl_graph.graph_cost_return(plot=False)
            
            results = temp.groupby(['Years']).sum()
            results_return = temp_return.groupby(['Years']).sum()
            
            results['Diff_Return'] = results['cumsum']-results_return['Cost_return']
            
            df_to_plot = results.copy()
            df_to_plot['Case'] = cs
            
            df_to_plot.reset_index(inplace=True)
            
            if i==0:
                df_to_plot_full = df_to_plot
            else:
                df_to_plot_full = df_to_plot_full.append(df_to_plot)

        
        if plot:
            
            fig = px.line(df_to_plot_full, x='Years', y = 'cumsum',color='Case')
            fig_2 = px.line(df_to_plot_full, x='Years', y = 'Diff_Return',color='Case')
            
            pio.show(fig_2)
            
            save_dir = str(Path(self.outdir).parent.parent.parent)+'/_Graphs_comp'
            
            # fig.write_html(save_dir+"/Cum_cost_inv_2050.html")
    
    
    def graph_comp_c_op_phase(self,case_studies,output_folder_bc, ampl_obj, ampl_uncert_collector = None, plot = True):
        pio.renderers.default = 'browser'
        
        if ampl_uncert_collector == None:
            ampl_uncert_collector = self.ampl_uncert_collector
        
        df_to_plot_full = pd.DataFrame()
        
        for i, cs in enumerate(case_studies):
            
            pkl_file = os.path.join(output_folder_bc[i],'_Results.pkl')
            
            ampl_graph = AmplGraph(pkl_file, ampl_obj, cs)
            temp = ampl_graph.graph_cost_op_phase(plot=False)
            
            results = temp.loc[temp['Years']=='2050']
            
            df_to_plot = results.copy()
            df_to_plot['Case'] = cs
            
            if i==0:
                df_to_plot_full = df_to_plot
            else:
                df_to_plot_full = df_to_plot_full.append(df_to_plot)

        
        if plot:
            
            fig = px.bar(df_to_plot_full, x='Category', y = 'cumsum',color='Case',barmode='group')
            fig_2 = px.bar(df_to_plot_full, x='Case', y = 'cumsum',color='Category',color_discrete_map=self.color_dict_full)
            
            save_dir = str(Path(self.outdir).parent.parent.parent)+'/_Graphs_comp'
            
            # fig.write_html(save_dir+"/Cum_cost_inv_2050.html")
    
        A  = 4
    
    def graph_local_RE(self, ampl_uncert_collector = None, plot = True):
        pio.renderers.default = 'browser'
        
        if ampl_uncert_collector == None:
            ampl_uncert_collector = self.ampl_uncert_collector
        
        col_plot = ['PV','WIND_ONSHORE','WIND_OFFSHORE']
        results = ampl_uncert_collector['Assets'].copy()
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
    
    
    
    
    def graph_layer(self, ampl_uncert_collector = None, plot = True):
        pio.renderers.default = 'browser'
        
        if ampl_uncert_collector == None:
            ampl_uncert_collector = self.ampl_uncert_collector
        
        col_plot = ['AMMONIA','ELECTRICITY','GAS','H2','WOOD','WET_BIOMASS','HEAT_HIGH_T',
                'HEAT_LOW_T_DECEN','HEAT_LOW_T_DHN','HVC','METHANOL',
                'MOB_FREIGHT_BOAT','MOB_FREIGHT_RAIL','MOB_FREIGHT_ROAD','MOB_PRIVATE',
                'MOB_PUBLIC','Sample']
        results = ampl_uncert_collector['Year_balance'].copy()
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
        year_balance = self.ampl_uncert_collector['Year_balance']
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

    @staticmethod
    def polyfit_func(x_in, y_in, threshold=0.99999999):
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
            The threshold for the R-squared parameter. The default is 0.99999.
    
        Returns
        -------
        poly_func : numpy.poly1d
            A one-dimensional polynomial.
    
        """
        order = 0
        r_squared = 0.
        while r_squared < threshold and order < 10:
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
