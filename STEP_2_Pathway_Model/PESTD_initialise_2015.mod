## Constraints needed to reproduce the scenario for BE in 2015
## All data are calculated in Excel file



# START : Tackle problem:
let f_min['YEAR_2015',"DHN_DEEP_GEO"] := 0;
let fmin_perc['YEAR_2015',"DHN_DEEP_GEO"] := 0;
# END

let f_max['YEAR_2015',"NUCLEAR"] := 5.925;


let re_share_primary ['YEAR_2015'] := 0.0;
let gwp_limit ['YEAR_2015'] := 150e9;#

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

# subject to elec_prod_GT_OIL: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['YEAR_2015','GT_OIL', h , td] ) = 200;
# subject to elec_prod_INCINERATOR: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['YEAR_2015','INCINERATOR', h , td] ) = 530;
# subject to elec_prod_BIOMASS_ST: sum {t in PERIODS, h in HOUR_OF_PERIOD [t], td in TYPICAL_DAY_OF_PERIOD [t]} (F_t ['YEAR_2015','BIOMASS_ST', h , td] ) = 3600;



let fmin_perc['YEAR_2015','TRUCK_NG'] := 0.053;
let fmax_perc['YEAR_2015','TRUCK_NG'] := 0.053;
let f_max['YEAR_2015','TRUCK_FUEL_CELL'] := 0;
let f_max['YEAR_2015','TRUCK_ELEC'] := 0;
let f_min['YEAR_2015','BOAT_FREIGHT_NG'] := 0;
let f_max['YEAR_2015','BOAT_FREIGHT_NG'] := 0;


#SOURCE : # Eurostat2017 p49
let fmin_perc['YEAR_2015','TRAMWAY_TROLLEY'] := 0.045;
let fmin_perc['YEAR_2015','BUS_COACH_DIESEL'] := 0.47;# 90%  du service publique hors train est en tram/metro
let fmin_perc['YEAR_2015','BUS_COACH_HYDIESEL'] := 0;
let fmin_perc['YEAR_2015','BUS_COACH_CNG_STOICH'] := 0.10;# 90%  du service publique hors train est en tram/metro
let fmin_perc['YEAR_2015','BUS_COACH_FC_HYBRIDH2'] := 0;
let fmin_perc['YEAR_2015','TRAIN_PUB'] := 0.385; #slide 4 de #slide 10 of https://mobilit.belgium.be/sites/default/files/chiffres_cles_mobilite_2017.pdf
let fmax_perc['YEAR_2015','TRAMWAY_TROLLEY'] := 0.045;
let fmax_perc['YEAR_2015','BUS_COACH_DIESEL'] := 1;
let fmax_perc['YEAR_2015','BUS_COACH_HYDIESEL'] := 0;
let fmax_perc['YEAR_2015','BUS_COACH_CNG_STOICH'] := 0.10;
let fmax_perc['YEAR_2015','BUS_COACH_FC_HYBRIDH2'] := 0;
let fmax_perc['YEAR_2015','TRAIN_PUB'] := 0.385;#slide 4 de #slide 10 of https://mobilit.belgium.be/sites/default/files/chiffres_cles_mobilite_2017.pdf

# Private mobility
let fmin_perc['YEAR_2015','CAR_GASOLINE'] := 0.3534;#slide 10 of https://mobilit.belgium.be/sites/default/files/chiffres_cles_mobilite_2017.pdf
let fmin_perc['YEAR_2015','CAR_DIESEL'] := 0.0;#slide 10 of https://mobilit.belgium.be/sites/default/files/chiffres_cles_mobilite_2017.pdf
let fmin_perc['YEAR_2015','CAR_NG'] := 0.01;
let fmin_perc['YEAR_2015','CAR_HEV'] := 0.0;#slide 10 of https://mobilit.belgium.be/sites/default/files/chiffres_cles_mobilite_2017.pdf
let fmin_perc['YEAR_2015','CAR_PHEV'] := 0.0;
let fmin_perc['YEAR_2015','CAR_BEV'] := 0.0;
let fmin_perc['YEAR_2015','CAR_FUEL_CELL'] := 0.0;
let fmax_perc['YEAR_2015','CAR_GASOLINE'] := 0.3535; #slide 10 of https://mobilit.belgium.be/sites/default/files/chiffres_cles_mobilite_2017.pdf
let fmax_perc['YEAR_2015','CAR_DIESEL'] := 1;#slide 10 of https://mobilit.belgium.be/sites/default/files/chiffres_cles_mobilite_2017.pdf
let fmax_perc['YEAR_2015','CAR_NG'] := 0.01;
let fmax_perc['YEAR_2015','CAR_HEV'] := 0.0;#slide 10 of https://mobilit.belgium.be/sites/default/files/chiffres_cles_mobilite_2017.pdf
let fmax_perc['YEAR_2015','CAR_PHEV'] := 0.0;
let fmax_perc['YEAR_2015','CAR_BEV'] := 0.0;
let fmax_perc['YEAR_2015','CAR_FUEL_CELL'] := 0.0;

# Industry - Case 2 (fixing elec output)
let fmin_perc ['YEAR_2015','IND_COGEN_GAS'] := 0.086;#
let fmin_perc ['YEAR_2015','IND_COGEN_WOOD'] := 0;#
let fmin_perc ['YEAR_2015','IND_COGEN_WASTE'] := 0.056;#
let fmin_perc ['YEAR_2015','IND_BOILER_GAS'] := 0;#
let fmin_perc ['YEAR_2015','IND_BOILER_WOOD'] := 0.0;#
let fmin_perc ['YEAR_2015','IND_BOILER_OIL'] := 0.2;#
let fmin_perc ['YEAR_2015','IND_BOILER_COAL'] := 0.3;#
let fmin_perc ['YEAR_2015','IND_BOILER_WASTE'] := 0;#
let fmin_perc ['YEAR_2015','IND_DIRECT_ELEC'] := 0.00;#

let fmax_perc ['YEAR_2015','IND_COGEN_GAS'] := 0.086;#0.0244;
let fmax_perc ['YEAR_2015','IND_COGEN_WOOD'] := 0;#0.0075;
let fmax_perc ['YEAR_2015','IND_COGEN_WASTE'] := 0.056;#0.0177;
let fmax_perc ['YEAR_2015','IND_BOILER_GAS'] := 1;#0.2433;
let fmax_perc ['YEAR_2015','IND_BOILER_WOOD'] := 0.0;#0.0697;
let fmax_perc ['YEAR_2015','IND_BOILER_OIL'] := 0.2;#0.256;
let fmax_perc ['YEAR_2015','IND_BOILER_COAL'] := 0.3;#0.0507;
let fmax_perc ['YEAR_2015','IND_BOILER_WASTE'] := 0;#0.056;
let fmax_perc ['YEAR_2015','IND_DIRECT_ELEC'] := 0.0;#0.2747;


# Heat Low T DHN
let loss_network ['YEAR_2015','HEAT_LOW_T_DHN'] := 0.0864;


# Case2  (fixing cogen electricity production)
let fmin_perc ['YEAR_2015','DHN_HP_ELEC'] := 0.0436;
let fmin_perc ['YEAR_2015','DHN_COGEN_GAS'] := 0.59413;
let fmin_perc ['YEAR_2015','DHN_COGEN_WOOD'] := 0.06603;
let fmin_perc ['YEAR_2015','DHN_COGEN_WASTE'] := 0.124080;#0.72823;
let fmin_perc ['YEAR_2015','DHN_BOILER_GAS'] := 0.13883;
let fmin_perc ['YEAR_2015','DHN_BOILER_WOOD'] := 0;
let fmin_perc ['YEAR_2015','DHN_BOILER_OIL'] := 0.00651;
let fmin_perc ['YEAR_2015','DHN_DEEP_GEO'] := 0.01;#0.00443;
let fmax_perc ['YEAR_2015','DHN_HP_ELEC'] := 0.0437;
let fmax_perc ['YEAR_2015','DHN_COGEN_GAS'] := 0.59413;
let fmax_perc ['YEAR_2015','DHN_COGEN_WOOD'] := 0.06603;
let fmax_perc ['YEAR_2015','DHN_COGEN_WASTE'] := 0.14080;#0.72823;
let fmax_perc ['YEAR_2015','DHN_BOILER_GAS'] := 0.13883;
let fmax_perc ['YEAR_2015','DHN_BOILER_WOOD'] := 0;
let fmax_perc ['YEAR_2015','DHN_BOILER_OIL'] := 0.00651;
let fmax_perc ['YEAR_2015','DHN_DEEP_GEO'] := 0.01;#0.00443;




# Heat Low T decentralized. Case2  (fixing elec out from cogen)
#From Heat Roadmap Belgium (2015) Figure 8.
let fmin_perc ['YEAR_2015','DEC_HP_ELEC'] := 0.011;
let fmin_perc ['YEAR_2015','DEC_THHP_GAS'] := 0;
let fmin_perc ['YEAR_2015','DEC_COGEN_GAS'] := 0.007;
let fmin_perc ['YEAR_2015','DEC_COGEN_OIL'] := 0.0;
let fmin_perc ['YEAR_2015','DEC_ADVCOGEN_GAS'] := 0;
let fmin_perc ['YEAR_2015','DEC_ADVCOGEN_H2'] := 0;
let fmin_perc ['YEAR_2015','DEC_BOILER_GAS'] := 0.0;
let fmin_perc ['YEAR_2015','DEC_BOILER_WOOD'] := 0.1;
let fmin_perc ['YEAR_2015','DEC_BOILER_OIL'] := 0.484;
let fmin_perc ['YEAR_2015','DEC_DIRECT_ELEC'] := 0.000;
let fmin_perc ['YEAR_2015','DEC_SOLAR'] := 0.002;

let fmax_perc ['YEAR_2015','DEC_HP_ELEC'] := 0.012;#0.05976717;
let fmax_perc ['YEAR_2015','DEC_THHP_GAS'] := 0;
let fmax_perc ['YEAR_2015','DEC_COGEN_GAS'] := 0.007;#0.00527278;
let fmax_perc ['YEAR_2015','DEC_COGEN_OIL'] := 0.0;#0.00050649;
let fmax_perc ['YEAR_2015','DEC_ADVCOGEN_GAS'] := 0;
let fmax_perc ['YEAR_2015','DEC_ADVCOGEN_H2'] := 0;
let fmax_perc ['YEAR_2015','DEC_BOILER_GAS'] := 1;#0.25706749;
let fmax_perc ['YEAR_2015','DEC_BOILER_WOOD'] := 0.3;#0.08228272;
let fmax_perc ['YEAR_2015','DEC_BOILER_OIL'] := 0.484;#0.49804229;
let fmax_perc ['YEAR_2015','DEC_SOLAR'] := 0.002;#0.00489076;
let fmax_perc ['YEAR_2015','DEC_DIRECT_ELEC'] := 0.00;#0.0921703;


# No PHS
let f_min ['YEAR_2015','PHS'] :=5.9;
let f_max ['YEAR_2015','PHS'] :=5.9;

# No TS :
let f_max ['YEAR_2015','TS_DEC_THHP_GAS'] :=0;
let f_max ['YEAR_2015','TS_DEC_HP_ELEC'] :=0;
let f_max ['YEAR_2015','TS_DEC_COGEN_GAS'] :=0;
let f_max ['YEAR_2015','TS_DEC_COGEN_OIL'] :=0;
let f_max ['YEAR_2015','TS_DEC_ADVCOGEN_GAS'] :=0;
let f_max ['YEAR_2015','TS_DEC_ADVCOGEN_H2'] :=0;
let f_max ['YEAR_2015','TS_DEC_BOILER_GAS'] :=0;
let f_max ['YEAR_2015','TS_DEC_BOILER_WOOD'] :=0;
let f_max ['YEAR_2015','TS_DEC_BOILER_OIL'] :=0;
let f_max ['YEAR_2015','TS_DEC_DIRECT_ELEC'] :=0;
let f_max ['YEAR_2015','TS_DHN_DAILY'] :=0;
let f_max ['YEAR_2015','TS_DHN_SEASONAL'] :=0;
let f_max ['YEAR_2015','TS_HIGH_TEMP'] :=0;

let f_max ['YEAR_2015','SLF_STO'] :=0;

# No synthetic fuels :
let f_max ['YEAR_2015',"BIO_HYDROLYSIS"] := 0;
let f_max ['YEAR_2015',"PYROLYSIS"] := 0;
let f_max ['YEAR_2015','SLF_TO_DIESEL'] :=0;
let f_max ['YEAR_2015','SLF_TO_GASOLINE'] :=0;
let f_max ['YEAR_2015','SLF_TO_LFO'] :=0;

fix F['YEAR_2015','NUCLEAR']:=5.925;
fix F['YEAR_2015','CCGT']:=3.925;
fix F['YEAR_2015','COAL_US']:=0.47;
fix F['YEAR_2015','COAL_IGCC']:=0;
#fix F['YEAR_2015','PV']:=3.247;
#fix F['YEAR_2015','WIND_ONSHORE']:=1.178;
#fix F['YEAR_2015','WIND_OFFSHORE']:=0.693;
#fix F['YEAR_2015','HYDRO_RIVER']:=0.087;
fix F['YEAR_2015','GEOTHERMAL']:=0;
#fix F['YEAR_2015','IND_COGEN_GAS']:=0.817;
fix F['YEAR_2015','IND_COGEN_WOOD']:=0;
#fix F['YEAR_2015','IND_COGEN_WASTE']:=0.532;
#fix F['YEAR_2015','IND_BOILER_GAS']:=3.04;
fix F['YEAR_2015','IND_BOILER_WOOD']:=0;
#fix F['YEAR_2015','IND_BOILER_OIL']:=1.699;
#fix F['YEAR_2015','IND_BOILER_COAL']:=2.689;
fix F['YEAR_2015','IND_BOILER_WASTE']:=0;
fix F['YEAR_2015','IND_DIRECT_ELEC']:=0;
#fix F['YEAR_2015','DHN_HP_ELEC']:=0.044;
#fix F['YEAR_2015','DHN_COGEN_GAS']:=0.348;
#fix F['YEAR_2015','DHN_COGEN_WOOD']:=0.059;
fix F['YEAR_2015','DHN_COGEN_WET_BIOMASS']:=0;
fix F['YEAR_2015','DHN_COGEN_BIO_HYDROLYSIS']:=0;
#fix F['YEAR_2015','DHN_COGEN_WASTE']:=0.064;
#fix F['YEAR_2015','DHN_BOILER_GAS']:=0.31;
fix F['YEAR_2015','DHN_BOILER_WOOD']:=0;
#fix F['YEAR_2015','DHN_BOILER_OIL']:=0.076;
#fix F['YEAR_2015','DHN_DEEP_GEO']:=0.005;
fix F['YEAR_2015','DHN_SOLAR']:=0;
#fix F['YEAR_2015','DEC_HP_ELEC']:=0.591;
fix F['YEAR_2015','DEC_THHP_GAS']:=0;
#fix F['YEAR_2015','DEC_COGEN_GAS']:=0.376;
fix F['YEAR_2015','DEC_COGEN_OIL']:=0;
fix F['YEAR_2015','DEC_ADVCOGEN_GAS']:=0;
fix F['YEAR_2015','DEC_ADVCOGEN_H2']:=0;
#fix F['YEAR_2015','DEC_BOILER_GAS']:=21.367;
#fix F['YEAR_2015','DEC_BOILER_WOOD']:=5.369;
#fix F['YEAR_2015','DEC_BOILER_OIL']:=25.984;
#fix F['YEAR_2015','DEC_SOLAR']:=0.513;
fix F['YEAR_2015','DEC_DIRECT_ELEC']:=0;
#fix F['YEAR_2015','TRAMWAY_TROLLEY']:=0.473;
#fix F['YEAR_2015','BUS_COACH_DIESEL']:=5.697;
fix F['YEAR_2015','BUS_COACH_HYDIESEL']:=0;
#fix F['YEAR_2015','BUS_COACH_CNG_STOICH']:=1.212;
fix F['YEAR_2015','BUS_COACH_FC_HYBRIDH2']:=0;
#fix F['YEAR_2015','TRAIN_PUB']:=5.035;
#fix F['YEAR_2015','CAR_GASOLINE']:=98.984;
#fix F['YEAR_2015','CAR_DIESEL']:=178.306;
#fix F['YEAR_2015','CAR_NG']:=2.801;
fix F['YEAR_2015','CAR_HEV']:=0;
fix F['YEAR_2015','CAR_PHEV']:=0;
fix F['YEAR_2015','CAR_BEV']:=0;
fix F['YEAR_2015','CAR_FUEL_CELL']:=0;
#fix F['YEAR_2015','TRAIN_FREIGHT']:=2.41;
#fix F['YEAR_2015','BOAT_FREIGHT_DIESEL']:=10.344;
fix F['YEAR_2015','BOAT_FREIGHT_NG']:=0;
#fix F['YEAR_2015','TRUCK_DIESEL']:=56.9;
fix F['YEAR_2015','TRUCK_FUEL_CELL']:=0;
#fix F['YEAR_2015','TRUCK_NG']:=3.185;
fix F['YEAR_2015','TRUCK_ELEC']:=0;
fix F['YEAR_2015','NON_ENERGY_OIL']:=0;
fix F['YEAR_2015','NON_ENERGY_NG']:=0;
fix F['YEAR_2015','PHS']:=5.9;
fix F['YEAR_2015','BATT_LI']:=0;
fix F['YEAR_2015','BEV_BATT']:=0;
fix F['YEAR_2015','PHEV_BATT']:=0;
fix F['YEAR_2015','TS_DEC_HP_ELEC']:=0;
fix F['YEAR_2015','TS_DEC_DIRECT_ELEC']:=0;
fix F['YEAR_2015','TS_DHN_DAILY']:=0;
fix F['YEAR_2015','TS_DHN_SEASONAL']:=0;
fix F['YEAR_2015','TS_DEC_THHP_GAS']:=0;
fix F['YEAR_2015','TS_DEC_COGEN_GAS']:=0;
fix F['YEAR_2015','TS_DEC_COGEN_OIL']:=0;
fix F['YEAR_2015','TS_DEC_ADVCOGEN_GAS']:=0;
fix F['YEAR_2015','TS_DEC_ADVCOGEN_H2']:=0;
fix F['YEAR_2015','TS_DEC_BOILER_GAS']:=0;
fix F['YEAR_2015','TS_DEC_BOILER_WOOD']:=0;
fix F['YEAR_2015','TS_DEC_BOILER_OIL']:=0;
fix F['YEAR_2015','TS_HIGH_TEMP']:=0;
fix F['YEAR_2015','SEASONAL_NG']:=0;
fix F['YEAR_2015','SEASONAL_H2']:=0;
fix F['YEAR_2015','CO2_STORAGE']:=0;
fix F['YEAR_2015','SLF_STO']:=0;
# fix F['YEAR_2015','EFFICIENCY']:=0.986;
# fix F['YEAR_2015','DHN']:=0.902;
# fix F['YEAR_2015','GRID']:=1.026;
# fix F['YEAR_2015','MOTORWAYS']:=0;
# fix F['YEAR_2015','ROADS']:=0;
# fix F['YEAR_2015','RAILWAYS']:=0;
fix F['YEAR_2015','H2_ELECTROLYSIS']:=0;
fix F['YEAR_2015','H2_NG']:=0;
fix F['YEAR_2015','H2_BIOMASS']:=0;
fix F['YEAR_2015','GASIFICATION_SNG']:=0;
fix F['YEAR_2015','PYROLYSIS']:=0;
fix F['YEAR_2015','ATM_CCS']:=0;
fix F['YEAR_2015','INDUSTRY_CCS']:=0;
fix F['YEAR_2015','SYN_METHANOLATION']:=0;
fix F['YEAR_2015','SYN_METHANATION']:=0;
#fix F['YEAR_2015','BIOMETHANATION']:=0.361;
fix F['YEAR_2015','BIO_HYDROLYSIS']:=0;
fix F['YEAR_2015','METHANE_TO_METHANOL']:=0;
fix F['YEAR_2015','SLF_TO_DIESEL']:=0;
fix F['YEAR_2015','SLF_TO_GASOLINE']:=0;
fix F['YEAR_2015','SLF_TO_LFO']:=0;
