# NEW : Param for Reinforcement Learning
param allow_foss >=0.0, <= 1.0 default 1.0; # Parameter to symbolise the action to forbid (or to allow) the use of fossil fuels

set NRE_RESOURCES := (RESOURCES diff RE_RESOURCES); # Set of non-renewable resources

subject to limit_use_fossil{y in YEARS_WND diff YEAR_ONE}:
	sum {i in NRE_RESOURCES, t in PERIODS} (F_t [y,i, t] * t_op [t]) <= allow_foss * sum {i in RESOURCES, t in PERIODS} (F_t [y,i, t] * t_op [t]);