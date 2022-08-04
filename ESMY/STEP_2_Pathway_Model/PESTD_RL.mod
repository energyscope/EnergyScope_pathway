# NEW : Param for Reinforcement Learning
param allow_foss >=0, <= 1 default 1; # Parameter to symbolise the action to forbid (or to allow) the use of fossil fuels

set NRE_RESOURCES := (RESOURCES diff RE_RESOURCES); # Set of non-renewable resources

subject to limit_use_fossil{y in YEARS_WND diff YEAR_ONE}:
	sum {i in NRE_RESOURCES, t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t]} (F_t [y,i, h, td] * t_op [h, td]) <= allow_foss * sum {i in RESOURCES, t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t]} (F_t [y,i, h, td] * t_op [h, td]);