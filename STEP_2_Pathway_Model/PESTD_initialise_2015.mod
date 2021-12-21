## Constraints needed to reproduce the scenario for BE in 2015
## All data are calculated in Excel file



subject to elec_prod_NUCLEAR: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]}   (   F_t ['YEAR_2015','NUCLEAR', h , td] ) = 24340;
subject to elec_prod_CCGT: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (        F_t ['YEAR_2015','CCGT', h , td] ) = 19669;#15693;
subject to elec_prod_COAL_US: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (     F_t ['YEAR_2015','COAL_US', h , td] ) = 3236;
subject to elec_prod_COAL_IGCC: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (   F_t ['YEAR_2015','COAL_IGCC', h , td] ) = 0;
subject to elec_prod_PV: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['YEAR_2015','PV', h , td] ) = 3376;
subject to elec_prod_WIND_ONSHORE: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]}  ( F_t ['YEAR_2015','WIND_ONSHORE' , h , td])  = 2509;#Data from ELIA 2015
subject to elec_prod_WIND_OFFSHORE: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} ( F_t ['YEAR_2015','WIND_OFFSHORE', h , td] ) = 2500;#Data from ELIA 2015
subject to elec_prod_HYDRO_RIVER: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['YEAR_2015','HYDRO_RIVER', h , td] ) = 365;
subject to elec_prod_GEOTHERMAL: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['YEAR_2015','GEOTHERMAL', h , td] ) = 0;
subject to biofuels_2015: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['YEAR_2015','BIOETHANOL', h , td] ) = 475.6;# 41 ktoe = >
subject to biofuels_2015_2: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['YEAR_2015','BIODIESEL', h , td] )  = 2865.2;# 223 + 24 ktoe =>
subject to biogas_2015: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['YEAR_2015','BIOMETHANATION', h , td] )  = 2656.4;#229 ktoe =>  

# new: 
subject to elec_prod_METHANOL: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['YEAR_2015','METHANOL', h , td] ) = end_uses_input['YEAR_2015',"NON_ENERGY"] * share_ned ['YEAR_2015',"METHANOL"];

# NED : 
let layers_in_out['YEAR_2015','HABER_BOSCH','HEAT_LOW_T_DHN'] := 0;

 	let f_min['YEAR_2015','GAS_STORAGE'] := 0;	let f_max['YEAR_2015','GAS_STORAGE'] := 10000;


 	let f_min['YEAR_2015','DHN_HP_ELEC'] := 0;	let f_max['YEAR_2015','DHN_HP_ELEC'] := 100;
 	let f_min['YEAR_2015','DHN_COGEN_GAS'] := 0;	let f_max['YEAR_2015','DHN_COGEN_GAS'] := 100;
 	let f_min['YEAR_2015','DHN_COGEN_WOOD'] := 0;	let f_max['YEAR_2015','DHN_COGEN_WOOD'] := 100;
 	let f_min['YEAR_2015','DHN_COGEN_WASTE'] := 0;	let f_max['YEAR_2015','DHN_COGEN_WASTE'] := 100;
#	let f_min['YEAR_2015','DHN_COGEN_WET_BIOMASS'] := 0;	let f_max['YEAR_2015','DHN_COGEN_WET_BIOMASS'] := 100;
#	let f_min['YEAR_2015','DHN_COGEN_BIO_HYDROLYSIS'] := 0;	let f_max['YEAR_2015','DHN_COGEN_BIO_HYDROLYSIS'] := 100;
 	let f_min['YEAR_2015','DHN_BOILER_GAS'] := 0;	let f_max['YEAR_2015','DHN_BOILER_GAS'] := 100;
#	let f_min['YEAR_2015','DHN_BOILER_WOOD'] := 0;	let f_max['YEAR_2015','DHN_BOILER_WOOD'] := 100;
 	let f_min['YEAR_2015','DHN_BOILER_OIL'] := 0;	let f_max['YEAR_2015','DHN_BOILER_OIL'] := 100;
 	let f_min['YEAR_2015','DHN_DEEP_GEO'] := 0;	let f_max['YEAR_2015','DHN_DEEP_GEO'] := 100;
#	let f_min['YEAR_2015','DHN_SOLAR'] := 0;	let f_max['YEAR_2015','DHN_SOLAR'] := 100;
 	let f_min['YEAR_2015','DEC_HP_ELEC'] := 0;	let f_max['YEAR_2015','DEC_HP_ELEC'] := 100;
#	let f_min['YEAR_2015','DEC_THHP_GAS'] := 0;	let f_max['YEAR_2015','DEC_THHP_GAS'] := 100;
 	let f_min['YEAR_2015','DEC_COGEN_GAS'] := 0;	let f_max['YEAR_2015','DEC_COGEN_GAS'] := 100;
#	let f_min['YEAR_2015','DEC_COGEN_OIL'] := 0;	let f_max['YEAR_2015','DEC_COGEN_OIL'] := 100;
#	let f_min['YEAR_2015','DEC_ADVCOGEN_GAS'] := 0;	let f_max['YEAR_2015','DEC_ADVCOGEN_GAS'] := 100;
#	let f_min['YEAR_2015','DEC_ADVCOGEN_H2'] := 0;	let f_max['YEAR_2015','DEC_ADVCOGEN_H2'] := 100;
 	let f_min['YEAR_2015','DEC_BOILER_GAS'] := 0;	let f_max['YEAR_2015','DEC_BOILER_GAS'] := 100;
 	let f_min['YEAR_2015','DEC_BOILER_WOOD'] := 0;	let f_max['YEAR_2015','DEC_BOILER_WOOD'] := 100;
 	let f_min['YEAR_2015','DEC_BOILER_OIL'] := 0;	let f_max['YEAR_2015','DEC_BOILER_OIL'] := 100;
 	let f_min['YEAR_2015','DEC_SOLAR'] := 0;	let f_max['YEAR_2015','DEC_SOLAR'] := 100;
#	let f_min['YEAR_2015','DEC_DIRECT_ELEC'] := 0;	let f_max['YEAR_2015','DEC_DIRECT_ELEC'] := 100;

