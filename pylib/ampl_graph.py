#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun. 13 2022

@author: rixhonx
"""

from pathlib import Path
import matplotlib.pyplot as plt
import pickle

import os,sys

pylibPath = os.path.abspath("../pylib")
if pylibPath not in sys.path:
    sys.path.insert(0, pylibPath)

class AMPLGraph:

    """

    The AmplGraph class allows to plot the relevant outputs (e.g. installed capacitites, used resources, costs)
    of an optimisation problem.

    Parameters
    ----------
    result_list: list(Pandas.DataFrame)
        Unpickled list where relevant outputs has been stored

    """

    def __init__(self, pkl_file):
        self.pkl_file = pkl_file
        self.save_list = self.ampl_collector.ampl_obj.sets['STORE_RESULTS']
        self.x_axis = [2020, 2025, 2030, 2035, 2040, 2045, 2050]
        self.pkl_results = self.unpkl()

    @staticmethod
    def unpkl(self):
        open_file = open(self.pkl_file,"rb")
        loaded_list = pickle.load(open_file)
        open_file.close()

        return loaded_list
    
    @staticmethod
    def is_number(s): 

        """
        Return True if s is a number, False otherwise.

        """
        try:
            float(s)
            return True
        except ValueError:
            pass
    
        return False
    
    # def save_all(output_name,save_folder_name,no_2015=False):

    #     """
    #     Save multiple graphs in a folder with a given name. The graphs saved are :
    #         - The technologies capacity during the transition in every sectors 
    #         - The resources used during the transition
    #         - The energy produced in the diffrent sectors
    #         - The electricity produced from fossil fuels versus from renewables resources
    #     _____________________________________________________________________________________________________________________

    #     output_name : name of the folder where the output are stored. 
        
    #     save_folder_name : name of the folder where the graphs will be saved (the folder will be inside a folder named "Graphs")

    #     no_2015 : boolean, if True then the year 2015 will not be showed in the graphs, otherwise it will be. 
    #     """

    #     THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    #     if not os.path.exists(os.path.join(THIS_FOLDER,'Graphs')):
    #         os.makedirs(os.path.join(THIS_FOLDER,'Graphs'))
    #     save_path = os.path.join(THIS_FOLDER,'Graphs',save_folder_name)
    #     if not os.path.exists(save_path):
    #         os.makedirs(save_path)

    #     if no_2015 == True:
    #         years = ['2020','2025','2030','2035','2040','2045','2050']
    #     else:
    #         years = ['2015','2020','2025','2030','2035','2040','2045','2050']
        
    #     # technologies capacity 
    #     sectors = ['Electricity','Heat_low_T','Heat_high_T','Mobility','Freight','Conversion','Storage','Storage_daily']
    #     self.stack_chart(os.path.join(THIS_FOLDER,output_name),sectors,save_folder_name=save_folder_name,no_2015=no_2015)

    #     # resources used 
    #     self.stack_chart(os.path.join(THIS_FOLDER,output_name),['Resources'],save_folder_name=save_folder_name,no_2015=no_2015)


    # @staticmethod
    # def stack_chart(output_name,sectors,save_folder_name = "none",no_2015=False):

    #     """
    #     Create and save the stack chart of the technologies capacity in the different sectors or the total resources used
    #     _____________________________________________________________________________________________________________________________

    #     output_name : name of the folder where the output are stored. 

    #     sectors : list containing the sectors to plot. 
    #                 If we want to plot the resources used, the vector must contain only 'Resources'. In this case, the EUD will also be plot in seperate graphs
    #                 Otherwise, the array contains the different sectors to plot 
    #                 Example : if we want to plot all the technology sectors then -->
    #                             sectors = ['Electricity','Heat_low_T','Heat_high_T','Mobility','Freight','Conversion','Storage']
    #                         or sectors = ['Electricity,'Heat_low_T'] if we only want those two sectors. 
        
    #     save_folder_name : name of the folder (in the folder named "Graphs") where the resulting graphs need to be saved.
    #                 Example : save_folder_name = 'pathway' to save the graph in a folder name "pathway" that will be in te big folder named "Graphs" 

    #     no_2015 : boolean, if True then the year 2015 will not be showed in the plot, otherwise it will be showed. 
        
    #     """

    #     THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    #     if not os.path.exists(os.path.join(THIS_FOLDER,'Graphs')):
    #         os.makedirs(os.path.join(THIS_FOLDER,'Graphs')) # Create the folder named "Graphs"
    #     save_path = os.path.join(THIS_FOLDER,'Graphs',save_folder_name)
    #     if not os.path.exists(save_path): 
    #         os.makedirs(save_path) # Create the folder named save_folder_name in the folder "Graphs"
        

    #     for sector in sectors: # for every sectors
    #         if sector == 'Resources':
    #             file_txt = os.path.join(output_name,'RES.txt')
    #         else:
    #             file_txt = os.path.join(output_name,'F_years.txt')
    #         file = open(file_txt, "r")
    #         num_of_lines = len(file.readlines())
    #         file.close()
    #         file = open(file_txt, "r")
    #         num_vect = 0 # will be number of column per line
            
    #         line = file.readline() 
    #         vect = line.split() 
    #         if no_2015:
    #             x = ['2020','2025','2030','2035','2040','2045','2050'] 
    #         else:
    #             x = ['2015','2020','2025','2030','2035','2040','2045','2050'] 
    #         num_vect = len(x) 

    #         # colors depending on the sectors 
    #         if sector == 'Electricity':
    #             color_dict = {"NUCLEAR":"deeppink", "CCGT":"darkorange", "COAL_US" : "black", "COAL_IGCC" : "dimgray", "PV" : "yellow", "WIND_ONSHORE" : "lawngreen", "WIND_OFFSHORE" : "green", "HYDRO_RIVER" : "blue", "GEOTHERMAL" : "firebrick"}
    #         elif sector == 'Heat_low_T':
    #             color_dict = {"DHN_HP_ELEC" : "blue", "DHN_COGEN_GAS" : "orange", "DHN_COGEN_WOOD" : "sandybrown", "DHN_COGEN_WASTE" : "olive", "DHN_COGEN_WET_BIOMASS" : "seagreen", "DHN_COGEN_BIO_HYDROLYSIS" : "springgreen", "DHN_BOILER_GAS" : "darkorange", "DHN_BOILER_WOOD" : "sienna", "DHN_BOILER_OIL" : "blueviolet", "DHN_DEEP_GEO" : "firebrick", "DHN_SOLAR" : "gold", "DEC_HP_ELEC" : "cornflowerblue", "DEC_THHP_GAS" : "lightsalmon", "DEC_COGEN_GAS" : "goldenrod", "DEC_COGEN_OIL" : "mediumpurple", "DEC_ADVCOGEN_GAS" : "burlywood", "DEC_ADVCOGEN_H2" : "violet", "DEC_BOILER_GAS" : "moccasin", "DEC_BOILER_WOOD" : "peru", "DEC_BOILER_OIL" : "darkorchid", "DEC_SOLAR" : "yellow", "DEC_DIRECT_ELEC" : "deepskyblue"}
    #         elif sector == 'Heat_high_T':
    #             color_dict = {"IND_COGEN_GAS":"orange", "IND_COGEN_WOOD":"peru", "IND_COGEN_WASTE" : "olive", "IND_BOILER_GAS" : "moccasin", "IND_BOILER_WOOD" : "goldenrod", "IND_BOILER_OIL" : "blueviolet", "IND_BOILER_COAL" : "black", "IND_BOILER_WASTE" : "olivedrab", "IND_DIRECT_ELEC" : "royalblue"}
    #         elif sector == 'Mobility':
    #             color_dict = {"TRAMWAY_TROLLEY" : "dodgerblue", "BUS_COACH_DIESEL" : "dimgrey", "BUS_COACH_HYDIESEL" : "gray", "BUS_COACH_CNG_STOICH" : "orange", "BUS_COACH_FC_HYBRIDH2" : "violet", "TRAIN_PUB" : "blue", "CAR_GASOLINE" : "black", "CAR_DIESEL" : "lightgray", "CAR_NG" : "moccasin", "CAR_HEV" : "salmon", "CAR_PHEV" : "lightsalmon", "CAR_BEV" : "deepskyblue", "CAR_FUEL_CELL" : "magenta"}
    #         elif sector == 'Freight':
    #             color_dict = {"TRAIN_FREIGHT" : "royalblue", "BOAT_FREIGHT_DIESEL" : "dimgrey", "BOAT_FREIGHT_NG" : "darkorange", "TRUCK_DIESEL" : "darkgrey", "TRUCK_FUEL_CELL" : "violet", "TRUCK_ELEC" : "dodgerblue", "TRUCK_NG" : "moccasin"}
    #         elif sector == 'Conversion':
    #             color_dict = {"H2_ELECTROLYSIS" : "violet", "H2_NG" : "magenta", "H2_BIOMASS" : "orchid", "GASIFICATION_SNG" : "orange", "PYROLYSIS" : "blueviolet", "ATM_CCS" : "black", "INDUSTRY_CCS" : "grey", "SYN_METHANOLATION" : "mediumpurple", "SYN_METHANATION" : "moccasin", "BIOMETHANATION" : "darkorange", "BIO_HYDROLYSIS" : "gold", "METHANE_TO_METHANOL" : "darkmagenta"}
    #         elif sector == 'Storage':
    #             color_dict = {"TS_DHN_SEASONAL" : "indianred", "BATT_LI" : "royalblue", "BEV_BATT" : "deepskyblue", "PHEV_BATT" : "lightskyeblue", "PHS" : "dodgerblue", "TS_DEC_HP_ELEC" : "blue", "TS_DHN_DAILY" : "lightcoral", "TS_HIGH_TEMP" : "red", "SEASONAL_NG" : "orange", "SEASONAL_H2" : "violet", "SLF_STO" : "blueviolet"}
    #         elif sector == 'Storage_daily':
    #             color_dict = {"BATT_LI" : "royalblue", "BEV_BATT" : "deepskyblue", "PHEV_BATT" : "lightskyeblue", "PHS" : "dodgerblue", "TS_DEC_HP_ELEC" : "blue", "TS_DHN_DAILY" : "lightcoral", "TS_HIGH_TEMP" : "red"}
    #         elif sector == 'Resources':
    #             color_dict = {"ELECTRICITY" : "royalblue", "GASOLINE" : "gray", "DIESEL" : "silver", "BIOETHANOL" : "darkorchid", "BIODIESEL" : "mediumpurple", "LFO" : "darkviolet", "NG" : "orange", "SNG" : "moccasin", "WOOD" : "peru", "WET_BIOMASS" : "seagreen", "COAL" : "black", "URANIUM" : "deeppink", "WASTE" : "olive", "H2" : "violet", "SLF" : "mediumpurple", "RES_WIND" : "limegreen", "RES_SOLAR" : "yellow", "RES_HYDRO" : "blue", "RES_GEO" : "firebrick"}    
    #             # To compare the different types of resources
    #             vect_fossil = ['GASOLINE','DIESEL','LFO','NG','COAL','URANIUM','WASTE']
    #             vect_renewable = ['RES_SOLAR','RES_WIND','RES_HYDRO','RES_GEO','WOOD','WET_BIOMASS']
    #             vect_synfuels = ['BIOETHANOL','BIODIESEL','H2','SLF','SNG']
    #             label_comp = ['Renewable','Fossil','Synfuels','Electricity']
    #             color_comp = ['green','grey','lightgreen','blue']
    #         y = np.zeros((num_of_lines-1,num_vect))
    #         comp_fos_ren_syn = np.zeros((4,num_vect))
    #         colors = []
    #         labels = []
    #         tech = 0
    #         for i in range(num_of_lines-1):
    #             line = file.readline() 
    #             vect = line.split() 
    #             array_str = np.array(vect[-num_vect:]) 
    #             array_num = array_str.astype(np.float) # numpy array of the line for a technology depending on the years
    #             if vect[0] in color_dict and sum(array_num) != 0: # If the technology is in the sectors of interesting and the tehcnology is used during the transition
    #                 if sector == 'Resources': 
    #                     y[tech][:] = np.divide(array_num,1000) # to convert GWh to TWh
    #                     # add the TWh of used resources in the good type of resources
    #                     if vect[0] in vect_renewable:
    #                         comp_fos_ren_syn[0][:] = np.add(np.divide(array_num,1000),comp_fos_ren_syn[0][:])
    #                     elif vect[0] in vect_fossil:
    #                         comp_fos_ren_syn[1][:] = np.add(np.divide(array_num,1000),comp_fos_ren_syn[1][:])
    #                     elif vect[0] in vect_synfuels:
    #                         comp_fos_ren_syn[2][:] = np.add(np.divide(array_num,1000),comp_fos_ren_syn[2][:])
    #                     else:
    #                         comp_fos_ren_syn[3][:] = np.add(np.divide(array_num,1000),comp_fos_ren_syn[3][:])
    #                 else:
    #                     y[tech][:] = array_num
    #                 tech = tech + 1
    #                 labels.append(vect[0]) 
    #                 colors.append(color_dict.get(vect[0])) 
        
    #         file.close()

    #         if sector == 'Resources':
    #             name_EUD = ['EUD_elec','EUD_lowT','EUD_highT','EUD_passenger','EUD_freight']
    #             color_EUD = ["turquoise","lightcoral","firebrick","lightgrey","darkgrey"]
    #             demand = np.zeros((len(name_EUD),len(x)))
    #             for year in range(len(x)):
    #                 path_year_balance = os.path.join(output_name,'YEAR_'+x[year],'year_balance.txt')
    #                 with open(path_year_balance,'r') as f:
    #                     year_balance = f.readlines()
    #                 name_vect = year_balance[0].split()[1:]
    #                 EUD = year_balance[-1].split()[1:]
    #                 for j in range(len(EUD)):
    #                     if name_vect[j] == 'ELECTRICITY':
    #                         demand[0][year] = float(EUD[j])/1000
    #                     elif name_vect[j] == 'HEAT_LOW_T_DHN' or name_vect[j] == 'HEAT_LOW_T_DECEN':
    #                         demand[1][year] = demand[1][year] + float(EUD[j])/1000
    #                     elif name_vect[j] == 'HEAT_HIGH_T':
    #                         demand[2][year] = float(EUD[j])/1000
    #                     elif name_vect[j] == 'MOB_PRIVATE' or name_vect[j] == 'MOB_PUBLIC':
    #                         demand[3][year] = demand[3][year] + float(EUD[j])/1000
    #                     elif name_vect[j] == 'MOB_FREIGHT_RAIL' or name_vect[j] == 'MOB_FREIGHT_BOAT' or name_vect[j] == 'MOB_FREIGHT_ROAD':
    #                         demand[4][year] = demand[4][year] + float(EUD[j])/1000
                
    #             # To print the change in the EUDs       
    #             # print("EUD_elec change is [%] : ", 100*(demand[0][-1]-demand[0][0])/demand[0][0])
    #             # print("EUD_lowT change is [%] : ", 100*(demand[1][-1]-demand[1][0])/demand[1][0])
    #             # print("EUD_highT change is [%] : ", 100*(demand[2][-1]-demand[2][0])/demand[2][0])
    #             # print("EUD_pass change is [%] : ", 100*(demand[3][-1]-demand[3][0])/demand[3][0])
    #             # print("EUD_freight change is [%] : ", 100*(demand[4][-1]-demand[4][0])/demand[4][0])

    #             # To print the EUDs depending on the years
    #             # print('EUD_lowT : ', demand[1])
    #             # print('EUD_highT : ', demand[2])
    #             # print('EUD_pass : ', demand[3])
    #             # print('EUD_freight : ', demand[4])
                
    #         # Stackplot
    #         plt.figure(figsize=(12,7))
    #         plt.stackplot(x,y,labels=labels,colors = colors)
    #         plt.legend(bbox_to_anchor=(0, 1, 1, 0), loc="lower center", ncol=6, fontsize=10)
    #         plt.xlabel('Years',fontsize=18)
    #         plt.gca().spines['right'].set_color('none')
    #         plt.gca().spines['top'].set_color('none')
    #         if sector == 'Storage' or sector == 'Storage_daily':
    #             plt.ylabel('Capacity [GWh]',fontsize=18)
    #         elif sector == 'Resources':
    #             plt.ylabel('Ressources used [TWh]',fontsize=18)
    #         elif sector == 'Mobility':
    #             plt.ylabel('Millions of passenger - km [Mpkm]',fontsize=18)
    #         elif sector == 'Freight':
    #             plt.ylabel('Millions of ton - km [Mtkm]',fontsize=18)
    #         else:
    #             plt.ylabel('Capacity [GW]',fontsize=18)
                
    #         plt.tick_params(labelsize=18)
    #         if save_folder_name == "none":
    #             plt.show()
    #         else:
    #             if sector == 'Resources':
    #                 plt.savefig(save_path + '/Resources_used')   
    #             else:
    #                 plt.savefig(save_path + '/capacity_'+sector) 
            
    #         if sector == 'Resources': # will print graphs with the EUD
    #             # renewable vs fossil vs synfuels vs elec
    #             plt.figure(figsize=(12,4))
    #             plt.stackplot(x,comp_fos_ren_syn,labels=label_comp,colors = color_comp)
    #             plt.legend(bbox_to_anchor=(0, 1, 1, 0), loc="lower center", ncol=6, fontsize=10)
    #             plt.xlabel('Years',fontsize=18)
    #             plt.ylabel('[TWh]',fontsize=18)
    #             plt.gca().spines['right'].set_color('none')
    #             plt.gca().spines['top'].set_color('none')
    #             plt.tick_params(labelsize=18)
    #             plt.savefig(save_path + '/comp_type_resources_used') 

    #             # electricity, low T heat and high T heat
    #             plt.figure(figsize=(12,7))
    #             plt.stackplot(x,demand[:3][:],labels=name_EUD[:3],colors = color_EUD[:3])
    #             plt.legend(bbox_to_anchor=(0, 1, 1, 0), loc="lower center", ncol=6, fontsize=10)
    #             plt.xlabel('Years',fontsize=22)
    #             plt.ylabel('EUD [TWh]',fontsize=22)
    #             plt.gca().spines['right'].set_color('none')
    #             plt.gca().spines['top'].set_color('none')
    #             plt.tick_params(labelsize=22)
    #             plt.savefig(save_path + '/EUD_elec_lowT_highT') 

    #             # passenger mobility
    #             plt.figure(figsize=(12,4))
    #             plt.stackplot(x,demand[3][:],labels=name_EUD[3],colors = color_EUD[3])
    #             plt.legend(bbox_to_anchor=(0, 1, 1, 0), loc="lower center", ncol=6, fontsize=10)
    #             plt.xlabel('Years',fontsize=22)
    #             plt.ylabel('EUD passenger mobility [Gpkmh]',fontsize=22)
    #             plt.gca().spines['right'].set_color('none')
    #             plt.gca().spines['top'].set_color('none')
    #             plt.tick_params(labelsize=22)
    #             plt.savefig(save_path + '/EUD_passenger_mob') 

    #             # freight mobility
    #             plt.figure(figsize=(12,4))
    #             plt.stackplot(x,demand[4][:],labels=name_EUD[4],colors = color_EUD[4])
    #             plt.legend(bbox_to_anchor=(0, 1, 1, 0), loc="lower center", ncol=6, fontsize=10)
    #             plt.xlabel('Years',fontsize=22)
    #             plt.ylabel('EUD freight mobility [Gtkmh]',fontsize=22)
    #             plt.gca().spines['right'].set_color('none')
    #             plt.gca().spines['top'].set_color('none')
    #             plt.tick_params(labelsize=22)
    #             plt.savefig(save_path + '/EUD_freight_mob') 


    @staticmethod
    def dict_color(sector):
        color_dict = {}
        
        if sector == 'Electricity':
            color_dict = {"NUCLEAR":"deeppink", "CCGT":"darkorange", "CCGT_AMMONIA":"slateblue", "COAL_US" : "black", "COAL_IGCC" : "dimgray", "PV" : "yellow", "WIND_ONSHORE" : "lawngreen", "WIND_OFFSHORE" : "green", "HYDRO_RIVER" : "blue", "GEOTHERMAL" : "firebrick", "ELECTRICITY" : "dodgerblue"}
        elif sector == 'Heat_low_T':
            color_dict = {"DHN_HP_ELEC" : "blue", "DHN_COGEN_GAS" : "orange", "DHN_COGEN_WOOD" : "sandybrown", "DHN_COGEN_WASTE" : "olive", "DHN_COGEN_WET_BIOMASS" : "seagreen", "DHN_COGEN_BIO_HYDROLYSIS" : "springgreen", "DHN_BOILER_GAS" : "darkorange", "DHN_BOILER_WOOD" : "sienna", "DHN_BOILER_OIL" : "blueviolet", "DHN_DEEP_GEO" : "firebrick", "DHN_SOLAR" : "gold", "DEC_HP_ELEC" : "cornflowerblue", "DEC_THHP_GAS" : "lightsalmon", "DEC_COGEN_GAS" : "goldenrod", "DEC_COGEN_OIL" : "mediumpurple", "DEC_ADVCOGEN_GAS" : "burlywood", "DEC_ADVCOGEN_H2" : "violet", "DEC_BOILER_GAS" : "moccasin", "DEC_BOILER_WOOD" : "peru", "DEC_BOILER_OIL" : "darkorchid", "DEC_SOLAR" : "yellow", "DEC_DIRECT_ELEC" : "deepskyblue"}
        elif sector == 'Heat_high_T':
            color_dict = {"IND_COGEN_GAS":"orange", "IND_COGEN_WOOD":"peru", "IND_COGEN_WASTE" : "olive", "IND_BOILER_GAS" : "moccasin", "IND_BOILER_WOOD" : "goldenrod", "IND_BOILER_OIL" : "blueviolet", "IND_BOILER_COAL" : "black", "IND_BOILER_WASTE" : "olivedrab", "IND_DIRECT_ELEC" : "royalblue"}
        elif sector == 'Mobility':
            color_dict = {"TRAMWAY_TROLLEY" : "dodgerblue", "BUS_COACH_DIESEL" : "dimgrey", "BUS_COACH_HYDIESEL" : "gray", "BUS_COACH_CNG_STOICH" : "orange", "BUS_COACH_FC_HYBRIDH2" : "violet", "TRAIN_PUB" : "blue", "CAR_GASOLINE" : "black", "CAR_DIESEL" : "lightgray", "CAR_NG" : "moccasin", "CAR_METHANOL":"orchid", "CAR_HEV" : "salmon", "CAR_PHEV" : "lightsalmon", "CAR_BEV" : "deepskyblue", "CAR_FUEL_CELL" : "magenta"}
        elif sector == 'Freight':
            color_dict = {"TRAIN_FREIGHT" : "royalblue", "BOAT_FREIGHT_DIESEL" : "dimgrey", "BOAT_FREIGHT_NG" : "darkorange", "BOAT_FREIGHT_METHANOL" : "fuchsia", "TRUCK_DIESEL" : "darkgrey", "TRUCK_FUEL_CELL" : "violet", "TRUCK_ELEC" : "dodgerblue", "TRUCK_NG" : "moccasin", "TRUCK_METHANOL" : "orchid"}
        elif sector == 'Ammonia':
            color_dict = {"HABER_BOSCH":"tomato", "AMMONIA" : "slateblue", "AMMONIA_RE" : "blue"}
        elif sector == 'Methanol':
            color_dict = {"SYN_METHANOLATION":"violet","METHANE_TO_METHANOL":"orange","BIOMASS_TO_METHANOL":"peru", "METHANOL" : "orchid", "METHANOL_RE" : "mediumvioletred"}
        elif sector == "HVC":
            color_dict = {"OIL_TO_HVC":"blueviolet", "GAS_TO_HVC":"orange", "BIOMASS_TO_HVC":"peru", "METHANOL_TO_HVC":"orchid"}
        elif sector == 'Conversion':
            color_dict = {"H2_ELECTROLYSIS" : "violet", "H2_NG" : "magenta", "H2_BIOMASS" : "orchid", "GASIFICATION_SNG" : "orange", "PYROLYSIS" : "blueviolet", "ATM_CCS" : "black", "INDUSTRY_CCS" : "grey", "SYN_METHANOLATION" : "mediumpurple", "SYN_METHANATION" : "moccasin", "BIOMETHANATION" : "darkorange", "BIO_HYDROLYSIS" : "gold", "METHANE_TO_METHANOL" : "darkmagenta"}
        elif sector == 'Storage':
            color_dict = {"TS_DHN_SEASONAL" : "indianred", "BATT_LI" : "royalblue", "BEV_BATT" : "deepskyblue", "PHEV_BATT" : "lightskyeblue", "PHS" : "dodgerblue", "TS_DEC_HP_ELEC" : "blue", "TS_DHN_DAILY" : "lightcoral", "TS_HIGH_TEMP" : "red", "SEASONAL_NG" : "orange", "SEASONAL_H2" : "violet", "SLF_STO" : "blueviolet", "TS_DEC_DIRECT_ELEC":"darkgoldenrod", "TS_DEC_THHP_GAS": "orange", "TS_DEC_COGEN_GAS":"coral", "TS_DEC_COGEN_OIL":"darkviolet", "TS_DEC_ADVCOGEN_GAS":"sandybrown", "TS_DEC_ADVCOGEN_H2": "plum", "TS_DEC_BOILER_GAS": "tan", "TS_DEC_BOILER_WOOD":"peru", "TS_DEC_BOILER_OIL": "darkviolet", "GAS_STORAGE": "orange", "H2_STORAGE": "violet", "CO2_STORAGE": "lightgray", "GASOLINE_STORAGE": "gray", "DIESEL_STORAGE": "silver", "AMMONIA_STORAGE": "slateblue", "LFO_STORAGE": "darkviolet"}
        elif sector == 'Storage_daily':
            color_dict = {"BATT_LI" : "royalblue", "BEV_BATT" : "deepskyblue", "PHEV_BATT" : "lightskyeblue", "TS_DEC_HP_ELEC" : "blue", "TS_DHN_DAILY" : "lightcoral", "TS_HIGH_TEMP" : "red", "TS_DEC_DIRECT_ELEC":"darkgoldenrod", "TS_DEC_THHP_GAS": "orange", "TS_DEC_COGEN_GAS":"coral", "TS_DEC_COGEN_OIL":"darkviolet", "TS_DEC_ADVCOGEN_GAS":"sandybrown", "TS_DEC_ADVCOGEN_H2": "plum", "TS_DEC_BOILER_GAS": "tan", "TS_DEC_BOILER_WOOD":"peru", "TS_DEC_BOILER_OIL": "darkviolet"}
        elif sector == 'Resources':
            color_dict = {"ELECTRICITY" : "royalblue", "GASOLINE" : "gray", "DIESEL" : "silver", "BIOETHANOL" : "mediumorchid", "BIODIESEL" : "mediumpurple", "LFO" : "darkviolet", "GAS" : "orange", "GAS_RE" : "moccasin", "WOOD" : "peru", "WET_BIOMASS" : "seagreen", "COAL" : "black", "URANIUM" : "deeppink", "WASTE" : "olive", "H2" : "violet", "H2_RE" : "plum", "AMMONIA" : "slateblue", "AMMONIA_RE" : "blue", "METHANOL" : "orchid", "METHANOL_RE" : "mediumvioletred", "CO2_EMISSIONS" : "gainsboro", "RES_WIND" : "limegreen", "RES_SOLAR" : "yellow", "RES_HYDRO" : "blue", "RES_GEO" : "firebrick", "ELEC_EXPORT" : "chartreuse","CO2_ATM": "dimgray", "CO2_INDUSTRY": "darkgrey", "CO2_CAPTURED": "lightslategrey"}    
            
        return color_dict