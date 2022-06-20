
##########################################
#### Initialisation for 2015 and 2020 ####
##########################################

### electrical capacity ###

fix F['YEAR_2020','PV']:=4.65;
fix F['YEAR_2020','WIND_ONSHORE']:=2.3;
fix F['YEAR_2020','WIND_OFFSHORE']:=1.55;
fix F['YEAR_2020','HYDRO_RIVER']:=0.11;
fix F['YEAR_2020','GEOTHERMAL']:=0;
fix F['YEAR_2020','NUCLEAR']:=5.925;
fix F['YEAR_2020','CCGT']:=3.925;
fix F['YEAR_2020','COAL_US']:=0;

# From https://www.elia.be/en/news/press-releases/2020/01/20200108_press-release_mix-electrique-2019
let fmin_perc['YEAR_2020',"PV"] := 0.035;
let fmax_perc['YEAR_2020',"PV"] := 0.042;
let fmin_perc['YEAR_2020',"NUCLEAR"] := 0.414;
let fmax_perc['YEAR_2020',"NUCLEAR"] := 0.488;
let fmin_perc['YEAR_2020',"WIND_ONSHORE"] := 0.034;
let fmax_perc['YEAR_2020',"WIND_ONSHORE"] := 0.04;
let fmin_perc['YEAR_2020',"WIND_OFFSHORE"] := 0.046;
let fmax_perc['YEAR_2020',"WIND_OFFSHORE"] := 0.055;


### different shares ###

fix Share_mobility_public['YEAR_2020']:=0.194;
fix Share_freight_train['YEAR_2020']:=0.102;
fix Share_freight_boat['YEAR_2020']:=0.16;
fix Share_heat_dhn['YEAR_2020']:=0.02;

### shares private mobility ###

let fmin_perc['YEAR_2020',"CAR_DIESEL"] := 0.51;
let fmin_perc['YEAR_2020',"CAR_GASOLINE"] := 0.485;
let fmin_perc['YEAR_2020',"CAR_NG"] := 0.002;
let fmin_perc['YEAR_2020',"CAR_BEV"] := 0.003;

let fmax_perc['YEAR_2020',"CAR_HEV"] := 0;
let fmax_perc['YEAR_2020',"CAR_PHEV"] := 0;
let fmax_perc['YEAR_2020',"CAR_FUEL_CELL"] := 0;

### shares public mobility ###

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

let fmin_perc['YEAR_2020',"IND_BOILER_GAS"] := 0.358;
let fmin_perc['YEAR_2020',"IND_BOILER_COAL"] := 0.3;
let fmin_perc['YEAR_2020',"IND_BOILER_OIL"] := 0.2;
let fmin_perc['YEAR_2020',"IND_COGEN_GAS"] := 0.086;
let fmin_perc['YEAR_2020',"IND_COGEN_WASTE"] := 0.056;

let fmax_perc['YEAR_2020',"IND_BOILER_WOOD"] := 0;
let fmax_perc['YEAR_2020',"IND_BOILER_WASTE"] := 0;
let fmax_perc['YEAR_2020',"IND_COGEN_WOOD"] := 0;
let fmax_perc['YEAR_2020',"IND_DIRECT_ELEC"] := 0;
