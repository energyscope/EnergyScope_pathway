import pandas as pd
import os
from pathlib import Path
import sobol
import numpy as np

# TODO adapt to updates and test
# TODO write doc

class AmplUQ:

    """

    The AmplUQ class allows to generate samples of uncertain parameters and
    change the values of the affected parameters of the ampl_object, run the
    pathway optimisation and return the total transition cost

    Parameters
    ----------
    ampl_obj : AmplObject object of ampl_object module
        Ampl object containing the optimisation problem and its attributes
    uq_file : string
        Path towards the file containing the uncertainty range

    """

    def __init__(self, ampl_obj):

        self.ampl_obj = ampl_obj
        project_path = Path(__file__).parents[1]
        self.uq_file = os.path.join(project_path,'uncertainties','uc_final.xlsx')


    def run_ampl_UQ(self,sample,years_wnd=['YEAR_2025','YEAR_2030','YEAR_2035','YEAR_2040','YEAR_2045','YEAR_2050']):

        # Test to update uncertain parameters
        uncer_params = sample

        self.transcript_uncertainties(uncer_params,years_wnd)
        
        solve_result = self.ampl_obj.run_ampl()
        
        if solve_result == 'solved':
            total_transition_cost = self.ampl_obj.collect_cost('TotalTransitionCost')[0]
        else:
            total_transition_cost = None

        return total_transition_cost
    
    def generate_one_sample(self, uq_exp, skip):
        
        size = 1
        
        l_b = uq_exp.my_data.stoch_data['l_b']
        u_b = uq_exp.my_data.stoch_data['u_b']
        
        
        uq_exp.x_u = np.zeros((size, uq_exp.dimension))
        uq_exp.x_u_scaled = np.zeros((size, uq_exp.dimension))
        
        skip = skip
        
        
        x_tr = sobol.sample(dimension=uq_exp.dimension,
                            n_points=1,
                            skip=skip)
        
        for i in range(uq_exp.dimension):
            uq_exp.x_u[:, i] = uq_exp.dists[i].ppf(x_tr[:, i])
        
        for i in range(uq_exp.dimension):
            for j in range(size):
                uq_exp.x_u_scaled[j, i] = ((uq_exp.x_u[j, i] - l_b[i]) /
                                         (u_b[i] - l_b[i]) * 2. - 1.)
        
        sample = dict(zip(uq_exp.my_data.stoch_data['names'],
                          uq_exp.x_u_scaled[0,:]))
        
        return sample
        

    def transcript_uncertainties(self, uncer_params,years_wnd):

        # to fill the undefined uncertainty parameters
        uncert_param = pd.read_excel(self.uq_file,sheet_name='Parameters',engine='openpyxl',index_col=0)
        
        mi = pd.MultiIndex.from_product([years_wnd,uncert_param.index],names=['Year','Parameter'])
        
        up = pd.DataFrame(0.0,index=mi,columns=['Value'])

        # Extract the new value from the RHEIA sampling
        for i,y in enumerate(years_wnd):
            range_y = pd.read_excel(self.uq_file,sheet_name=y,engine='openpyxl',index_col=0)
            for key in uncer_params:
                low, high = range_y.loc[key]['Range_min'], range_y.loc[key]['Range_max']
                up_y_key = (uncer_params[key]+1.0)/2.0 * (high - low) + low
                up.loc[y,key] = up_y_key

        c_op = self.ampl_obj.get_elem('c_op',type_of_elem='Param').copy()
        c_inv = self.ampl_obj.get_elem('c_inv',type_of_elem='Param').copy()
        c_maint = self.ampl_obj.get_elem('c_maint',type_of_elem='Param').copy()
        avail = self.ampl_obj.get_elem('avail',type_of_elem='Param').copy()
        c_p_t = self.ampl_obj.get_elem('c_p_t',type_of_elem='Param').copy()
        f_max = self.ampl_obj.get_elem('f_max',type_of_elem='Param').copy()
        solar_area = self.ampl_obj.get_elem('solar_area',type_of_elem='Param').copy()
        share_mobility_public_max = self.ampl_obj.get_elem('share_mobility_public_max',type_of_elem='Param').copy()
        layers_in_out = self.ampl_obj.get_elem('layers_in_out',type_of_elem='Param').copy()
        end_uses_demand_year = self.ampl_obj.get_elem('end_uses_demand_year',type_of_elem='Param').copy()
        
        # Interest rate
        self.ampl_obj.set_params('i_rate',self.ampl_obj.params['i_rate'].value()*(1. + float(up.loc[(slice(None),'param_i_rate'),:].Value[0])))
        
        # Limit to changes
        self.ampl_obj.set_params('limit_LT_renovation',self.ampl_obj.params['limit_LT_renovation'].value()*(1. + float(up.loc[(slice(None),'delta_change_lt_heat'),:].Value[0])))
        self.ampl_obj.set_params('limit_pass_mob_changes',self.ampl_obj.params['limit_pass_mob_changes'].value()*(1. + float(up.loc[(slice(None),'delta_change_pax'),:].Value[0])))
        self.ampl_obj.set_params('limit_freight_changes',self.ampl_obj.params['limit_freight_changes'].value()*(1. + float(up.loc[(slice(None),'delta_change_freight'),:].Value[0])))
        
        
        # Reinforcement of the grid
        self.ampl_obj.set_params('c_grid_extra',self.ampl_obj.params['c_grid_extra'].value() * (1. + float(up.loc[(slice(None),'grid_enforce'),:].Value[0])))


        for y in years_wnd:
            
            # Hourly capacity factors of VRES
            self.ampl_obj.set_params('c_p_t',c_p_t.loc[(y,['PV']),:] * (1. + float(up.loc[(slice(None),'cpt_pv'),:].Value[0])))
            self.ampl_obj.set_params('c_p_t',c_p_t.loc[(y,['WIND_ONSHORE']),:] * (1. + float(up.loc[(slice(None),'cpt_winds'),:].Value[0])))
            self.ampl_obj.set_params('c_p_t',c_p_t.loc[(y,['WIND_OFFSHORE']),:] * (1. + float(up.loc[(slice(None),'cpt_winds'),:].Value[0])))

            # Maintenance cost
            self.ampl_obj.set_params('c_maint',c_maint.loc[[y]] * (1. + up.loc[y,'c_maint_var'].Value))

            # Availability of resources
            self.ampl_obj.set_params('avail',avail.loc[(y,['ELECTRICITY']),:]*(1. + up.loc[y,'avail_elec'].Value))
            self.ampl_obj.set_params('avail',avail.loc[(y,['WOOD']),:]*(1. + up.loc[y,'avail_biomass'].Value))
            self.ampl_obj.set_params('avail',avail.loc[(y,['WET_BIOMASS']),:]*(1. + up.loc[y,'avail_biomass'].Value))
            

            # Operational cost of resources
            ## Fossil hydrocarbons
            self.ampl_obj.set_params('c_op',c_op.loc[(y,['GASOLINE']),:]*(1. + up.loc[y,'c_op_hydrocarbons'].Value))
            self.ampl_obj.set_params('c_op',c_op.loc[(y,['DIESEL']),:]*(1. + up.loc[y,'c_op_hydrocarbons'].Value))
            self.ampl_obj.set_params('c_op',c_op.loc[(y,['LFO']),:]*(1. + up.loc[y,'c_op_hydrocarbons'].Value))
            self.ampl_obj.set_params('c_op',c_op.loc[(y,['H2']),:]*(1. + up.loc[y,'c_op_hydrocarbons'].Value))
            self.ampl_obj.set_params('c_op',c_op.loc[(y,['GAS']),:]*(1. + up.loc[y,'c_op_hydrocarbons'].Value))
            self.ampl_obj.set_params('c_op',c_op.loc[(y,['METHANOL']),:]*(1. + up.loc[y,'c_op_hydrocarbons'].Value))
            self.ampl_obj.set_params('c_op',c_op.loc[(y,['AMMONIA']),:]*(1. + up.loc[y,'c_op_hydrocarbons'].Value))

            ## Electrofuels
            self.ampl_obj.set_params('c_op',c_op.loc[(y,['H2_RE']),:]*(1. + up.loc[y,'c_op_syn_fuels'].Value))
            self.ampl_obj.set_params('c_op',c_op.loc[(y,['GAS_RE']),:]*(1. + up.loc[y,'c_op_syn_fuels'].Value))
            self.ampl_obj.set_params('c_op',c_op.loc[(y,['METHANOL_RE']),:]*(1. + up.loc[y,'c_op_syn_fuels'].Value))
            self.ampl_obj.set_params('c_op',c_op.loc[(y,['AMMONIA_RE']),:]*(1. + up.loc[y,'c_op_syn_fuels'].Value))

            ## Biofuels
            self.ampl_obj.set_params('c_op',c_op.loc[(y,['BIODIESEL']),:]*(1. + up.loc[y,'c_op_biofuels'].Value))
            self.ampl_obj.set_params('c_op',c_op.loc[(y,['BIOETHANOL']),:]*(1. + up.loc[y,'c_op_biofuels'].Value))

            ## Electricity
            self.ampl_obj.set_params('c_op',c_op.loc[(y,['ELECTRICITY']),:]*(1. + up.loc[y,'c_op_elec'].Value))


            # Update mobility cost
            ## Buses
            self.ampl_obj.set_params('c_inv',c_inv.loc[(y,['BUS_COACH_DIESEL']),:] * (1. + up.loc[y,'c_inv_bus'].Value) * (1. + up.loc[y,'c_inv_ic_prop'].Value))
            self.ampl_obj.set_params('c_inv',c_inv.loc[(y,['BUS_COACH_HYDIESEL']),:] * (1. + up.loc[y,'c_inv_bus'].Value) * 0.5 * ((1. + up.loc[y,'c_inv_ic_prop'].Value) + (1. + up.loc[y,'c_inv_e_prop'].Value)))
            self.ampl_obj.set_params('c_inv',c_inv.loc[(y,['BUS_COACH_CNG_STOICH']),:] * (1. + up.loc[y,'c_inv_bus'].Value) * (1. + up.loc[y,'c_inv_ic_prop'].Value))
            self.ampl_obj.set_params('c_inv',c_inv.loc[(y,['BUS_COACH_FC_HYBRIDH2']),:] * (1. + up.loc[y,'c_inv_bus'].Value) * (1. + up.loc[y,'c_inv_fc_prop'].Value))

            ## Cars
            self.ampl_obj.set_params('c_inv',c_inv.loc[(y,['CAR_GASOLINE']),:] * (1. + up.loc[y,'c_inv_car'].Value) * (1. + up.loc[y,'c_inv_ic_prop'].Value))
            self.ampl_obj.set_params('c_inv',c_inv.loc[(y,['CAR_DIESEL']),:] * (1. + up.loc[y,'c_inv_car'].Value) * (1. + up.loc[y,'c_inv_ic_prop'].Value))
            self.ampl_obj.set_params('c_inv',c_inv.loc[(y,['CAR_NG']),:] * (1. + up.loc[y,'c_inv_car'].Value) * (1. + up.loc[y,'c_inv_ic_prop'].Value))
            self.ampl_obj.set_params('c_inv',c_inv.loc[(y,['CAR_METHANOL']),:] * (1. + up.loc[y,'c_inv_car'].Value) * (1. + up.loc[y,'c_inv_ic_prop'].Value))
            self.ampl_obj.set_params('c_inv',c_inv.loc[(y,['CAR_HEV']),:] * (1. + up.loc[y,'c_inv_car'].Value) * 0.5 * ((1. + up.loc[y,'c_inv_ic_prop'].Value) + (1. + up.loc[y,'c_inv_e_prop'].Value)))
            self.ampl_obj.set_params('c_inv',c_inv.loc[(y,['CAR_PHEV']),:] * (1. + up.loc[y,'c_inv_car'].Value) * 0.5 * ((1. + up.loc[y,'c_inv_ic_prop'].Value) + (1. + up.loc[y,'c_inv_e_prop'].Value)))
            self.ampl_obj.set_params('c_inv',c_inv.loc[(y,['CAR_BEV']),:] * (1. + up.loc[y,'c_inv_car'].Value) * (1. + up.loc[y,'c_inv_e_prop'].Value))
            self.ampl_obj.set_params('c_inv',c_inv.loc[(y,['CAR_FUEL_CELL']),:] * (1. + up.loc[y,'c_inv_car'].Value) * (1. + up.loc[y,'c_inv_fc_prop'].Value))

            ## Boats
            self.ampl_obj.set_params('c_inv',c_inv.loc[(y,['BOAT_FREIGHT_DIESEL']),:] * (1. + up.loc[y,'c_inv_ic_prop'].Value))
            self.ampl_obj.set_params('c_inv',c_inv.loc[(y,['BOAT_FREIGHT_NG']),:] * (1. + up.loc[y,'c_inv_ic_prop'].Value))
            self.ampl_obj.set_params('c_inv',c_inv.loc[(y,['BOAT_FREIGHT_METHANOL']),:] * (1. + up.loc[y,'c_inv_ic_prop'].Value))

            ## Trucks
            self.ampl_obj.set_params('c_inv',c_inv.loc[(y,['TRUCK_DIESEL']),:] * (1. + up.loc[y,'c_inv_ic_prop'].Value))
            self.ampl_obj.set_params('c_inv',c_inv.loc[(y,['TRUCK_FUEL_CELL']),:] * (1. + up.loc[y,'c_inv_fc_prop'].Value))
            self.ampl_obj.set_params('c_inv',c_inv.loc[(y,['TRUCK_ELEC']),:] * (1. + up.loc[y,'c_inv_e_prop'].Value))
            self.ampl_obj.set_params('c_inv',c_inv.loc[(y,['TRUCK_NG']),:] * (1. + up.loc[y,'c_inv_ic_prop'].Value))
            self.ampl_obj.set_params('c_inv',c_inv.loc[(y,['TRUCK_METHANOL']),:] * (1. + up.loc[y,'c_inv_ic_prop'].Value))

            ## Grid, efficiency and pv
            self.ampl_obj.set_params('c_inv',c_inv.loc[(y,['GRID']),:] * (1. + up.loc[y,'c_inv_grid'].Value))
            self.ampl_obj.set_params('c_inv',c_inv.loc[(y,['EFFICIENCY']),:] * (1. + up.loc[y,'c_inv_efficiency'].Value))
            self.ampl_obj.set_params('c_inv',c_inv.loc[(y,['PV']),:] * (1. + up.loc[y,'c_inv_pv'].Value))
                
            ## Nuclear SMR
            self.ampl_obj.set_params('c_inv',c_inv.loc[(y,['NUCLEAR_SMR']),:] * (1. + up.loc[y,'c_inv_nuclear_smr'].Value))
            
            
            # fmax
            self.ampl_obj.set_params('f_max',f_max.loc[(y,['PV']),:] * (1. + up.loc[y,'f_max_pv'].Value))
            self.ampl_obj.set_params('solar_area',solar_area.loc[[y]] * (1. + up.loc[y,'f_max_pv'].Value)) #To make sure the area constraint does not limit the maximum capacity of PV
            self.ampl_obj.set_params('f_max',f_max.loc[(y,['WIND_ONSHORE']),:] * (1. + up.loc[y,'f_max_windon'].Value))
            self.ampl_obj.set_params('f_max',f_max.loc[(y,['WIND_OFFSHORE']),:] * (1. + up.loc[y,'f_max_windoff'].Value))

            # Share of public mobility in passenger mobility
            self.ampl_obj.set_params('share_mobility_public_max',share_mobility_public_max.loc[[y]] * (1. + up.loc[y,'pourc_pub_max'].Value))

            # Efficiency of fuel cells and electric vehicles
            self.ampl_obj.set_params('layers_in_out',layers_in_out.loc[(y,['BUS_COACH_FC_HYBRIDH2'],['H2']),:] * (1. + up.loc[y,'eff_fc_prop'].Value))
            self.ampl_obj.set_params('layers_in_out',layers_in_out.loc[(y,['CAR_FUEL_CELL'],['H2']),:] * (1. + up.loc[y,'eff_fc_prop'].Value))
            self.ampl_obj.set_params('layers_in_out',layers_in_out.loc[(y,['TRUCK_FUEL_CELL'],['H2']),:] * (1. + up.loc[y,'eff_fc_prop'].Value))

            self.ampl_obj.set_params('layers_in_out',layers_in_out.loc[(y,['BUS_COACH_HYDIESEL'],['ELECTRICITY']),:] * (1. + up.loc[y,'eff_e_prop'].Value))
            self.ampl_obj.set_params('layers_in_out',layers_in_out.loc[(y,['CAR_HEV'],['ELECTRICITY']),:] * (1. + up.loc[y,'eff_e_prop'].Value))
            self.ampl_obj.set_params('layers_in_out',layers_in_out.loc[(y,['CAR_PHEV'],['ELECTRICITY']),:] * (1. + up.loc[y,'eff_e_prop'].Value))
            self.ampl_obj.set_params('layers_in_out',layers_in_out.loc[(y,['CAR_BEV'],['ELECTRICITY']),:] * (1. + up.loc[y,'eff_e_prop'].Value))
            self.ampl_obj.set_params('layers_in_out',layers_in_out.loc[(y,['TRUCK_ELEC'],['ELECTRICITY']),:] * (1. + up.loc[y,'eff_e_prop'].Value))

            # End-use demands
            self.ampl_obj.set_params('end_uses_demand_year',end_uses_demand_year.loc[y,slice(None),'HOUSEHOLDS'] * (1. + up.loc[y,'households_eud'].Value))
            self.ampl_obj.set_params('end_uses_demand_year',end_uses_demand_year.loc[y,slice(None),'SERVICES'] * (1. + up.loc[y,'services_eud'].Value))
            self.ampl_obj.set_params('end_uses_demand_year',end_uses_demand_year.loc[y,slice(None),'INDUSTRY'] * (1. + up.loc[y,'industry_eud'].Value))
            self.ampl_obj.set_params('end_uses_demand_year',end_uses_demand_year.loc[y,'MOBILITY_PASSENGER',slice(None)] * (1. + up.loc[y,'passenger_eud'].Value))
            
            # Availability of nuclear-smr: only, possibly from 2040
            if y == 'YEAR_2040' and up.loc[y,'f_max_nuclear_smr'].Value >= 0.9:
                self.ampl_obj.set_params('f_max',f_max.loc[(y,['NUCLEAR_SMR']),:] + 6)
            if y == 'YEAR_2045' and up.loc[y,'f_max_nuclear_smr'].Value >= 0.8:
                self.ampl_obj.set_params('f_max',f_max.loc[(y,['NUCLEAR_SMR']),:] + 6)
            if y == 'YEAR_2050' and up.loc[y,'f_max_nuclear_smr'].Value >= 0.6:
                self.ampl_obj.set_params('f_max',f_max.loc[(y,['NUCLEAR_SMR']),:] + 6)
            
            
            
