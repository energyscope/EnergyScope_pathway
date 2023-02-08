# NEW : Param for Reinforcement Learning
set ENERGY_MIX := (RESOURCES diff {'ELEC_EXPORT','CO2_EMISSIONS','CO2_ATM','CO2_INDUSTRY','CO2_CAPTURED'}); # Set of resources considered in the primary energy mix

set NRE_RESOURCES := (ENERGY_MIX diff {RE_RESOURCES}); # Set of non-renewable resources

set some_NRE_RESOURCES := {'COAL','GAS','LFO'};

set other_NRE_RESOURCES := (NRE_RESOURCES diff {some_NRE_RESOURCES});

param allow_some_foss >=0.0, <= 1.0 default 1.0; # Parameter to symbolise the action to forbid (or to allow) the use of fossil fuels
param allow_other_foss >=0.0, <= 1.0 default 1.0; # Parameter to symbolise the action to forbid (or to allow) the use of fossil fuels

set YEARS_FOR_CONSTR := {'YEAR_2020'} union YEAR_ONE;

set TRANS_EUD_INPUT := {'MOBILITY_PASSENGER','MOBILITY_FREIGHT'};
set END_USES_INPUT_WO_TRANS := (END_USES_INPUT diff {TRANS_EUD_INPUT});
param eud_wo_trans {y in YEARS_WND} := sum {i in END_USES_INPUT_WO_TRANS} (end_uses_input [y, i]);

subject to limit_use_fossil_some{y in YEARS_WND diff YEARS_FOR_CONSTR}:
	sum {t in PERIODS, res in some_NRE_RESOURCES} (F_t [y,res, t] * t_op [t]) <= allow_some_foss * sum {i in ENERGY_MIX, t in PERIODS} (F_t [y,i, t] * t_op [t]);

subject to limit_use_fossil_other{y in YEARS_WND diff YEARS_FOR_CONSTR}:
	sum {t in PERIODS, res in other_NRE_RESOURCES} (F_t [y,res, t] * t_op [t]) <= allow_other_foss * sum {i in ENERGY_MIX, t in PERIODS} (F_t [y,i, t] * t_op [t]);

var RE_cons {YEARS_WND} >=0;
subject to comp_RE_cons {y in YEARS_WND diff YEAR_ONE}:
	RE_cons [y] = sum {i in RE_RESOURCES, t in PERIODS} (F_t [y,i, t] * t_op [t]);

var energy_cons {YEARS_WND} >=0;
subject to comp_energy_cons {y in YEARS_WND diff YEAR_ONE}:
	energy_cons [y] = sum {i in ENERGY_MIX, t in PERIODS} (F_t [y,i, t] * t_op [t]);

var final_energy_cons_trans {YEARS_WND} >=0;
subject to comp_energy_cons_trans {y in YEARS_WND diff YEAR_ONE}:
	final_energy_cons_trans [y] = sum {t in PERIODS, i in LAYERS, s in {"MOBILITY_PASSENGER","MOBILITY_FREIGHT"}, ss in END_USES_TYPES_OF_CATEGORY[s], tech in TECHNOLOGIES_OF_END_USES_TYPE[ss]: layers_in_out[y, tech,i] < 0} (-layers_in_out[y, tech,i]*F_t [y,tech, t] * t_op [t]);

# var eud_wo_trans {YEARS_WND} >=0;
# subject to comp_eud_wo_trans {y in YEARS_WND diff YEAR_ONE}:
# 	eud_wo_trans [y] = sum {i in END_USES_INPUT_WO_TRANS} (end_uses_input [y, i]);