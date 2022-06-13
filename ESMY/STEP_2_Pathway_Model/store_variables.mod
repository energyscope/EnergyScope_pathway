# -------------------------------------------------------------------------------------------------------------------------													
#	mod file to save variables along the way											
# -------------------------------------------------------------------------------------------------------------------------		

# NEW VARIABLE FOR MYOPIC
var F_wnd {YEARS_WND, TECHNOLOGIES} >= 0; # F_wnd: Installed capacity during the window of interest
var F_up_to {YEARS_UP_TO, TECHNOLOGIES} >= 0; # F_up_to: Installed capacity from the start of the optimisation (2015)
var F_new_up_to {PHASE_UP_TO union {"2010_2015"}, TECHNOLOGIES} >= 0; #[GW/GWh] Accounts for the additional new capacity installed in a new phase from the start of the optimisation (2015)
var F_decom_up_to {PHASE_UP_TO,PHASE_UP_TO union {"2010_2015"}, TECHNOLOGIES} >= 0; #[GW] Accounts for the decommissioned capacity in a new phase from the start of the optimisation (2015)
var F_old_up_to {PHASE_UP_TO,TECHNOLOGIES} >=0, default 0; #[GW] Retired capacity during a phase with respect to the main output from the start of the optimisation (2015)
var Res_wnd {YEARS_WND diff YEAR_ONE, RESOURCES} >= 0, default 0; #[GWh] Resources used in the current window
var Tech_wnd {YEARS_WND diff YEAR_ONE, LAYERS, TECHNOLOGIES diff STORAGE_TECH union RESOURCES}, default 0; #[GWh] Variable to store share of different end-use layer over the years in the current window
var EUD_wnd {YEARS_WND diff YEAR_ONE, LAYERS}, default 0; # Variable to store end-use demands
var C_inv_wnd {YEARS_WND diff YEAR_ONE, TECHNOLOGIES} >= 0, default 0; #[€] Variable to store annualised investment costs of technologies
var C_op_maint_wnd {YEARS_WND diff YEAR_ONE, TECHNOLOGIES union RESOURCES} >= 0, default 0; #[€] Variable to store operational costs of resources or maintenance costs of technologies
var F_used_year_start_next{YEAR_ONE_NEXT, TECHNOLOGIES} >= 0;


set SET_INIT_SOL := {"F_up_to",	"F_new_up_to",	"F_decom_up_to",	"F_old_up_to",	"F_used_year_start_next"};
set STORE_RESULTS := {"F_wnd", "Res_wnd", "C_inv_wnd", "C_op_maint_wnd", "Tech_wnd", "EUD_wnd"};

## Constraints for storing variables
subject to store_F_wnd {j in TECHNOLOGIES, y in YEARS_WND}:
	F_wnd[y,j] = F[y,j];

subject to store_F_up_to {j in TECHNOLOGIES, y in YEARS_UP_TO}:
	F_up_to[y,j] = F[y,j];

subject to store_F_new_up_to {p in PHASE_UP_TO union {"2010_2015"}, j in TECHNOLOGIES}:
	F_new_up_to[p,j] = F_new[p,j];

subject to store_F_old_up_to {p in PHASE_UP_TO, j in TECHNOLOGIES}:
	F_old_up_to[p,j] = F_old[p,j];

subject to store_F_decom_up_to {p_decom in PHASE_UP_TO, p_built in PHASE_UP_TO union {"2010_2015"}, j in TECHNOLOGIES}:
	F_decom_up_to[p_decom,p_built,j] = F_decom[p_decom,p_built,j];

subject to store_F_used_year_start_next {y in YEAR_ONE_NEXT, j in TECHNOLOGIES}:
	F_used_year_start_next[y, j] = F_used_year_start[y,j];

## To store resources used
subject to store_res_up_to {y in YEARS_WND diff YEAR_ONE, j in RESOURCES}:
	Res_wnd [y, j] = sum {t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t]} (F_t [y,j,h,td] * t_op [h, td]);

## To store share of production and consumption of END_USE layers
subject to store_tech {y in YEARS_WND diff YEAR_ONE, tech in (TECHNOLOGIES diff STORAGE_TECH) union RESOURCES, l in LAYERS}:
    Tech_wnd [y,l,tech] = sum {t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t]} layers_in_out [y,tech,l] * F_t [y,tech, h, td];

subject to store_EUD {y in YEARS_WND diff YEAR_ONE, l in LAYERS}:
	EUD_wnd [y,l] = sum {t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t]} End_uses [y,l, h, td];

subject to store_cost_inv {y in YEARS_WND diff YEAR_ONE, tech in TECHNOLOGIES}:
	C_inv_wnd [y, tech] = tau[y,tech] * C_inv[y,tech];

subject to store_cost_op_maint {y in YEARS_WND diff YEAR_ONE, j in TECHNOLOGIES union RESOURCES}:
	C_op_maint_wnd [y, j] = (if j in TECHNOLOGIES  
		then
			C_maint[y,j]
		else
			C_op[y,j]);

# subject to store_GWP_wnd {y in YEARS_WND diff YEAR_ONE}:
# 	GWP_wnd [y] = sum {i in RESOURCES} GWP_op [y,i];