# -------------------------------------------------------------------------------------------------------------------------													
#	EnergyScope TD is an open-source energy model suitable for country scale analysis. It is a simplified representation of an urban or national energy system accounting for the energy flows												
#	within its boundaries. Based on a hourly resolution, it optimises the design and operation of the energy system while minimizing the cost of the system.												
#													
#	Copyright (C) <2018-2019> <Ecole Polytechnique FÃ©dÃ©rale de Lausanne (EPFL), Switzerland and UniversitÃ© catholique de Louvain (UCLouvain), Belgium>
#													
#	Licensed under the Apache License, Version 2.0 (the "License");												
#	you may not use this file except in compliance with the License.												
#	You may obtain a copy of the License at												
#													
#		http://www.apache.org/licenses/LICENSE-2.0												
#													
#	Unless required by applicable law or agreed to in writing, software												
#	distributed under the License is distributed on an "AS IS" BASIS,												
#	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.												
#	See the License for the specific language governing permissions and												
#	limitations under the License.												
#													
#	Description and complete License: see LICENSE file.												
# -------------------------------------------------------------------------------------------------------------------------		

## NEW SETS FOR PATHWAY:

set YEARS ;#..  2050 by 25;
set PHASE ;
set PHASE_START {PHASE} within YEARS;
set PHASE_STOP  {PHASE} within YEARS;
set YEARS_WND within YEARS;
set PHASE_WND within PHASE;
set YEARS_UP_TO within YEARS;
set PHASE_UP_TO within PHASE;
set YEAR_ONE within YEARS;
set YEAR_ONE_NEXT within YEARS;

#########################
###  SETS [Figure 3]  ###
#########################

## MAIN SETS: Sets whose elements are input directly in the data file
set PERIODS; # time periods
set SECTORS; # sectors of the energy system
set END_USES_INPUT; # Types of demand (end-uses). Input to the model
set END_USES_CATEGORIES; # Categories of demand (end-uses): electricity, heat, mobility
set END_USES_TYPES_OF_CATEGORY {END_USES_CATEGORIES}; # Types of demand (end-uses).
set RESOURCES; # Resources: fuels (renewables and fossils) and electricity imports
set RES_IMPORT_CONSTANT within RESOURCES; # resources imported at constant power (e.g. NG, diesel, ...)
set BIOFUELS within RESOURCES; # imported biofuels.
set EXPORT within RESOURCES; # exported resources
set END_USES_TYPES := setof {i in END_USES_CATEGORIES, j in END_USES_TYPES_OF_CATEGORY [i]} j; # secondary set
set TECHNOLOGIES_OF_END_USES_TYPE {END_USES_TYPES}; # set all energy conversion technologies (excluding storage technologies and infrastructure)
set STORAGE_TECH; #  set of storage technologies 
set STORAGE_OF_END_USES_TYPES {END_USES_TYPES} within STORAGE_TECH; # set all storage technologies related to an end-use types (used for thermal solar (TS))
set INFRASTRUCTURE; # Infrastructure: DHN, grid, and intermediate energy conversion technologies (i.e. not directly supplying end-use demand)
set RE_TECH; # Set composed of PV, WIND_ON and WIND_OFF

## SECONDARY SETS: a secondary set is defined by operations on MAIN SETS
set LAYERS := (RESOURCES diff BIOFUELS diff EXPORT) union END_USES_TYPES; # Layers are used to balance resources/products in the system
set TECHNOLOGIES := (setof {i in END_USES_TYPES, j in TECHNOLOGIES_OF_END_USES_TYPE [i]} j) union STORAGE_TECH union INFRASTRUCTURE; 
set TECHNOLOGIES_OF_END_USES_CATEGORY {i in END_USES_CATEGORIES} within TECHNOLOGIES := setof {j in END_USES_TYPES_OF_CATEGORY[i], k in TECHNOLOGIES_OF_END_USES_TYPE [j]} k;
set RE_RESOURCES within RESOURCES; # List of RE resources (including wind hydro solar), used to compute the RE share
set V2G within TECHNOLOGIES;   # EVs which can be used for vehicle-to-grid (V2G).
set EVs_BATT   within STORAGE_TECH; # specific battery of EVs 
set EVs_BATT_OF_V2G {V2G}; # Makes the link between batteries of EVs and the V2G technology
set STORAGE_DAILY within STORAGE_TECH;# Storages technologies for daily application 
set TS_OF_DEC_TECH {TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}} ; # Makes the link between TS and the technology producing the heat

## Additional SETS: only needed for printing out results (not represented in Figure 3).
set COGEN within TECHNOLOGIES; # cogeneration tech
set BOILERS within TECHNOLOGIES; # boiler tech

#NEW DEPENDENT:
set AGE {TECHNOLOGIES,PHASE} within PHASE union {"2020_2025"} union {"STILL_IN_USE"};


#################################
### PARAMETERS [Tables 1-2]   ###
#################################

## NEW PARAMETERS FOR PATHWAY:
param max_inv_phase {PHASE} default Infinity;#Unlimited
param t_phase ;
param diff_2015_phase {PHASE};
param gwp_limit_transition >=0 default Infinity; #To limit CO2 emissions over the transition
param decom_allowed {PHASE,PHASE union {"2020_2025"},TECHNOLOGIES} default 0;
param remaining_years {TECHNOLOGIES,PHASE} >=0;
param limit_LT_renovation >= 0;
param limit_pass_mob_changes >= 0;
param limit_freight_changes >= 0;
param efficiency {YEARS} >=0 default 1;

## Parameters added to include time series in the model [Table 1]
param lighting_month {PERIODS} >= 0, <= 1; # %_lighting: factor for sharing lighting across months (adding up to 1)
param heating_month {PERIODS} >= 0, <= 1; # %_sh: factor for sharing space heating across months (adding up to 1)
param c_p_t {YEARS, TECHNOLOGIES, PERIODS} >= 0, <= 1 default 1; # capacity factor of each technology and resource, defined on monthly basis. Different than 1 if F_Mult_t (t) <= c_p_t (t) * F_Mult

## Parameters added to define scenarios and technologies [Table 2]
param end_uses_demand_year {YEARS, END_USES_INPUT, SECTORS} >= 0 default 0; # end_uses_year [GWh]: table end-uses demand vs sectors (input to the model). Yearly values. [Mpkm] or [Mtkm] for passenger or freight mobility.
param end_uses_input {y in YEARS, i in END_USES_INPUT} := sum {s in SECTORS} (end_uses_demand_year [y,i,s]); # end_uses_input (Figure 1.4) [GWh]: total demand for each type of end-uses across sectors (yearly energy) as input from the demand-side model. [Mpkm] or [Mtkm] for passenger or freight mobility.
param i_rate > 0 default 0.015; # discount rate [-]: real discount rate
param re_share_primary {YEARS} >= 0 default 0; # re_share [-]: minimum share of primary energy coming from RE
param gwp_limit {YEARS} >= 0 default 0;    # [ktCO2-eq./year] maximum gwp emissions allowed.
param share_mobility_public_min {YEARS} >= 0, <= 1 default 0; # %_public,min [-]: min limit for penetration of public mobility over total mobility 
param share_mobility_public_max {YEARS} >= 0, <= 1 default 0; # %_public,max [-]: max limit for penetration of public mobility over total mobility 
# Share train vs truck in freight transportation
param share_freight_train_min {YEARS} >= 0, <= 1 default 0; # % min limit for penetration of train in freight transportation
param share_freight_train_max {YEARS} >= 0, <= 1 default 0; # % max limit for penetration of train in freight transportation
param share_freight_road_min {YEARS}  >= 0, <= 1 default 0; # % min limit for penetration of road in freight transportation
param share_freight_road_max {YEARS}  >= 0, <= 1 default 0; # % max limit for penetration of road in freight transportation
param share_freight_boat_min {YEARS}  >= 0, <= 1 default 0; # % min limit for penetration of boat in freight transportation
param share_freight_boat_max {YEARS}  >= 0, <= 1 default 0; # % max limit for penetration of boat in freight transportation

# share dhn vs decentralized for low-T heating
param share_heat_dhn_min {YEARS} >= 0, <= 1 default 0; # %_dhn,min [-]: min limit for penetration of dhn in low-T heating
param share_heat_dhn_max {YEARS} >= 0, <= 1 default 0; # %_dhn,max [-]: max limit for penetration of dhn in low-T heating
param share_ned {YEARS, END_USES_TYPES_OF_CATEGORY["NON_ENERGY"]} >= 0, <= 1; # %_ned [-] share of non-energy demand per type of feedstocks.
param t_op {PERIODS}; # duration of each time period [h]
param f_max {YEARS,TECHNOLOGIES} >= 0 default 0; # Maximum feasible installed capacity [GW], refers to main output. storage level [GWh] for STORAGE_TECH
param f_min {YEARS,TECHNOLOGIES} >= 0 default 0; # Minimum feasible installed capacity [GW], refers to main output. storage level [GWh] for STORAGE_TECH
param fmax_perc {YEARS,TECHNOLOGIES} >= 0, <= 1 default 1; # value in [0,1]: this is to fix that a technology can at max produce a certain % of the total output of its sector over the entire year
param fmin_perc {YEARS,TECHNOLOGIES} >= 0, <= 1 default 0; # value in [0,1]: this is to fix that a technology can at min produce a certain % of the total output of its sector over the entire year
param avail {YEARS,RESOURCES} >= 0 default 0; # Yearly availability of resources [GWh/y]
param c_op {YEARS,RESOURCES} >= 0 default 0; # cost of resources in the different periods [MCHF/GWh]
param vehicule_capacity {YEARS,TECHNOLOGIES} >=0, default 0; #  veh_capa [capacity/vehicles] Average capacity (pass-km/h or t-km/h) per vehicle. It makes the link between F and the number of vehicles
param peak_sh_factor >= 0;   # %_Peak_sh [-]: ratio between highest yearly demand and highest TDs demand
param layers_in_out {YEARS,RESOURCES union TECHNOLOGIES diff STORAGE_TECH,LAYERS}; # f: input/output Resources/Technologies to Layers. Reference is one unit ([GW] or [Mpkm/h] or [Mtkm/h]) of (main) output of the resource/technology. input to layer (output of technology) > 0.
param c_inv {YEARS,TECHNOLOGIES} >= 0 default 0; # Specific investment cost [Meuros/GW].[Meuros/GWh] for STORAGE_TECH
param c_maint {YEARS,TECHNOLOGIES} >= 0 default 0; # O&M cost [MCHF/GW/year]: O&M cost does not include resource (fuel) cost. [MCHF/GWh/year] for STORAGE_TECH
param lifetime {YEARS,TECHNOLOGIES} >= 0 default 0; # n: lifetime [years]
param tau {y in YEARS, i in TECHNOLOGIES} := i_rate * (1 + i_rate)^lifetime [y,i] / (((1 + i_rate)^lifetime [y,i]) - 1); # Annualisation factor ([-]) for each different technology [Eq. 2]
param gwp_constr {YEARS, TECHNOLOGIES} >= 0 default 0; # GWP emissions associated to the construction of technologies [ktCO2-eq./GW]. Refers to [GW] of main output
param gwp_op {YEARS, RESOURCES} >= 0 default 0; # GWP emissions associated to the use of resources [ktCO2-eq./GWh]. Includes extraction/production/transportation and combustion
param c_p {YEARS, TECHNOLOGIES} >= 0, <= 1 default 1; # yearly capacity factor of each technology [-], defined on annual basis. Different than 1 if sum {t in PERIODS} F_t (t) <= c_p * F
param storage_eff_in {YEARS, STORAGE_TECH , LAYERS} >= 0, <= 1  default 0; # eta_sto_in [-]: efficiency of input to storage from layers.  If 0 storage_tech/layer are incompatible
param storage_eff_out {YEARS, STORAGE_TECH , LAYERS} >= 0, <= 1 default 0; # eta_sto_out [-]: efficiency of output from storage to layers. If 0 storage_tech/layer are incompatible
param storage_losses {YEARS, STORAGE_TECH} >= 0, <= 1 default 0; # %_sto_loss [-]: Self losses in storage (required for Li-ion batteries). Value = self discharge in 1 hour.
param storage_charge_time    {YEARS, STORAGE_TECH} >= 0 default 0; # t_sto_in [h]: Time to charge storage (Energy to Power ratio). If value =  5 <=>  5h for a full charge.
param storage_discharge_time {YEARS, STORAGE_TECH} >= 0 default 0; # t_sto_out [h]: Time to discharge storage (Energy to Power ratio). If value =  5 <=>  5h for a full discharge.
param storage_availability {YEARS, STORAGE_TECH} >=0, default 1;# %_sto_avail [-]: Storage technology availability to charge/discharge. Used for EVs 
param loss_network {YEARS, END_USES_TYPES} >= 0 default 0; # %_net_loss: Losses coefficient [0; 1] in the networks (grid and DHN)
param batt_per_car {YEARS, V2G} >= 0 default 0; # ev_Batt_size [GWh]: Battery size per EVs car technology
param c_grid_extra >=0; # # Cost to reinforce the grid due to IRE penetration [Meuros/GW of (PV + Wind)].
param elec_max_import_capa  {YEARS} >=0;
param solar_area	 {YEARS} >= 0; # Maximum land available for PV deployment [km2]
param power_density_pv >=0 default 0;# Maximum power irradiance for PV.
param power_density_solar_thermal >=0 default 0;# Maximum power irradiance for solar thermal.


##Additional parameter (not presented in the paper)
param total_time := sum {t in PERIODS} (t_op [t]); # added just to simplify equations

# NEW : PARAM DEPEN?DENT:
param annualised_factor {p in PHASE} := 1 / ((1 + i_rate)^diff_2015_phase[p] ); # Annualisation factor for each different technology

#################################
###  VARIABLES [Tables 3-4]   ###
#################################

## NEW VARIABLES FOR PATHWAY:
var F_new {PHASE union {"2020_2025"}, TECHNOLOGIES} >= 0; #[GW/GWh] Accounts for the additional new capacity installed in a new phase
var F_decom {PHASE,PHASE union {"2020_2025"}, TECHNOLOGIES} >= 0; #[GW] Accounts for the decommissioned capacity in a new phase
var F_old {PHASE,TECHNOLOGIES} >=0, default 0; #[GW] Retired capacity during a phase with respect to the main output
var C_inv_phase {PHASE} >=0; #[M€/GW] Phase total annualised investment cost
var C_inv_phase_tech {PHASE,TECHNOLOGIES} >=0; #[M€/GW] Phase total annualised investment cost, per technology
var C_op_phase_tech {PHASE,TECHNOLOGIES} >= 0;
var C_op_phase_res {PHASE,RESOURCES} >= 0;
var C_inv_return {TECHNOLOGIES} >=0; #[M€] Money given back for existing technologies after 2050 to compute the objective function
#var Fixed_phase_investment;
var C_opex {YEARS} >=0;
var C_tot_opex >=0;
var C_tot_capex >=0;
var TotalGWPTransition >=0;
var Delta_change {PHASE,TECHNOLOGIES} >=0;

var Gwp_tot_cost >=0;

##Independent variables [Table 3] :
var Share_mobility_public {y in YEARS} >= share_mobility_public_min [y], <= share_mobility_public_max [y]; # %_Public: Ratio [0; 1] public mobility over total passenger mobility
var Share_freight_train {y in YEARS}, >= share_freight_train_min [y], <= share_freight_train_max [y]; # %_Rail: % of freight mobility attributed to train
var Share_freight_road {y in YEARS}, >= share_freight_road_min [y], <= share_freight_road_max [y]; # %_Rail: % of freight mobility attributed to train
var Share_freight_boat {y in YEARS}, >= share_freight_boat_min [y], <= share_freight_boat_max [y]; # %_Rail: % of freight mobility attributed to train
var Share_heat_dhn {y in YEARS}, >= share_heat_dhn_min [y], <= share_heat_dhn_max [y]; # %_DHN: Ratio [0; 1] centralized over total low-temperature heat
var F {YEARS, TECHNOLOGIES} >= 0; # F: Installed capacity ([GW]) with respect to main output (see layers_in_out). [GWh] for STORAGE_TECH.
var F_t {YEARS, RESOURCES union TECHNOLOGIES, PERIODS} >= 0; # F_t: Operation in each period. multiplication factor with respect to the values in layers_in_out table. Takes into account c_p
var Storage_in {YEARS, i in STORAGE_TECH, LAYERS, PERIODS} >= 0; # Sto_in: Power [GW] input to the storage in a certain period
var Storage_out {YEARS, i in STORAGE_TECH, LAYERS, PERIODS} >= 0; # Sto_out: Power [GW] output from the storage in a certain period
var Power_nuclear {YEARS}  >=0; # [GW] P_Nuc: Constant load of nuclear
var Shares_mobility_passenger {YEARS, TECHNOLOGIES_OF_END_USES_CATEGORY["MOBILITY_PASSENGER"]} >=0; # %_MobPass [-]: Constant share of passenger mobility
# NEW VARIABLE
var Shares_mobility_freight {YEARS, TECHNOLOGIES_OF_END_USES_CATEGORY["MOBILITY_FREIGHT"]} >=0; # %_Freight [-]: Constant share of passenger mobility
var Shares_lowT_dec {YEARS, TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}}>=0 ; # %_HeatDec [-]: Constant share of heat Low T decentralised + its specific thermal solar
var F_solar         {YEARS, TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}} >=0; # F_sol [GW]: Solar thermal installed capacity per heat decentralised technologies
var F_t_solar       {YEARS, TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}, PERIODS} >= 0; # F_t_sol [GW]: Solar thermal operating per heat decentralised technologies

##Dependent variables [Table 4] :
var End_uses {YEARS, LAYERS, PERIODS} >= 0; # total demand for each type of end-uses (monthly power). Defined for all layers (0 if not demand). [Mpkm] or [Mtkm] for passenger or freight mobility.
var TotalCost {YEARS} >= 0; # C_tot [MCHF/year]: Total cost of the system.
var C_inv {YEARS, TECHNOLOGIES} >= 0; #C_inv [MCHF]: Total investment cost of each technology
var C_maint {YEARS, TECHNOLOGIES} >= 0; #C_maint [MCHF/year]: Total O&M cost of each technology (excluding resource cost)
var C_op {YEARS, RESOURCES} >= 0; #C_op [MCHF/year]: Total O&M cost of each resource
var TotalGWP {YEARS} >= 0; # GWP_tot [ktCO2-eq./year]: Total global warming potential (GWP) emissions in the system
var GWP_constr {YEARS, TECHNOLOGIES} >= 0; # GWP_constr [ktCO2-eq.]: Total emissions of the technologies
var GWP_op {YEARS, RESOURCES} >= 0; #  GWP_op [ktCO2-eq.]: Total yearly emissions of the resources [ktCO2-eq./y]
var Network_losses {YEARS, END_USES_TYPES, PERIODS} >= 0; # Net_loss [GW]: Losses in the networks (normally electricity grid and DHN)
var Storage_level {YEARS, STORAGE_TECH, PERIODS} >= 0; # Sto_level [GWh]: Energy stored at each period

# Variables RL:

#########################################
###      CONSTRAINTS Eqs [1-42]       ###
#########################################



## End-uses demand calculation constraints 
#-----------------------------------------

# [Figure 4] From annual energy demand to hourly power demand. End_uses is non-zero only for demand layers.
subject to end_uses_t {y in YEARS_WND diff YEAR_ONE, l in LAYERS, t in PERIODS}:
	End_uses [y,l, t] = (if l == "ELECTRICITY" 
		then
			(end_uses_input[y,l] / total_time + end_uses_input[y,"LIGHTING"] * lighting_month [t] / t_op [t]) + Network_losses [y,l,t]
		else (if l == "HEAT_LOW_T_DHN" then
			(end_uses_input[y,"HEAT_LOW_T_HW"] / total_time + end_uses_input[y,"HEAT_LOW_T_SH"] * heating_month [t] / t_op [t]) * Share_heat_dhn [y] + Network_losses [y,l,t]
		else (if l == "HEAT_LOW_T_DECEN" then
			(end_uses_input[y,"HEAT_LOW_T_HW"] / total_time + end_uses_input[y,"HEAT_LOW_T_SH"] * heating_month [t] / t_op [t]) * (1 - Share_heat_dhn [y])
		else (if l == "MOB_PUBLIC" then
			(end_uses_input[y,"MOBILITY_PASSENGER"] / total_time) * Share_mobility_public [y]
		else (if l == "MOB_PRIVATE" then
			(end_uses_input[y,"MOBILITY_PASSENGER"] / total_time) * (1 - Share_mobility_public [y])
		else (if l == "MOB_FREIGHT_RAIL" then
			(end_uses_input[y,"MOBILITY_FREIGHT"] / total_time) * Share_freight_train [y]
		else (if l == "MOB_FREIGHT_ROAD" then
			(end_uses_input[y,"MOBILITY_FREIGHT"] / total_time) * Share_freight_road [y]
		else (if l == "MOB_FREIGHT_BOAT" then
			(end_uses_input[y,"MOBILITY_FREIGHT"] / total_time) * Share_freight_boat [y]
		else (if l == "HEAT_HIGH_T" then
			end_uses_input[y,l] / total_time
		else (if l == "HVC" then
			end_uses_input[y,"NON_ENERGY"] * share_ned [y,"HVC"] / total_time
		else (if l == "AMMONIA" then
			end_uses_input[y,"NON_ENERGY"] * share_ned [y,"AMMONIA"] / total_time
		else (if l == "METHANOL" then
			end_uses_input[y,"NON_ENERGY"] * share_ned [y,"METHANOL"] / total_time
		else 
			0 )))))))))))); # For all layers which don't have an end-use demand


## Cost
#------

# [Eq. 1]	
subject to totalcost_cal {y in YEARS_UP_TO union YEARS_WND}:
	TotalCost [y] = sum {j in TECHNOLOGIES} (tau [y,j]  * C_inv [y,j] + C_maint [y,j]) + sum {i in RESOURCES} C_op [y,i];
	
# [Eq. 3] Investment cost of each technology
subject to investment_cost_calc {y in YEARS_UP_TO union YEARS_WND,j in TECHNOLOGIES}: 
	C_inv [y,j] = c_inv [y,j] * F [y,j];
		
# [Eq. 4] O&M cost of each technology
subject to main_cost_calc {y in YEARS_UP_TO union YEARS_WND, j in TECHNOLOGIES}: 
	C_maint [y,j] = c_maint [y,j] * F [y,j];		

# [Eq. 5] Total cost of each resource
## To store resources used
var Res {YEARS diff {'YEAR_2015','YEAR_2020'}, RESOURCES} >= 0, default 0; #[GWh] Resources used in the current window
subject to store_res {y in YEARS_WND diff YEAR_ONE, j in RESOURCES}:
	Res [y, j] = sum {t in PERIODS} (F_t [y,j,t] * t_op [t]);
subject to op_cost_calc {y in YEARS_UP_TO union YEARS_WND, i in RESOURCES}:
	C_op [y,i] = c_op [y,i] * Res [y, i] ;

## Emissions
#-----------

# [Eq. 6]
subject to totalGWP_calc {y in YEARS_UP_TO union YEARS_WND}:
	TotalGWP [y] =  sum {i in RESOURCES} GWP_op [y,i];
	#JUST RESOURCES : TotalGWP [y] =  sum {i in RESOURCES} GWP_op [y,i];
	#BASED ON LCA:    TotalGWP [y] = sum {j in TECHNOLOGIES} (GWP_constr [y,j] / lifetime [y,j]) + sum {i in RESOURCES} GWP_op [y,i];
	
# [Eq. 7]
subject to gwp_constr_calc {y in YEARS_UP_TO union YEARS_WND, j in TECHNOLOGIES}:
	GWP_constr [y,j] = gwp_constr [y,j] * F [y,j];

# [Eq. 8]
subject to gwp_op_calc {y in YEARS_UP_TO union YEARS_WND, i in RESOURCES}:
	GWP_op [y,i] = gwp_op [y,i] * Res [y,i];	

# [Eq. XX] total transition gwp calculation
subject to totalGWPTransition_calculation : # category: GWP_calc
	TotalGWPTransition = TotalGWP ["YEAR_2025"] + sum {p in PHASE_UP_TO union PHASE_WND,y_start in PHASE_START [p],y_stop in PHASE_STOP [p]}  (t_phase * (TotalGWP [y_start] + TotalGWP [y_stop])/2);
	
## Multiplication factor
#-----------------------
	
# [Eq. 9] min & max limit to the size of each technology
subject to size_limit {y in YEARS_WND diff YEAR_ONE, j in TECHNOLOGIES}:
	f_min [y,j] <= F [y,j] <= f_max [y,j];
	
# [Eq. 10] relation between power and capacity via period capacity factor. This forces max hourly output (e.g. renewables)
subject to capacity_factor_t {y in YEARS_WND diff YEAR_ONE, j in TECHNOLOGIES, t in PERIODS}:
	F_t [y,j, t] <= F [y,j] * c_p_t [y, j, t];
	
# [Eq. 11] relation between mult_t and mult via yearly capacity factor. This one forces total annual output
subject to capacity_factor {y in YEARS_WND diff YEAR_ONE, j in TECHNOLOGIES}:
	sum {t in PERIODS} (F_t [y,j, t] * t_op [t]) <= F [y,j] * c_p [y,j] * total_time;	
		
## Resources
#-----------

# [Eq. 12] Resources availability equation
subject to resource_availability {y in YEARS_WND diff YEAR_ONE, i in RESOURCES}:
	Res [y,i] <= avail [y,i];

# [Eq. 2.12-bis] Constant flow of import for resources listed in SET RES_IMPORT_CONSTANT
var Import_constant {y in YEARS diff YEAR_ONE, RES_IMPORT_CONSTANT} >= 0;
subject to resource_constant_import {y in YEARS_WND diff YEAR_ONE, i in RES_IMPORT_CONSTANT, t in PERIODS}:
	F_t [y, i, t] * t_op [t] = Import_constant [y, i];


## Layers
#--------

# [Eq. 13] Layer balance equation with storage. Layers: input > 0, output < 0. Demand > 0. Storage: in > 0, out > 0;
# output from technologies/resources/storage - input to technologies/storage = demand. Demand has default value of 0 for layers which are not end_uses
subject to layer_balance {y in YEARS_WND diff YEAR_ONE, l in LAYERS, t in PERIODS}:
		sum {i in RESOURCES union TECHNOLOGIES diff STORAGE_TECH } 
		(layers_in_out[y,i, l] * F_t [y,i, t]) 
		+ sum {j in STORAGE_TECH diff STORAGE_DAILY} (Storage_out [y,j, l, t] - Storage_in [y,j, l, t] )
		- End_uses [y, l, t]
		= 0;
	
## Storage	
#---------
	
# [Eq. 14] The level of the storage represents the amount of energy stored at a certain time.
subject to storage_level {y in YEARS_WND diff YEAR_ONE, j in STORAGE_TECH diff STORAGE_DAILY, t in PERIODS}:
	Storage_level [y, j, t] = (if t == 1 then
	 			Storage_level [y, j, card(PERIODS)] * (1.0 -  storage_losses[y,j])
				+ t_op [t] * (   (sum {l in LAYERS: storage_eff_in [y,j,l] > 0}  (Storage_in [y, j, l, t]  * storage_eff_in  [y, j, l])) 
				                   - (sum {l in LAYERS: storage_eff_out [y,j,l] > 0} (Storage_out [y, j, l, t] / storage_eff_out [y, j, l])))
	else
	 			Storage_level [y, j, t-1] * (1.0 -  storage_losses[y, j])
				+ t_op [t] * (   (sum {l in LAYERS: storage_eff_in [y, j,l] > 0}  (Storage_in [y, j, l, t]  * storage_eff_in  [y, j, l])) 
				                   - (sum {l in LAYERS: storage_eff_out [y, j,l] > 0} (Storage_out [y, j, l, t] / storage_eff_out [y, j, l])))
				);

# [Eq. 15] Bounding daily storage
subject to impose_storage {y in YEARS_WND diff YEAR_ONE, j in STORAGE_TECH diff STORAGE_DAILY, t in PERIODS}:
	Storage_level [y, j, t] = F_t [y, j, t];
	
# [Eq. 16] Bounding seasonal storage
subject to limit_energy_stored_to_maximum {y in YEARS_WND diff YEAR_ONE, j in STORAGE_TECH diff STORAGE_DAILY, t in PERIODS}:
	Storage_level [y, j, t] <= F [y, j];# Never exceed the size of the storage unit
	
# [Eqs. 17-18] Each storage technology can have input/output only to certain layers. If incompatible then the variable is set to 0
subject to storage_layer_in {y in YEARS_WND diff YEAR_ONE, j in STORAGE_TECH diff STORAGE_DAILY, l in LAYERS, t in PERIODS}:
	(if storage_eff_in [y, j, l]=0 then  Storage_in [y, j, l, t]  = 0);
subject to storage_layer_out {y in YEARS_WND diff YEAR_ONE, j in STORAGE_TECH diff STORAGE_DAILY, l in LAYERS, t in PERIODS}:
	(if storage_eff_out [y, j, l]=0 then  Storage_out [y, j, l, t]  = 0);
		
# [Eq. 19] limit the Energy to power ratio. 
subject to limit_energy_to_power_ratio {y in YEARS_WND diff YEAR_ONE, j in STORAGE_TECH diff {"BEV_BATT","PHEV_BATT"} diff STORAGE_DAILY, l in LAYERS, t in PERIODS}:
	Storage_in [y, j, l, t] * storage_charge_time[y, j] + Storage_out [y, j, l, t] * storage_discharge_time[y, j] <=  F [y, j] * storage_availability[y, j];

# # [Eq. 19] limit the Energy to power ratio. 
# subject to limit_energy_to_power_ratio_bis {y in YEARS_WND diff YEAR_ONE, i in V2G, j in EVs_BATT_OF_V2G[i] , l in LAYERS, h in HOURS, td in TYPICAL_DAYS}:
# 	Storage_in [y, j, l, h, td] * storage_charge_time[y, j] + (Storage_out [y, j, l, h, td] + layers_in_out[y, i,"ELECTRICITY"]* F_t [y, i, h, td] ) * storage_discharge_time[y, j] <=  (F [y, j] - F_t[y,i,h,td] / vehicule_capacity[y,i] * batt_per_car[y,i] ) * storage_availability[y, j];

## Infrastructure
#----------------

# [Eq. 20] Calculation of losses for each end-use demand type (normally for electricity and DHN)
subject to network_losses {y in YEARS_WND diff YEAR_ONE, eut in END_USES_TYPES, t in PERIODS}:
	Network_losses [y, eut, t] = (sum {j in RESOURCES union TECHNOLOGIES diff STORAGE_TECH: layers_in_out [y,j, eut] > 0} ((layers_in_out[y,j, eut]) * F_t [y, j, t])) * loss_network [y,eut];

# [Eq. 21] Extra grid cost for integrating 1 GW of RE is estimated to 367.8Meuros per GW of intermittent renewable (27beuros to integrate the overall potential) 
subject to extra_grid {y in YEARS_WND diff YEAR_ONE}:
	F [y,"GRID"] >= 1 +  (c_grid_extra / c_inv[y,"GRID"]) *(    (F [y, "WIND_ONSHORE"] + F [y, "WIND_OFFSHORE"] + F [y, "PV"]      )
					                                     - (f_min [y,"WIND_ONSHORE"] + f_min [y,"WIND_OFFSHORE"] + f_min [y,"PV"]) );


# [Eq. 22] DHN: assigning a cost to the network
subject to extra_dhn  {y in YEARS_WND diff YEAR_ONE}:
	F [y, "DHN"] = sum {j in TECHNOLOGIES diff STORAGE_TECH: layers_in_out [y, j,"HEAT_LOW_T_DHN"] > 0} (layers_in_out [y, j,"HEAT_LOW_T_DHN"] * F [y, j]);

## Additional constraints
#------------------------
	
# [Eq. 23] Fix nuclear production constant : 
subject to constantNuc {y in YEARS_WND diff YEAR_ONE, t in PERIODS}:
	F_t [y, "NUCLEAR", t] = Power_nuclear [y];

# [Eq. 24] Operating strategy in mobility passenger (to make model more realistic)
# Each passenger mobility technology (j) has to supply a constant share  (Shares_mobility_passenger[j]) of the passenger mobility demand
subject to operating_strategy_mob_passenger{y in YEARS_WND diff YEAR_ONE, j in TECHNOLOGIES_OF_END_USES_CATEGORY["MOBILITY_PASSENGER"], t in PERIODS}:
	F_t [y, j, t]   = Shares_mobility_passenger [y, j] * (end_uses_input[y, "MOBILITY_PASSENGER"] / total_time);
	
	
# NEW CONSTRAINT to fix the use of trucks (not having FC trucks during summer and other during winter).
# [Eq. 25Â¤ Operating strategy in mobility freight (to make model more realistic)
# Each freight mobility technology (j) has to supply a constant share  (Shares_mobility_freight[j]) of the passenger mobility demand
subject to operating_strategy_mobility_freight{y in YEARS_WND diff YEAR_ONE, j in TECHNOLOGIES_OF_END_USES_CATEGORY["MOBILITY_FREIGHT"], t in PERIODS}:
	F_t [y, j, t] = Shares_mobility_freight [y, j] * (end_uses_input[y, "MOBILITY_FREIGHT"] / total_time);
	
# [Eq. 26] To impose a constant share in the mobility
subject to Freight_shares {y in YEARS_WND diff YEAR_ONE} :
	Share_freight_train [y] + Share_freight_road [y] + Share_freight_boat [y] = 1;

	
## Thermal solar & thermal storage:

# [Eq. 26] relation between decentralised thermal solar power and capacity via period capacity factor.
subject to thermal_solar_capacity_factor {y in YEARS_WND diff YEAR_ONE, j in TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}, t in PERIODS}:
	F_t_solar [y, j, t] <= F_solar[y, j] * c_p_t[y, "DEC_SOLAR", t];
	
# [Eq. 27] Overall thermal solar is the sum of specific thermal solar 	
subject to thermal_solar_total_capacity {y in YEARS_WND diff YEAR_ONE}:
	F [y, "DEC_SOLAR"] >= sum {j in TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}} F_solar[y, j];

# [Eq. 28]: Decentralised thermal technology must supply a constant share of heat demand.
subject to decentralised_heating_balance  {y in YEARS_WND diff YEAR_ONE, j in TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}, i in TS_OF_DEC_TECH[j], t in PERIODS}:
	F_t [y, j, t] + F_t_solar [y, j, t] + sum {l in LAYERS } ( Storage_out [y, i, l, t] - Storage_in [y, i, l, t])  
		= Shares_lowT_dec[y, j] * (end_uses_input[y,"HEAT_LOW_T_HW"] / total_time + end_uses_input[y,"HEAT_LOW_T_SH"] * heating_month [t] / t_op [t]);

## EV storage :

# [Eq. 32] Compute the equivalent size of V2G batteries based on the installed capacity, the capacity per vehicles and the battery capacity per EVs technology
subject to EV_storage_size {y in YEARS_WND diff YEAR_ONE, j in V2G, i in EVs_BATT_OF_V2G[j]}:
	F [y, i] = F[y,j] / vehicule_capacity [y,j] * batt_per_car[y,j];# Battery size proportional to the number of cars
	
# [Eq. 33]  Impose EVs to be supplied by their battery.
subject to EV_storage_for_V2G_demand {y in YEARS_WND diff YEAR_ONE, j in V2G, i in EVs_BATT_OF_V2G[j], t in PERIODS}:
	Storage_out [y, i,"ELECTRICITY",t] >=  - layers_in_out[y,j,"ELECTRICITY"]* F_t [y, j, t];

# # [Eq. 2.31-bis]  Impose a minimum state of charge at some hours of the day:
# subject to ev_minimum_state_of_charge {j in V2G, i in EVs_BATT_OF_V2G[j], y in YEARS_WND diff YEAR_ONE,  t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t]}:
# 	Storage_level [y, i, t] >=  F [y, i] * state_of_charge_ev [i, h];
		
## Peak demand :

# [Eq. 34] Peak in decentralized heating
subject to peak_lowT_dec {y in YEARS_WND diff YEAR_ONE, j in TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}, t in PERIODS}:
	F [y, j] >= peak_sh_factor * F_t [y, j, t] ;

# [Eq. 35] Calculation of max heat demand in DHN (1st constrain required to linearised the max function)
var Max_Heat_Demand {YEARS} >= 0;
subject to max_dhn_heat_demand {y in YEARS_WND diff YEAR_ONE, t in PERIODS}:
	Max_Heat_Demand [y] >= End_uses [y, "HEAT_LOW_T_DHN", t];
# Peak in DHN
subject to peak_lowT_dhn {y in YEARS_WND diff YEAR_ONE}:
	sum {j in TECHNOLOGIES_OF_END_USES_TYPE ["HEAT_LOW_T_DHN"], i in STORAGE_OF_END_USES_TYPES["HEAT_LOW_T_DHN"]} (F [y, j] + F[y, i]/storage_discharge_time[y, i]) >= peak_sh_factor * Max_Heat_Demand [y];
		

## Adaptation for the case study: Constraints needed for the application to Switzerland (not needed in standard LP formulation)
#-----------------------------------------------------------------------------------------------------------------------

# [Eq. 34]  constraint to reduce the GWP subject to gwp_limit :
subject to minimum_GWP_reduction  {y in YEARS_WND diff YEAR_ONE} :
	TotalGWP [y] <= gwp_limit [y];

# [Eq. XX] Constraint to limit the emissions below a budget (gwp_limit_transition) 
subject to minimum_GWP_transition  : # category: GWP_calc
	TotalGWPTransition <= gwp_limit_transition;
		
# [Eq. 36] Definition of min/max output of each technology as % of total output in a given layer. 
subject to f_max_perc {y in YEARS_WND diff YEAR_ONE, eut in END_USES_TYPES, j in TECHNOLOGIES_OF_END_USES_TYPE[eut]}:
	sum {t in PERIODS} (F_t [y,j,t] * t_op[t]) <= fmax_perc [y,j] * sum {j2 in TECHNOLOGIES_OF_END_USES_TYPE[eut], t in PERIODS} (F_t [y,j2, t] * t_op[t]);
subject to f_min_perc {y in YEARS_WND diff YEAR_ONE, eut in END_USES_TYPES, j in TECHNOLOGIES_OF_END_USES_TYPE[eut]}:
	sum {t in PERIODS} (F_t [y,j,t] * t_op[t]) >= fmin_perc [y,j] * sum {j2 in TECHNOLOGIES_OF_END_USES_TYPE[eut], t in PERIODS} (F_t [y,j2, t] * t_op[t]);

# [Eq. 39] Energy efficiency is a fixed cost
subject to extra_efficiency {y in YEARS_WND diff YEAR_ONE}:
	F [y,"EFFICIENCY"] = efficiency [y];	

# [Eq. 38] Limit electricity import capacity
subject to max_elec_import {y in YEARS_WND diff YEAR_ONE, t in PERIODS}:
	F_t [y, "ELECTRICITY", t] * t_op [t] <= elec_max_import_capa [y];
	
# [Eq. 39] Limit surface area for solar
subject to solar_area_limited {y in YEARS_WND diff YEAR_ONE} :
	F[y, "PV"] / power_density_pv + ( F [y, "DEC_SOLAR"] + F [y, "DHN_SOLAR"] ) / power_density_solar_thermal <= solar_area [y];

## Define technologies change during phases:
#-------------------------------------------

# [Eq. XX] Relate the installed capacity between years
# --> Check p2 HERE --> OK
subject to phase_new_build {p in PHASE_WND, y_start in PHASE_START[p], y_stop in PHASE_STOP[p], i in TECHNOLOGIES}:
	F[y_stop,i] = F[y_start,i] + F_new[p,i] - F_old [p,i] 
  											     - sum {p2 in {PHASE_WND union PHASE_UP_TO union {"2020_2025"}}} F_decom[p,p2,i];

# [Eq. XX] Impose decom_allowed to 0 when not physical
# --> Check p_built HERE --> Check if p_decom in PHASE ne change pas les résultats !!!!!!!!
subject to define_f_decom_properly {p_decom in PHASE, p_built in PHASE union {"2020_2025"}, i in TECHNOLOGIES}:
	if decom_allowed[p_decom,p_built,i] == 0 then F_decom [p_decom,p_built,i] = 0;

# [Eq. XX] Intialise the first phase based on YEAR_2015 results
subject to F_new_initialisation {tech in TECHNOLOGIES}:
	F_new ["2020_2025",tech] = F["YEAR_2025",tech]; # Generate F_new2015_2020

# [Eq. XX] Impose the exact capacity that reaches its lifetime
# --> Check p2 HERE --> OK : p2 in PHASE
subject to phase_out_assignement {i in TECHNOLOGIES, p in PHASE_WND, age in AGE [i,p]}:
	F_old [p,i] = if (age == "STILL_IN_USE") then  0 #<=> no problem
					else F_new [age,i]    - sum {p2 in PHASE_WND union PHASE_UP_TO} F_decom [p2,age,i];

subject to no_decom_if_no_built {i in TECHNOLOGIES, p in PHASE_WND union PHASE_UP_TO union {"2020_2025"}}:
	F_new [p, i] -  sum {p2 in PHASE_WND union PHASE_UP_TO} F_decom [p2,p,i] >= 0;

# Limit renovation rate:
# [Eq. XX] Define the amount of change between years
var F_used_year_start{YEARS_WND, TECHNOLOGIES} >= 0;
subject to compute_F_used_year_start{p in PHASE_WND, y_start in PHASE_START[p] diff YEAR_ONE, j in TECHNOLOGIES} :
	F_used_year_start[y_start,j] = (sum {t in PERIODS} F_t [y_start,j, t] * t_op[t]);

subject to delta_change_definition {p in PHASE_WND, y_start in PHASE_START[p], y_stop in PHASE_STOP[p], j in TECHNOLOGIES} :
	Delta_change [p,j] >= F_used_year_start[y_start,j] - (sum {t in PERIODS} F_t [y_stop,j, t] * t_op[t]) ;

# [Eq. XX] Limit the amount of change for low temperature heating
subject to limit_changes_heat {p in PHASE_WND union PHASE_UP_TO, y_start in PHASE_START[p], y_stop in PHASE_STOP[p]} :
	sum {euc in END_USES_TYPES_OF_CATEGORY["HEAT_LOW_T"], j in TECHNOLOGIES_OF_END_USES_TYPE[euc]} Delta_change[p,j] 
		<= limit_LT_renovation * (end_uses_input[y_start,"HEAT_LOW_T_HW"] + end_uses_input[y_start,"HEAT_LOW_T_SH"]) ;


# [Eq. XX] Limit the amount of change for passenger mobility
subject to limit_changes_mob {p in PHASE_WND union PHASE_UP_TO, y_start in PHASE_START[p], y_stop in PHASE_STOP[p]} :
	sum {euc in END_USES_TYPES_OF_CATEGORY["MOBILITY_PASSENGER"], j in TECHNOLOGIES_OF_END_USES_TYPE[euc]} Delta_change[p,j] 
		<= limit_pass_mob_changes * (end_uses_input[y_start,"MOBILITY_PASSENGER"]);

# [Eq. XX] Limit the amount of change for freight mobility
subject to limit_changes_freight {p in PHASE_WND union PHASE_UP_TO, y_start in PHASE_START[p], y_stop in PHASE_STOP[p]} :
	sum {euc in END_USES_TYPES_OF_CATEGORY["MOBILITY_FREIGHT"], j in TECHNOLOGIES_OF_END_USES_TYPE[euc]} Delta_change[p,j] 
		<= limit_freight_changes * (end_uses_input[y_start,"MOBILITY_FREIGHT"]);

## Compute cost during phase:
#----------------------------
	
# [Eq. XX] Compute capital expenditure for transition
subject to total_capex: # category: COST_calc
	C_tot_capex = sum{p in PHASE_WND union PHASE_UP_TO union {"2020_2025"}} C_inv_phase [p]
				 - sum {i in TECHNOLOGIES} C_inv_return [i];# euros_2015

# [Eq. XX] Compute the total investment cost per phase
subject to investment_computation {p in PHASE_WND union PHASE_UP_TO union {"2020_2025"}, y_start in PHASE_START[p], y_stop in PHASE_STOP[p]}:
	 C_inv_phase [p] = sum {i in TECHNOLOGIES} F_new [p,i] * annualised_factor [p] * ( c_inv [y_start,i] + c_inv [y_stop,i] ) / 2; #In bÃ¢â€šÂ¬

subject to investment_computation_tech {p in PHASE_WND union PHASE_UP_TO union {"2020_2025"}, y_start in PHASE_START[p], y_stop in PHASE_STOP[p], i in TECHNOLOGIES}:
	 C_inv_phase_tech [p,i] = F_new [p,i] * annualised_factor [p] * ( c_inv [y_start,i] + c_inv [y_stop,i] ) / 2; #In bÃ¢â€šÂ¬

subject to investment_return {i in TECHNOLOGIES}:
	C_inv_return [i] = sum {p in PHASE_WND union PHASE_UP_TO union {"2020_2025"},y_start in PHASE_START [p],y_stop in PHASE_STOP [p]} 
	( remaining_years [i,p] / lifetime [y_start,i] * (F_new [p,i] - sum {p2 in PHASE_WND union PHASE_UP_TO} (F_decom [p2,p,i]) )  * annualised_factor [p] * ( c_inv [y_start,i] + c_inv [y_stop,i] ) / 2 ) ;

# [Eq. XX] Compute operating cost for transition
subject to Opex_tot_cost_calculation :# category: COST_calc
	C_tot_opex = C_opex["YEAR_2025"] 
				 + t_phase *  sum {p in PHASE_WND union PHASE_UP_TO,y_start in PHASE_START [p],y_stop in PHASE_STOP [p]} ( 
					                 (C_opex [y_start] + C_opex [y_stop])/2 *annualised_factor[p] ); #In euros_2015

# [Eq. XX] Compute operating cost for years
subject to Opex_cost_calculation{y in YEARS_WND union YEARS_UP_TO} : # category: COST_calc
	C_opex [y] = sum {j in TECHNOLOGIES} C_maint [y,j] + sum {i in RESOURCES} C_op [y,i]; #In â‚¬_y

subject to operation_computation_tech {p in PHASE_WND union PHASE_UP_TO, y_start in PHASE_START[p], y_stop in PHASE_STOP[p], i in TECHNOLOGIES}:
	C_op_phase_tech [p,i] = t_phase *   ((C_maint [y_start,i] + C_maint [y_stop,i])/2 *annualised_factor[p] ); #In euros_2015

subject to operation_computation_res {p in PHASE_WND union PHASE_UP_TO, y_start in PHASE_START[p], y_stop in PHASE_STOP[p], i in RESOURCES}:
	C_op_phase_res [p,i] = t_phase *   ((C_op [y_start,i] + C_op [y_stop,i])/2 *annualised_factor[p] ); #In euros_2015

# [Eq. XX] We could either limit the max investment on a period or fix that these investments must be equals in â‚¬_2015
subject to maxInvestment {p in PHASE_WND}:
	 C_inv_phase [p] <= max_inv_phase[p]; #In bÃ¢â€šÂ¬
# subject to sameInvestmentPerPhase {p in PHASE}:
# 	 C_inv_phase [p] = Fixed_phase_investment; #In bÃ¢â€šÂ¬

##########################
### OBJECTIVE FUNCTION ###
##########################


# var TotalTransitionCost >=0; #Overall transition cost.
# subject to New_totalTransitionCost_calculation :
# 	TotalTransitionCost = C_tot_capex + C_tot_opex;
# minimize obj: TotalTransitionCost;
# Can choose between TotalTransitionCost_calculation and TotalGWP and TotalCost
minimize  TotalTransitionCost: C_tot_capex + C_tot_opex + Gwp_tot_cost;#sum {y in YEARS} TotalCost [y];
# subject to New_totalTransitionCost_calculation :
# 	TotalTransitionCost = C_tot_capex + C_tot_opex;