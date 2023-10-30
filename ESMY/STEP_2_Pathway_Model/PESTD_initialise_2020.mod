
##########################################
#### Initialisation for 2020 ####
##########################################

### Electricity production ###
# SOURCE_1: https://www.elia.be/en/news/press-releases/2021/01/20210107_belgium-s-electricity-mix-in-2020
# SOURCE_2: For missing data (hydro, coal, geothermal, ...) EU reference scenario 2020 - Trends to 2050
# SOURCE_3: https://economie.fgov.be/fr/publications/energy-key-data-fevrier-2022#:~:text=La%20Direction%20g%C3%A9n%C3%A9rale%20de%20l'Energie%20produit%20et%20publie%2C%20chaque,%C3%A9volution%20au%20fil%20du%20temps.

subject to elec_prod_NUCLEAR_2020: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]}   (   F_t ['YEAR_2020','NUCLEAR', h , td] ) = 34400; #from SPF_Economie, versus 31700 from ELIA, versus 34883 from EU
# subject to elec_prod_CCGT_2020: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (        F_t ['YEAR_2020','CCGT', h , td] ) = 26800; #from SPF_Economie, versus 27 800 from ELIA, versus 27602 from EU
subject to elec_prod_WIND_OFFSHORE_2020: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} ( F_t ['YEAR_2020','WIND_OFFSHORE', h , td] ) = 6989; #versus 6700 from ELIA, versus 6826 from EU (SPF_Economie gives 12.8 TWh for all the wind)
subject to elec_prod_WIND_ONSHORE_2020: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]}  ( F_t ['YEAR_2020','WIND_ONSHORE' , h , td])  = 5811; #from SPF_Economie, versus 4100 from ELIA, versus 4052 from EU (SPF_Economie gives 12.8 TWh for all the wind)
subject to elec_prod_PV_2020: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['YEAR_2020','PV', h , td] ) = 5100; #from SPF_Economie, versus 4300 from ELIA, versus 4327 from EU
subject to elec_prod_GEOTHERMAL_2020: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['YEAR_2020','GEOTHERMAL', h , td] ) = 0; #from EU
subject to elec_prod_HYDRO_RIVER_2020: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['YEAR_2020','HYDRO_RIVER', h , td] ) = 353; #from EU (confirmed by SPF_Economie, 300)
subject to elec_prod_COAL_US_2020: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (     F_t ['YEAR_2020','COAL_US', h , td] ) = 1900; #from SPF_Economie
subject to elec_prod_COAL_IGCC_2020: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (   F_t ['YEAR_2020','COAL_IGCC', h , td] ) = 0; #As done by GL for 2015
subject to no_elec_import_2020: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (   F_t ['YEAR_2020','ELECTRICITY', h , td] ) = 0; #from SPF_Economie


### Production of bioethanol and biodiesel
# SOURCE: https://op.europa.eu/en/publication-detail/-/publication/14d7e768-1b50-11ec-b4fe-01aa75ed71a1 --> Values for 2019
subject to bioethanol_2020: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['YEAR_2020','BIOETHANOL', h , td] ) = 1504.9;# 129.4 ktoe = >
subject to biodiesel_2020: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['YEAR_2020','BIODIESEL', h , td] ) = 4139.1;# 355.9 ktoe = >

### No import of electrofuels in 2020
subject to no_H2_RE_2020: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['YEAR_2020','H2_RE', h , td] ) = 0.0;
subject to no_GAS_RE_2020: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['YEAR_2020','GAS_RE', h , td] ) = 0.0;
subject to no_AMMONIA_RE_2020: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['YEAR_2020','AMMONIA_RE', h , td] ) = 0.0;
subject to no_METHANOL_RE_2020: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['YEAR_2020','METHANOL_RE', h , td] ) = 0.0;

### Production of biomethane
# SOURCE: https://www.cng-mobility.ch/wp-content/uploads/2020/09/EBA-Conference-1-Sept-2020-Dirk-Focroul.pdf
subject to biogas_2020: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['YEAR_2020','BIOMETHANATION', h , td] )  = 2500;

### Non-energy demand production ###
# SOURCE: https://scholar.google.com/citations?view_op=view_citation&hl=fr&user=i3Y6c7wAAAAJ&citation_for_view=i3Y6c7wAAAAJ:2osOgNQ5qMEC
subject to ned_prod_METHANOL_2020: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['YEAR_2020','METHANOL', h , td] ) = end_uses_input['YEAR_2020',"NON_ENERGY"] * share_ned ['YEAR_2020',"METHANOL"]; #Only import of methanol in 2020 to supply methanol
subject to ned_prod_HVC_2020: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['YEAR_2020','OIL_TO_HVC', h , td] ) = end_uses_input['YEAR_2020',"NON_ENERGY"] * share_ned ['YEAR_2020',"HVC"]; #Only Naphtha/LPG cracking to supply HVC
subject to ned_prod_AMMONIA_2020: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['YEAR_2020','HABER_BOSCH', h , td] ) = end_uses_input['YEAR_2020',"NON_ENERGY"] * share_ned ['YEAR_2020',"AMMONIA"]; #Only Haber-Bosch cracking to supply ammonia


### As done per GL for 2015
let layers_in_out['YEAR_2020','HABER_BOSCH','HEAT_LOW_T_DHN'] := 0;
# let f_min['YEAR_2020','GAS_STORAGE'] := 0;	let f_max['YEAR_2020','GAS_STORAGE'] := 10000;
# let f_min['YEAR_2020','DHN_HP_ELEC'] := 0;	let f_max['YEAR_2020','DHN_HP_ELEC'] := 100;
# let f_min['YEAR_2020','DHN_COGEN_GAS'] := 0;	let f_max['YEAR_2020','DHN_COGEN_GAS'] := 100;
# let f_min['YEAR_2020','DHN_COGEN_WOOD'] := 0;	let f_max['YEAR_2020','DHN_COGEN_WOOD'] := 100;
# let f_min['YEAR_2020','DHN_COGEN_WASTE'] := 0;	let f_max['YEAR_2020','DHN_COGEN_WASTE'] := 100;
# let f_min['YEAR_2020','DHN_BOILER_GAS'] := 0;	let f_max['YEAR_2020','DHN_BOILER_GAS'] := 100;
# let f_min['YEAR_2020','DHN_BOILER_OIL'] := 0;	let f_max['YEAR_2020','DHN_BOILER_OIL'] := 100;
# let f_min['YEAR_2020','DHN_DEEP_GEO'] := 0;	let f_max['YEAR_2020','DHN_DEEP_GEO'] := 100;
# let f_min['YEAR_2020','DEC_HP_ELEC'] := 0;	let f_max['YEAR_2020','DEC_HP_ELEC'] := 100;
# let f_min['YEAR_2020','DEC_COGEN_GAS'] := 0;	let f_max['YEAR_2020','DEC_COGEN_GAS'] := 100;
# let f_min['YEAR_2020','DEC_BOILER_GAS'] := 0;	let f_max['YEAR_2020','DEC_BOILER_GAS'] := 100;
# let f_min['YEAR_2020','DEC_BOILER_WOOD'] := 0;	let f_max['YEAR_2020','DEC_BOILER_WOOD'] := 100;
# let f_min['YEAR_2020','DEC_BOILER_OIL'] := 0;	let f_max['YEAR_2020','DEC_BOILER_OIL'] := 100;
# let f_min['YEAR_2020','DEC_SOLAR'] := 0;	let f_max['YEAR_2020','DEC_SOLAR'] := 100;



### different shares ###
# Mobility
# SOURCE1: EU reference scenario 2020 - Trends to 2050
# SOURCE2: https://op.europa.eu/en/publication-detail/-/publication/14d7e768-1b50-11ec-b4fe-01aa75ed71a1 - Values for 2019
fix Share_mobility_public['YEAR_2020']:=0.188;
fix Share_freight_train['YEAR_2020']:=0.101;
fix Share_freight_boat['YEAR_2020']:=0.145;

fix Share_heat_dhn['YEAR_2020']:=0.02; # As done by GL for 2015 because no additional information found

### shares private mobility ###
# SOURCE: https://mobilit.belgium.be/sites/default/files/resources/files/chiffres_cles_mobilite_belgique_v2021.pdf
let fmin_perc['YEAR_2020',"CAR_DIESEL"] := 0.479;
let fmin_perc['YEAR_2020',"CAR_GASOLINE"] := 0.485;
let fmin_perc['YEAR_2020',"CAR_HEV"] := 0.03;
let fmin_perc['YEAR_2020',"CAR_NG"] := 0.002;
let fmin_perc['YEAR_2020',"CAR_BEV"] := 0.004;

let fmax_perc['YEAR_2020',"CAR_PHEV"] := 0;
let fmax_perc['YEAR_2020',"CAR_FUEL_CELL"] := 0;
let fmax_perc['YEAR_2020',"CAR_METHANOL"] := 0;

### shares public mobility ###
# SOURCE: https://op.europa.eu/en/publication-detail/-/publication/14d7e768-1b50-11ec-b4fe-01aa75ed71a1 - Values for 2019
# Repartition between different kind of buses as GL for 2015
let fmin_perc['YEAR_2020',"BUS_COACH_DIESEL"] := 0.43;
let fmin_perc['YEAR_2020',"BUS_COACH_CNG_STOICH"] := 0.09;
let fmin_perc['YEAR_2020',"TRAIN_PUB"] := 0.43;
let fmin_perc['YEAR_2020',"TRAMWAY_TROLLEY"] := 0.05;

let fmax_perc['YEAR_2020',"BUS_COACH_HYDIESEL"] := 0;
let fmax_perc['YEAR_2020',"BUS_COACH_FC_HYBRIDH2"] := 0;

### shares Freight ###
let fmax_perc['YEAR_2020',"BOAT_FREIGHT_NG"] := 0;
let fmax_perc['YEAR_2020',"TRUCK_FUEL_CELL"] := 0;
let fmax_perc['YEAR_2020',"TRUCK_ELEC"] := 0;
let fmax_perc['YEAR_2020',"TRUCK_NG"] := 0;


### shares decentralised low T heat ###
# SOURCE: As done by GL for 2015
let fmin_perc['YEAR_2020',"DEC_BOILER_OIL"] := 0.484;
let fmin_perc['YEAR_2020',"DEC_BOILER_GAS"] := 0.396;
let fmin_perc['YEAR_2020',"DEC_BOILER_WOOD"] := 0.1;
let fmin_perc['YEAR_2020',"DEC_COGEN_GAS"] := 0.007;
let fmin_perc['YEAR_2020',"DEC_HP_ELEC"] := 0.011;
let fmin_perc['YEAR_2020',"DEC_SOLAR"] := 0.002;

let fmax_perc['YEAR_2020',"DEC_COGEN_OIL"] := 0;
let fmax_perc['YEAR_2020',"DEC_THHP_GAS"] := 0;
let fmax_perc['YEAR_2020',"DEC_DIRECT_ELEC"] := 0;
let fmax_perc['YEAR_2020',"DEC_ADVCOGEN_H2"] := 0;
let fmax_perc['YEAR_2020',"DEC_ADVCOGEN_GAS"] := 0;

### shares DHN low T heat ###
# SOURCE: As done by GL for 2015
let fmin_perc['YEAR_2020',"DHN_COGEN_GAS"] := 0.594;
let fmin_perc['YEAR_2020',"DHN_COGEN_WOOD"] := 0.066;
let fmin_perc['YEAR_2020',"DHN_COGEN_WASTE"] := 0.141;
let fmin_perc['YEAR_2020',"DHN_BOILER_GAS"] := 0.139;
let fmin_perc['YEAR_2020',"DHN_BOILER_OIL"] := 0.007;
let fmin_perc['YEAR_2020',"DHN_HP_ELEC"] := 0.044;

let fmax_perc['YEAR_2020',"DHN_BOILER_WOOD"] := 0;
let fmax_perc['YEAR_2020',"DHN_DEEP_GEO"] := 0;
let fmax_perc['YEAR_2020',"DHN_SOLAR"] := 0;

### shares high T heat ###
# SOURCE: As done by GL for 2015
let fmin_perc['YEAR_2020',"IND_BOILER_GAS"] := 0.358;
let fmin_perc['YEAR_2020',"IND_BOILER_COAL"] := 0.3;
let fmin_perc['YEAR_2020',"IND_BOILER_OIL"] := 0.2;
let fmin_perc['YEAR_2020',"IND_COGEN_GAS"] := 0.086;
let fmin_perc['YEAR_2020',"IND_COGEN_WASTE"] := 0.056;

let fmax_perc['YEAR_2020',"IND_BOILER_WOOD"] := 0;
let fmax_perc['YEAR_2020',"IND_BOILER_WASTE"] := 0;
let fmax_perc['YEAR_2020',"IND_COGEN_WOOD"] := 0;
let fmax_perc['YEAR_2020',"IND_DIRECT_ELEC"] := 0;
