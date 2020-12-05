import pandas as pd
import matplotlib.pyplot as plt
import wget
import numpy as np
from sklearn.linear_model import LinearRegression
import datetime
# Other dependencies: xlrd needed for reading Excel-file into Python

# REQUIRED INPUT (EDIT HERE) #
region = 'Östergötland'
region_trend = 'Östergötland'
region_tot = 461583

kommun = 'Linköping'
kommun_tot = 163051

filepath = '/path/to/where/you/want/to/store/the/data'
#------ CODE BEGINS HERE ------ #
width = 0.2
height = 0.3
kommun_week = round((kommun_tot/100000)*50) # WFTDA calc, max allowable cases per week
kommun_day = round(kommun_week/14) # WFTDA calc, max allowable cases per day
region_week = round((region_tot/100000)*50) # WFTDA calc, max allowable cases per week
region_day = round(region_week/14) # WFTDA calc, max allowable cases per day

url = 'https://www.arcgis.com/sharing/rest/content/items/b5e7488e117749c19881cce45db13f7e/data'
wget.download(url, filepath + 'Covid19.xlsx') # Download data from Folkhälsomyndigheten
veckodata_region = pd.read_excel(filepath + 'Covid19.xlsx', sheet_name=6)
veckodata_kommun = pd.read_excel(filepath + 'Covid19.xlsx', sheet_name=7)
seven_day_average = pd.read_excel(filepath + 'Covid19.xlsx', sheet_name=0)

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

def trend_plot(date):
    # Filter out data, trend_filt is a dataframe with column 'Statistikdatum' and 'Region'
    # Statistikdatum entries are datetime64 objects
    trend_filt = seven_day_average[['Statistikdatum', region_trend]]
    tmp = trend_filt[trend_filt['Statistikdatum'] <= date]
    # Last 7 days
    end_date = date - datetime.timedelta(days=7)
    one_week = tmp[tmp['Statistikdatum'] > end_date]

    cases_last_week = one_week[region].sum()

    # Calculate trend over last 7 days
    y = np.array(one_week[region].tolist())
    x = [1, 2, 3, 4, 5, 6, 7]
    x_reshaped = np.array(x).reshape((-1,1))
    model = LinearRegression().fit(x_reshaped, y)
    y_trend = model.intercept_ + model.coef_*x

    ax = plt.gca()
    ax.set_axisbelow(True)
    plt.plot(x, y_trend, color = 'red')
    plt.bar(x, y)
    plt.ylim(0,250)
    
    plt.title('7-dagars från: ' + str(date.strftime('%Y-%m-%d')) + ' i ' + region + ', koefficient: ' + str(round(model.coef_[0])) + ', konstant: ' + str(round(model.intercept_)))
    plt.xlabel('Datum')
    plt.ylabel('Antal nya fall')
    plt.legend(['7-dagars trend', 'Antal fall per dag'], loc = 'upper left')
    plt.grid(True)
    # Add dates to the x-ticks
    plt.xticks(x, one_week['Statistikdatum'].map(lambda x: x.strftime('%Y-%m-%d')), rotation=20)
    # print out the intercept and coef
    #print('Coefficient (a): ' + str(model.coef_))
    #print('Offset (b): ' + str(model.intercept_))

    return cases_last_week
    
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
    plt.subplot(321)
    ax = plt.gca()
    kommun_filt.plot(x = 'veckonummer', y = 'target', color = 'blue', use_index = True, ax = ax)
    kommun_filt.plot(x = 'veckonummer', y = 'average', use_index = True, ax = ax, color = 'blue',
                     linestyle = 'dashed')   
    kommun_filt.plot(x = 'veckonummer', y = 'target2', color = 'orange',
                     use_index = True, ax = ax)
    kommun_filt.plot(x = 'veckonummer', y = 'nya_fall_vecka', linestyle = 'dashed',
                     color = 'orange', use_index = True, ax=ax)
   
    plt.gca().set_xticks(kommun_filt["veckonummer"].unique())
    plt.title(kommun + ' kommun')
    plt.xlabel('Veckonummer')
    plt.ylabel('Antal')
    plt.grid(True)
    L=plt.legend(loc = 'upper left')
    L.get_texts()[0].set_text('Max antal per 14-dagars-period (WFTDA)')
    L.get_texts()[1].set_text('Nya fall per 14-dagars-period')
    L.get_texts()[2].set_text('WFTDA-värdet delat med 2')
    L.get_texts()[3].set_text('Nya fall per vecka')
 
def region_plot(cases_last_week):
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
    plt.subplot(322)
    ax = plt.gca()
    region_filt.plot(x = 'veckonummer', y = 'target', color = 'blue', use_index = True, ax = ax)
    region_filt.plot(x = 'veckonummer', y = 'average', use_index = True, ax = ax, color = 'blue',
                     linestyle = 'dashed',)   
    region_filt.plot(x = 'veckonummer', y = 'target2', color = 'orange',
                     use_index = True, ax = ax)
    region_filt.plot(x = 'veckonummer', y = 'Antal_fall_vecka', linestyle = 'dashed',
                     color = 'orange', use_index = True, ax=ax)
    #region_filt.plot(x = 'veckonummer', y = 'Antal_intensivvårdade_vecka', use_index = True, ax=ax)
    #region_filt.plot(x = 'veckonummer', y = 'Antal_avlidna_vecka', use_index = True, ax=ax)

    plt.gca().set_xticks(region_filt["veckonummer"].unique())
    plt.title(region + ' region')
    plt.xlabel('Veckonummer')
    plt.ylabel('Antal')
    plt.grid(True)
    L=plt.legend(loc = 'upper left')
    L.get_texts()[0].set_text('Max antal per 14-dagars-period (WFTDA)')
    L.get_texts()[1].set_text('Nya fall per 14-dagars-period')
    L.get_texts()[2].set_text('WFTDA-värdet delat med 2')
    L.get_texts()[3].set_text('Nya fall per vecka')
    #L.get_texts()[4].set_text('Nya intensivvårdade per vecka')
    #L.get_texts()[5].set_text('Avlidna per vecka')


def test_plot(date_list):
    trend_values = [0]*len(date_list)
    intercept_values = [0]*len(date_list)
    i = 0
    for date in date_list:    
        # Filter out data, trend_filt is a dataframe with column 'Statistikdatum' and 'Region'
        # Statistikdatum entries are datetime64 objects
        trend_filt = seven_day_average[['Statistikdatum', region]]
        tmp = trend_filt[trend_filt['Statistikdatum'] <= date]
        # Last 14 days
        two_weeks = tmp[tmp['Statistikdatum'] > (date - datetime.timedelta(days=14))]
        # Last 7 days
        one_week = tmp[tmp['Statistikdatum'] > (date - datetime.timedelta(days=7))]

        # Cases over 14 days
        cases = two_weeks[region].sum()

        # Calculate trend over last 7 days
        y = np.array(one_week[region].tolist())
        x = [1, 2, 3, 4, 5, 6, 7]
        x_reshaped = np.array(x).reshape((-1,1))
        model = LinearRegression().fit(x_reshaped, y)
        y_trend = model.intercept_ + model.coef_*x

        trend_values[i] = model.coef_[0]
        intercept_values[i] = model.intercept_
        i = i + 1
    return trend_values, intercept_values
        

#------ MAIN ------ #
# This code produces the following plots:
#  - 7-day trend for the last 7-days
#  - 7-day trend for the previous 7-day period
#  - Number of cases per week for a commune, and the WFTDA benchmark
#  - Number of cases per week for a region, and the WFTDA benchmark

# Setup the figure that will hold all four plots
fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(20, 15))
plt.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=0.9, wspace=width, hspace=height)
plt.clf()
#------ TREND ------ #
# For the trend, create the start-date for each 7-day period to plot
end_date_now = datetime.datetime.today() - datetime.timedelta(days=1)
end_date_last_week = end_date_now - datetime.timedelta(days=7)

# Plot the 7-day trend for the previous 7-day period
plt.subplot(323)   
trend_plot(end_date_last_week)

# Plot the 7-day trend based on the last 7 days
plt.subplot(324)
cases_last_week = trend_plot(end_date_now)

#------ Constant and coeff ----- #
duration = 14
date_list = [end_date_now - datetime.timedelta(days=x) for x in range(duration-1, -1, -1)]
date_print = [date.strftime('%Y-%m-%d') for date in date_list]

trend_values, intercept_values = test_plot(date_list)

plt.subplot(325)
ax = plt.gca()
x = [i for i in range(0, duration)]
plt.plot(x, trend_values, color = 'orange', marker='x')
plt.plot(x, [0]*len(x), color = 'grey')
plt.xticks(x, date_print, rotation=20)
plt.title('Koefficient för 7-dagars trend, per dag')
plt.xlabel('Datum')
plt.ylabel('Koefficient')
plt.ylim(-25, 30)
plt.grid(True)

plt.subplot(326)
ax = plt.gca()
plt.plot(x, intercept_values, color = 'purple', marker='o')
#plt.plot(x, [0]*len(x), color = 'grey')
plt.xticks(x, date_print, rotation=20)
plt.title('Konstant för 7-dagars trend, per dag')
plt.xlabel('Datum')
plt.ylabel('Konstant')
plt.ylim(0, 230)
plt.grid(True)

#------ COMMUNE ------ #
# Plot the number of cases per week for a commune
kommun_plot()

#------ REGION ------ #
# Plot the number of cases per week for a region
region_plot(cases_last_week)

# Save the figure
plt.savefig(filepath + region + '_overall_plot.png')
