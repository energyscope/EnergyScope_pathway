import numpy as  np
from numpy import pi
import random

import os,sys

import functools
print = functools.partial(print, flush=True)

import gym
from gym import error, spaces, utils
from gym.utils import seeding

# pylibPath = os.path.abspath("../pylib")    # WARNING ! pwd is where the MAIN file was launched !!!
# if pylibPath not in sys.path:
#     sys.path.insert(0, pylibPath)

import logging

logger = logging.getLogger(__name__)

class EsmyTdV0(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self,**kwargs):
        print("Initializing the MECA2675EnvV0", flush=True)

        out_dir = kwargs['out_dir']
 
        print('\nAll the output data will be stored in {}'.format(out_dir) )


        #--------------------- Initialization ---------------------#

        # Fossil initiatilization
        self.fossil = 100 # Installed capacity of fossil-based production plant
        self.eff_fossil = 0.65 # Efficiency of fossil-based production plant
        self.EUD_foss = self.eff_fossil * self.fossil # Production by fossil-based plant
        self.cp_foss = 1 # Load factor of fossil-based plant

        # PV initialization
        self.PV_init = 0 # Installed capacity of PV
        self.PV = self.PV_init
        self.eff_PV = 1 # Efficiency of PV
        self.EUD_PV = self.eff_PV * self.PV_init # Production by PV
        self.cp_PV_init = 0.2 # Load factor of PV
        self.cp_PV = self.cp_PV_init

        # Storage initialization
        self.sto_init = 0 # Storage capacity
        self.sto = self.sto_init
        
        # Total demand to supply
        self.EUD_init = self.EUD_foss * self.cp_foss + self.EUD_PV * self.cp_PV_init
        self.EUD = self.EUD_init

        # Maximum of years to accomplish the transition
        self.max_it = 50

        #---------------------- Observation space --------------------#

        self.max_PV = 300 # Maximum installed capacity of PV
        self.min_PV = 0 # Minimum installed capacity of PV
        self.max_sto = 150 # Maximum installed capacity of storage
        self.min_sto = 0 # Minimum installed capacity of storage

        obshigh = np.array([self.max_PV, self.max_sto])
        obslow = np.array([self.min_PV, self.min_sto])

        self.obshigh = obshigh
        self.obslow  = obslow

        print('obslow  = {}'.format(obslow) )
        print('obshigh = {}'.format(obshigh) )

        self.observation_space = spaces.Box(low=obslow, high=obshigh, dtype=np.int32)

        #----------------------- Action space ----------------------#

        self.max_inc_PV = 10
        self.max_inc_sto = 10
        self.min_inc_PV = 0
        self.min_inc_sto = 0

        acthigh = np.array([self.max_inc_PV, self.max_inc_sto])
        actlow = np.array([self.min_inc_PV, self.min_inc_sto])

        self.action_space = spaces.Discrete(3)

        self.it = 0
        self.file_rew  = open('{}reward.txt'.format(out_dir), 'w')
        self.file_ret  = open('{}return.txt'.format(out_dir), 'w')
        self.file_observation = open('{}observation.txt'.format(out_dir),'w')


#------------------------------------------------------------------------------#
#                               PUBLIC FUNCTIONS                               #
#------------------------------------------------------------------------------#


    def step(self,action):
        """
        First, you take the action (--> control the system)
        Then, you see what system you end up in (--> get the observation)
        Finally, given the system you're in, you can see how good you are (--> compute the reward)
        """

        print('\n\n--------------------------------------------------------------------' )
        print('------------------------ STARTING ITERATION {} -----------------------'.format(self.it))
        print('--------------------------------------------------------------------\n')

        # 1) Take action
        print(' ')
        print('in step - action = {}'.format(action))
        print(' ')

        self._take_action( action )

        # 2) Observed what happened
        observation = self._get_observation()

        obs = np.c_[self.obslow, observation, self.obshigh]

        print(' ')
        print('in step')
        print('obs_low           obs       obs_high')
        print(obs)
        print(' ')
        
        # 3) Critique what happened
        reward, done = self._get_reward()

        print(' ')
        print('in step - reward = {}'.format(reward))
        print(' ')

        # 4) Tell if it's over
        episode_over = True if done == 1 else False

        # 5) Give more info if needed
        info = {}

        self.it += 1

        print('\n--------------------------------------------------------------------')
        print('---------------------- DONE WITH THIS ITERATION  --------------------')
        print('--------------------------------------------------------------------\n\n')

        return observation, reward, episode_over, info
    
    # Reset function to initialize the environment at the beginning of each episode
    # To add stochasticity, the End-Use-Demand to satisfy at each episode can vary by +/- 10%
    def reset(self):
        print("RESET THE PROBLEM")
        self.file_ret.write('{}\n'.format(self.it))
        self.file_ret.flush()
        self.PV = self.PV_init
        self.sto = self.sto_init
        self.cp_PV = self.cp_PV_init
        self.it = 0
        self.EUD = self.EUD_init*(1+random.uniform(-0.1,0.1))

        return self.PV, self.sto

    # Function not necessary as the visualisation of the results is done in the Jupyter Notebook
    def render(self, mode='human'):
        """ Not necessary so far """
        print("in render")

    def close(self):
        """ Not really necessary """
        print("in close")

#------------------------------------------------------------------------------#
#                              PRIVATE FUNCTIONS                               #
#------------------------------------------------------------------------------#

    # Besides writing information in output file, returns the state in which the agent is. This state consists of the amounts of PV and storage capacity
    def _get_observation(self):
        
        self.file_observation.write('{:.2f} {:.1f} {:.1f} {:.1f} {:.2f} {:.1f} \n'.format(self.it,self.PV,self.sto,self.EUD, self.cp_PV, self.eff_PV))
        self.file_observation.flush()

        return np.array([self.PV, self.sto])
    
    # Returns the reward depending on the state the agent ends up in, after taking the action
    def _get_reward(self):

        if self.PV > self.max_PV or self.sto > self.max_sto:
            reward = -10
            done = 1
        elif self.eff_PV * self.PV * self.cp_PV >= self.EUD :
            reward = +10
            done = 1
        else :
            reward = min(1,1/(self.EUD - self.eff_PV * self.PV * self.cp_PV))
            done = 0

        self.file_rew.write('{:.2f} {:.6f}\n'.format(self.it,reward))
        self.file_rew.flush()

        return reward, done

    
    # Three different actions can be taken:
    # 0: Increase by 10 the amount of PV
    # 1: Incrase by 5 the amount of PV and the amount of storage
    # 2: Increase by 10 the amount of storage
    def _take_action(self,action):

        err_msg = "%r (%s) invalid" % (action, type(action))
        assert self.action_space.contains(action), err_msg

        print('\n------------------------ A C T I O N S -----------------------')

        PV = self.PV
        sto = self.sto

        if action == 0:
            PV_inc = self.max_inc_PV
            sto_inc = 0
        elif action == 1:
            PV_inc = int(self.max_inc_PV/2)
            sto_inc = int(self.max_inc_sto/2)
        else:
            PV_inc = 0
            sto_inc = self.max_inc_sto
        
        PV = PV + PV_inc
        sto = sto + sto_inc
        cp_PV = self.cp_PV_init * (1+sto/50)

        self.PV = PV
        self.sto = sto
        self.cp_PV = cp_PV