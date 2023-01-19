# NEW : Param for Reinforcement Learning
set ENERGY_MIX := (RESOURCES diff {'ELEC_EXPORT','CO2_EMISSIONS','CO2_ATM','CO2_INDUSTRY','CO2_CAPTURED'}); # Set of resources considered in the primary energy mix

set NRE_RESOURCES := (ENERGY_MIX diff {RE_RESOURCES}); # Set of non-renewable resources

set some_NRE_RESOURCES := {'H2','AMMONIA','METHANOL'};

set other_NRE_RESOURCES := (NRE_RESOURCES diff {some_NRE_RESOURCES});

param allow_some_foss >=0.0, <= 1.0 default 1.0; # Parameter to symbolise the action to forbid (or to allow) the use of fossil fuels
param allow_other_foss >=0.0, <= 1.0 default 1.0; # Parameter to symbolise the action to forbid (or to allow) the use of fossil fuels


set YEARS_FOR_CONSTR := {'YEAR_2020'} union YEAR_ONE;

subject to limit_use_fossil_some{y in YEARS_WND diff YEARS_FOR_CONSTR}:
	sum {t in PERIODS, res in some_NRE_RESOURCES} (F_t [y,res, t] * t_op [t]) <= allow_some_foss * sum {i in ENERGY_MIX, t in PERIODS} (F_t [y,i, t] * t_op [t]);

subject to limit_use_fossil_other{y in YEARS_WND diff YEARS_FOR_CONSTR}:
	sum {t in PERIODS, res in other_NRE_RESOURCES} (F_t [y,res, t] * t_op [t]) <= allow_other_foss * sum {i in ENERGY_MIX, t in PERIODS} (F_t [y,i, t] * t_op [t]);


# subject to limit_use_fossil_res{y in YEARS_WND diff YEARS_FOR_CONSTR, res in some_NRE_RESOURCES}:
# 	sum {t in PERIODS} (F_t [y,res, t] * t_op [t]) <= allow_foss_res[res] * sum {i in ENERGY_MIX, t in PERIODS} (F_t [y,i, t] * t_op [t]);

var energy_cons {YEARS_WND, {"HEAT_LOW_T","HEAT_HIGH_T"}} >=0;
subject to comp_energy_cons {y in YEARS_WND diff YEAR_ONE, s in {"HEAT_LOW_T","HEAT_HIGH_T"}}:
	energy_cons [y, s] = sum {t in PERIODS, i in LAYERS, ss in END_USES_TYPES_OF_CATEGORY[s], tech in TECHNOLOGIES_OF_END_USES_TYPE[ss]: layers_in_out[y, tech,i] < 0} (-layers_in_out[y, tech,i]*F_t [y,tech, t] * t_op [t]);

var elec_cons {YEARS_WND, {"HEAT_LOW_T","HEAT_HIGH_T"}} >=0;
subject to comp_elec_cons {y in YEARS_WND diff YEAR_ONE, s in {"HEAT_LOW_T","HEAT_HIGH_T"}}:
	elec_cons [y, s] = sum {t in PERIODS, ss in END_USES_TYPES_OF_CATEGORY[s], tech in TECHNOLOGIES_OF_END_USES_TYPE[ss]: layers_in_out[y, tech,'ELECTRICITY'] < 0} (-layers_in_out[y, tech,'ELECTRICITY']*F_t [y,tech, t] * t_op [t]);

var prod_BEV {YEARS_WND} >=0;
subject to comp_share_BEV {y in YEARS_WND diff YEAR_ONE}:
	prod_BEV [y] = sum {t in PERIODS} (F_t [y,"CAR_BEV",t] * t_op[t]);

var EUD_mob_private {YEARS_WND} >=0;
subject to comp_EUD_mob_private {y in YEARS_WND diff YEAR_ONE}:
	EUD_mob_private [y] = sum {t in PERIODS} (End_uses [y,"MOB_PRIVATE",t] * t_op[t]);