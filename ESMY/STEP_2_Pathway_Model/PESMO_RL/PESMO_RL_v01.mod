# NEW : Param for Reinforcement Learning
param allow_foss >=0.0, <= 1.0 default 1.0; # Parameter to symbolise the action to forbid (or to allow) the use of fossil fuels

set ENERGY_MIX := (RESOURCES diff {'ELEC_EXPORT','CO2_EMISSIONS','CO2_ATM','CO2_INDUSTRY','CO2_CAPTURED'}); # Set of resources considered in the primary energy mix

set NRE_RESOURCES := (ENERGY_MIX diff {RE_RESOURCES}); # Set of non-renewable resources

subject to limit_use_fossil{y in YEARS_WND diff YEAR_ONE}:
	sum {i in NRE_RESOURCES, t in PERIODS} (F_t [y,i, t] * t_op [t]) <= allow_foss * sum {i in ENERGY_MIX, t in PERIODS} (F_t [y,i, t] * t_op [t]);