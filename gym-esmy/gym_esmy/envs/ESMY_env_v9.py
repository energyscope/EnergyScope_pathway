import numpy as  np
from copy import deepcopy

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
from ampl_uq import AmplUQ
from rheia.CASES.determine_stoch_des_space import StochasticDesignSpace
import rheia.UQ.pce as uq

import logging

logger = logging.getLogger(__name__)

class EsmyV9(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self,**kwargs):
        print("Initializing the EsmyV9", flush=True)

        out_dir = kwargs['out_dir']
        self.v = kwargs['v']
 
        print('\nAll the output data will be stored in {}'.format(out_dir))


        #--------------------- Initialization ---------------------#
        self.solve_result = "?"
        self.it = 0
        self.cum_gwp_init = 0.0
        self.cum_gwp = self.cum_gwp_init
        self.cum_cost_init = 0.0
        self.cum_cost = self.cum_cost_init
        self.RE_in_mix_init = 0.0
        self.RE_installed = self.RE_in_mix_init
        self.Energy_efficiency_init = 0.0
        self.Energy_efficiency = self.Energy_efficiency_init

        self.target_2050 = 3406.92
        self.target_2035 = 86445
        self.n_year_opti = 10
        self.n_year_overlap = 5

        self.skip = 123454 # For sample generation

        if 'type_of_model' in kwargs:
            self.type_of_model = kwargs['type_of_model']
        else:
            self.type_of_model = 'MO'
        
        if 'nb_done' in kwargs:
            self.nb_done = kwargs['nb_done']
        else:
            self.nb_done = 0


        self.pth_esmy = os.path.join(Path(pylibPath).parent,'ESMY')

        self.pth_model = os.path.join(self.pth_esmy,'STEP_2_Pathway_Model')

        if self.type_of_model == 'MO':
            self.mod_1_path = [os.path.join(self.pth_model,'PESMO_model.mod'),
                        os.path.join(self.pth_model,'PESMO_store_variables.mod'),
                        os.path.join(self.pth_model,'PESMO_RL','PESMO_RL_v{}.mod'.format(self.v)),
                        os.path.join(self.pth_model,'PES_store_variables.mod')]
            self.mod_2_path = [os.path.join(self.pth_model,'PESMO_initialise_2020.mod'),
                        os.path.join(self.pth_model,'fix.mod')]
            self.dat_path = [os.path.join(self.pth_model,'PESMO_data_all_years.dat')]
        else:
            self.mod_1_path = [os.path.join(self.pth_model,'PESTD_model.mod'),
                    os.path.join(self.pth_model,'PESTD_store_variables.mod'),
                    os.path.join(self.pth_model,'PESTD_RL','PESTD_RL_v{}.mod'.format(self.v)),
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
                        'presolve_eps': 1e-6,
                        'presolve_fixeps': 1e-6,
                        'show_boundtol': 0,
                        'gurobi_options': self.gurobi_options_str,
                        '_log_input_only': False}
        

        #--------------------- Initializing objects ----------------#
        self.ampl_obj_0 = AmplObject(self.mod_1_path, self.mod_2_path, self.dat_path, self.ampl_options, type_model = self.type_of_model)
        self.ampl_obj_0.clean_history()
        self.ampl_pre = AmplPreProcessor(self.ampl_obj_0, self.n_year_opti, self.n_year_overlap)


        # self.carbon_budget = 1756703.8 #Linear decrease between 106600kt_CO2_eq in 2020 (from EC Trends towards 2050) and 3406.92 (from Gauthier)
        self.carbon_budget = 1224935.4 #Infered from CO2_eq-emissions of Belgium in 2020 (106.6Mt), of world in 2020 (34.81Gt, from ourworldindata) and world carbon budget (400Gt, from climate analytics)

        self.cost_budget = 1.2e6

        self.gwp_per_year = dict.fromkeys(self.ampl_obj_0.sets['YEARS'],0.0)
        self.cost_per_year = dict.fromkeys(self.ampl_obj_0.sets['YEARS'],0.0)
        self.RE_in_mix_per_year = dict.fromkeys(self.ampl_obj_0.sets['YEARS'],0.0)
        self.Energy_efficiency_per_year = dict.fromkeys(self.ampl_obj_0.sets['YEARS'],0.0)

        self.i_epoch = 0

        #---------------------- Uncertainties --------------------#
        uq_dict = {'case' : 'ES_PATHWAY',
                    'eval_type' : 'UQ',
                    'design_space' : 'design_space.csv',
                    'sampling method': 'SOBOL'}

        space_obj = StochasticDesignSpace(uq_dict['eval_type'],uq_dict['case'],uq_dict['design_space'])
        my_data = uq.Data(uq_dict, space_obj)
        my_data.read_stoch_parameters()
        uq_experiment = uq.RandomExperiment(my_data, 0)
        uq_experiment.create_distributions()
        self.uq_experiment = uq_experiment
        

        #---------------------- Observation space --------------------#
        self.min_gwp = 1e3
        self.max_gwp = 5e6

        self.min_cost = 3e5
        self.max_cost = 3e6

        self.min_RE_in_mix = 0
        self.max_RE_in_mix = 1

        self.min_Energy_efficiency = 0
        self.max_Energy_efficiency = 1

        self.max_it = len(self.ampl_pre.years_opti)

        obslow = np.array([self.min_gwp, self.min_cost, self.min_RE_in_mix,
            self.min_Energy_efficiency])
        obshigh = np.array([self.max_gwp, self.max_cost, self.max_RE_in_mix,
            self.max_Energy_efficiency])

        self.obslow = obslow
        self.obshigh = obshigh

        self.observation_space = spaces.Box(low=self.obslow, high=self.obshigh, dtype=np.float32)

        #----------------------- Action space ----------------------#

        self.max_gwp_limit = 2*[1.0] #123000 ktCO2
        self.min_gwp_limit = 2*[0.0] #3406 ktCO2

        actlow = np.array(self.min_gwp_limit)
        acthigh = np.array(self.max_gwp_limit)


        self.actlow = actlow
        self.acthigh  = acthigh

        print('actlow  = {}'.format(actlow))
        print('acthigh = {}'.format(acthigh))


        self.action_space = spaces.Box(low=self.actlow, high=self.acthigh, dtype=np.float32)

        self.file_rew  = open('{}/reward.txt'.format(out_dir), 'w')
        self.file_observation = open('{}/observation.txt'.format(out_dir),'w')
        self.file_action = open('{}/action.txt'.format(out_dir),'w')
        self.file_cost = open('{}/cost.txt'.format(out_dir),'w')


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
        self.curr_years_wnd = self.ampl_pre.write_seq_opti(self.it)

        self.ampl_obj = AmplObject(self.mod_1_path, self.mod_2_path, self.dat_path, self.ampl_options, type_model = self.type_of_model)
        
        
        """
        Modify the parameters to account for uncertainties
        """
        
        ampl_uq = AmplUQ(self.ampl_obj)
        
        skip = self.skip+self.i_epoch+self.nb_done*100-1
        
        sample = ampl_uq.generate_one_sample(uq_exp = self.uq_experiment, skip=skip)
        years_wnd=['YEAR_2025','YEAR_2030','YEAR_2035','YEAR_2040','YEAR_2045','YEAR_2050']
        ampl_uq.transcript_uncertainties(sample,years_wnd)
        
        # 1) Take action
        print(' ')
        print('in step - action = {}'.format(action))
        print(' ')

        self._take_action( action )
        
        if self.it > 0:
            self.curr_years_wnd.remove(self.ampl_pre.year_to_rm)

        # 2) Observed what happened

        observation = self._get_observation()

        obs = np.c_[self.obslow, self.unscale_obs(observation), self.obshigh]

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
    def reset(self):
        print("RESET THE PROBLEM")
        self.it = 0
        self.i_epoch += 1
        self.cum_gwp = self.cum_gwp_init
        self.cum_cost = self.cum_cost_init
        self.RE_in_mix = self.RE_in_mix_init
        self.Energy_efficiency = self.Energy_efficiency_init

        self.ampl_obj_0.clean_history()
        years = self.ampl_obj_0.sets['YEARS']
        self.gwp_per_year = dict.fromkeys(years,0.0)
        self.cost_per_year = dict.fromkeys(years,0.0)
        self.ampl_obj = AmplObject(self.mod_1_path, self.mod_2_path, self.dat_path, self.ampl_options, type_model = self.type_of_model)
        self.ampl_pre = AmplPreProcessor(self.ampl_obj, self.n_year_opti, self.n_year_overlap)

        return self._scale_obs(np.array([self.cum_gwp, self.cum_cost,self.RE_in_mix,
            self.Energy_efficiency], dtype=np.float32))

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
        
        
        if self.solve_result == 'solved':
            gwp_dict = self.ampl_obj.collect_gwp(self.curr_years_wnd)
            self.cum_cost, cost_dict = self.ampl_obj.collect_cost('TotalTransitionCost',self.curr_years_wnd)
    
            energy_cons = self.ampl_obj.vars['energy_cons']
            RE_cons = self.ampl_obj.vars['RE_cons']
            final_energy_cons_trans = self.ampl_obj.vars['final_energy_cons_trans']
            eud_wo_trans = self.ampl_obj.params['eud_wo_trans']
    
            for y in self.curr_years_wnd:
                self.gwp_per_year[y] = gwp_dict[y]
                self.cost_per_year[y] = cost_dict[y]
                self.RE_in_mix_per_year[y] = RE_cons[y].value()/energy_cons[y].value()
                self.Energy_efficiency_per_year[y] = (final_energy_cons_trans[y].value()+eud_wo_trans[y])/energy_cons[y].value()
            
        t_phase = self.ampl_obj.params['t_phase'].value()
        self.cum_gwp = self.gwp_per_year['YEAR_2020'] * (1+t_phase/2)

        years_up_to = self.ampl_obj.sets['YEARS_UP_TO']

        year_n = years_up_to.pop()
        years_up_to.pop(0)

        for y in years_up_to:
            self.cum_gwp += self.gwp_per_year[y] * t_phase
        
        self.cum_gwp += self.gwp_per_year[year_n] * t_phase/2
    
        state_year = self.curr_years_wnd[1]
    
        self.RE_in_mix = self.RE_in_mix_per_year[state_year]
        self.Energy_efficiency = self.Energy_efficiency_per_year[state_year]

        self.file_observation.write('{} {:.1f}'.format(self.it,self.cum_gwp))
        for k in self.gwp_per_year:
            self.file_observation.write(' {:.1f}'.format(self.gwp_per_year[k]))
        for k in self.RE_in_mix_per_year:
            self.file_observation.write(' {:.2f}'.format(self.RE_in_mix_per_year[k]))
        for k in self.Energy_efficiency_per_year:
            self.file_observation.write(' {:.2f}'.format(self.Energy_efficiency_per_year[k]))

        self.file_observation.write('\n')
        self.file_observation.flush()

        cost_to_print = '{} {:.2f}'.format(self.it,self.cum_cost)

        for k in self.cost_per_year:
            cost_to_print += ' {:.2f}'.format(self.cost_per_year[k])

        cost_to_print += '\n'
        self.file_cost.write(cost_to_print)
        self.file_cost.flush()
        
        if self.solve_result == 'solved':
            return self._scale_obs(np.array([self.cum_gwp, self.cum_cost,self.RE_in_mix,
                self.Energy_efficiency], dtype=np.float32))
        else:
            return self._scale_obs(np.array([0,0,0,0], dtype=np.float32))
    
    # Returns the reward depending on the state the agent ends up in, after taking the action
    def _get_reward(self):
        if not (self.solve_result == 'solved'):
            status_2050 = 'Failure_imp_({})'.format(self.solve_result)
            reward = -300
            done = 1
        else:
            status_2050 = ''
            if self.it < self.max_it - 1:
                if self.carbon_budget < self.cum_gwp:
                    status_2050 = 'Failure'
                    # reward = 200/(self.it+1) * (self.carbon_budget-self.cum_gwp)/self.carbon_budget
                    reward = 200 * (self.carbon_budget-self.cum_gwp)/self.carbon_budget
                    done = 1
                else:
                    reward = 0
                    done = 0
            else :
                reward = 200 * min((self.carbon_budget-self.cum_gwp)/self.carbon_budget,0) + 100 * (self.cost_budget-self.cum_cost)/(self.cost_budget)
                if self.carbon_budget < self.cum_gwp:
                    status_2050 = 'Failure'
                else:
                    reward += 30
                    status_2050 = 'Success'
                done = 1

        self.file_rew.write('{} {:.2f} {}\n'.format(self.it,reward,status_2050))
        self.file_rew.flush()

        return reward, done


    def _take_action(self,action):
        
        
        err_msg = "%r (%s) invalid" % (action, type(action))
        assert self.action_space.contains(action), err_msg

        print('\n------------------------ A C T I O N S -----------------------')

        self._get_action_to_ampl(action)
        
        self.solve_result = self.ampl_obj.run_ampl()

        act_to_print = '{} {}'.format(self.i_epoch,self.it)

        for i in range(len(action)):
            act_to_print += ' {:.2f}'.format(action[i])
        
        act_to_print += '\n'

        self.file_action.write(act_to_print)
        self.file_action.flush()
    
    def _scale_obs(self,obs_unscaled):
        low, high = self.observation_space.low, self.observation_space.high
        return 2.0 * ((obs_unscaled - low) / (high-low)) - 1.0
    
    def unscale_obs(self,obs_scaled):
        low, high = self.observation_space.low, self.observation_space.high
        return (obs_scaled+1.0)/2.0 * (high - low) + low
    
    def _get_action_to_ampl(self,action):
        action = action.astype('float64')
        
        years_wnd = self.ampl_obj.sets['YEARS_WND'].copy()
        years_wnd.pop(0)
        
        gwp_limit_0 = action[0]*(123000-self.target_2050) + self.target_2050
        gwp_limit_1 = action[1]*(123000-self.target_2050) + self.target_2050
        
        self.ampl_obj.set_params('gwp_limit',{(years_wnd[0]):gwp_limit_0})
        self.ampl_obj.set_params('gwp_limit',{(years_wnd[1]):gwp_limit_1})