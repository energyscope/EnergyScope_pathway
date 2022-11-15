# NEW : Param for Reinforcement Learning
param allow_foss >=0.0, <= 1.0 default 1.0; # Parameter to symbolise the action to forbid (or to allow) the use of fossil fuels

set ENERGY_MIX := (RESOURCES diff {'ELEC_EXPORT','CO2_EMISSIONS','CO2_ATM','CO2_INDUSTRY','CO2_CAPTURED'}); # Set of resources considered in the primary energy mix

set NRE_RESOURCES := (ENERGY_MIX diff {RE_RESOURCES}); # Set of non-renewable resources

param conso_energy_sector {END_USES_CATEGORIES} >= 0.1, <= 0.2 default 0.2; # Parameter to symbolise the action to forbid (or to allow) the use of fossil fuels, in each end_uses_sectors

subject to limit_use_fossil{y in YEARS_WND diff YEAR_ONE}:
	sum {i in NRE_RESOURCES, t in PERIODS} (F_t [y,i, t] * t_op [t]) <= allow_foss * sum {i in ENERGY_MIX, t in PERIODS} (F_t [y,i, t] * t_op [t]);

var cons_sector {YEARS_WND diff YEAR_ONE, END_USES_CATEGORIES} >= 0;

subject to comput_cons_sector {y in YEARS_WND diff YEAR_ONE, s in END_USES_CATEGORIES}:
	cons_sector [y, s] = sum {t in PERIODS, i in LAYERS, ss in END_USES_TYPES_OF_CATEGORY[s], tech in TECHNOLOGIES_OF_END_USES_TYPE[ss]: layers_in_out[y, tech,i] < 0} (-layers_in_out[y, tech,i]*F_t [y,tech, t] * t_op [t]);

var cons_primary_energy {YEARS_WND diff YEAR_ONE} >= 0;

subject to comput_cons_primary_energy {y in YEARS_WND diff YEAR_ONE}:
	cons_primary_energy [y] = sum {t in PERIODS, j in ENERGY_MIX} (F_t [y,j, t] * t_op [t]);

subject to limit_energy_conso_sector{y in YEARS_WND diff YEAR_ONE, s in END_USES_CATEGORIES}:
	cons_sector [y,s] <= conso_energy_sector [s] * cons_primary_energy [y];