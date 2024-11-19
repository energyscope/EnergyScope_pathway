# -------------------------------------------------------------------------------------------------------------------------													
#	mod file to save variables along the way											
# -------------------------------------------------------------------------------------------------------------------------		

set SET_INIT_SOL := {"F_up_to",	"F_new_up_to",	"F_decom_up_to",	"F_old_up_to",	"F_used_year_start_next", "Res_up_to"};

## Constraints for storing variables
var F_up_to {YEARS_UP_TO, TECHNOLOGIES} >= 0; # F_up_to: Installed capacity from the start of the optimisation (2020)
subject to store_F_up_to {j in TECHNOLOGIES, y in YEARS_UP_TO}:
	F_up_to[y,j] = F[y,j];

var F_new_up_to {PHASE_UP_TO union {"2020_2025"}, TECHNOLOGIES} >= 0; #[GW/GWh] Accounts for the additional new capacity installed in a new phase from the start of the optimisation (2020)
subject to store_F_new_up_to {p in PHASE_UP_TO union {"2020_2025"}, j in TECHNOLOGIES}:
	F_new_up_to[p,j] = F_new[p,j];

var F_old_up_to {PHASE_UP_TO,TECHNOLOGIES} >=0, default 0; #[GW] Retired capacity during a phase with respect to the main output from the start of the optimisation (2020)
subject to store_F_old_up_to {p in PHASE_UP_TO, j in TECHNOLOGIES}:
	F_old_up_to[p,j] = F_old[p,j];

var F_decom_up_to {PHASE_UP_TO,PHASE_UP_TO union {"2020_2025"}, TECHNOLOGIES} >= 0; #[GW] Accounts for the decommissioned capacity in a new phase from the start of the optimisation (2020)
subject to store_F_decom_up_to {p_decom in PHASE_UP_TO, p_built in PHASE_UP_TO union {"2020_2025"}, j in TECHNOLOGIES}:
	F_decom_up_to[p_decom,p_built,j] = F_decom[p_decom,p_built,j];

var F_used_year_start_next{YEAR_ONE_NEXT, TECHNOLOGIES} >= 0;
subject to store_F_used_year_start_next {y in YEAR_ONE_NEXT, j in TECHNOLOGIES}:
	F_used_year_start_next[y, j] = F_used_year_start[y,j];

var Res_up_to {YEARS_UP_TO, RESOURCES} >= 0; # Res_up_to: Used resources from the start of the optimisation (2020)
subject to store_Res_up_to {j in RESOURCES, y in YEARS_UP_TO}:
	Res_up_to[y,j] = Res[y,j];