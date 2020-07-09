import pandas as pd
import matplotlib.pyplot as plt
import wget
# Other dependencies: xlrd needed for reading Excel-file into Python

# REQUIRED INPUT (EDIT HERE) #
region = 'Östergötland'
region_tot = 461583
kommun = 'Linköping'
kommun_tot = 163051
filepath = '/path/to/where/you/want/to/store/the/data'


#------ CODE BEGINS HERE ------ #

kommun_week = round((kommun_tot/100000)*25) # WFTDA calc, max allowable cases per week
kommun_day = round(kommun_week/14) # WFTDA calc, max allowable cases per day
region_week = round((region_tot/100000)*25) # WFTDA calc, max allowable cases per week
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
    data = data.fillna(0)
    data = data.astype(int)
    return data

def kommun_plot():
    # Get the right rows (rows where kolumn KnNamn == Linköping)
    kommun_filt = veckodata_kommun[veckodata_kommun["KnNamn"] == kommun]
    # Clean the data
    kommun_filt = clean_data(kommun_filt, ['KnNamn', 'Stadsdel','Kommun_stadsdel'])
    # Create data for the horizontal target line and insert
    kommun_filt.insert(loc = 0, column = "target", value = kommun_week)

    # Create the plot, x: week numbers [veckonummer], y: number of new cases [nya_fall_vecka]
    plt.figure(1)
    ax = plt.gca()
    kommun_filt.plot(x = 'veckonummer', y = 'nya_fall_vecka', use_index = True, ax=ax)
    kommun_filt.plot(x = 'veckonummer', y = 'target', use_index = True, ax = ax)
    
    plt.gca().set_xticks(kommun_filt["veckonummer"].unique())
    plt.title(kommun)
    plt.xlabel('Veckonummer')
    plt.ylabel('Antal')
    L=plt.legend()
    L.get_texts()[0].set_text('Nya fall per vecka')
    L.get_texts()[1].set_text('Max antal per vecka (WFTDA)')
    plt.savefig(filepath + 'plot_kommun.png')

kommun_plot()

def region_plot():
    # Get the right rows (rows where kolumn region == Östergötland)
    region_filt = veckodata_region[veckodata_region["Region"] == region]
    # Clean the data
    region_filt = clean_data(region_filt, ['Region'])
    # Create data for the horizontal target line and insert
    region_filt.insert(loc = 0, column = "target", value = region_week)
    
    # Create the plot, x: week numbers [veckonummer], y: number of new cases [nya_fall_vecka]
    plt.figure(2)
    ax = plt.gca()
    region_filt.plot(x = 'veckonummer', y = 'Antal_fall_vecka', use_index = True, ax=ax)
    region_filt.plot(x = 'veckonummer', y = 'target', use_index = True, ax = ax)
    region_filt.plot(x = 'veckonummer', y = 'Antal_intensivvårdade_vecka', use_index = True, ax=ax)
    region_filt.plot(x = 'veckonummer', y = 'Antal_avlidna_vecka', use_index = True, ax=ax)

    plt.gca().set_xticks(region_filt["veckonummer"].unique())
    plt.title(region)
    plt.xlabel('Veckonummer')
    plt.ylabel('Antal')
    L=plt.legend()
    L.get_texts()[0].set_text('Nya fall per vecka')
    L.get_texts()[1].set_text('Max antal per vecka (WFTDA)')
    L.get_texts()[2].set_text('Nya intensivvårdade per vecka')
    L.get_texts()[3].set_text('Avlidna per vecka')
    plt.savefig(filepath + 'plot_region.png')

region_plot()
