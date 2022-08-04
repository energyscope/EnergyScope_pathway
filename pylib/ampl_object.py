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

    def __init__(self, mod_1_path, mod_2_path, data_path, options, ampl_path=None):

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
            self.t = self.ampl.getData('_solve_elapsed_time;').toList()[0]

        except Exception as e:
            print(e)
            raise
    
    """

    Function to of the LP optimization problem

    """
    def get_sets(self):
        
        for name, obj in self.ampl.getSets():
            if len(obj.instances()) <= 1:
                self.sets[name] = obj.getValues().toList()
            else:
                self.sets[name] = self.get_subset(obj)

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
    

    """"

    Collect the relevant outputs to store 

    """
    def get_outputs(self):

        store_list = self.sets['STORE_RESULTS']

        for k in store_list:
            self.outputs[k] = self.to_pd(self.ampl.getVariable(k).getValues())
    

    def clean_history(self):
        open(os.path.join(self.dir,'fix.mod'), 'w').close()
        open(os.path.join(self.dir,'PESTD_data_remaining_wnd.dat'), 'w').close()
        open(os.path.join(self.dir,'seq_opti.dat'), 'w').close()


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
    
    def get_action(self,action):
        action = action.astype('float64')
        allow_foss = action[0]
        sub_renew = action[1]

        curr_year_wnd = self.sets['YEARS_WND']
        re_tech = self.sets['RE_TECH']

        lst_tpl_re_tech = [(y,t) for y in curr_year_wnd for t in re_tech]
        
        for i in lst_tpl_re_tech:
            new_value = self.params['c_inv'][i]*sub_renew
            self.set_params('c_inv',{i:new_value})
        
        self.set_params('allow_foss',allow_foss)


    
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

    # @staticmethod
    # def to_pd_pivot(amplpy_df):
    #     """
    #     Function to transform an amplpy.DataFrame into pandas.DataFrame for easier manipulation

    #     Parameters
    #     ----------
    #     amplpy_df : amplpy.DataFrame
    #     amplpy dataframe to transform


    #     Returns
    #     -------
    #     df : pandas.DataFrame
    #     DataFrame transformed as 'long' dataframe (can be easily pivoted later)
    #     """
    
    #     nindices = amplpy_df.getNumIndices()
    #     headers = amplpy_df.getHeaders()
    #     columns = {header: list(amplpy_df.getColumn(header)) for header in headers}
    #     df = pd.DataFrame(columns)
    #     if nindices==1:
    #         df = df.set_index(headers[0])
    #         df.index.name = None # get rid of the name of the index (multilevel)
    #     elif nindices==2:
    #         df = df.pivot(index=headers[0], columns=headers[1], values=headers[2])
    #         df.index.name = None # get rid of the name of the index (multilevel)
    #     elif nindices==3:
    #         dic = dict()
    #         for i in set(columns[headers[0]]):
    #             dic[i] = df[df[headers[0]]==i].pivot(index=headers[2], columns=headers[1], values=headers[3])
    #             dic[i].index.name = None # to get rid of name (multilevel)
    #         df = dic
    #     elif nindices==4:
    #         dic = dict()
    #         for i in set(columns[headers[0]]):
    #             dic[i] = dict()
    #             for j in set(columns[headers[3]]):
    #                 dic[i][int(j)] = df.loc[(df[headers[0]]==i) & (df[headers[3]]==j),:].pivot(index=headers[2], columns=headers[1], values=headers[4])
    #                 dic[i][int(j)].index.name = None # to get rid of name (multilevel)
    #         df = dic
        
    #     return df