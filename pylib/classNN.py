#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 12:13:20 2020
@author: ransquin

Add ons Tue Dec  1: coquelet

Class that can store a policy as a neural network, to apply it from scratch from somwhere.
"""

import numpy as np        
import pickle

class NeuralNetwork:
    
    def __init__(self,myModelFile):
        '''
        
        Parameters
        ----------
        myModelFile : str
            path to the file in which the dictionnary containing the model is stored

        Returns
        -------
        None.

        '''
        
        def tanh(x): return np.tanh(x)
        def relu(x): return np.maximum(0,x)
        
        file  = open(myModelFile, 'rb')
        model = pickle.load(file)
        
        self.std_epsilon  = 1E-12
        
        self.numHiddenL   = model['numHiddenL']
        self.numIn        = model['numIn']
        self.numOut       = model['numOut']
        
        self.allActivFun  = {'tanh':tanh,'relu':relu}
        activFun          = model['activFun']
        self.activFun     = self.allActivFun[activFun]
        self.layers       = model['layers']
        self.normLayers   = model['normLayers']
        self.layerNorm    = model['layerNorm']
        self.actSpaceHigh = model['actSpaceHigh']
        

    def computeNN(self,inputs):
        '''
        Function computing the output of the neural network model built in __init__

        Parameters
        ----------
        inputs : array-like
            inputs to the neural network, size of the NN first layer

        Returns
        -------
        output : array-like
            outputs on the neural network, size of the NN last layer

        '''
        
        if len(self.layers[0][0]) != len(inputs):
            print('ERROR ! inputs should have size {}'.format(len(self.layers[0][0])))
            return False
        
        output = inputs
                
        #------------------------- Hidden Layers ----------------------------#
        for i in range(0,self.numHiddenL):
            W = self.layers[i][0]   # weights
            b = self.layers[i][1]   # bias                
            
            output  = np.dot(output,W) + b
            
            if self.layerNorm:
                
                beta   = self.normLayers[i][0]    # offset
                gamma  = self.normLayers[i][1]    # scale
                
                mean   = np.mean(output)
                std    = np.std( output)
                
                output = gamma * (output - mean)/(std + self.std_epsilon) + beta
                
            output  = self.activFun(output)
        
        #------------------------- Output Layer -----------------------------#
        W = self.layers[-1][0]               # weights
        b = self.layers[-1][1]               # bias                
        output  = np.dot(output,W) + b
        output  = np.tanh(output)            # Alway tanh for the last layer. If ReLU, no output could be < 0
            
        output  = output*self.actSpaceHigh    # scaling
        output = output.astype(np.float32)
        
        return output
    
