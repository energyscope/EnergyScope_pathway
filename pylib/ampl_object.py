#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 08 2022

@author: rixhonx
"""

# import numpy as np
from pathlib import Path
import pandas as pd
from amplpy import AMPL, Environment
from copy import deepcopy
import logging
import numpy as np

import os,sys

pylibPath = os.path.abspath("../pylib")
if pylibPath not in sys.path:
    sys.path.insert(0, pylibPath)

class AmplObject:

    """

    The AmplObject class allows to set an optimization problem in ampl, solve it,
     and interface with it trough the amplpy API and some additionnal functions

    Parameters
    ----------
    mod_1_path : list(pathlib.Path)
        List specifying the path of the different .mod files with the model of the LP problem
        in ampl syntax. These files have to be allocated to the ampl problem BEFORE the .dat files
    mod_2_path : list(pathlib.Path)
        List specifying the path of the different .mod files with the model of the LP problem
        in ampl syntax. These files have to be allocated to the ampl problem AFTER the .dat files
    data_path : list(pathlib.Path)
        List specifying the path of the different .dat files with the data of the LP problem
        in ampl syntax
    ampl_path : pathlib.Path
        Path towards the license AMPL of the user 
    options : dict
        Dictionary of the different options for ampl and the cplex solver

    """

    def __init__(self, mod_1_path, mod_2_path, data_path, options, type_model = 'MO',ampl_path=None):

        print("\n\n#-----------------------------------------#")
        print("\nInitializing ampl problem...")


        self.dir = Path(mod_1_path[0]).parent
        self.mod_1_path = mod_1_path
        self.mod_2_path = mod_2_path
        self.data_path = data_path
        self.ampl_path = ampl_path
        self.options = options
        self.ampl = self.set_ampl(mod_1_path, mod_2_path, data_path, options, ampl_path)
        self.vars = self.ampl.getVariables()
        self.params = self.ampl.getParameters()
        self.sets = dict()
        self.t = float()
        self.outputs = dict()
        self.type_model = type_model

        # create empty dictionary to be filled with main results
        self.results = dict.fromkeys(['TotalCost', 'C_inv_phase', 'C_inv_phase_tech',
                                      'C_op_phase_tech','C_op_phase_res',
                                      'Cost_breakdown', 'Cost_return', 
                                      'TotalGwp','Gwp_breakdown', 'Resources',
                                      'Assets', 'New_old_decom',
                                      'F_decom','Sto_assets', 'Year_balance'])

        # Store names of sets
        self.get_sets()


    """"

    Run the LP optimization with AMPL and saves the running time in self.t

    """
    def run_ampl(self):
        try:
            self.ampl._startRecording('session.log')
            # self.ampl.eval("option times 1, gentimes 1;") 
            self.ampl.solve()
            # self.ampl.eval("option times 0, gentimes 0;")
            self.ampl.eval('display solve_result;')
            self.ampl.eval('display _solve_elapsed_time;')
            self.ampl.eval('display _ampl_elapsed_time;')
            self.ampl.setOption('log_file', "")
            self.t = self.ampl.getData('_solve_elapsed_time;').toList()[0]

        except Exception as e:
            print(e)
            raise
        return self.ampl.getData('solve_result;').toList()[0]
    """

    Function to of the LP optimization problem

    """
    def get_sets(self):
        
        for name, obj in self.ampl.getSets():
            if len(obj.instances()) <= 1:
                self.sets[name] = obj.getValues().toList()
            else:
                self.sets[name] = self.get_subset(obj)
        
        

    def get_elem(self, elem_name:str,type_of_elem = 'Var'):
        """Function to extract the mentioned variable and store it into self.outputs
        Parameters
        ----------
        var_name: str
        Name of the variable to extract from the optimisation problem results. Should be written as in the .mod file
        Returns
        -------
        elem: pd.DataFrame()
        DataFrame containing the values of the different elements of the variable.
        The n first columns give the n sets on which it is indexed
        and the last column give the value obtained from the optimization.
        """
        if type_of_elem == 'Var':
            ampl_elem = self.ampl.getVariable(elem_name)
        elif type_of_elem == 'Param':
            ampl_elem = self.ampl.getParameter(elem_name)
        # Getting the names of the sets
        indexing_sets = [s.capitalize() for s in ampl_elem.getIndexingSets()]
        # Getting the data of the variable into a pandas dataframe
        amplpy_df = ampl_elem.getValues()
        elem = amplpy_df.toPandas()
        # getting the number of indices. If elem has more then 1 index, we set it as a MultiIndex
        n_indices = amplpy_df.getNumIndices()
        if n_indices>1:
            elem.index = pd.MultiIndex.from_tuples(elem.index, names=indexing_sets)
        else:
            elem.index = pd.Index(elem.index, name=indexing_sets[0])
        # getting rid of '.val' (4 trailing characters of the string) into columns names such that the name of the columns correspond to the variable
        if type_of_elem == 'Var':
            elem.rename(columns=lambda x: x[:-4], inplace=True)
            self.outputs[elem_name] = elem
        #self.to_pd(ampl_elem.getValues()).rename(columns={(var_name+'.val'):var_name})

        return elem
    """"

    Change the value of the parameter "name" to new "value"

    Parameters
    ----------
    name : string
    Name of the parameter to change the value

    value : dict(tuple: float)
    Dictionary of which the key is a tuple specifying which element of the parameter must be changed
    and the value to set is a float

    """
    def set_params(self, name, value):
        if len(self.ampl.get_parameter(name).instances()) == 1:
            self.ampl.get_parameter(name).set(1.0*value) # 1.0* aims to convert potential float32 into float64 that is compatible with ampl object
        else:
            self.ampl.get_parameter(name).setValues(value)
    

    def clean_history(self):
        open(os.path.join(self.dir,'fix.mod'), 'w').close()
        open(os.path.join(self.dir,'PESTD_data_remaining_wnd.dat'), 'w').close()
        open(os.path.join(self.dir,'PES_seq_opti.dat'), 'w').close()


    def set_init_sol(self):
    
        fix_0 = os.path.join(self.dir,'fix_0.mod')
        fix = os.path.join(self.dir,'fix.mod')

        with open(fix_0,'w+', encoding='utf-8') as fp:
            variables = self.ampl.getVariables()
            for k in self.sets['SET_INIT_SOL']:
                for i, v in variables[k]:
                    print('fix {}:={};'.format(v.name(),v.value()), file = fp)
                print("\n", file = fp)
                    
        with open(fix_0) as fin, open(fix,'w+', encoding='utf-8') as fout:
            for line in fin:
                line = line.replace("_up_to","")
                line = line.replace("_next","")
                fout.write(line)
        
        os.remove(fix_0)
    
    def collect_gwp(self, years):
        gwp_dict = dict.fromkeys(years)

        TotalGWP = self.vars['TotalGWP']
        for y in years:
            gwp_dict[y] = TotalGWP[y].value()
        
        return gwp_dict
    
    def collect_cost(self,objective_name, years):
        objective = self.ampl.get_objective(objective_name)
        objective = objective.value()

        cost_dict = dict.fromkeys(years)
        TotalCost = self.vars['TotalCost']

        for y in years:
            cost_dict[y] = TotalCost[y].value()
        
        return [objective, cost_dict]
    
    #############################
    #       STATIC METHODS      #
    #############################

    @staticmethod
    def set_ampl(mod_1_path, mod_2_path, data_path, options, ampl_path=''):
        """

        Initialize the AMPL() object containing the LP problem

        Parameters
        ----------
        mod_path : list(pathlib.Path)
        List specifying the path of the different .mod files with the model of the LP problem
        in ampl syntax

        data_path : list(pathlib.Path)
        List specifying the path of the different .dat files with the data of the LP problem
        in ampl syntax

        options : dict
        Dictionary of the different options for ampl and the cplex solver

        ampl_path : pathlib.Path
        Path towards the license AMPL of the user

        Returns
        -------
        ampl object created

        """
        try:
            # Create an AMPL instance
            if ampl_path == None:
                ampl = AMPL()
            else:
                ampl = AMPL(Environment(ampl_path))
            # define solver
            ampl.setOption('solver', 'gurobi')
            # set options
            for o in options:
                ampl.setOption(o, options[o])
            # Read the model and data files.
            for m in mod_1_path:
                if not os.path.exists(m):
                    open(m,"w+")
                ampl.read(m)
            for d in data_path:
                if not os.path.exists(d):
                    open(d,"w+")
                ampl.readData(d)
            for m in mod_2_path:
                if not os.path.exists(m):
                    open(m,"w+")
                ampl.read(m)
        except Exception as e:
            print(e)
            raise

        return ampl

    
    @staticmethod
    def get_subset(my_set):
        """
        Function to extract the subsets of set containing sets from the AMPL() object

        Parameters
        ----------
        my_set : amplpy.set.Set
        2-dimensional set to extract


        Returns
        -------
        d : dict()
        dictionary containing the subsets as lists
        """
        
        d = dict()
        for n, o in my_set.instances():
            try:
                d[n] = o.getValues().toList()
            except Exception as e:
                d[n] = list()
        return d
    
    @staticmethod
    def get_subparam(my_param):
        """
        Function to extract the subsets of set containing sets from the AMPL() object

        Parameters
        ----------
        my_set : amplpy.set.Set
        2-dimensional set to extract


        Returns
        -------
        d : dict()
        dictionary containing the subsets as lists
        """
        
        d = dict()
        for n, o in my_param.instances():
            try:
                d[n] = o
            except Exception as e:
                d[n] = list()
        return d
    

    
    @staticmethod
    def to_pd(amplpy_df):
        """
        Function to transform an amplpy.DataFrame into pandas.DataFrame for easier manipulation

        Parameters
        ----------
        amplpy_df : amplpy.DataFrame into pandas.DataFrame
        amplpy dataframe to transform


        Returns
        -------
        df : pandas.DataFrame
        DataFrame transformed as 'long' dataframe (can be easily pivoted later)
        """
        
        headers = amplpy_df.getHeaders()
        columns = {header: list(amplpy_df.getColumn(header)) for header in headers}
        df = pd.DataFrame(columns)
        df = df.rename(columns={headers[-1]:'Value'})
        df = df.set_index(list(headers[:-1]))
        df.index.name = None # get rid of the name of the index (multilevel)
        return df

    @staticmethod
    def to_pd_pivot(amplpy_df):
        """
        Function to transform an amplpy.DataFrame into pandas.DataFrame for easier manipulation

        Parameters
        ----------
        amplpy_df : amplpy.DataFrame
        amplpy dataframe to transform


        Returns
        -------
        df : pandas.DataFrame
        DataFrame transformed as 'long' dataframe (can be easily pivoted later)
        """
    
        nindices = amplpy_df.getNumIndices()
        headers = amplpy_df.getHeaders()
        columns = {header: list(amplpy_df.getColumn(header)) for header in headers}
        df = pd.DataFrame(columns)
        if nindices==1:
            df = df.set_index(headers[0])
            df.index.name = None # get rid of the name of the index (multilevel)
        elif nindices==2:
            df = df.pivot(index=headers[0], columns=headers[1], values=headers[2])
            df.index.name = None # get rid of the name of the index (multilevel)
        elif nindices==3:
            dic = dict()
            for i in set(columns[headers[0]]):
                dic[i] = df[df[headers[0]]==i].pivot(index=headers[2], columns=headers[1], values=headers[3])
                dic[i].index.name = None # to get rid of name (multilevel)
            df = dic
        elif nindices==4:
            dic = dict()
            for i in set(columns[headers[0]]):
                dic[i] = dict()
                for j in set(columns[headers[3]]):
                    dic[i][int(j)] = df.loc[(df[headers[0]]==i) & (df[headers[3]]==j),:].pivot(index=headers[2], columns=headers[1], values=headers[4])
                    dic[i][int(j)].index.name = None # to get rid of name (multilevel)
            df = dic
        
        return df

    def get_results(self):
        """Wrapper function to get the summary results"""
        logging.info('Getting summary')
        self.get_total_cost()
        self.get_cost_breakdown()
        self.get_cost_return()
        self.get_total_gwp()
        self.get_gwp_breakdown()
        self.get_resources()
        self.get_assets()
        self.get_new_old_decom()
        self.get_F_decom()
        self.get_year_balance()
        
        return
    
    def get_total_cost(self):
        """Get the total annualized cost of the energy system of the different years
            It is stored into self.outputs['TotalCost'] and into self.results['TotalCost']
        """
        logging.info('Getting TotalCost')
        total_cost = self.get_elem('TotalCost').reset_index()
        total_cost['Years'] = pd.Categorical(total_cost['Years'], self.sets['YEARS_WND'])
        total_cost = total_cost[total_cost['Years'].notna()]
        total_cost = total_cost.set_index(['Years'])
        total_cost.sort_index(inplace=True)
        self.results['TotalCost'] = total_cost
        
        c_inv_phase = self.get_elem('C_inv_phase')
        c_inv_phase_index = c_inv_phase.index.names
        c_inv_phase = c_inv_phase.rename_axis(index={c_inv_phase_index[0]:'Phases'},axis=1)
        c_inv_phase = c_inv_phase.reset_index()
        c_inv_phase['Phases'] = pd.Categorical(c_inv_phase['Phases'],['2015_2020'] + self.sets['PHASE_UP_TO'])
        c_inv_phase = c_inv_phase[c_inv_phase['Phases'].notna()]
        c_inv_phase = c_inv_phase.set_index(['Phases'])
        c_inv_phase.sort_index(inplace=True)
        self.results['C_inv_phase'] = c_inv_phase
        
        c_inv_phase_tech = self.get_elem('C_inv_phase_tech')
        c_inv_phase_tech_index = c_inv_phase_tech.index.names
        c_inv_phase_tech = c_inv_phase_tech.rename_axis(index={c_inv_phase_tech_index[0]:'Phases'},axis=1)
        c_inv_phase_tech = c_inv_phase_tech.reset_index()
        phases = sorted(set(['2015_2020'] + self.sets['PHASE_UP_TO'] + self.sets['PHASE_WND']))
        c_inv_phase_tech['Phases'] = pd.Categorical(c_inv_phase_tech['Phases'],phases)
        c_inv_phase_tech = c_inv_phase_tech[c_inv_phase_tech['Phases'].notna()]
        c_inv_phase_tech = c_inv_phase_tech.set_index(['Phases','Technologies'])
        c_inv_phase_tech.sort_index(inplace=True)
        self.results['C_inv_phase_tech'] = c_inv_phase_tech
        
        c_op_phase_tech = self.get_elem('C_op_phase_tech')
        c_op_phase_tech_index = c_op_phase_tech.index.names
        c_op_phase_tech = c_op_phase_tech.rename_axis(index={c_op_phase_tech_index[0]:'Phases'},axis=1)
        c_op_phase_tech = c_op_phase_tech.reset_index()
        c_op_phase_tech['Phases'] = pd.Categorical(c_op_phase_tech['Phases'],self.sets['PHASE_UP_TO'])
        c_op_phase_tech = c_op_phase_tech[c_op_phase_tech['Phases'].notna()]
        c_op_phase_tech = c_op_phase_tech.set_index(['Phases','Technologies'])
        c_op_phase_tech.sort_index(inplace=True)
        self.results['C_op_phase_tech'] = c_op_phase_tech
        
        c_op_phase_res = self.get_elem('C_op_phase_res')
        c_op_phase_res_index = c_op_phase_res.index.names
        c_op_phase_res = c_op_phase_res.rename_axis(index={c_op_phase_res_index[0]:'Phases'},axis=1)
        c_op_phase_res = c_op_phase_res.reset_index()
        c_op_phase_res['Phases'] = pd.Categorical(c_op_phase_res['Phases'],self.sets['PHASE_UP_TO'])
        c_op_phase_res = c_op_phase_res[c_op_phase_res['Phases'].notna()]
        c_op_phase_res = c_op_phase_res.set_index(['Phases','Resources'])
        c_op_phase_res.sort_index(inplace=True)
        self.results['C_op_phase_res'] = c_op_phase_res
        
        
        return
    
    def get_cost_breakdown(self):
        """Gets the cost breakdown and stores it into the results"""
        logging.info('Getting Cost_breakdown')

        # Get the different costs variables
        c_inv = self.get_elem('C_inv')
        c_maint = self.get_elem('C_maint')
        c_op = self.get_elem('C_op')

        # set index names (for later merging)
        index_names = ['Years', 'Elements']
        c_inv.index.names = index_names
        c_maint.index.names = index_names
        c_op.index.names = index_names

        # Annualize the investiments
        tau = self.to_pd(self.params['tau'].getValues())
        tau.index.names = index_names

        c_inv_ann = c_inv.mul(tau['Value'], axis=0)

        # concat c_exch_network to c_inv_ann
        # c_inv_ann = pd.concat([c_inv_ann, c_exch_network.rename(columns={'C_exch_network': 'C_inv'})], axis=0)

        # Merge costs into cost breakdown
        cost_breakdown = c_inv_ann.merge(c_maint, left_index=True, right_index=True, how='outer') \
            .merge(c_op, left_index=True, right_index=True, how='outer')
        # Set Years and technologies/resources as categorical data for sorting
        cost_breakdown = cost_breakdown.reset_index()
        cost_breakdown['Years'] = pd.Categorical(cost_breakdown['Years'], self.sets['YEARS_WND'])
        cost_breakdown = cost_breakdown[cost_breakdown['Years'].notna()]
        self.categorical_esmy(df=cost_breakdown, col_name='Elements', el_name='Elements')
        cost_breakdown.sort_values(by=['Years', 'Elements'], axis=0, ignore_index=True, inplace=True)
        cost_breakdown.set_index(['Years', 'Elements'], inplace=True)

        # put very small values as nan
        # threshold = 1e-2
        threshold = 0
        cost_breakdown = cost_breakdown.mask((cost_breakdown > -threshold) & (cost_breakdown < threshold), np.nan)

        # Store into results
        cost_breakdown.replace(0, np.nan, inplace=True)
        self.results['Cost_breakdown'] = cost_breakdown
        return
        
    
    def get_cost_return(self):
        """Gets the cost return and stores it into the results"""
        logging.info('Getting Cost_return')
        c_inv_return = self.get_elem('C_inv_return')
        last_year_of_wnd = self.sets['YEARS_WND'][-1]
        cost_return = c_inv_return.copy()
        cost_return['Years'] = [last_year_of_wnd]*len(c_inv_return.index.unique())
        cost_return = cost_return.reset_index().set_index(['Years', 'Technologies'])
        
        c_inv_phase_tech = self.results['C_inv_phase_tech'].copy()
        c_inv_phase_tech.reset_index(inplace=True)
        c_inv_phase_tech['Phases'] = c_inv_phase_tech['Phases'].map(lambda x: 'YEAR_'+x[-4:])
        c_inv_phase_tech.rename(columns={'Phases':'Years'},inplace=True)
        c_inv_phase_tech = c_inv_phase_tech.set_index(['Years','Technologies'])
        c_inv_phase_tech.sort_values(by=['Years'],inplace=True)
        for g_name, g_df in c_inv_phase_tech.groupby(['Technologies']):
            c_inv_phase_tech.loc[g_df.index,'cumsum'] = c_inv_phase_tech.loc[g_df.index,'C_inv_phase_tech'].cumsum()
        
        c_inv_phase_tech.drop(columns={'C_inv_phase_tech'},inplace=True)
        c_inv_phase_tech = c_inv_phase_tech.loc[c_inv_phase_tech.index.get_level_values('Years') == last_year_of_wnd,:]
        
        cost_return = cost_return.merge(c_inv_phase_tech,left_index=True, right_index=True, how='outer')
        
        self.results['Cost_return'] = cost_return
        return

    def get_total_gwp(self):
        """Get the total gwp of the energy system of the different years
            It is stored into self.results['TotalGwp']
        """
        logging.info('Getting TotalGwp')
        total_gwp = self.get_elem('TotalGWP').reset_index()
        total_gwp['Years'] = pd.Categorical(total_gwp['Years'], self.sets['YEARS_WND'])
        total_gwp = total_gwp[total_gwp['Years'].notna()]
        
        gwp_cost = pd.DataFrame(index=self.sets['YEARS_WND'],columns=['Gwp_cost'])
        gwp_cost.index.set_names('Years',inplace=True)
        for y in self.sets['YEARS_WND']:
            if not(y in self.sets['YEAR_ONE']):
                gwp_cost.loc[y] = -self.ampl.get_constraint('minimum_GWP_reduction')[y].dual()

        gwp_limit = self.to_pd(self.params['gwp_limit'].getValues())
        gwp_limit.index.set_names('Years',inplace=True)
        gwp_limit.rename(columns={'Value':'Gwp_limit'},inplace=True)
        gwp_limit = gwp_limit.loc[gwp_limit.index.get_level_values('Years').isin(self.sets['YEARS_WND']),:]

        total_gwp = total_gwp.set_index(['Years'])
        total_gwp = total_gwp.merge(gwp_limit, left_on=['Years'], right_index=True)\
            .merge(gwp_cost, left_on=['Years'], right_index=True)
        total_gwp.sort_index(inplace=True)
        self.results['TotalGwp'] = total_gwp
        return

    def get_gwp_breakdown(self):
        """Get the gwp breakdown [ktCO2e/y] of the technologies and resources"""
        logging.info('Getting Gwp_breakdown')

        # Get GWP_constr and GWP_op
        gwp_constr = self.get_elem('GWP_constr')  
        gwp_op = self.get_elem('GWP_op')

        # set index names (for later merging)
        index_names = ['Years', 'Elements']
        gwp_constr.index.names = index_names
        gwp_op.index.names = index_names

        # Get lifetime of technologies from input data
        lifetime = self.to_pd(self.params['lifetime'].getValues())
        lifetime.index.names = index_names

        # annualize GWP_constr by dividing by lifetime
        gwp_constr_ann = pd.DataFrame(gwp_constr.div(lifetime['Value'],axis=0),
                                      columns=['GWP_constr'])

        # merging emissions into gwp_breakdown
        gwp_breakdown = gwp_constr_ann.merge(gwp_op,left_index=True, right_index=True, how='outer').reset_index()

        # Set Years and technologies/resources as categorical data for sorting
        gwp_breakdown['Years'] = pd.Categorical(gwp_breakdown['Years'], self.sets['YEARS_WND'])
        gwp_breakdown = gwp_breakdown[gwp_breakdown['Years'].notna()]
        self.categorical_esmy(df=gwp_breakdown, col_name='Elements', el_name='Elements')
        gwp_breakdown.sort_values(by=['Years', 'Elements'], axis=0, ignore_index=True, inplace=True)
        gwp_breakdown.set_index(['Years', 'Elements'], inplace=True)

        # put very small values as nan
        # threshold = 1e-2
        threshold = 0
        gwp_breakdown = gwp_breakdown.mask((gwp_breakdown > -threshold) & (gwp_breakdown < threshold), np.nan)

        # store into results
        gwp_breakdown.replace(0, np.nan, inplace=True)
        self.results['Gwp_breakdown'] = gwp_breakdown
        return
        

    def get_resources(self):
        """Get the Resources yearly local and exterior production, and import and exports as well as exchanges"""
        logging.info('Getting Yearly resources and exchanges')

        # EXTRACTING DATA FROM OPTIMISATION MODEL

        # Get results related to Resources and Exchanges and sum over all layers
        # year local production and import from exterior
        resources = self.get_elem('Res')
        index_names = ['Years', 'Resources']
        resources.index.names = index_names
        resources = resources.reset_index()
        
        resources['Years'] = pd.Categorical(resources['Years'], self.sets['YEARS_WND'])
        resources = resources[resources['Years'].notna()]
        self.categorical_esmy(df=resources, col_name='Resources', el_name='Resources')
        resources.sort_values(by=['Years', 'Resources'], axis=0, ignore_index=True, inplace=True)
        resources.set_index(['Years', 'Resources'], inplace=True)

        # put very small values as nan
        # threshold = 1e-2
        threshold = 0
        resources = resources.mask((resources > -threshold) & (resources < threshold), np.nan)
        
        resources.replace(0, np.nan, inplace=True)
        self.results['Resources'] = resources
        return
    
    def get_assets(self):
        """Gets the assets and stores it into the results,
        for storage assets, and additional data set is created (Sto_assets)

        self.results['Assets']: Each asset is defined by its installed capacity (F) [GW],
                                the bound on it (f_min,f_max) [GW]
                                and its production on its main output layer (F_year) [GWh]
                                It has the following columns:
                                ['Years', 'Technologies', 'F', 'f_min', 'f_max', 'F_year']
                                containing the following information:
                                [region name,
                                technology name,
                                installed capacity [GW] (or [GWh] for storage technologies),
                                lower bound on the installed capacity [GW] (or [GWh] for storage technologies),
                                upper bound on the installed capacity [GW] (or [GWh] for storage technologies),
                                year production [GWh] (or losses for storage technologies)
                                ]

        self.results['Sto_assets']: It has the following columns:
                                    ['Years', 'Technologies', 'F', 'f_min', 'f_max', 'Losses', 'Year_energy_flux',
                                    'Storage_in_max', 'Storage_out_max']
                                    containing the following information:
                                    [region name,
                                    technology name,
                                    installed capacity [GWh],
                                    lower bound on the instaled capacity [GWh],
                                    upper bound on the installed capacity [GWh],
                                    year losses [GWh],
                                    year energy flux going out of the storage technology [GWh],
                                    maximum input power [GW],
                                    maximum output power [GW]
                                    ]

        """
        logging.info('Getting Assets and Storage assets')

        # EXTRACTING OPTIMISATION MODEL RESULTS
        # installed capacity
        f = self.get_elem('F')
        tech = self.sets['TECHNOLOGIES'].copy()
        sto_tech_daily = self.sets['STORAGE_DAILY'].copy()
        sto_tech_daily.remove('BEV_BATT')
        sto_tech_daily.remove('PHEV_BATT')
        
        F_t = self.get_elem('F_t')
        F_t_tech = F_t.loc[F_t.index.get_level_values('Resources union technologies').isin(tech),:]
        
        F_t_tech = F_t_tech.rename_axis(index={'Resources union technologies':'Technologies'},axis=1)

        # energy produced by the technology
        # Remove the daily storage technologies from the results in case of monthly model
        if self.type_model == 'MO':
            f_year = self.from_agg_to_year(ts=F_t_tech) \
                .groupby(['Years', 'Technologies']).sum() \
                .rename(columns={'F_t':'F_year'})
            f_year = f_year.loc[~f_year.index.get_level_values('Technologies').isin(sto_tech_daily),:]
            # Get Storage_power (power balance at each month)
            storage_in = self.get_elem('Storage_in') \
                .groupby(['Years', 'I in storage_tech', 'Periods']).sum()
            storage_in = storage_in.loc[~storage_in.index.get_level_values('I in storage_tech').isin(sto_tech_daily),:]
            storage_out = self.get_elem('Storage_out') \
                .groupby(['Years', 'I in storage_tech', 'Periods']).sum()
            storage_out = storage_out.loc[~storage_out.index.get_level_values('I in storage_tech').isin(sto_tech_daily),:]
        else:
            f_year = self.from_agg_to_year(ts=F_t_tech
                                             .reset_index().set_index(['Typical_days', 'Hours'])) \
                .groupby(['Years', 'Technologies']).sum() \
                .rename(columns={'F_t': 'F_year'})
            # Get Storage_power (power balance at each hour)
            storage_in = self.get_elem('Storage_in') \
                .groupby(['Years', 'I in storage_tech', 'Hours', 'Typical_days']).sum()
            storage_out = self.get_elem('Storage_out') \
                .groupby(['Years', 'I in storage_tech', 'Hours', 'Typical_days']).sum()


        # ASSETS COMPUTATIONS
        # Get the bounds on F (f_min,f_max)
        # create frames for concatenation (list of df to concat)
        index_names = ['Years', 'Technologies']
        
        f_min = self.to_pd(self.params['f_min'].getValues())
        f_min.index.names = index_names
        f_min.columns=['f_min']
        f_max = self.to_pd(self.params['f_max'].getValues())
        f_max.index.names = index_names
        f_max.columns=['f_max']
        # for n, r in self.Years.items():
        #     frames.append(r.data['Technologies'].loc[:, ['f_min', 'f_max']].copy())
        assets = f.merge(f_min, left_on=['Years', 'Technologies'], right_index=True) \
            .merge(f_max, left_on=['Years', 'Technologies'], right_index=True) \
            .merge(f_year, left_on=['Years', 'Technologies'], right_on=['Years', 'Technologies']).reset_index()
        # set Years and Technologies as categorical data and sort it
        assets['Years'] = pd.Categorical(assets['Years'], self.sets['YEARS_WND'])
        assets = assets[assets['Years'].notna()]
        self.categorical_esmy(df=assets, col_name='Technologies', el_name='Technologies')
        assets.sort_values(by=['Years', 'Technologies'], axis=0, ignore_index=True, inplace=True)
        assets.set_index(['Years', 'Technologies'], inplace=True)
        # put very small values as nan
        # threshold = 1e-2
        threshold = 0
        assets = assets.mask((assets > -threshold) & (assets < threshold), np.nan)
        # threshold = 1e-1
        threshold = 0
        assets['F_year'] = assets['F_year'].mask((assets['F_year'] > -threshold) & (assets['F_year'] < threshold), np.nan)

        # STORAGE ASSETS COMPUTATIONS
        # compute the balance
        storage_power = storage_out.merge(-storage_in, left_index=True, right_index=True)
        storage_power = storage_power.loc[storage_power.index.get_level_values('Years').isin(self.sets['YEARS_WND']),:]
        storage_power['Storage_power'] = storage_power['Storage_out'] + storage_power['Storage_in']
        # losses are the sum of the balance over the year
        if self.type_model == 'MO':
            sto_losses = self.from_agg_to_year(ts=pd.DataFrame(storage_power['Storage_power']))\
                .groupby(['Years', 'I in storage_tech']).sum()
        else:
            sto_losses = self.from_agg_to_year(ts=storage_power['Storage_power']
                                              .reset_index().set_index(['Typical_days', 'Hours'])) \
                .groupby(['Years', 'I in storage_tech']).sum()
        # Update F_year in assets df for STORAGE_TECH
        assets.loc[sto_losses.index, 'F_year'] = sto_losses['Storage_power']

        # replace Storage_in and Storage_out by values deduced from Storage_power
        # such that at each time period the flow goes only in 1 direction
        threshold = 1e-2
        storage_power['Storage_in'] = storage_power['Storage_power'].mask((storage_power['Storage_power'] > -threshold),
                                                                          np.nan)
        storage_power['Storage_out'] = storage_power['Storage_power'].mask((storage_power['Storage_power'] < threshold),
                                                                           np.nan)
        # Compute total over the year by mapping periods
        if self.type_model == 'MO':
            sto_flux_year = self.from_agg_to_year(ts=storage_power)\
                .groupby(['Years', 'I in storage_tech']).sum() \
                .rename(columns={'Storage_out': 'Year_energy_flux'}).drop(columns=['Storage_in', 'Storage_power'])
        else:
            sto_flux_year = self.from_agg_to_year(ts=storage_power.reset_index().set_index(['Typical_days', 'Hours']))\
                .groupby(['Years', 'I in storage_tech']).sum() \
                .rename(columns={'Storage_out': 'Year_energy_flux'}).drop(columns=['Storage_in', 'Storage_power'])
        # create sto_assets from copy() of assets
        sto_assets = assets.copy()
        sto_assets.rename(columns={'F_year': 'Losses'}, inplace=True)
        # merge it with sto_flux_year
        sto_flux_year.index.set_names(sto_assets.index.names, inplace=True)  # set proper name to index
        sto_assets = sto_assets.merge(sto_flux_year, left_index=True, right_on=['Years', 'Technologies'],
                                      how='right')
        # Get storage_charge_time and storage_discharge_time from input data
        # and compute maximum input and output power of the storage technology
        storage_charge_time = self.to_pd(self.params['storage_charge_time'].getValues())
        storage_charge_time.index.names = index_names
        storage_charge_time.columns=['storage_charge_time']
        storage_charge_time = storage_charge_time.loc[storage_charge_time.index.get_level_values('Years').isin(self.sets['YEARS_WND']),:]
        storage_charge_time = storage_charge_time.loc[~storage_charge_time.index.get_level_values('Technologies').isin(sto_tech_daily),:]
        storage_discharge_time = self.to_pd(self.params['storage_discharge_time'].getValues())
        storage_discharge_time.index.names = index_names
        storage_discharge_time.columns=['storage_discharge_time']
        storage_discharge_time = storage_discharge_time.loc[storage_discharge_time.index.get_level_values('Years').isin(self.sets['YEARS_WND']),:]
        storage_discharge_time = storage_discharge_time.loc[~storage_discharge_time.index.get_level_values('Technologies').isin(sto_tech_daily),:]
        sto_assets = sto_assets.merge(storage_charge_time, left_on=['Years', 'Technologies'], right_index=True)\
            .merge(storage_discharge_time, left_on=['Years', 'Technologies'], right_index=True)
        sto_assets['Storage_in_max'] = sto_assets['F'] / sto_assets['storage_charge_time']
        sto_assets['Storage_out_max'] = sto_assets['F'] / sto_assets['storage_discharge_time']
        sto_assets.drop(columns=['storage_charge_time', 'storage_discharge_time'], inplace=True)
        # set Region and Technology as categorical data and sort it
        sto_assets.reset_index(inplace=True)
        sto_assets['Years'] = pd.Categorical(sto_assets['Years'], self.sets['YEARS_WND'])
        self.categorical_esmy(df=sto_assets, col_name='Technologies', el_name='Technologies')
        sto_assets.sort_values(by=['Years', 'Technologies'], axis=0, ignore_index=True, inplace=True)
        sto_assets.set_index(['Years', 'Technologies'], inplace=True)
        # put very small values as nan
        threshold = 1
        sto_assets = sto_assets.mask((sto_assets > -threshold) & (sto_assets < threshold), np.nan)

        # Store into results
        assets.replace(0, np.nan, inplace=True)
        self.results['Assets'] = assets
        sto_assets.replace(0, np.nan, inplace=True)
        self.results['Sto_assets'] = sto_assets
        return
    
    def get_new_old_decom(self):
        F_new = self.get_elem('F_new')
        f_new_index = F_new.index.names
        F_new = F_new.rename_axis(index={f_new_index[0]:'Phases'},axis=1)
        
        F_old = self.get_elem('F_old')
        f_old_index = F_old.index.names
        F_old = F_old.rename_axis(index={f_old_index[0]:'Phases'},axis=1)
        
        F_decom = self.get_elem('F_decom')
        F_decom = F_decom.groupby(['Phase','Technologies']).sum()
        f_decom_index = F_decom.index.names
        F_decom = F_decom.rename_axis(index={f_decom_index[0]:'Phases'},axis=1)
        

        index_names = ['Phases', 'Technologies']
    
        assets = F_new.merge(F_old, left_on=['Phases', 'Technologies'], right_index=True)\
                .merge(F_decom, left_on=['Phases', 'Technologies'], right_index=True).reset_index()
        # set Years and Technologies as categorical data and sort it
        assets['Phases'] = pd.Categorical(assets['Phases'], ['2015_2020']+self.sets['PHASE_UP_TO'])
        assets = assets[assets['Phases'].notna()]
        self.categorical_esmy(df=assets, col_name='Technologies', el_name='Technologies')
        assets.sort_values(by=['Phases', 'Technologies'], axis=0, ignore_index=True, inplace=True)
        assets.set_index(index_names, inplace=True)
        # put very small values as nan
        # threshold = 1e-2
        threshold = 0
        assets = assets.mask((assets < threshold), np.nan)
        assets.dropna(how='all',inplace=True)
        
        self.results['New_old_decom'] = assets
        return
    
    def get_F_decom(self):
        F_decom = self.get_elem('F_decom')
        f_decom_index = F_decom.index.names
        F_decom = F_decom.rename_axis(index={f_decom_index[0]:'Phases'},axis=1)
        self.results['F_decom'] = F_decom
        return
        
    
    def get_year_balance(self):
        """Get the year energy balance of each layer"""
        logging.info('Getting Year_balance')
        sto_tech_daily = self.sets['STORAGE_DAILY'].copy()
        # Layer of which we have limited interest
        # col_plot = ['AMMONIA','ELECTRICITY','GAS','H2','HEAT_HIGH_T',
        #         'HEAT_LOW_T_DECEN','HEAT_LOW_T_DHN','HVC','METHANOL',
        #         'MOB_FREIGHT_BOAT','MOB_FREIGHT_RAIL','MOB_FREIGHT_ROAD','MOB_PRIVATE',
        #         'MOB_PUBLIC']

        # EXTRACT RESULTS FROM OPTIMISATION MODEL
        if self.type_model == 'MO':
            end_uses = -self.from_agg_to_year(ts=self.get_elem('End_uses')) \
                .groupby(['Years', 'Layers']).sum()
        else:
            end_uses = -self.from_agg_to_year(ts=self.get_elem('End_uses')
                                                .reset_index().set_index(['Typical_days', 'Hours'])) \
                .groupby(['Years', 'Layers']).sum()

        end_uses = end_uses.reset_index()
        end_uses['Elements'] = 'END_USES'
        end_uses = end_uses.reset_index().pivot(index=['Years', 'Elements'], columns=['Layers'], values=['End_uses'])
        end_uses.columns = end_uses.columns.droplevel(level=0)

        # If not computed yet compute assets and resources
        if self.results['Assets'] is None:
            self.get_assets()
        if self.results['Resources'] is None:
            self.get_resources()

        # get previously computed results, year fluxes of resources and technologies
        f_year = (self.results['Assets']['F_year'].fillna(0)).reset_index() \
            .rename(columns={'Technologies': 'Elements'}).astype({'Elements': str})
        r_year = (self.results['Resources'].fillna(0)) \
            .reset_index().rename(columns={'Resources': 'Elements', 'Res': 'R_year'}).astype({'Elements': str})

        year_fluxes = pd.concat([r_year.set_index(['Years', 'Elements'])['R_year'],
                                 f_year.set_index(['Years', 'Elements'])['F_year']
                                 ], axis=0)

        # Get storage_charge_time and storage_discharge_time from input data
        # and compute maximum input and output power of the storage technology
        # create frames for concatenation (list of df to concat)
        self.to_pd(self.params['f_min'].getValues())
        lio = self.to_pd(self.params['layers_in_out'].getValues())
        sto_eff = self.to_pd(self.params['storage_eff_in'].getValues())
        sto_eff = sto_eff.mask(sto_eff > 0.001, 1)  # storage eff only used to know on which layer it has an impact
        all_eff = pd.concat([lio, sto_eff], axis=0)
        if self.type_model == 'MO':
            all_eff = all_eff.loc[~all_eff.index.get_level_values('index1').isin(sto_tech_daily),:]
        

        # layers_in_out_all = pd.concat([all_eff], axis=0, keys=self.sets['YEARS'])
        layers_in_out_all = all_eff
        layers_in_out_all.reset_index(inplace=True)
        layers_in_out_all=layers_in_out_all.pivot(index=['index0','index1'],columns='index2',values='Value')
        layers_in_out_all.index.set_names(year_fluxes.index.names, inplace=True)
        year_balance = layers_in_out_all.mul(year_fluxes, axis=0)
        # add eud
        year_balance = pd.concat([year_balance, end_uses], axis=0)

        # Set regions, elements and layers as categorical data for sorting
        year_balance = year_balance.reset_index()
        year_balance['Years'] = pd.Categorical(year_balance['Years'], self.sets['YEARS_WND'])
        year_balance = year_balance[year_balance['Years'].notna()]
        ordered_tech = list(self.sets['TECHNOLOGIES'])
        ordered_res = list(self.sets['RESOURCES'])
        ordered_list = ordered_tech.copy()
        ordered_list.extend(ordered_res)
        ordered_list.append('END_USES')
        year_balance['Elements'] = pd.Categorical(year_balance['Elements'], ordered_list)
        year_balance.sort_values(by=['Years', 'Elements'], axis=0, ignore_index=True, inplace=True)
        year_balance.set_index(['Years', 'Elements'], inplace=True)

        # put very small values as nan
        # threshold = 1e-1
        threshold = 0
        year_balance = year_balance.mask((year_balance.min(axis=1) > -threshold) & (year_balance.max(axis=1) < threshold),
                                         np.nan)
        # year_balance = year_balance[col_plot]
        # Store into results
        year_balance.replace(0, np.nan, inplace=True)
        self.results['Year_balance'] = year_balance
        return

    def categorical_esmy(self, df: pd.DataFrame, col_name: str, el_name: str):
        """Transform the column (col_name) of the dataframe (df) into categorical data of the type el_name
        df is modified by the function.

        Parameters
        __________
        df: pd.DataFrame()
        DataFrame to modify

        col_name: str
        Name of the column to transform into categorical data

        el_name: {'Layers', 'Elements', 'Technologies', 'Resources'}
        Type of element to consider. The order of the categorical data is taken from the input data.
        Layers are taken as the set LAYERS
        Elements are taken as the concatenation of the sets TECHNOLOGIES and RESOURCES
        Technologies are taken as the set TECHNOLOGIES
        Resources are taken as the set RESOURCES
        """
        if el_name == 'Layers':
            ordered_list = self.sets['LAYERS']
        elif el_name == 'Elements':
            ordered_tech = list(self.sets['TECHNOLOGIES'])
            ordered_res = list(self.sets['RESOURCES'])
            ordered_list = ordered_tech.copy()
            ordered_list.extend(ordered_res)
        elif el_name == 'Technologies':
            # if el_name is Technologies or Resources
            ordered_list = list(self.sets['TECHNOLOGIES'])
        else:
            # if el_name is Technologies or Resources
            ordered_list = list(self.sets['RESOURCES'])

        df[col_name] = pd.Categorical(df[col_name], ordered_list)
        return
    
    def from_agg_to_year(self, ts):
        """Converts time series on TDs or months to yearly time series

        Parameters
        ----------
        ts_mo: pandas.DataFrame
        Multiindex dataframe of hourly data for each hour of each TD or each month.
        The index should be of the form (TD_number, hour_of_the_day) or (period)
    

        """
        if self.type_model == 'MO':
            t_op = self.params['t_op'].getValues().toPandas()
            ts_yr = ts.copy()
            for c in ts.columns:
                ts_yr[c] = ts[c].mul(t_op['t_op'],level='Periods')

            return pd.DataFrame(ts_yr,dtype=float)
        else:
            t_h_td = self.sets['T_H_TD']
            t_h_td = pd.DataFrame(t_h_td,columns=['H_of_Y','H_of_D','TD_number'],dtype = float)

            td_h = t_h_td.loc[:, ['TD_number', 'H_of_D']]
            ts_yr = td_h.merge(ts, left_on=['TD_number', 'H_of_D'], right_index=True).sort_index()
            return ts_yr.drop(columns=['TD_number', 'H_of_D'])
