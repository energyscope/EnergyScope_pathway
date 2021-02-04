## Constraints needed to reproduce the scenario for CH in 2011
## All data are calculated in Excel file


subject to elec_prod_NUCLEAR: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]}   (   F_t ['NUCLEAR', h , td] ) = 24340;
subject to elec_prod_CCGT: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (        F_t ['CCGT', h , td] ) = 19669;#15693;
subject to elec_prod_COAL_US: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (     F_t ['COAL_US', h , td] ) = 3236;
subject to elec_prod_COAL_IGCC: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (   F_t ['COAL_IGCC', h , td] ) = 0;
subject to elec_prod_PV: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['PV', h , td] ) = 3376;
subject to elec_prod_WIND_ONSHORE: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]}  ( F_t ['WIND_ONSHORE' , h , td])  = 2509;#Data from ELIA 2015
subject to elec_prod_WIND_OFFSHORE: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} ( F_t ['WIND_OFFSHORE', h , td] ) = 2500;#Data from ELIA 2015
subject to elec_prod_HYDRO_RIVER: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['HYDRO_RIVER', h , td] ) = 365;
subject to elec_prod_GEOTHERMAL: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['GEOTHERMAL', h , td] ) = 0;
subject to biofuels_2015: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['BIOETHANOL', h , td] ) = 475.6;# 41 ktoe = >
subject to biofuels_2015_2: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['BIODIESEL', h , td] )  = 2865.2;# 223 + 24 ktoe =>
subject to biogas_2015: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['BIOMETHANATION', h , td] )  = 2656.4;#229 ktoe =>  

# subject to elec_prod_GT_OIL: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['GT_OIL', h , td] ) = 200;
# subject to elec_prod_INCINERATOR: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['INCINERATOR', h , td] ) = 530;
# subject to elec_prod_BIOMASS_ST: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['BIOMASS_ST', h , td] ) = 3600;



let fmin_perc['TRUCK_NG'] := 0.053;
let fmax_perc['TRUCK_NG'] := 0.053;
let f_max['TRUCK_FUEL_CELL'] := 0;
let f_max['TRUCK_ELEC'] := 0;
let f_min['BOAT_FREIGHT_NG'] := 0;
let f_max['BOAT_FREIGHT_NG'] := 0;


#SOURCE : # Eurostat2017 p49
let fmin_perc['TRAMWAY_TROLLEY'] := 0.045;
let fmin_perc['BUS_COACH_DIESEL'] := 0.47;# 90%  du service publique hors train est en tram/metro
let fmin_perc['BUS_COACH_HYDIESEL'] := 0;
let fmin_perc['BUS_COACH_CNG_STOICH'] := 0.10;# 90%  du service publique hors train est en tram/metro
let fmin_perc['BUS_COACH_FC_HYBRIDH2'] := 0;
let fmin_perc['TRAIN_PUB'] := 0.385; #slide 4 de #slide 10 of https://mobilit.belgium.be/sites/default/files/chiffres_cles_mobilite_2017.pdf
let fmax_perc['TRAMWAY_TROLLEY'] := 0.045;
let fmax_perc['BUS_COACH_DIESEL'] := 1;
let fmax_perc['BUS_COACH_HYDIESEL'] := 0;
let fmax_perc['BUS_COACH_CNG_STOICH'] := 0.10;
let fmax_perc['BUS_COACH_FC_HYBRIDH2'] := 0;
let fmax_perc['TRAIN_PUB'] := 0.385;#slide 4 de #slide 10 of https://mobilit.belgium.be/sites/default/files/chiffres_cles_mobilite_2017.pdf

# Private mobility
let fmin_perc['CAR_GASOLINE'] := 0.3534;#slide 10 of https://mobilit.belgium.be/sites/default/files/chiffres_cles_mobilite_2017.pdf
let fmin_perc['CAR_DIESEL'] := 0.0;#slide 10 of https://mobilit.belgium.be/sites/default/files/chiffres_cles_mobilite_2017.pdf
let fmin_perc['CAR_NG'] := 0.01;
let fmin_perc['CAR_HEV'] := 0.0;#slide 10 of https://mobilit.belgium.be/sites/default/files/chiffres_cles_mobilite_2017.pdf
let fmin_perc['CAR_PHEV'] := 0.0;
let fmin_perc['CAR_BEV'] := 0.0;
let fmin_perc['CAR_FUEL_CELL'] := 0.0;
let fmax_perc['CAR_GASOLINE'] := 0.3535; #slide 10 of https://mobilit.belgium.be/sites/default/files/chiffres_cles_mobilite_2017.pdf
let fmax_perc['CAR_DIESEL'] := 1;#slide 10 of https://mobilit.belgium.be/sites/default/files/chiffres_cles_mobilite_2017.pdf
let fmax_perc['CAR_NG'] := 0.01;
let fmax_perc['CAR_HEV'] := 0.0;#slide 10 of https://mobilit.belgium.be/sites/default/files/chiffres_cles_mobilite_2017.pdf
let fmax_perc['CAR_PHEV'] := 0.0;
let fmax_perc['CAR_BEV'] := 0.0;
let fmax_perc['CAR_FUEL_CELL'] := 0.0;

# Industry - Case 2 (fixing elec output)
let fmin_perc ['IND_COGEN_GAS'] := 0.086;#
let fmin_perc ['IND_COGEN_WOOD'] := 0;#
let fmin_perc ['IND_COGEN_WASTE'] := 0.056;#
let fmin_perc ['IND_BOILER_GAS'] := 0;#
let fmin_perc ['IND_BOILER_WOOD'] := 0.0;#
let fmin_perc ['IND_BOILER_OIL'] := 0.2;#
let fmin_perc ['IND_BOILER_COAL'] := 0.3;#
let fmin_perc ['IND_BOILER_WASTE'] := 0;#
let fmin_perc ['IND_DIRECT_ELEC'] := 0.00;#

let fmax_perc ['IND_COGEN_GAS'] := 0.086;#0.0244;
let fmax_perc ['IND_COGEN_WOOD'] := 0;#0.0075;
let fmax_perc ['IND_COGEN_WASTE'] := 0.056;#0.0177;
let fmax_perc ['IND_BOILER_GAS'] := 1;#0.2433;
let fmax_perc ['IND_BOILER_WOOD'] := 0.0;#0.0697;
let fmax_perc ['IND_BOILER_OIL'] := 0.2;#0.256;
let fmax_perc ['IND_BOILER_COAL'] := 0.3;#0.0507;
let fmax_perc ['IND_BOILER_WASTE'] := 0;#0.056;
let fmax_perc ['IND_DIRECT_ELEC'] := 0.0;#0.2747;


# Heat Low T DHN
let loss_network ['HEAT_LOW_T_DHN'] := 0.0864;


# Case2  (fixing cogen electricity production)
let fmin_perc ['DHN_HP_ELEC'] := 0.0436;
let fmin_perc ['DHN_COGEN_GAS'] := 0.59413;
let fmin_perc ['DHN_COGEN_WOOD'] := 0.06603;
let fmin_perc ['DHN_COGEN_WASTE'] := 0.124080;#0.72823;
let fmin_perc ['DHN_BOILER_GAS'] := 0.13883;
let fmin_perc ['DHN_BOILER_WOOD'] := 0;
let fmin_perc ['DHN_BOILER_OIL'] := 0.00651;
let fmin_perc ['DHN_DEEP_GEO'] := 0.01;#0.00443;
let fmax_perc ['DHN_HP_ELEC'] := 0.0437;
let fmax_perc ['DHN_COGEN_GAS'] := 0.59413;
let fmax_perc ['DHN_COGEN_WOOD'] := 0.06603;
let fmax_perc ['DHN_COGEN_WASTE'] := 0.14080;#0.72823;
let fmax_perc ['DHN_BOILER_GAS'] := 0.13883;
let fmax_perc ['DHN_BOILER_WOOD'] := 0;
let fmax_perc ['DHN_BOILER_OIL'] := 0.00651;
let fmax_perc ['DHN_DEEP_GEO'] := 0.01;#0.00443;




# Heat Low T decentralized. Case2  (fixing elec out from cogen)
#From Heat Roadmap Belgium (2015) Figure 8.
let fmin_perc ['DEC_HP_ELEC'] := 0.011;
let fmin_perc ['DEC_THHP_GAS'] := 0;
let fmin_perc ['DEC_COGEN_GAS'] := 0.007;
let fmin_perc ['DEC_COGEN_OIL'] := 0.0;
let fmin_perc ['DEC_ADVCOGEN_GAS'] := 0;
let fmin_perc ['DEC_ADVCOGEN_H2'] := 0;
let fmin_perc ['DEC_BOILER_GAS'] := 0.0;
let fmin_perc ['DEC_BOILER_WOOD'] := 0.1;
let fmin_perc ['DEC_BOILER_OIL'] := 0.484;
let fmin_perc ['DEC_DIRECT_ELEC'] := 0.000;
let fmin_perc ['DEC_SOLAR'] := 0.002;

let fmax_perc ['DEC_HP_ELEC'] := 0.012;#0.05976717;
let fmax_perc ['DEC_THHP_GAS'] := 0;
let fmax_perc ['DEC_COGEN_GAS'] := 0.007;#0.00527278;
let fmax_perc ['DEC_COGEN_OIL'] := 0.0;#0.00050649;
let fmax_perc ['DEC_ADVCOGEN_GAS'] := 0;
let fmax_perc ['DEC_ADVCOGEN_H2'] := 0;
let fmax_perc ['DEC_BOILER_GAS'] := 1;#0.25706749;
let fmax_perc ['DEC_BOILER_WOOD'] := 0.3;#0.08228272;
let fmax_perc ['DEC_BOILER_OIL'] := 0.484;#0.49804229;
let fmax_perc ['DEC_SOLAR'] := 0.002;#0.00489076;
let fmax_perc ['DEC_DIRECT_ELEC'] := 0.00;#0.0921703;


# No PHS
let f_min ['PHS'] :=5.9;
let f_max ['PHS'] :=5.9;

# No TS :
let f_max ['TS_DEC_THHP_GAS'] :=0;
let f_max ['TS_DEC_HP_ELEC'] :=0;
let f_max ['TS_DEC_COGEN_GAS'] :=0;
let f_max ['TS_DEC_COGEN_OIL'] :=0;
let f_max ['TS_DEC_ADVCOGEN_GAS'] :=0;
let f_max ['TS_DEC_ADVCOGEN_H2'] :=0;
let f_max ['TS_DEC_BOILER_GAS'] :=0;
let f_max ['TS_DEC_BOILER_WOOD'] :=0;
let f_max ['TS_DEC_BOILER_OIL'] :=0;
let f_max ['TS_DEC_DIRECT_ELEC'] :=0;
let f_max ['TS_DHN_DAILY'] :=0;
let f_max ['TS_DHN_SEASONAL'] :=0;
let f_max ['TS_HIGH_TEMP'] :=0;

let f_max ['SLF_STO'] :=0;

# No synthetic fuels :
let f_max ["BIO_HYDROLYSIS"] := 0;
let f_max ["PYROLYSIS"] := 0;
let f_max ['SLF_TO_DIESEL'] :=0;
let f_max ['SLF_TO_GASOLINE'] :=0;
let f_max ['SLF_TO_LFO'] :=0;

fix F['NUCLEAR']:=5.925;
fix F['CCGT']:=3.925;
fix F['COAL_US']:=0.47;
fix F['COAL_IGCC']:=0;
fix F['PV']:=3.247;
fix F['WIND_ONSHORE']:=1.178;
fix F['WIND_OFFSHORE']:=0.693;
fix F['HYDRO_RIVER']:=0.087;
fix F['GEOTHERMAL']:=0;
fix F['IND_COGEN_GAS']:=0.817;
fix F['IND_COGEN_WOOD']:=0;
fix F['IND_COGEN_WASTE']:=0.532;
fix F['IND_BOILER_GAS']:=3.04;
fix F['IND_BOILER_WOOD']:=0;
fix F['IND_BOILER_OIL']:=1.699;
fix F['IND_BOILER_COAL']:=2.689;
fix F['IND_BOILER_WASTE']:=0;
fix F['IND_DIRECT_ELEC']:=0;
fix F['DHN_HP_ELEC']:=0.044;
fix F['DHN_COGEN_GAS']:=0.348;
fix F['DHN_COGEN_WOOD']:=0.059;
fix F['DHN_COGEN_WET_BIOMASS']:=0;
fix F['DHN_COGEN_BIO_HYDROLYSIS']:=0;
fix F['DHN_COGEN_WASTE']:=0.064;
fix F['DHN_BOILER_GAS']:=0.31;
fix F['DHN_BOILER_WOOD']:=0;
fix F['DHN_BOILER_OIL']:=0.076;
fix F['DHN_DEEP_GEO']:=0.005;
fix F['DHN_SOLAR']:=0;
fix F['DEC_HP_ELEC']:=0.591;
fix F['DEC_THHP_GAS']:=0;
fix F['DEC_COGEN_GAS']:=0.376;
fix F['DEC_COGEN_OIL']:=0;
fix F['DEC_ADVCOGEN_GAS']:=0;
fix F['DEC_ADVCOGEN_H2']:=0;
fix F['DEC_BOILER_GAS']:=21.367;
fix F['DEC_BOILER_WOOD']:=5.369;
fix F['DEC_BOILER_OIL']:=25.984;
fix F['DEC_SOLAR']:=0.513;
fix F['DEC_DIRECT_ELEC']:=0;
fix F['TRAMWAY_TROLLEY']:=0.473;
fix F['BUS_COACH_DIESEL']:=5.697;
fix F['BUS_COACH_HYDIESEL']:=0;
fix F['BUS_COACH_CNG_STOICH']:=1.212;
fix F['BUS_COACH_FC_HYBRIDH2']:=0;
fix F['TRAIN_PUB']:=5.035;
fix F['CAR_GASOLINE']:=98.984;
fix F['CAR_DIESEL']:=178.306;
fix F['CAR_NG']:=2.801;
fix F['CAR_HEV']:=0;
fix F['CAR_PHEV']:=0;
fix F['CAR_BEV']:=0;
fix F['CAR_FUEL_CELL']:=0;
fix F['TRAIN_FREIGHT']:=2.41;
fix F['BOAT_FREIGHT_DIESEL']:=10.344;
fix F['BOAT_FREIGHT_NG']:=0;
fix F['TRUCK_DIESEL']:=56.9;
fix F['TRUCK_FUEL_CELL']:=0;
fix F['TRUCK_NG']:=3.185;
fix F['TRUCK_ELEC']:=0;
fix F['NON_ENERGY_OIL']:=0;
fix F['NON_ENERGY_NG']:=0;
fix F['PHS']:=5.9;
fix F['BATT_LI']:=0;
fix F['BEV_BATT']:=0;
fix F['PHEV_BATT']:=0;
fix F['TS_DEC_HP_ELEC']:=0;
fix F['TS_DEC_DIRECT_ELEC']:=0;
fix F['TS_DHN_DAILY']:=0;
fix F['TS_DHN_SEASONAL']:=0;
fix F['TS_DEC_THHP_GAS']:=0;
fix F['TS_DEC_COGEN_GAS']:=0;
fix F['TS_DEC_COGEN_OIL']:=0;
fix F['TS_DEC_ADVCOGEN_GAS']:=0;
fix F['TS_DEC_ADVCOGEN_H2']:=0;
fix F['TS_DEC_BOILER_GAS']:=0;
fix F['TS_DEC_BOILER_WOOD']:=0;
fix F['TS_DEC_BOILER_OIL']:=0;
fix F['TS_HIGH_TEMP']:=0;
fix F['SEASONAL_NG']:=0;
fix F['SEASONAL_H2']:=0;
fix F['CO2_STORAGE']:=0;
fix F['SLF_STO']:=0;
# fix F['EFFICIENCY']:=0.986;
# fix F['DHN']:=0.902;
# fix F['GRID']:=1.026;
# fix F['MOTORWAYS']:=0;
# fix F['ROADS']:=0;
# fix F['RAILWAYS']:=0;
fix F['H2_ELECTROLYSIS']:=0;
fix F['H2_NG']:=0;
fix F['H2_BIOMASS']:=0;
fix F['GASIFICATION_SNG']:=0;
fix F['PYROLYSIS']:=0;
fix F['ATM_CCS']:=0;
fix F['INDUSTRY_CCS']:=0;
fix F['SYN_METHANOLATION']:=0;
fix F['SYN_METHANATION']:=0;
fix F['BIOMETHANATION']:=0.361;
fix F['BIO_HYDROLYSIS']:=0;
fix F['METHANE_TO_METHANOL']:=0;
fix F['SLF_TO_DIESEL']:=0;
fix F['SLF_TO_GASOLINE']:=0;
fix F['SLF_TO_LFO']:=0;



#let f_min['NUCLEAR'] := 0;	let f_max['NUCLEAR'] := 1e9;
#let f_min['CCGT'] := 0;	let f_max['CCGT'] := 1e9;
#let f_min['COAL_US'] := 0;	let f_max['COAL_US'] := 1e9;
#let f_min['COAL_IGCC'] := 0;	let f_max['COAL_IGCC'] := 1e9;
let f_min['PV'] := 0;	let f_max['PV'] := 1e9;
let f_min['WIND_ONSHORE'] := 0;	let f_max['WIND_ONSHORE'] := 1e9;
let f_min['WIND_OFFSHORE'] := 0;	let f_max['WIND_OFFSHORE'] := 1e9;
let f_min['HYDRO_RIVER'] := 0;	let f_max['HYDRO_RIVER'] := 1e9;
#let f_min['GEOTHERMAL'] := 0;	let f_max['GEOTHERMAL'] := 1e9;
let f_min['IND_COGEN_GAS'] := 0;	let f_max['IND_COGEN_GAS'] := 1e9;
let f_min['IND_COGEN_WOOD'] := 0;	let f_max['IND_COGEN_WOOD'] := 1e9;
let f_min['IND_COGEN_WASTE'] := 0;	let f_max['IND_COGEN_WASTE'] := 1e9;
let f_min['IND_BOILER_GAS'] := 0;	let f_max['IND_BOILER_GAS'] := 1e9;
let f_min['IND_BOILER_WOOD'] := 0;	let f_max['IND_BOILER_WOOD'] := 1e9;
let f_min['IND_BOILER_OIL'] := 0;	let f_max['IND_BOILER_OIL'] := 1e9;
let f_min['IND_BOILER_COAL'] := 0;	let f_max['IND_BOILER_COAL'] := 1e9;
let f_min['IND_BOILER_WASTE'] := 0;	let f_max['IND_BOILER_WASTE'] := 1e9;
let f_min['IND_DIRECT_ELEC'] := 0;	let f_max['IND_DIRECT_ELEC'] := 1e9;
let f_min['DHN_HP_ELEC'] := 0;	let f_max['DHN_HP_ELEC'] := 1e9;
let f_min['DHN_COGEN_GAS'] := 0;	let f_max['DHN_COGEN_GAS'] := 1e9;
let f_min['DHN_COGEN_WOOD'] := 0;	let f_max['DHN_COGEN_WOOD'] := 1e9;
let f_min['DHN_COGEN_WET_BIOMASS'] := 0;	let f_max['DHN_COGEN_WET_BIOMASS'] := 1e9;
let f_min['DHN_COGEN_BIO_HYDROLYSIS'] := 0;	let f_max['DHN_COGEN_BIO_HYDROLYSIS'] := 1e9;
let f_min['DHN_COGEN_WASTE'] := 0;	let f_max['DHN_COGEN_WASTE'] := 1e9;
let f_min['DHN_BOILER_GAS'] := 0;	let f_max['DHN_BOILER_GAS'] := 1e9;
let f_min['DHN_BOILER_WOOD'] := 0;	let f_max['DHN_BOILER_WOOD'] := 1e9;
let f_min['DHN_BOILER_OIL'] := 0;	let f_max['DHN_BOILER_OIL'] := 1e9;
let f_min['DHN_DEEP_GEO'] := 0;	let f_max['DHN_DEEP_GEO'] := 1e9;
let f_min['DHN_SOLAR'] := 0;	let f_max['DHN_SOLAR'] := 1e9;
let f_min['DEC_HP_ELEC'] := 0;	let f_max['DEC_HP_ELEC'] := 1e9;
let f_min['DEC_THHP_GAS'] := 0;	let f_max['DEC_THHP_GAS'] := 1e9;
let f_min['DEC_COGEN_GAS'] := 0;	let f_max['DEC_COGEN_GAS'] := 1e9;
let f_min['DEC_COGEN_OIL'] := 0;	let f_max['DEC_COGEN_OIL'] := 1e9;
let f_min['DEC_ADVCOGEN_GAS'] := 0;	let f_max['DEC_ADVCOGEN_GAS'] := 1e9;
let f_min['DEC_ADVCOGEN_H2'] := 0;	let f_max['DEC_ADVCOGEN_H2'] := 1e9;
let f_min['DEC_BOILER_GAS'] := 0;	let f_max['DEC_BOILER_GAS'] := 1e9;
let f_min['DEC_BOILER_WOOD'] := 0;	let f_max['DEC_BOILER_WOOD'] := 1e9;
let f_min['DEC_BOILER_OIL'] := 0;	let f_max['DEC_BOILER_OIL'] := 1e9;
let f_min['DEC_SOLAR'] := 0;	let f_max['DEC_SOLAR'] := 1e9;
let f_min['DEC_DIRECT_ELEC'] := 0;	let f_max['DEC_DIRECT_ELEC'] := 1e9;
let f_min['TRAMWAY_TROLLEY'] := 0;	let f_max['TRAMWAY_TROLLEY'] := 1e9;
let f_min['BUS_COACH_DIESEL'] := 0;	let f_max['BUS_COACH_DIESEL'] := 1e9;
let f_min['BUS_COACH_HYDIESEL'] := 0;	let f_max['BUS_COACH_HYDIESEL'] := 1e9;
let f_min['BUS_COACH_CNG_STOICH'] := 0;	let f_max['BUS_COACH_CNG_STOICH'] := 1e9;
#let f_min['BUS_COACH_FC_HYBRIDH2'] := 0;	let f_max['BUS_COACH_FC_HYBRIDH2'] := 1e9;
let f_min['TRAIN_PUB'] := 0;	let f_max['TRAIN_PUB'] := 1e9;
let f_min['CAR_GASOLINE'] := 0;	let f_max['CAR_GASOLINE'] := 1e9;
let f_min['CAR_DIESEL'] := 0;	let f_max['CAR_DIESEL'] := 1e9;
let f_min['CAR_NG'] := 0;	let f_max['CAR_NG'] := 1e9;
let f_min['CAR_HEV'] := 0;	let f_max['CAR_HEV'] := 1e9;
let f_min['CAR_PHEV'] := 0;	let f_max['CAR_PHEV'] := 1e9;
#let f_min['CAR_BEV'] := 0;	let f_max['CAR_BEV'] := 1e9;
#let f_min['CAR_FUEL_CELL'] := 0;	let f_max['CAR_FUEL_CELL'] := 1e9;
let f_min['TRAIN_FREIGHT'] := 0;	let f_max['TRAIN_FREIGHT'] := 1e9;
let f_min['BOAT_FREIGHT_DIESEL'] := 0;	let f_max['BOAT_FREIGHT_DIESEL'] := 1e9;
#let f_min['BOAT_FREIGHT_NG'] := 0;	let f_max['BOAT_FREIGHT_NG'] := 1e9;
let f_min['TRUCK_DIESEL'] := 0;	let f_max['TRUCK_DIESEL'] := 1e9;
#let f_min['TRUCK_FUEL_CELL'] := 0;	let f_max['TRUCK_FUEL_CELL'] := 1e9;
let f_min['TRUCK_NG'] := 0;	let f_max['TRUCK_NG'] := 1e9;
let f_min['TRUCK_ELEC'] := 0;	let f_max['TRUCK_ELEC'] := 1e9;
let f_min['NON_ENERGY_OIL'] := 0;	let f_max['NON_ENERGY_OIL'] := 1e9;
let f_min['NON_ENERGY_NG'] := 0;	let f_max['NON_ENERGY_NG'] := 1e9;
let f_min['PHS'] := 0;	let f_max['PHS'] := 1e9;
#let f_min['BATT_LI'] := 0;	let f_max['BATT_LI'] := 1e9;
let f_min['BEV_BATT'] := 0;	let f_max['BEV_BATT'] := 1e9;
let f_min['PHEV_BATT'] := 0;	let f_max['PHEV_BATT'] := 1e9;
#let f_min['TS_DEC_HP_ELEC'] := 0;	let f_max['TS_DEC_HP_ELEC'] := 1e9;
#let f_min['TS_DEC_DIRECT_ELEC'] := 0;	let f_max['TS_DEC_DIRECT_ELEC'] := 1e9;
#let f_min['TS_DHN_DAILY'] := 0;	let f_max['TS_DHN_DAILY'] := 1e9;
#let f_min['TS_DHN_SEASONAL'] := 0;	let f_max['TS_DHN_SEASONAL'] := 1e9;
#let f_min['TS_DEC_THHP_GAS'] := 0;	let f_max['TS_DEC_THHP_GAS'] := 1e9;
#let f_min['TS_DEC_COGEN_GAS'] := 0;	let f_max['TS_DEC_COGEN_GAS'] := 1e9;
#let f_min['TS_DEC_COGEN_OIL'] := 0;	let f_max['TS_DEC_COGEN_OIL'] := 1e9;
#let f_min['TS_DEC_ADVCOGEN_GAS'] := 0;	let f_max['TS_DEC_ADVCOGEN_GAS'] := 1e9;
#let f_min['TS_DEC_ADVCOGEN_H2'] := 0;	let f_max['TS_DEC_ADVCOGEN_H2'] := 1e9;
#let f_min['TS_DEC_BOILER_GAS'] := 0;	let f_max['TS_DEC_BOILER_GAS'] := 1e9;
#let f_min['TS_DEC_BOILER_WOOD'] := 0;	let f_max['TS_DEC_BOILER_WOOD'] := 1e9;
#let f_min['TS_DEC_BOILER_OIL'] := 0;	let f_max['TS_DEC_BOILER_OIL'] := 1e9;
#let f_min['TS_HIGH_TEMP'] := 0;	let f_max['TS_HIGH_TEMP'] := 1e9;
#let f_min['SEASONAL_NG'] := 0;	let f_max['SEASONAL_NG'] := 1e9;
#let f_min['SEASONAL_H2'] := 0;	let f_max['SEASONAL_H2'] := 1e9;
#let f_min['CO2_STORAGE'] := 0;	let f_max['CO2_STORAGE'] := 1e9;
#let f_min['SLF_STO'] := 0;	let f_max['SLF_STO'] := 1e9;
let f_min['EFFICIENCY'] := 0;	let f_max['EFFICIENCY'] := 1e9;
let f_min['DHN'] := 0;	let f_max['DHN'] := 1e9;
let f_min['GRID'] := 0;	let f_max['GRID'] := 1e9;
let f_min['MOTORWAYS'] := 0;	let f_max['MOTORWAYS'] := 1e9;
let f_min['ROADS'] := 0;	let f_max['ROADS'] := 1e9;
let f_min['RAILWAYS'] := 0;	let f_max['RAILWAYS'] := 1e9;
#let f_min['H2_ELECTROLYSIS'] := 0;	let f_max['H2_ELECTROLYSIS'] := 1e9;
#let f_min['H2_NG'] := 0;	let f_max['H2_NG'] := 1e9;
#let f_min['H2_BIOMASS'] := 0;	let f_max['H2_BIOMASS'] := 1e9;
#let f_min['GASIFICATION_SNG'] := 0;	let f_max['GASIFICATION_SNG'] := 1e9;
#let f_min['PYROLYSIS'] := 0;	let f_max['PYROLYSIS'] := 1e9;
#let f_min['ATM_CCS'] := 0;	let f_max['ATM_CCS'] := 1e9;
#let f_min['INDUSTRY_CCS'] := 0;	let f_max['INDUSTRY_CCS'] := 1e9;
#let f_min['SYN_METHANOLATION'] := 0;	let f_max['SYN_METHANOLATION'] := 1e9;
#let f_min['SYN_METHANATION'] := 0;	let f_max['SYN_METHANATION'] := 1e9;
let f_min['BIOMETHANATION'] := 0;	let f_max['BIOMETHANATION'] := 1e9;
#let f_min['BIO_HYDROLYSIS'] := 0;	let f_max['BIO_HYDROLYSIS'] := 1e9;
#let f_min['METHANE_TO_METHANOL'] := 0;	let f_max['METHANE_TO_METHANOL'] := 1e9;
#let f_min['SLF_TO_DIESEL'] := 0;	let f_max['SLF_TO_DIESEL'] := 1e9;
#let f_min['SLF_TO_GASOLINE'] := 0;	let f_max['SLF_TO_GASOLINE'] := 1e9;
#let f_min['SLF_TO_LFO'] := 0;	let f_max['SLF_TO_LFO'] := 1e9;

		

# No PHS
let f_min ['PHS'] :=5.9;
let f_max ['PHS'] :=5.9;

# No TS :
let f_max ['TS_DEC_THHP_GAS'] :=0;
let f_max ['TS_DEC_HP_ELEC'] :=0;
let f_max ['TS_DEC_COGEN_GAS'] :=0;
let f_max ['TS_DEC_COGEN_OIL'] :=0;
let f_max ['TS_DEC_ADVCOGEN_GAS'] :=0;
let f_max ['TS_DEC_ADVCOGEN_H2'] :=0;
let f_max ['TS_DEC_BOILER_GAS'] :=0;
let f_max ['TS_DEC_BOILER_WOOD'] :=0;
let f_max ['TS_DEC_BOILER_OIL'] :=0;
let f_max ['TS_DEC_DIRECT_ELEC'] :=0;
let f_max ['TS_DHN_DAILY'] :=0;
let f_max ['TS_DHN_SEASONAL'] :=0;
let f_max['TRUCK_FUEL_CELL'] := 0;
let f_max['TRUCK_ELEC'] := 0;
let f_min['BOAT_FREIGHT_NG'] := 0;
let f_max['BOAT_FREIGHT_NG'] := 0;
		