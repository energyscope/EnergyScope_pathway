import numpy as np
import pandas as pd
from pathlib import Path
from amplpy import AMPL, DataFrame
from esmc.postprocessing import amplpy2pd as a2p



class OptiProbl:
    """

    The OptiProbl class allows to set an optimization problem in ampl, solve it,
     and interface with it trough the amplpy API and some additionnal functions

    Parameters
    ----------
    mod_path : pathlib.Path
        Specifies the path of the .mod file defining the LP problem in ampl syntax
    data_path : list(pathlib.Path)
        List specifying the path of the different .dat files with the data of the LP problem
        in ampl syntax
    options : dict
        Dictionary of the different options for ampl and the cplex solver

    """

    def __init__(self, mod_path, data_path, options):
        # instantiate different attributes
        self.dir = Path()
        self.dir = mod_path.parent
        self.mod_path = mod_path
        self.data_path = data_path
        self.options = options
        self.ampl = self.set_ampl(mod_path, data_path, options)
        self.vars = list()
        self.params = list()
        self.sets = dict()
        self.t = float()
        self.outputs = dict()

        # get values of attributes
        self.get_vars()
        self.get_params()
        self.get_sets()
        return

    def run_ampl(self):
        """

               Run the LP optimization with AMPL and saves the running time in self.t

               """
        try:
            self.ampl.solve()
            self.ampl.eval('display solve_result;')
            self.ampl.eval('display _solve_elapsed_time;')
            self.t = self.ampl.getData('_solve_elapsed_time;').toList()[0]

        except Exception as e:
            print(e)
            raise

    def get_vars(self):
        """

        Get the name of the LP optimization problem's variables

        """
        self.vars = list()
        for name, values in self.ampl.getVariables():
            self.vars.append(name)

    def get_params(self):
        """

        Get the name of the LP optimization problem's parameters

               """
        self.params = list()
        for n, p in self.ampl.getParameters():
            self.params.append(n)

    def get_sets(self):
        """

               Function to sets of the LP optimization problem

                      """
        self.sets = dict()
        for name, obj in self.ampl.getSets():
            if len(obj.instances()) <= 1:
                self.sets[name] = obj.getValues().toList()
            else:
                self.sets[name] = self.get_subset(obj)

    def print_inputs(self, directory=None):
        """

        Prints the sets, parameters' names and variables' names of the LP optimization problem

        Parameters
        ----------
        directory : pathlib.Path
        Path of the directory where to save the inputs

        """
        # default directory
        if directory is None:
            directory = self.dir / 'inputs'
        # creating inputs dir
        directory.mkdir(parents=True, exist_ok=True)
        # printing inputs
        a2p.print_json(self.sets, directory / 'sets.json')
        a2p.print_json(self.params, directory / 'parameters.json')
        a2p.print_json(self.vars, directory / 'variables.json')

        return

    def get_outputs(self):
        """

               Function to extract the values of each variable after running the optimization problem

                      """
        # function to get the outputs of ampl under the form of a dict filled with one df for each variable
        amplpy_sol = self.ampl.getVariables()
        self.outputs = dict()
        for name, var in amplpy_sol:
            self.outputs[name] = self.to_pd(var.getValues())

    def print_outputs(self, directory=None):
        """

        Prints the outputs (dictionary of pd.DataFrame()) into the directory as one csv per DataFrame

        Parameters
        ----------
        directory : pathlib.Path
        Path of the directory where to save the dataframes

        """
        # default directory
        if directory is None:
            directory = self.dir / 'outputs'
        # creating outputs dir
        directory.mkdir(parents=True, exist_ok=True)
        # printing outputs
        for ix, (key, val) in enumerate(self.outputs.items()):
            val.to_csv(directory / (str(key) + '.csv'))
        return

    def read_outputs(self, directory=None):
        """

        Reads the outputs previously printed into csv files to recover a case study without running it again

        Parameters
        ----------
        directory : pathlib.Path
        Path of the directory where the outputs are saved

        """
        # default directory
        if directory is None:
            directory = self.dir / 'outputs'
        # read outputs
        self.outputs = dict()
        for v in self.vars:
            self.outputs[v] = pd.read_csv(directory / (v + '.csv'), index_col=0)

    def print_step1_out(self, step1_out_dir):  # TODO to be moved to temporal aggregation class

        # printing .out file
        outputs_step1 = self.outputs
        cm = outputs_step1['Cluster_matrix'].pivot(index='index0', columns='index1', values='Cluster_matrix.val')
        cm.index.name = None
        out = pd.DataFrame(cm.mul(np.arange(1, 366), axis=0).sum(axis=0)).astype(int)
        out.to_csv(step1_out_dir, header=False, index=False, sep='\t')
        return

    #############################
    #       STATIC METHODS      #
    #############################

    @staticmethod
    def set_ampl(mod_path, data_path, options):
        """

        Initialize the AMPL() object containing the LP problem

        Parameters
        ----------
         mod_path : pathlib.Path
        Specifies the path of the .mod file defining the LP problem in ampl syntax

        data_path : list(pathlib.Path)
        List specifying the path of the different .dat files with the data of the LP problem
        in ampl syntax

        options : dict
        Dictionary of the different options for ampl and the cplex solver

        Returns
        -------
        ampl object created

        """
        try:
            # Create an AMPL instance
            ampl = AMPL()
            # define solver
            ampl.setOption('solver', 'cplex')
            # set options
            for o in options:
                ampl.setOption(o, options[o])
            # Read the model and data files.
            ampl.read(mod_path)
            for d in data_path:
                ampl.readData(d)
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
                   amplpy_df : amplpy.DataFrame
                   amplpy dataframe to transform


                      Returns
                      -------
                      df : pandas.DataFrame
                      DataFrame transformed as 'long' dataframe (can be easily pivoted later)
                      """
        headers = amplpy_df.getHeaders()
        columns = {header: list(amplpy_df.getColumn(header)) for header in headers}
        df = pd.DataFrame(columns)
        return df