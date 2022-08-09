import numpy as  np
from numpy import pi
import random

from pathlib import Path

import os,sys

import functools
print = functools.partial(print, flush=True)

import gym
from gym import spaces

curr_dir = Path(os.path.dirname(__file__))

pylibPath = os.path.join(curr_dir.parent.parent.parent,'pylib')    # WARNING ! pwd is where the MAIN file was launched !!!

if pylibPath not in sys.path:
    sys.path.insert(0, pylibPath)

from ampl_object import AmplObject
from ampl_preprocessor import AmplPreProcessor
from ampl_collector import AmplCollector

import logging

logger = logging.getLogger(__name__)

class EsmyMoV0(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self,**kwargs):
        print("Initializing the EsmyMoV0", flush=True)

        out_dir = kwargs['out_dir']
 
        print('\nAll the output data will be stored in {}'.format(out_dir))


        #--------------------- Initialization ---------------------#
        self.it = 0
        self.cum_gwp_init = 0.0
        self.cum_gwp = self.cum_gwp_init
        self.target_2050 = 3406.92
        self.n_year_opti = 10
        self.n_year_overlap = 5

        self.type_of_model = 'MO'

        self.pth_esmy = os.path.join(Path(pylibPath).parent,'ESMY')

        self.pth_model = os.path.join(self.pth_esmy,'STEP_2_Pathway_Model')

        if self.type_of_model == 'MO':
            self.mod_1_path = [os.path.join(self.pth_model,'PESMO_model.mod'),
                        os.path.join(self.pth_model,'PESMO_store_variables.mod'),
                        os.path.join(self.pth_model,'PESMO_RL.mod'),
                        os.path.join(self.pth_model,'PES_store_variables.mod')]
            self.mod_2_path = [os.path.join(self.pth_model,'PESMO_initialise_2020.mod'),
                        os.path.join(self.pth_model,'fix.mod')]
            self.dat_path = [os.path.join(self.pth_model,'PESMO_data_all_years.dat')]
        else:
            self.mod_1_path = [os.path.join(self.pth_model,'PESTD_model.mod'),
                    os.path.join(self.pth_model,'PESTD_store_variables.mod'),
                    os.path.join(self.pth_model,'PESTD_RL.mod'),
                    os.path.join(self.pth_model,'PES_store_variables.mod')]
            self.mod_2_path = [os.path.join(self.pth_model,'PESTD_initialise_2020.mod'),
                    os.path.join(self.pth_model,'fix.mod')]
            self.dat_path = [os.path.join(self.pth_model,'PESTD_data_all_years.dat'),
                        os.path.join(self.pth_model,'PESTD_12TD.dat')]

        self.dat_path += [os.path.join(self.pth_model,'PES_data_all_years.dat'),
             os.path.join(self.pth_model,'PES_seq_opti.dat'),
             os.path.join(self.pth_model,'PES_data_year_related.dat'),
             os.path.join(self.pth_model,'PES_data_efficiencies.dat'),
             os.path.join(self.pth_model,'PES_data_set_AGE_2020.dat'),
             os.path.join(self.pth_model,'PES_data_remaining_wnd.dat'),
             os.path.join(self.pth_model,'PES_data_decom_allowed_2020.dat')]
        
        ## Options for ampl and gurobi
        self.gurobi_options = ['predual=-1',
                        'method = 2', # 2 is for barrier method
                        'crossover=0',
                        'prepasses = 3',
                        'barconvtol=1e-6',                
                        'presolve=-1'] # Not a good idea to put it to 0 if the model is too big

        self.gurobi_options_str = ' '.join(self.gurobi_options)

        self.ampl_options = {'show_stats': 1,
                        'log_file': os.path.join(self.pth_model,'log.txt'),
                        'presolve': 10,
                        'presolve_eps': 1e-7,
                        'presolve_fixeps': 1e-7,
                        'show_boundtol': 0,
                        'gurobi_options': self.gurobi_options_str,
                        '_log_input_only': False}

        #---------------------- Observation space --------------------#
        self.min_gwp = 0
        self.max_gwp = 1e10

        obslow = np.array([self.min_gwp])
        obshigh = np.array([self.max_gwp])

        self.obslow = obslow
        self.obshigh = obshigh

        self.observation_space = spaces.Box(low=self.obslow, high=self.obshigh, dtype=np.float32)

        #----------------------- Action space ----------------------#
        self.max_allow_fossil_norm = 1.0
        self.min_allow_fossil_norm = -1.0
        self.max_allow_fossil_scal = 1.0
        self.min_allow_fossil_scal = 0.0


        self.max_sub_renew_norm = 1.0
        self.min_sub_renew_norm = -1.0
        self.max_sub_renew_scal = 0.5
        self.min_sub_renew_scal = 0.0

        actlow = np.array([self.min_allow_fossil_norm, self.min_sub_renew_norm])
        acthigh = np.array([self.max_allow_fossil_norm, self.max_sub_renew_norm])

        self.actlow = actlow
        self.acthigh  = acthigh

        print('actlow  = {}'.format(actlow))
        print('acthigh = {}'.format(acthigh))


        self.action_space = spaces.Box(low=self.actlow, high=self.acthigh, dtype=np.float32)

        #--------------------- Initializing objects ----------------#
        self.ampl_obj_0 = AmplObject(self.mod_1_path, self.mod_2_path, self.dat_path, self.ampl_options)
        self.ampl_obj_0.clean_history()
        self.ampl_pre = AmplPreProcessor(self.ampl_obj_0, self.n_year_opti, self.n_year_overlap)
        # self.ampl_collector = AmplCollector(self.ampl_obj_0, output_file, expl_text)

        # Maximum of phases to accomplish the transition
        self.max_it = len(self.ampl_pre.years_opti)

        self.gwp_per_year = dict.fromkeys(self.ampl_obj_0.sets['YEARS'],0.0)


        self.file_rew  = open('{}/reward.txt'.format(out_dir), 'w')
        self.file_ret  = open('{}/return.txt'.format(out_dir), 'w')
        self.file_observation = open('{}/observation.txt'.format(out_dir),'w')


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

        self.ampl_pre.remaining_update(self.it)
        self.curr_years_wnd, self.year_to_rm = self.ampl_pre.write_seq_opti(self.it)

        self.ampl_obj = AmplObject(self.mod_1_path, self.mod_2_path, self.dat_path, self.ampl_options)

        # 1) Take action
        print(' ')
        print('in step - action = {}'.format(action))
        print(' ')

        self._take_action( action )
        
        if self.it > 0:
            self.curr_years_wnd.remove(self.year_to_rm)

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
        self.ampl_obj.set_init_sol()

        print('\n--------------------------------------------------------------------')
        print('---------------------- DONE WITH THIS ITERATION  --------------------')
        print('--------------------------------------------------------------------\n\n')

        return observation, reward, episode_over, info
    
    # Reset function to initialize the environment at the beginning of each episode
    # To add stochasticity, the End-Use-Demand to satisfy at each episode can vary by +/- 10%
    def reset(self):
        print("RESET THE PROBLEM")
        self.it = 0
        self.file_ret.write('{}\n'.format(self.it))
        self.file_ret.flush()
        self.cum_gwp = self.cum_gwp_init
        self.ampl_obj_0.clean_history()
        self.gwp_per_year = dict.fromkeys(self.ampl_obj_0.sets['YEARS'],0.0)
        self.ampl_obj = AmplObject(self.mod_1_path, self.mod_2_path, self.dat_path, self.ampl_options)
        self.ampl_pre = AmplPreProcessor(self.ampl_obj, self.n_year_opti, self.n_year_overlap)

        return np.array([self.cum_gwp], dtype=np.float32)

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
        gwp_dict = self.ampl_obj.collect_gwp(self.curr_years_wnd)

        for y in self.curr_years_wnd:
            self.gwp_per_year[y] = gwp_dict[y]
        
        t_phase = self.ampl_obj.params['t_phase'].value()
        self.cum_gwp = self.gwp_per_year['YEAR_2020'] * (1+t_phase/2)

        years_up_to = self.ampl_obj.sets['YEARS_UP_TO']
        year_n = years_up_to.pop()
        for i, y in enumerate(years_up_to):
            self.cum_gwp += self.gwp_per_year[y] * t_phase
        
        self.cum_gwp += self.gwp_per_year[year_n] * t_phase/2

        self.file_observation.write('{:.1f} {:.1f} '.format(self.it,self.cum_gwp))
        for k in self.gwp_per_year:
            self.file_observation.write('{:.1f} '.format(self.gwp_per_year[k]))
        self.file_observation.write('\n')
        self.file_observation.flush()

        return np.array([self.cum_gwp], dtype=np.float32)
    
    # Returns the reward depending on the state the agent ends up in, after taking the action
    def _get_reward(self):

        if self.it < self.max_it - 1:
            reward = 0.0
            done = 0
        else :
            if self.gwp_per_year['YEAR_2050'] > self.target_2050:
                # reward = -self.cum_gwp
                reward = -10
            else:
                # reward = self.target_2050 - self.gwp_per_year['YEAR_2050']
                reward = 10
            done = 1
            # reward = -self.cum_gwp
            # done = 1

        self.file_rew.write('{:.2f} {:.6f}\n'.format(self.it,reward))
        self.file_rew.flush()

        return reward, done


    def _take_action(self,action):

        err_msg = "%r (%s) invalid" % (action, type(action))
        assert self.action_space.contains(action), err_msg

        print('\n------------------------ A C T I O N S -----------------------')

        self.max_allow_fossil_norm = 1.0
        self.min_allow_fossil_norm = -1.0
        self.max_allow_fossil_scal = 1.0
        self.min_allow_fossil_scal = 0.0


        self.max_sub_renew_norm = 1.0
        self.min_sub_renew_norm = -1.0
        self.max_sub_renew_scal = 0.5
        self.min_sub_renew_scal = 0.0

        action[0] = (action[0] - self.min_allow_fossil_norm)/(self.max_allow_fossil_norm - self.min_allow_fossil_norm)*(self.max_allow_fossil_scal-self.min_allow_fossil_scal)+self.min_allow_fossil_scal
        action[1] = (action[1] - self.min_sub_renew_norm)/(self.max_sub_renew_norm - self.min_sub_renew_norm)*(self.max_sub_renew_scal-self.min_sub_renew_scal)+self.min_sub_renew_scal
        self.ampl_obj.get_action(action)
        
        self.ampl_obj.run_ampl()

        self.ampl_obj.get_outputs()