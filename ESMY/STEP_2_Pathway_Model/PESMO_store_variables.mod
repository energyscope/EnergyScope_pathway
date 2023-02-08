# -------------------------------------------------------------------------------------------------------------------------													
#	mod file to save variables along the way											
# -------------------------------------------------------------------------------------------------------------------------		

## To store share of production and consumption of END_USE layers
# var Tech_wnd {YEARS_WND diff YEAR_ONE, LAYERS, TECHNOLOGIES diff STORAGE_TECH union RESOURCES}, default 0; #[GWh] Variable to store share of different end-use layer over the years in the current window
# subject to store_tech {y in YEARS_WND diff YEAR_ONE, tech in (TECHNOLOGIES diff STORAGE_TECH) union RESOURCES, l in LAYERS}:
#     Tech_wnd [y,l,tech] = sum {t in PERIODS} layers_in_out [y,tech,l] * F_t [y,tech, t] * t_op [t];

var EUD_wnd {YEARS_WND diff YEAR_ONE, LAYERS}, default 0; # Variable to store end-use demands
subject to store_EUD {y in YEARS_WND diff YEAR_ONE, l in LAYERS}:
	EUD_wnd [y,l] = sum {t in PERIODS} End_uses [y,l, t] * t_op [t];