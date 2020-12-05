import pandas as pd
import matplotlib.pyplot as plt
import wget
import numpy as np
from sklearn.linear_model import LinearRegression
import datetime
# Other dependencies: xlrd needed for reading Excel-file into Python

# REQUIRED INPUT (EDIT HERE) #
region = 'Östergötland'
region_tot = 461583

filepath = '/path/to/where/you/want/to/store/the/data'
start_date = datetime.datetime.strptime('2020-08-17', '%Y-%m-%d')
end = datetime.datetime.strptime('2020-10-26', '%Y-%m-%d')
#------ CODE BEGINS HERE ------ #
class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'
   
region_two_week = round((region_tot/100000)*50) # WFTDA calc, max allowable cases per week
region_day = round(region_two_week/14) # WFTDA calc, max allowable cases per day

url = 'https://www.arcgis.com/sharing/rest/content/items/b5e7488e117749c19881cce45db13f7e/data'
wget.download(url, filepath + 'Covid19.xlsx') # Download data from Folkhälsomyndigheten
seven_day_average = pd.read_excel(filepath + 'Covid19.xlsx', sheet_name=0)

def calc_twoweek_region(data):
    data = data.copy(deep=True)
    num_rows = len(data.index)
    average = [0] * num_rows
    for i in range(1, num_rows):
        average[i] = (data.iloc[i-1]['Antal_fall_vecka'] +
                      data.iloc[i]['Antal_fall_vecka'])
    return average

# Start
tier = 0
days = 0
days_since_increase = 0

date_list = [start_date + datetime.timedelta(days=x) for x in range(0, (end-start_date).days)]

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

    
    # Tier tracking
    if tier == 0:
        if cases < region_two_week:
            tier = 1
            action = 'Step up to Tier 1 from Baseline Conditions'
            days = 1
        else:
            action = 'Remain, Baseline Condition of number of allowed cases not fulfilled'
    elif tier == 1:
        # Add a count, number of days since 7-day trend, when it hits 7, affects action!
        # days_since_increase, always increases if it is already more than 0
        if days_since_increase > 0:
           days_since_increase = days_since_increase + 1
        # set to 1 at first positive trend
        # reset to 0 if OK after 7 days
        if model.coef_ > 0:
            action = 'Stay at Tier 1, 7-day increase trend'
            days = 1
            if days_since_increase == 0:
               days_since_increase = 1
        else:
            if days >= 14:
                action = 'Step up to Tier 2 from Tier 1, 14-days passed with no 7-day increase trend'
                tier = 2
                days = 1
            else:
                action = 'Stay at Tier 1, no 7-day increase, but 14 days has not passed yet'
                days = days + 1

    # 7 days has passed since there was a positive 7-day trend, check if still positive
    # If after 7 days
    if days_since_increase == 8:
         if model.coef_ > 0:
            action = 'Return to Baseline'
            tier = 0
         days_since_increase = 0 # Either if returning to baseline, or if no longer positive, reset

    # Printing
    print('#----------' + str(date.strftime('%Y-%m-%d')) + '---------#')
    print(f"{color.BOLD}Action: {color.END}{action}")
    print(f"{color.BOLD}Trend: {color.END}{model.coef_}")
    print(f"{color.BOLD}Tier: {color.END}{tier} , number of days spent at this tier: {days}")
    print(f"{color.BOLD}Number of days with positive 7-day trend in a row:" +
          f"{color.END}{days_since_increase}")
    print(f"{color.BOLD}Number of cases over 14-days: {color.END}{cases}")
    print(f"{color.BOLD}Max number of allowable cases over 14-days (WFTDA):"
          + f"{color.END}{region_two_week}")


# Plot 7-day trend for the last 7-days
plt.figure(3)
ax = plt.gca()
plt.plot(x, y_trend, color = 'red')
plt.bar(x, y)

plt.title('7 dagars trend')
plt.xlabel('Dagar')
plt.ylabel('Antal nya fall')
plt.axis([0.5, 7.5, 0, 30])
plt.savefig(filepath + 'plot_trend_' + region + '.png')
