# -------------------------------------------------------------------------------------------------------------------------													
#	mod file to save variables along the way											
# -------------------------------------------------------------------------------------------------------------------------		

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

subject to store_F_decom_for_each_p_decom {p in PHASE_UP_TO, j in TECHNOLOGIES}:
	F_decom_p_decom[p, j] = sum {p2 in {"2010_2015"} union PHASE_UP_TO} F_decom[p,p2,j];

subject to store_F_decom_for_each_p_build {p in {"2010_2015"} union PHASE_UP_TO, j in TECHNOLOGIES}:
	F_decom_p_build[p, j] = sum {p2 in PHASE_UP_TO} F_decom[p2,p,j];

subject to store_F_used_year_start_next {y in YEAR_ONE_NEXT, j in TECHNOLOGIES}:
	F_used_year_start_next[y, j] = F_used_year_start[y,j];

# subject to store_F_t_wnd {y in YEARS_UP_TO, j in TECHNOLOGIES, h in HOURS, td in TYPICAL_DAYS}:
#     F_t_up_to[y,j,h,td] = F_t[y,j,h,td];

## To store resources used
subject to store_res_up_to {y in YEARS_WND diff YEAR_ONE, j in RESOURCES}:
	Res_wnd [y, j] = sum {t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t]} (F_t [y,j,h,td] * t_op [h, td]);

## To store share of production and consumption of END_USE layers
subject to store_tech {y in YEARS_WND, tech in TECHNOLOGIES diff STORAGE_TECH,c in END_USES_CATEGORIES, l in END_USES_TYPES_OF_CATEGORY[c]}:
    Tech_wnd [y,tech,l] = sum {t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t]} layers_in_out [y,tech,l] * F_t [y,tech, h, td];

subject to store_cost_inv {y in YEARS_WND, tech in TECHNOLOGIES}:
	C_inv_wnd [y,tech] = tau[y,tech] * C_inv[y,tech];

subject to store_cost_op_maint {y in YEARS_WND, j in TECHNOLOGIES union RESOURCES}:
	C_op_maint_wnd [y,j] = (if j in TECHNOLOGIES  
		then
			C_maint[y,j]
		else
			C_op[y,j]);