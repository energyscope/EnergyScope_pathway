import os
import re

def pathway_window(years_window = 35, years_overlap = 0):


    list_year = ['YEAR_2015','YEAR_2020','YEAR_2025','YEAR_2030',	
        'YEAR_2035','YEAR_2040','YEAR_2045','YEAR_2050']
    list_phase = ['2015_2020','2020_2025','2025_2030',
        '2030_2035','2035_2040','2040_2045','2045_2050']

    t_phase = 5 #Year of a phase

    if years_window % 5 != 0:
        raise ValueError('Error : the number of years in the window of optimisation is not correct.\nIt should be a multiple of 5')
    elif years_window > 35 or years_window <= 0:
        raise ValueError('Error : the number of years in the window of optimisation is not correct.\nIt cannot be smaller than 0 or greater than 35')
    elif years_window < t_phase:
        raise ValueError('Error : the number of years in the window of optimisation is not correct.\nIt must be bigger or equal to the number of years within a phase')
    elif years_window <= years_overlap:
        raise ValueError('Error : the overlap is too long.\nIt must be smaller than the window of optimisation')
    if years_overlap % 5 != 0:
        raise ValueError('Error : the number of years of overlap is not correct.\nIt should be a multiple of 5')


    n_phase_window = int(years_window/t_phase)
    n_year_window = int(years_window/t_phase)
    n_phase_overlap = int(years_overlap/t_phase)
    n_year_overlap = int(years_overlap/t_phase)

    years_opti = [[] for i in range(len(list_year))]
    phases_opti = [[] for i in range(len(list_phase))]
    

    for i in range(len(years_opti)):
        years_opti[i] = list_year[i*(n_year_window)-i*(n_year_overlap):(n_year_window+1)*(i+1)-i*(n_year_overlap+1)]
        if (n_year_window+1)*(i+1)-i*(n_year_overlap+1) >= len(list_year):
            break

    for i in range(len(phases_opti)):
        phases_opti[i] = list_phase[i*(n_phase_window)-i*(n_phase_overlap):(n_phase_window)*(i+1)-i*(n_phase_overlap)]
        if (n_phase_window)*(i+1)-i*(n_phase_overlap) >= len(list_phase):
            break

    years_opti = [ele for ele in years_opti if ele != []]
    phases_opti = [ele for ele in phases_opti if ele != []]
    
    years_up_to = [[] for i in range(len(years_opti))]
    phases_up_to = [[] for i in range(len(phases_opti))]
    
    for i in range(len(years_up_to)-1):
        years_up_to[i] = list_year[0:(n_year_window+1)*(i+1)-i*(n_year_overlap+1)-n_year_overlap]
    years_up_to[-1] = list_year
    
    for i in range(len(phases_up_to)-1):
        phases_up_to[i] = list_phase[0:(n_phase_window)*(i+1)-i*(n_phase_overlap)-n_phase_overlap]
    phases_up_to[-1] = list_phase
            
    
    return years_opti, phases_opti, years_up_to, phases_up_to

def write_seq_opti(curr_window_y, curr_window_p, years_up_to, phases_up_to, folder, year_one, i):
    with open(os.path.join(folder,'seq_opti.dat'),'w+', encoding='utf-8') as f:
            f.write('set YEARS_WND := ' )
            for year in curr_window_y:
                f.write('%s ' %year)
            f.write('; \n')
            f.write('set PHASE_WND := ')
            for phase in curr_window_p:
                f.write('%s ' %phase)
            f.write('; \n')
            f.write('set YEARS_UP_TO := ')
            for year in years_up_to:
                f.write('%s ' %year)
            f.write('; \n')
            f.write('set PHASE_UP_TO := ')
            for phase in phases_up_to:
                f.write('%s ' %phase)
            f.write(';\n')
            
            f.write('set YEAR_ONE')
            if i>0 :
                f.write(':= %s' %year_one)
            f.write(';')
                

def remaining_update(file, pth_model,PHASE_WND):
    n_phase = len(PHASE_WND)
    with open(os.path.join(pth_model,file),encoding='utf-8') as fp:
        next(fp)
        l = fp.readlines()
        n = len(re.split(r'\t+', l[0].rstrip('\t')))
    with open(os.path.join(pth_model,'PESTD_data_remaining_wnd.dat'),'w+', encoding='utf-8') as f:
        f.write('param remaining_years : ' )
        for phase in PHASE_WND:
            f.write('%s ' %phase)
        f.write(':= \n')
        with open(os.path.join(pth_model,file),encoding='utf-8') as fp:
            next(fp)
            for line in fp:
                list_line = re.split(r'\t+', line.rstrip('\t'))
                if len(list_line) < n:
                    break
                else:
                    f.write(list_line[0]+'\t')
                    for i in range(len(list_line)-n_phase-1,len(list_line)-1):
                        f.write(list_line[i]+'\t')
                    f.write('\n')
        f.write('; \n')
            
            