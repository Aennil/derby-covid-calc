import pandas as pd
import matplotlib.pyplot as plt
import wget
# Other dependencies: xlrd needed for reading Excel-file into Python

# REQUIRED INPUT (EDIT HERE) #
region = 'Östergötland'
region_tot = 461583

#kommun = 'Norrköping'
#kommun_tot = 143302
kommun = 'Linköping'
kommun_tot = 163051
filepath = '/path/to/where/you/want/to/store/the/data'

# Flera regioner och kommuner i en lista, kör kommun_plot på varje

#------ CODE BEGINS HERE ------ #

kommun_week = round((kommun_tot/100000)*50) # WFTDA calc, max allowable cases per week
kommun_day = round(kommun_week/14) # WFTDA calc, max allowable cases per day
region_week = round((region_tot/100000)*50) # WFTDA calc, max allowable cases per week
region_day = round(region_week/14) # WFTDA calc, max allowable cases per day

url = 'https://www.arcgis.com/sharing/rest/content/items/b5e7488e117749c19881cce45db13f7e/data'
wget.download(url, filepath + 'Covid19.xlsx') # Download data from Folkhälsomyndigheten
veckodata_region = pd.read_excel(filepath + 'Covid19.xlsx', sheet_name=6)
veckodata_kommun = pd.read_excel(filepath + 'Covid19.xlsx', sheet_name=7)

def clean_data(data, columns_to_filter):
    data = data.copy(deep=True)
    # Replace "<15" with 15 (kind of a worst case but can at least be plotted)
    data = data.replace(to_replace = "<15", value = 15)
    # Further cleanup, remove columns not in use, fill missing values with zeroes, convert to Integer
    data = data.drop(columns=columns_to_filter)
    data = data.tail(10) # Only keep last 10 weeks!
    data = data.fillna(0)
    data = data.astype(int)
    return data

def calc_twoweek(data):
    data = data.copy(deep=True)
    num_rows = len(data.index)
    average = [0] * num_rows
    for i in range(1, num_rows):
        average[i] = (data.iloc[i-1]['nya_fall_vecka'] +
                      data.iloc[i]['nya_fall_vecka'])
    return average

def calc_twoweek_region(data):
    data = data.copy(deep=True)
    num_rows = len(data.index)
    average = [0] * num_rows
    for i in range(1, num_rows):
        average[i] = (data.iloc[i-1]['Antal_fall_vecka'] +
                      data.iloc[i]['Antal_fall_vecka'])
    return average

def kommun_plot():
    # Get the right rows (rows where kolumn KnNamn == Linköping)
    kommun_filt = veckodata_kommun[veckodata_kommun["KnNamn"] == kommun]
    # Clean the data
    kommun_filt = clean_data(kommun_filt, ['KnNamn', 'Stadsdel','Kommun_stadsdel'])
    # Create data for the horizontal target line and insert
    kommun_filt.insert(loc = 0, column = "target", value = kommun_week)
    kommun_filt.insert(loc = 0, column = "target2", value = kommun_week/2)
    # Create sum of two weeks (this should be compared to the WFTDA target)
    kommun_filt.insert(loc = 0, column = "average", value = calc_twoweek(kommun_filt))
    
    # Create the plot, x: week numbers [veckonummer], y: number of new cases [nya_fall_vecka]
    plt.figure(1)
    ax = plt.gca()
    kommun_filt.plot(x = 'veckonummer', y = 'target', color = 'purple', use_index = True, ax = ax)
    kommun_filt.plot(x = 'veckonummer', y = 'average', use_index = True, ax = ax, color = 'green')   
    kommun_filt.plot(x = 'veckonummer', y = 'target2', color = 'purple', linestyle = 'dashed',
                     use_index = True, ax = ax)
    kommun_filt.plot(x = 'veckonummer', y = 'nya_fall_vecka', linestyle = 'dashed',
                     color = 'green', use_index = True, ax=ax)
   
    plt.gca().set_xticks(kommun_filt["veckonummer"].unique())
    plt.title(kommun)
    plt.xlabel('Veckonummer')
    plt.ylabel('Antal')
    L=plt.legend()
    L.get_texts()[0].set_text('Max antal per 14-dagars-period (WFTDA)')
    L.get_texts()[1].set_text('Nya fall per 14-dagars-period')
    L.get_texts()[2].set_text('WFTDA-värdet delat med 2')
    L.get_texts()[3].set_text('Nya fall per vecka')
 
    plt.savefig(filepath + 'plot_' + kommun + '.png')

kommun_plot()

def region_plot():
    # Get the right rows (rows where kolumn region == Östergötland)
    region_filt = veckodata_region[veckodata_region["Region"] == region]
    # Clean the data
    region_filt = clean_data(region_filt, ['Region'])
    # Create data for the horizontal target line and insert
    region_filt.insert(loc = 0, column = "target", value = region_week)
    region_filt.insert(loc = 0, column = "target2", value = region_week/2)
    # Create sum of two weeks (this should be compared to the WFTDA target)
    region_filt.insert(loc = 0, column = "average", value = calc_twoweek_region(region_filt))
   
    # Create the plot, x: week numbers [veckonummer], y: number of new cases [nya_fall_vecka]
    plt.figure(2)
    ax = plt.gca()
    region_filt.plot(x = 'veckonummer', y = 'target', color = 'purple', use_index = True, ax = ax)
    region_filt.plot(x = 'veckonummer', y = 'average', use_index = True, ax = ax, color = 'green')   
    region_filt.plot(x = 'veckonummer', y = 'target2', color = 'purple', linestyle = 'dashed',
                     use_index = True, ax = ax)
    region_filt.plot(x = 'veckonummer', y = 'Antal_fall_vecka', linestyle = 'dashed',
                     color = 'green', use_index = True, ax=ax)
    #region_filt.plot(x = 'veckonummer', y = 'Antal_intensivvårdade_vecka', use_index = True, ax=ax)
    #region_filt.plot(x = 'veckonummer', y = 'Antal_avlidna_vecka', use_index = True, ax=ax)

    plt.gca().set_xticks(region_filt["veckonummer"].unique())
    plt.title(region)
    plt.xlabel('Veckonummer')
    plt.ylabel('Antal')
    L=plt.legend()
    L.get_texts()[0].set_text('Max antal per 14-dagars-period (WFTDA)')
    L.get_texts()[1].set_text('Nya fall per 14-dagars-period')
    L.get_texts()[2].set_text('WFTDA-värdet delat med 2')
    L.get_texts()[3].set_text('Nya fall per vecka')
    #L.get_texts()[4].set_text('Nya intensivvårdade per vecka')
    #L.get_texts()[5].set_text('Avlidna per vecka')
    
    plt.savefig(filepath + 'plot_' + region + '.png')

region_plot()
