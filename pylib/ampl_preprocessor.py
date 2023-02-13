#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 08 2022

@author: rixhonx
"""

from pathlib import Path

import os,sys
from copy import deepcopy
import re

pylibPath = os.path.abspath("../pylib")
if pylibPath not in sys.path:
    sys.path.insert(0, pylibPath)

class AmplPreProcessor:

    """

    The AmplPreProcessor class allows to update the files that depend on the 
    current window of optimisation 

    Parameters
    ----------
    ampl_obj : AmplObject object of ampl_object module
        Ampl object containing the optimisation problem and its attributes
    n_years_wnd : int
        Duration in years of the time windows. To avoid overshooting the end of the time horizon,
        the last window of optimisation might be shorter than n_years_wnd
    n_years_overlap : int
        Duration in years of the overlap between two windows of optimisation
    t_phase : int
        Duration in years of a phase

    """

    def __init__(self, ampl_obj, n_years_wnd = 10, n_years_overlap = 5, t_phase = 5):

        self.mod_path = ampl_obj.dir
        self.list_year = ampl_obj.sets['YEARS']
        self.list_phase = ampl_obj.sets['PHASE']
        self.without_2015(self)
        self.years_opti = list()
        self.phases_opti = list()
        self.years_up_to = list()
        self.phases_up_to = list()
        self.t_phase = t_phase
        self.n_years_wnd = n_years_wnd
        self.n_years_overlap = n_years_overlap
        self.year_to_rm = '' # Year to remove when saving the results

        self.pathway_window(self)

    '''
    Update the sets YEARS_WND, PHASE_WND, YEARS_UP_TO, PHASE_UP_TO,
    YEAR_ONE, YEAR_ONE_NEXT and write them down in the PES_seq_opti.dat file

    Parameters
    ----------
    i : Integer
        The number of time window currently optimised

    Outputs
    -------
    year_one : String
        The first year of the time window currently optimised
    '''
    def write_seq_opti(self, i):
        
        curr_years_wnd = self.years_opti[i]
        curr_phases_wnd = self.phases_opti[i]
        curr_years_up_to = self.years_up_to[i]
        curr_phases_up_to = self.phases_up_to[i]

        year_one = self.years_opti[i][0]

        if i > 0:
            self.year_to_rm = year_one

        if i == len(self.years_opti)-1:
            next_year_one = False
            year_one_next  = ''
        else:
            next_year_one = True
            year_one_next = self.years_opti[i+1][0]

        with open(os.path.join(self.mod_path,'PES_seq_opti.dat'),'w+', encoding='utf-8') as f:
            f.write('set YEARS_WND := ' )
            for year in curr_years_wnd:
                f.write('%s ' %year)
            f.write('; \n')
            f.write('set PHASE_WND := ')
            for phase in curr_phases_wnd:
                f.write('%s ' %phase)
            f.write('; \n')
            f.write('set YEARS_UP_TO := ')
            for year in curr_years_up_to:
                f.write('%s ' %year)
            f.write('; \n')
            f.write('set PHASE_UP_TO := ')
            for phase in curr_phases_up_to:
                f.write('%s ' %phase)
            f.write(';\n')
            
            f.write('set YEAR_ONE')
            if i>0 :
                f.write(':= %s' %year_one)
            f.write(';\n')
            
            f.write('set YEAR_ONE_NEXT')
            if next_year_one:
                f.write(':= %s' %year_one_next)
            f.write(';')

        return curr_years_wnd


    '''
    Update the remaining years of lifetime of each technology from 2015 to the end of the
    time window currently optimised

    Parameters
    ----------
    i : Integer
        The number of time window currently optimised
    file_in : String
        Name of the original file where remaining years of lifetime are computed from 2015 to 2050
    file_out : String
        Name of the file where remaining years of lifetime are computed from 2015 to the end of 
        the time window currently optimised
    '''
    def remaining_update(self,i,file_in = 'PES_data_remaining.dat', file_out = 'PES_data_remaining_wnd.dat'):
        
        curr_phases_up_to = ['2015_2020'] + self.phases_up_to[i]
        curr_phases_wnd = self.phases_opti[i]
        phase_list = deepcopy(curr_phases_up_to)
        n_year_overlap = self.n_years_overlap
        pth_model = self.mod_path

        last_phase = self.list_phase[-1]

        pth_file = os.path.join(pth_model,file_in)

        if n_year_overlap > 0 and curr_phases_wnd[-1] != last_phase:
            n_phase_extra = int(n_year_overlap/5)
            phase_list += curr_phases_wnd[-n_phase_extra:]
        n_phase = len(phase_list)
        with open(pth_file,encoding='utf-8') as fp:
            next(fp)
            l = fp.readlines()
            n = len(re.split(r'\t+', l[0].rstrip('\t')))
        with open(os.path.join(pth_model,file_out),'w+', encoding='utf-8') as f:
            f.write('param remaining_years : ' )
            for phase in phase_list:
                f.write('%s ' %phase)
            f.write(':= \n')
            with open(pth_file,encoding='utf-8') as fp:
                next(fp)
                for line in fp:
                    list_line = re.split(r'\t+', line.rstrip('\t'))
                    if len(list_line) < n:
                        break
                    else:
                        f.write(list_line[0]+'\t')
                        for i in range(len(list_line)-n_phase-1,len(list_line)-1):
                            f.write(list_line[i]+'\t')
                        f.write('\n')
            f.write('; \n')
    
    
    

    @staticmethod
    def pathway_window(self):
        '''
        Function to split the sets YEARS and PHASE into the different sub-sets depending on the 
        number of years of the time windows and the number of overlapping years between each time window
        '''
        years_opti = [[] for i in range(len(self.list_year))]
        phases_opti = [[] for i in range(len(self.list_phase))]

        years_window = self.n_years_wnd
        years_overlap = self.n_years_overlap

        if years_window % 5 != 0:
            raise ValueError('Error : the number of years in the window of optimisation is not correct.\nIt should be a multiple of 5')
        elif years_window > 30 or years_window <= 0:
            raise ValueError('Error : the number of years in the window of optimisation is not correct.\nIt cannot be smaller than 0 or greater than 30')
        elif years_window < self.t_phase:
            raise ValueError('Error : the number of years in the window of optimisation is not correct.\nIt must be bigger or equal to the number of years within a phase')
        elif years_window <= years_overlap:
            raise ValueError('Error : the overlap is too long.\nIt must be smaller than the window of optimisation')
        if years_overlap % 5 != 0:
            raise ValueError('Error : the number of years of overlap is not correct.\nIt should be a multiple of 5')
        
        n_phase_window = int(years_window/self.t_phase)
        n_year_window = int(years_window/self.t_phase)
        n_phase_overlap = int(years_overlap/self.t_phase)
        n_year_overlap = int(years_overlap/self.t_phase)

        for i in range(len(years_opti)):
            years_opti[i] = self.list_year[i*(n_year_window)-i*(n_year_overlap):(n_year_window+1)*(i+1)-i*(n_year_overlap+1)]
            if (n_year_window+1)*(i+1)-i*(n_year_overlap+1) >= len(self.list_year):
                break

        for i in range(len(phases_opti)):
            phases_opti[i] = self.list_phase[i*(n_phase_window)-i*(n_phase_overlap):(n_phase_window)*(i+1)-i*(n_phase_overlap)]
            if (n_phase_window)*(i+1)-i*(n_phase_overlap) >= len(self.list_phase):
                break

        years_opti = [ele for ele in years_opti if ele != []]
        phases_opti = [ele for ele in phases_opti if ele != []]
        
        years_up_to = [[] for i in range(len(years_opti))]
        phases_up_to = [[] for i in range(len(phases_opti))]
        
        for i in range(len(years_up_to)-1):
            years_up_to[i] = self.list_year[0:(n_year_window+1)*(i+1)-i*(n_year_overlap+1)-n_year_overlap]
        years_up_to[-1] = self.list_year
        
        for i in range(len(phases_up_to)-1):
            phases_up_to[i] = self.list_phase[0:(n_phase_window)*(i+1)-i*(n_phase_overlap)-n_phase_overlap]
        phases_up_to[-1] = self.list_phase

        self.years_opti = years_opti
        self.phases_opti = phases_opti
        self.years_up_to = years_up_to
        self.phases_up_to = phases_up_to

    @staticmethod
    def without_2015(self):
        self.list_year.remove('YEAR_2015')
        self.list_phase.remove('2015_2020')
