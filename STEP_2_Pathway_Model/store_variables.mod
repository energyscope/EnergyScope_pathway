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

subject to store_F_t_wnd {y in YEARS_WND, j in TECHNOLOGIES diff STORAGE_TECH, h in HOURS, td in TYPICAL_DAYS}:
    F_t_wnd[y,j,h,td] = F_t[y,j,h,td];

## To store resources used
subject to store_res_up_to {y in YEARS_WND, j in RESOURCES}:
	Res_wnd [y, j] = sum {t in PERIODS, h in HOUR_OF_PERIOD[t], td in TYPICAL_DAY_OF_PERIOD[t]} (F_t [y,j,h,td] * t_op [h, td]);

## To store share of production in Electricity layer
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