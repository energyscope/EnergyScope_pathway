#s!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  26 2022

@author: rixhonx
"""


print("General imports")
import numpy as np
from numpy import pi
import os,sys
from os import system

pylibPath = os.path.abspath("/home/ucl/tfl/coquelet/LoFiIPC/pylib")
sys.path.insert(0, pylibPath)
from DEL import *


if len(sys.argv) > 1:
    v   = 'v' + sys.argv[1]
    rundir =  sys.argv[2] + '/'

else:
    print('ERROR - You did not provide any argument. Please provide version and run_dir.')
    sys.exit(0)


batch_timesteps = 500

out_dir_test = '../out/test_{}/{}'.format(v,rundir)
nbatches = len(next(os.walk(out_dir_test))[1])
ntests   = 10
stats = np.zeros((ntests,3,nbatches))   

print('nbatches = {}, ntests = {}'.format(nbatches,ntests))

for batch in range(1,nbatches+1):

    for j in range(1,ntests+1):    

        out_dir_test_batch = out_dir_test + 'batch{}/test{}/'.format(batch,j)    
        
        print(out_dir_test_batch)       

        #---------------------- Compute mean return -----------------------------#
        
        Return  = np.loadtxt(out_dir_test_batch + 'return.txt')
        if Return.ndim == 1:
            Return = 0
        else:
            Return  = np.mean(Return[:,1])
        ep = batch * batch_timesteps

        #-------------------- Compute equivalent loads --------------------------#

        MFn     = np.loadtxt(out_dir_test_batch + 'MFn.txt')
        dt      = 0.2
        T_HPF   = 60/12.1
        nit_HPF = int(T_HPF/dt)
        t0      = 80
        tf      = 180
        ind0    = find_ind(MFn[:,0], t0)
        indf    = find_ind(MFn[:,0], tf)
        t       = MFn[ind0:indf,0]
        dt      = tf-t0
        M       = MFn[ind0:indf,1]
        
        bin_size   = 1E5
        bin_min    = 0E5
        bin_max    = 10E6
        cycles,Mrf = compute_rf_cycles(t,dt,M,bin_min,bin_max,bin_size)
        MFn_eq     = compute_Meq(Mrf,dt)

        #-------------------------- Store stats --------------------------------#

        stats[j-1,:,batch-1] = ep, Return, MFn_eq

stats = np.array([ stats[0,0,:],                              # number of steps
                   np.mean(  stats[:,1,:], axis = 0),         # mean of the mean return (over the steps & over the tests)
                   np.mean(  stats[:,2,:], axis = 0),         # mean DEL (over the tests) 
                   np.median(stats[:,1,:], axis = 0),         # median of the mean return 
                   np.median(stats[:,2,:], axis = 0),         # median DEL  
                   np.std(   stats[:,1,:], axis = 0),         # std of the mean return
                   np.std(   stats[:,2,:], axis = 0)   ])     # std of DEL 

np.savetxt(out_dir_test + 'stats.txt', np.transpose(stats), header = 'steps, mean of the mean episode return, mean of the damage equivalent MFn, median of the two and std of the two')
