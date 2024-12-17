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

#########################
###  SETS [Figure 3]  ###
#########################

## MAIN SETS: Sets whose elements are input directly in the data file
set PERIODS := 1 .. 8760; # time periods (hours of the year)
set HOURS := 1 .. 24; # hours of the day
set TYPICAL_DAYS:= 1 .. 12; # typical days
set T_H_TD within {PERIODS, HOURS, TYPICAL_DAYS}; # set linking periods, hours, days, typical days
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

##Additional SETS added just to simplify equations.
set TYPICAL_DAY_OF_PERIOD {t in PERIODS} := setof {h in HOURS, td in TYPICAL_DAYS: (t,h,td) in T_H_TD} td; #TD_OF_PERIOD(T)
set HOUR_OF_PERIOD {t in PERIODS} := setof {h in HOURS, td in TYPICAL_DAYS: (t,h,td) in T_H_TD} h; #H_OF_PERIOD(T)

## Additional SETS: only needed for printing out results (not represented in Figure 3).
set COGEN within TECHNOLOGIES; # cogeneration tech
set BOILERS within TECHNOLOGIES; # boiler tech

#NEW DEPENDENT:
set AGE {TECHNOLOGIES,PHASE} within PHASE union {"2010_2015"} union {"STILL_IN_USE"};


#################################
### PARAMETERS [Tables 1-2]   ###
#################################

## NEW PARAMETERS FOR PATHWAY:
param max_inv_phase {PHASE} default Infinity;#Unlimited
param t_phase ;
param diff_2015_phase {PHASE};
param gwp_limit_transition >=0 default Infinity; #To limit CO2 emissions over the transition
param decom_allowed {PHASE,PHASE union {"2010_2015"},TECHNOLOGIES} default 0;
param remaining_years {TECHNOLOGIES,PHASE} >=0;
param limit_LT_renovation >= 0;
param limit_pass_mob_changes >= 0;
param limit_freight_changes >= 0;
param efficiency {YEARS} >=0 default 1;

## Parameters added to include time series in the model [Table 1]
param electricity_time_series {HOURS, TYPICAL_DAYS} >= 0, <= 1; # %_elec [-]: factor for sharing lighting across typical days (adding up to 1)
param heating_time_series {HOURS, TYPICAL_DAYS} >= 0, <= 1; # %_sh [-]: factor for sharing space heating across typical days (adding up to 1)
param mob_pass_time_series {HOURS, TYPICAL_DAYS} >= 0, <= 1; # %_pass [-]: factor for sharing passenger transportation across Typical days (adding up to 1) based on https://www.fhwa.dot.gov/policy/2013cpr/chap1.cfm
param mob_freight_time_series {HOURS, TYPICAL_DAYS} >= 0, <= 1; # %_fr [-]: factor for sharing freight transportation across Typical days (adding up to 1)
param c_p_t {TECHNOLOGIES, HOURS, TYPICAL_DAYS} default 1; #Hourly capacity factor [-]. If = 1 (default value) <=> no impact.

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
param t_op {HOURS, TYPICAL_DAYS} default 1;# [h]: operating time 
param f_max {YEARS,TECHNOLOGIES} >= 0 default 0; # Maximum feasible installed capacity [GW], refers to main output. storage level [GWh] for STORAGE_TECH
param f_min {YEARS,TECHNOLOGIES} >= 0 default 0; # Minimum feasible installed capacity [GW], refers to main output. storage level [GWh] for STORAGE_TECH
param fmax_perc {YEARS,TECHNOLOGIES} >= 0, <= 1 default 1; # value in [0,1]: this is to fix that a technology can at max produce a certain % of the total output of its sector over the entire year
param fmin_perc {YEARS,TECHNOLOGIES} >= 0, <= 1 default 0; # value in [0,1]: this is to fix that a technology can at min produce a certain % of the total output of its sector over the entire year
param avail {YEARS,RESOURCES} >= 0 default 0; # Yearly availability of resources [GWh/y]
param c_op {YEARS,RESOURCES} >= 0 default 0; # cost of resources in the different periods [MCHF/GWh]
param vehicule_capacity {YEARS,TECHNOLOGIES} >=0, default 0; #  veh_capa [capacity/vehicles] Average capacity (pass-km/h or t-km/h) per vehicle. It makes the link between F and the number of vehicles
param peak_sh_factor >= 0;   # %_Peak_sh [-]: ratio between highest yearly demand and highest TDs demand
param layers_in_out {YEARS,RESOURCES union TECHNOLOGIES diff STORAGE_TECH , LAYERS}; # f: input/output Resources/Technologies to Layers. Reference is one unit ([GW] or [Mpkm/h] or [Mtkm/h]) of (main) output of the resource/technology. input to layer (output of technology) > 0.
param c_inv {YEARS,TECHNOLOGIES} >= 0 default 0; # Specific investment cost [MCHF/GW].[MCHF/GWh] for STORAGE_TECH
param c_maint {YEARS,TECHNOLOGIES} >= 0 default 0; # O&M cost [MCHF/GW/year]: O&M cost does not include resource (fuel) cost. [MCHF/GWh/year] for STORAGE_TECH
param lifetime {YEARS,TECHNOLOGIES} >= 0 default 0; # n: lifetime [years]
param tau {y in YEARS, i in TECHNOLOGIES} # Annualisation factor ([-]) for each different technology [Eq. 2]
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
param state_of_charge_ev {EVs_BATT,HOURS} >= 0, default 0; # Minimum state of charge of the EV during the day. 
param c_grid_extra >=0; # # Cost to reinforce the grid due to IRE penetration [Meuros/GW of (PV + Wind)].
param elec_max_import_capa  {YEARS} >=0;
param solar_area	 {YEARS} >= 0; # Maximum land available for PV deployment [km2]
param power_density_pv >=0 default 0;# Maximum power irradiance for PV.
param power_density_solar_thermal >=0 default 0;# Maximum power irradiance for solar thermal.


##Additional parameter (not presented in the paper)
param total_time := sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (t_op [h, td]); # [h]. added just to simplify equations

# NEW : PARAM DEPEN?DENT:
param annualised_factor {p in PHASE} := 1 / ((1 + i_rate)^diff_2015_phase[p] ); # Annualisation factor for each different technology

#################################
###  VARIABLES [Tables 3-4]   ###
#################################

## NEW VARIABLES FOR PATHWAY:
var F_new {PHASE union {"2010_2015"}, TECHNOLOGIES} >= 0; #[GW/GWh] Accounts for the additional new capacity installed in a new phase
var F_decom {PHASE,PHASE union {"2010_2015"}, TECHNOLOGIES} >= 0; #[GW] Accounts for the decommissioned capacity in a new phase
var F_old {PHASE,TECHNOLOGIES} >=0, default 0; #[GW] Retired capacity during a phase with respect to the main output
var C_inv_phase {PHASE} >=0; #[M€/GW] Phase total annualised investment cost
var C_inv_return {TECHNOLOGIES} >=0; #[M€] Money given back for existing technologies after 2050 to compute the objective function
#var Fixed_phase_investment;
var C_opex {YEARS} >=0;
var C_tot_opex >=0;
var C_tot_capex >=0;
var TotalTransitionCost >=0; #Overall transition cost.
var TotalGWPTransition >=0;
var Delta_change {PHASE,TECHNOLOGIES} >=0;

##Independent variables [Table 3] :
var Share_mobility_public {y in YEARS} >= share_mobility_public_min [y], <= share_mobility_public_max [y]; # %_Public: Ratio [0; 1] public mobility over total passenger mobility
var Share_freight_train {y in YEARS}, >= share_freight_train_min [y], <= share_freight_train_max [y]; # %_Rail: % of freight mobility attributed to train
var Share_freight_road {y in YEARS}, >= share_freight_road_min [y], <= share_freight_road_max [y]; # %_Rail: % of freight mobility attributed to train
var Share_freight_boat {y in YEARS}, >= share_freight_boat_min [y], <= share_freight_boat_max [y]; # %_Rail: % of freight mobility attributed to train
var Share_heat_dhn {y in YEARS}, >= share_heat_dhn_min [y], <= share_heat_dhn_max [y]; # %_DHN: Ratio [0; 1] centralized over total low-temperature heat
var F {YEARS, TECHNOLOGIES} >= 0; # F: Installed capacity ([GW]) with respect to main output (see layers_in_out). [GWh] for STORAGE_TECH.
var F_t {YEARS, RESOURCES union TECHNOLOGIES, HOURS, TYPICAL_DAYS} >= 0; # F_t: Operation in each period [GW] or, for STORAGE_TECH, storage level [GWh]. multiplication factor with respect to the values in layers_in_out table. Takes into account c_p
var Storage_in {YEARS, i in STORAGE_TECH, LAYERS, HOURS, TYPICAL_DAYS} >= 0; # Sto_in [GW]: Power input to the storage in a certain period
var Storage_out {YEARS, i in STORAGE_TECH, LAYERS, HOURS, TYPICAL_DAYS} >= 0; # Sto_out [GW]: Power output from the storage in a certain period
var Power_nuclear {YEARS}  >=0; # [GW] P_Nuc: Constant load of nuclear
var Shares_mobility_passenger {YEARS, TECHNOLOGIES_OF_END_USES_CATEGORY["MOBILITY_PASSENGER"]} >=0; # %_MobPass [-]: Constant share of passenger mobility
# NEW VARIABLE
var Shares_mobility_freight {YEARS, TECHNOLOGIES_OF_END_USES_CATEGORY["MOBILITY_FREIGHT"]} >=0; # %_Freight [-]: Constant share of passenger mobility
var Shares_lowT_dec {YEARS, TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}}>=0 ; # %_HeatDec [-]: Constant share of heat Low T decentralised + its specific thermal solar
var F_solar         {YEARS, TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}} >=0; # F_sol [GW]: Solar thermal installed capacity per heat decentralised technologies
var F_t_solar       {YEARS, TECHNOLOGIES_OF_END_USES_TYPE["HEAT_LOW_T_DECEN"] diff {"DEC_SOLAR"}, h in HOURS, td in TYPICAL_DAYS} >= 0; # F_t_sol [GW]: Solar thermal operating per heat decentralised technologies

##Dependent variables [Table 4] :
var End_uses {YEARS, LAYERS, HOURS, TYPICAL_DAYS} >= 0; #EndUses [GW]: total demand for each type of end-uses (hourly power). Defined for all layers (0 if not demand). [Mpkm] or [Mtkm] for passenger or freight mobility.
var TotalCost {YEARS} >= 0; # C_tot [ktCO2-eq./year]: Total GWP emissions in the system.
var C_inv {YEARS, TECHNOLOGIES} >= 0; #C_inv [MCHF]: Total investment cost of each technology
var C_maint {YEARS, TECHNOLOGIES} >= 0; #C_maint [MCHF/year]: Total O&M cost of each technology (excluding resource cost)
var C_op {YEARS, RESOURCES} >= 0; #C_op [MCHF/year]: Total O&M cost of each resource
var TotalGWP {YEARS} >= 0; # GWP_tot [ktCO2-eq./year]: Total global warming potential (GWP) emissions in the system
var GWP_constr {YEARS, TECHNOLOGIES} >= 0; # GWP_constr [ktCO2-eq.]: Total emissions of the technologies
var GWP_op {YEARS, RESOURCES} >= 0; #  GWP_op [ktCO2-eq.]: Total yearly emissions of the resources [ktCO2-eq./y]
var Network_losses {YEARS, END_USES_TYPES, HOURS, TYPICAL_DAYS} >= 0; # Net_loss [GW]: Losses in the networks (normally electricity grid and DHN)
var Storage_level {YEARS, STORAGE_TECH, PERIODS} >= 0; # Sto_level [GWh]: Energy stored at each period

#########################################
###      CONSTRAINTS Eqs [1-42]       ###
#########################################



## End-uses demand calculation constraints 
#-----------------------------------------

# [Figure 4] From annual energy demand to hourly power demand. End_uses is non-zero only for demand layers.
subject to end_uses_t {y in YEARS, l in LAYERS, h in HOURS, td in TYPICAL_DAYS}:
	End_uses [y,l, h, td] = (if l == "ELECTRICITY" 
		then
			(end_uses_input[y,l] / total_time + end_uses_input[y,"LIGHTING"] * electricity_time_series [h, td] / t_op [h, td] ) + Network_losses [y,l,h,td]
		else (if l == "HEAT_LOW_T_DHN" then
			(end_uses_input[y,"HEAT_LOW_T_HW"] / total_time + end_uses_input[y,"HEAT_LOW_T_SH"] * heating_time_series [h, td] / t_op [h, td] ) * Share_heat_dhn [y] + Network_losses [y,l,h,td]
		else (if l == "HEAT_LOW_T_DECEN" then
			(end_uses_input[y,"HEAT_LOW_T_HW"] / total_time + end_uses_input[y,"HEAT_LOW_T_SH"] * heating_time_series [h, td] / t_op [h, td] ) * (1 - Share_heat_dhn [y])
		else (if l == "MOB_PUBLIC" then
			(end_uses_input[y,"MOBILITY_PASSENGER"] * mob_pass_time_series [h, td] / t_op [h, td]  ) * Share_mobility_public [y]
		else (if l == "MOB_PRIVATE" then
			(end_uses_input[y,"MOBILITY_PASSENGER"] * mob_pass_time_series [h, td] / t_op [h, td]  ) * (1 - Share_mobility_public [y])
		else (if l == "MOB_FREIGHT_RAIL" then
			(end_uses_input[y,"MOBILITY_FREIGHT"]   * mob_freight_time_series [h, td] / t_op [h, td] ) *  Share_freight_train [y]
		else (if l == "MOB_FREIGHT_ROAD" then
			(end_uses_input[y,"MOBILITY_FREIGHT"]   * mob_freight_time_series [h, td] / t_op [h, td] ) *  Share_freight_road [y]
		else (if l == "MOB_FREIGHT_BOAT" then
			(end_uses_input[y,"MOBILITY_FREIGHT"]   * mob_freight_time_series [h, td] / t_op [h, td] ) *  Share_freight_boat [y]
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
# [Eq. 3] Investment cost of each technology
# [Eq. 4] O&M cost of each technology
# [Eq. 5] Total cost of each resource

## Emissions
#-----------

# [Eq. 6]
# [Eq. 7]
# [Eq. 8]
# [Eq. XX] total transition gwp calculation

## Multiplication factor
#-----------------------
	
# [Eq. 9] min & max limit to the size of each technology

# [Eq. 10] relation between power and capacity via period capacity factor. This forces max hourly output (e.g. renewables)
# [Eq. 11] relation between mult_t and mult via yearly capacity factor. This one forces total annual output
		
## Resources
#-----------

# [Eq. 12] Resources availability equation
# [Eq. 2.12-bis] Constant flow of import for resources listed in SET RES_IMPORT_CONSTANT
var Import_constant {y in YEARS, RES_IMPORT_CONSTANT} >= 0;


## Layers
#--------

# [Eq. 13] Layer balance equation with storage. Layers: input > 0, output < 0. Demand > 0. Storage: in > 0, out > 0;
	
## Storage	
#---------
	
# [Eq. 14] The level of the storage represents the amount of energy stored at a certain time.
# [Eq. 15] Bounding daily storage
# [Eq. 16] Bounding seasonal storage

# [Eqs. 17-18] Each storage technology can have input/output only to certain layers. If incompatible then the variable is set to 0
# [Eq. 19] limit the Energy to power ratio. 
# [Eq. 19] limit the Energy to power ratio. 
subject to limit_energy_to_power_ratio_bis {y in YEARS, i in V2G, j in EVs_BATT_OF_V2G[i] , l in LAYERS, h in HOURS, td in TYPICAL_DAYS}:
	Storage_in [y, j, l, h, td] * storage_charge_time[y, j] + (Storage_out [y, j, l, h, td] + layers_in_out[y, i,"ELECTRICITY"]* F_t [y, i, h, td] ) * storage_discharge_time[y, j] <=  F [y, j] * storage_availability[y, j];

## Infrastructure
#----------------

# [Eq. 20] Calculation of losses for each end-use demand type (normally for electricity and DHN)
# [Eq. 21] Extra grid cost for integrating 1 GW of RE is estimated to 367.8Meuros per GW of intermittent renewable (27beuros to integrate the overall potential) 
# [Eq. 22] DHN: assigning a cost to the network

## Additional constraints
#------------------------
	
# [Eq. 23] Fix nuclear production constant : 
# [Eq. 24] Operating strategy in mobility passenger (to make model more realistic)
# NEW CONSTRAINT to fix the use of trucks (not having FC trucks during summer and other during winter).
# [Eq. 25Â¤ Operating strategy in mobility freight (to make model more realistic)
# [Eq. 26] To impose a constant share in the mobility
	
## Thermal solar & thermal storage:

# [Eq. 26] relation between decentralised thermal solar power and capacity via period capacity factor.
# [Eq. 27] Overall thermal solar is the sum of specific thermal solar 	

# [Eq. 28]: Decentralised thermal technology must supply a constant share of heat demand.

## EV storage :

# [Eq. 32] Compute the equivalent size of V2G batteries based on the installed capacity, the capacity per vehicles and the battery capacity per EVs technology
	
# [Eq. 33]  Impose EVs to be supplied by their battery.
	
# [Eq. 2.31-bis]  Impose a minimum state of charge at some hours of the day:

		
## Peak demand :

# [Eq. 34] Peak in decentralized heating
# [Eq. 35] Calculation of max heat demand in DHN (1st constrain required to linearised the max function)
var Max_Heat_Demand {YEARS} >= 0;
		

## Adaptation for the case study: Constraints needed for the application to Switzerland (not needed in standard LP formulation)
#-----------------------------------------------------------------------------------------------------------------------

# [Eq. 34]  constraint to reduce the GWP subject to gwp_limit :
# [Eq. XX] Constraint to limit the emissions below a budget (gwp_limit_transition) 


# [Eq. 35] Minimum share of RE in primary energy supply
		
# [Eq. 36] Definition of min/max output of each technology as % of total output in a given layer. 

# [Eq. 39] Energy efficiency is a fixed cost

# [Eq. 38] Limit electricity import capacity
	
# [Eq. 39] Limit surface area for solar

# [Eq. XX] Force the system to consume all the WASTE available.


## Define technologies change during phases:
#-------------------------------------------

# [Eq. XX] Relate the installed capacity between years
# [Eq. XX] Impose decom_allowed to 0 when not physical

# [Eq. XX] Intialise the first phase based on YEAR_2015 results
# [Eq. XX] Impose the exact capacity that reaches its lifetime
				;


# Limit renovation rate:
# [Eq. XX] Define the amount of change between years 
# [Eq. XX] Limit the amount of change for low temperature heating
# [Eq. XX] Limit the amount of change for passenger mobility
# [Eq. XX] Limit the amount of change for freight mobility

## Compute cost during phase:
#----------------------------

# [Eq. XX] Total transition cost = capex + opex
subject to New_totalTransitionCost_calculation :
	TotalTransitionCost = C_tot_capex + C_tot_opex;
	
# [Eq. XX] Compute capital expenditure for transition
subject to total_capex: # category: COST_calc
	C_tot_capex = sum {i in TECHNOLOGIES} C_inv ["YEAR_2015",i] # 2015 investment
				 + sum{p in PHASE} C_inv_phase [p]
				 - sum {i in TECHNOLOGIES} C_inv_return [i];# euros_2015
				 
# [Eq. XX] Compute operating cost for transition
subject to Opex_tot_cost_calculation :# category: COST_calc
	C_tot_opex = C_opex["YEAR_2015"] 
				 + t_phase *  sum {p in PHASE,y_start in PHASE_START [p],y_stop in PHASE_STOP [p]} ( 
					                 (C_opex [y_start] + C_opex [y_stop])/2 *annualised_factor[p] ); #In euros_2015

# [Eq. XX] Compute operating cost for years
subject to Opex_cost_calculation{y in YEARS} : # category: COST_calc
	C_opex [y] = sum {j in TECHNOLOGIES} C_maint [y,j] + sum {i in RESOURCES} C_op [y,i]; #In â‚¬_y

					
# [Eq. XX] Compute the total investment cost per phase
subject to investment_computation {p in PHASE, y_start in PHASE_START[p], y_stop in PHASE_STOP[p]}:
	 C_inv_phase [p] = sum {i in TECHNOLOGIES} F_new [p,i] * annualised_factor [p] * ( c_inv [y_start,i] + c_inv [y_stop,i] ) / 2; #In bÃ¢â€šÂ¬

# [Eq. XX] We could either limit the max investment on a period or fix that these investments must be equals in â‚¬_2015
subject to maxInvestment {p in PHASE}:
	 C_inv_phase [p] <= max_inv_phase[p]; #In bÃ¢â€šÂ¬

# [Eq. XX] 
subject to investment_return {i in TECHNOLOGIES}:
	C_inv_return [i] = sum {p in PHASE,y_start in PHASE_START [p],y_stop in PHASE_STOP [p]} ( remaining_years [i,p] / lifetime [y_start,i] * F_new [p,i] * annualised_factor [p] * ( c_inv [y_start,i] + c_inv [y_stop,i] ) / 2 ) ;





##########################
### OBJECTIVE FUNCTION ###
##########################



# Can choose between TotalTransitionCost_calculation and TotalGWP and TotalCost
minimize obj:  TotalTransitionCost;#sum {y in YEARS} TotalCost [y];

