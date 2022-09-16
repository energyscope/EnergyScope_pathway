#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  1 19:13:20 2020
@author: coquelet
"""

import numpy as np        
import pickle


def SaveNeuralNetwork(model,myModelFile):
    '''
    Function converting the NN model saved by stable baselines 
    to one where only the information necessary for recomputing the output is saved
    Necessary information is saved in a dictionnary
    Goal: become totally independant from stable baselines/tensorflow

    Parameters
    ----------
    model : structure
        model used by stablebaselines
    myModelFile : str
        path to the file in which the dictionnary will be stored

    Returns
    -------
    None.

    '''
    
    numHiddenL   = len(model.policy_kwargs['layers'])
    numIn        = len(model.observation_space.high)
    numOut       = len(model.action_space.high)
    actSpaceHigh = model.action_space.high
    
    allActivFun  = ['tanh', 'sigmoid' ,'softplus','relu']
    activFun     = '0'
    for act in allActivFun:
        if act in str(model.policy_kwargs['act_fun']):
            activFun = act
    if activFun == '0':
        print('ERROR ! activFun should be tanh, sigmoid, softplus or relu')
        return 0

    params       = model.get_parameters()
    keys         = [ k for k,_ in params.items() if 'model/pi' in k]
    keys         = keys[:-2]
    
    if int(len(keys)/2) > numHiddenL:
        layerNorm  = True
        layers     = [ [params[keys[4*i]], params[keys[4*i+1]]] for i in range(numHiddenL+1)]
        normLayers = [ [params[keys[4*i+2]], params[keys[4*i+3]]] for i in range(numHiddenL)]
    else:
        layerNorm  = False
        layers     = [ [params[keys[2*i]], params[keys[2*i+1]]] for i in range(numHiddenL+1)]
        normLayers = []
        
    myModelDict = {'numHiddenL'   : numHiddenL,
                   'numIn'        : numIn,
                   'numOut'       : numOut,
                   'activFun'     : activFun,
                   'actSpaceHigh' : actSpaceHigh,
                   'layerNorm'    : layerNorm,
                   'layers'       : layers,
                   'normLayers'   : normLayers
                   }
        
    # Saving the dictionnary to file
    file = open(myModelFile, 'wb')
    pickle.dump(myModelDict,file)

    return 1