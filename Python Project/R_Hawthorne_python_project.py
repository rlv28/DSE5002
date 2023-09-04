# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 15:42:30 2023

@author: HawthorneR
"""
import openpyxl
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import re
import requests





'''
read in all the data files 
including the currency codes I got from https://www.exchangerate-api.com/docs/supported-currencies
'''


cost_of_living_df = pd.read_csv('Python Project/cost_of_living.csv')
country_codes_df = pd.read_excel('Python Project/country_codes.xlsx', engine='openpyxl')
ds_salaries_df = pd.read_csv('Python Project/ds_salaries.csv')
levels_fyi_salary_data_df = pd.read_csv('Python Project/Levels_Fyi_Salary_Data.csv')
currency_codes = pd.read_csv('Python Project/currency_codes.csv')

#removning th () from the country names
country_codes_df['Country'] = country_codes_df['Country'].str.replace('\(.*\)','')



#convert currency codes df to dictionary, using country as key and 3-alpha code as value
from collections import defaultdict
# Function to return a default
# values for keys that is not
# present
def def_value():
    return "Not Present"

country_code_dict = defaultdict(def_value, zip(country_codes_df['Country'], country_codes_df['Alpha-2 code']))

currency_codes_dict= defaultdict(def_value, zip(currency_codes['Country'], currency_codes['Currency Code']))

'''
get just data science salaries for entry level (less then 4 years of expereince),
fulltime employes from 
Levels_fyi_slary_data_df and ds_salaries_df

Then return columns with salary date, location, and salary

reindex

'''
data_science_levels_fyi_salary_data_df = levels_fyi_salary_data_df.loc[(levels_fyi_salary_data_df["title"] =='Data Scientist')
                              &(levels_fyi_salary_data_df["yearsofexperience"] < 4),
                              ['timestamp','totalyearlycompensation', 'location']]



data_science_ds_salaries_df = ds_salaries_df.loc[(ds_salaries_df['job_title'] == 'Data Scientist') 
                   & (ds_salaries_df['employment_type'] == 'FT') 
                   & (ds_salaries_df['experience_level'] == 'EN'), 
                   ['work_year' , 'salary_in_usd' , 'employee_residence']]

data_science_ds_salaries_df = data_science_ds_salaries_df.reset_index(drop=True)

data_science_levels_fyi_salary_data_df = data_science_levels_fyi_salary_data_df.reset_index(drop=True)

'''
cleaning data:
    for data_science_levels_fyi_salary_data_df
    create work_year column
    
    break location into city, state and country
    add country code
    
    convert total yearly compensation to 2023 USD and rename
    
    
    
    
'''
data_science_levels_fyi_salary_data_df.dtypes

data_science_levels_fyi_salary_data_df['work_year'] = pd.to_datetime(data_science_levels_fyi_salary_data_df['timestamp'] , format='%m/%d/%Y %H:%M:%S').dt.year

data_science_levels_fyi_salary_data_df[['city','state','country']] = data_science_levels_fyi_salary_data_df["location"].str.split(', ',expand=True)

 
#####add country for those locations that only had city and state

for idx, value in enumerate (data_science_levels_fyi_salary_data_df['state']):  
    if (len(value) == 2) & (data_science_levels_fyi_salary_data_df['country'][idx] == None):
        data_science_levels_fyi_salary_data_df['country'][idx] = 'United States'
    elif data_science_levels_fyi_salary_data_df['country'][idx] == None:
        print(idx)
    
###only printed index of 161 which correlates to Israel
data_science_levels_fyi_salary_data_df['country'][161] = 'Israel' 

###add currency code for currency conversion
data_science_levels_fyi_salary_data_df['currency_code']=''
data_science_levels_fyi_salary_data_df['employee_residence']=''

for idx, value in enumerate (data_science_levels_fyi_salary_data_df['country']):
    data_science_levels_fyi_salary_data_df['currency_code'][idx] = [val for key, val in currency_codes_dict.items() if re.search(value, key)]
    data_science_levels_fyi_salary_data_df['employee_residence'][idx] = [val for key, val in country_code_dict.items() if value in key]

###I don't know why Hong Kong won't work so I fixed them here:
    
for idx, value in enumerate (data_science_levels_fyi_salary_data_df['country']):
    if value == 'Hong Kong (SAR)':
        data_science_levels_fyi_salary_data_df['currency_code'][idx] = ["HKD"]
        data_science_levels_fyi_salary_data_df['employee_residence'][idx] = ['HK']

for idx, value in enumerate (data_science_levels_fyi_salary_data_df['country']):
    if value == "United States":
        data_science_levels_fyi_salary_data_df['employee_residence'][idx] = ['US']
    if value == "India":
        data_science_levels_fyi_salary_data_df['employee_residence'][idx] = ['IN']
    if value == "Ireland":
        data_science_levels_fyi_salary_data_df['employee_residence'][idx] = ['IE']

###cnvert to US currency
data_science_levels_fyi_salary_data_df['salary_in_usd']=''


for idx, value in enumerate (data_science_levels_fyi_salary_data_df['totalyearlycompensation']): 
    if (data_science_levels_fyi_salary_data_df['currency_code'][idx] != ["USD"]):
        data_science_levels_fyi_salary_data_df['salary_in_usd'][idx] = convert_currency(value, data_science_levels_fyi_salary_data_df['currency_code'][idx][0] )
    else:
        data_science_levels_fyi_salary_data_df['salary_in_usd'][idx]=value    

####Make copies to merge without extra columns and then merge

data_science_levels_fyi_salary_data_df_merge = data_science_levels_fyi_salary_data_df.drop(['timestamp','totalyearlycompensation','location','currency_code'],axis=1)

for idx, value in enumerate(data_science_levels_fyi_salary_data_df_merge['employee_residence']):
    data_science_levels_fyi_salary_data_df_merge['employee_residence'][idx]= value[0]
    

salary_df = pd.merge(data_science_levels_fyi_salary_data_df_merge, data_science_ds_salaries_df, how = 'outer')


#change money to 2023 dollars using SSA AWI values. 
#Increase from:
#2018 to 2019: 3.75%
#2019 to 2021: 2.83%
#2020 to 2021: 8.89%
#2021 to 2022: 4.8%
#2022 to 2023: 4.2%
#source: 
#https://www.ssa.gov/oact/TR/TRassum.html and 
#https://www.ssa.gov/oact/cola/awidevelop.html

salary_df['salary_in_2023']=''

for idx, value in enumerate(salary_df['work_year']):
    if value == 2018:
        salary_df['salary_in_2023'][idx] = salary_df['salary_in_usd'][idx]*1.0375*1.0283*1.089*1.048*1.042
    if value == 2019:
        salary_df['salary_in_2023'][idx] = salary_df['salary_in_usd'][idx]*1.0283*1.089*1.048*1.042
    if value == 2020:
        salary_df['salary_in_2023'][idx] = salary_df['salary_in_usd'][idx]*1.089*1.048*1.042
    if value == 2021:
        salary_df['salary_in_2023'][idx] = salary_df['salary_in_usd'][idx]*1.048*1.042
    if value == 2022:
        salary_df['salary_in_2023'][idx] = salary_df['salary_in_usd'][idx]*1.042






'''
manipulating cost of living data. Sense we don't have data for each most cities
outside the US, I am planning to look at all data overall grouped by country. Then 
look more specifically at the US.

to do this I first am breaking apart the "City" column in the cost of living data into
city, state and country and then remove the old "City" column.

2-digit country codes are then added to align with the salary data.
'''

cost_of_living_df[['city','state','country']] = cost_of_living_df["City"].str.split(', ',expand=True)
cost_of_living_df['employee_residence']=''


for idx, value in enumerate (cost_of_living_df['state']):  
    if (cost_of_living_df['country'][idx] == None):
        cost_of_living_df['country'][idx] = cost_of_living_df['state'][idx]

for idx, value in enumerate (cost_of_living_df['country']): 
    cost_of_living_df['employee_residence'][idx] = [val for key, val in country_code_dict.items() if value in key]

    
#the following pulled two keys from the dictionary
for idx, value in enumerate (cost_of_living_df['country']):
    if value == "United States":
        cost_of_living_df['employee_residence'][idx] = ['US']
    if value == "India":
        cost_of_living_df['employee_residence'][idx] = ['IN']
    if value == "Ireland":
        cost_of_living_df['employee_residence'][idx] = ['IE']
    if value == "Georgia":
        cost_of_living_df['employee_residence'][idx] = ['GE']


### replace unknown countr code with none. These countries will not play into the 
# since all salary data had country codes

for idx, value in enumerate(cost_of_living_df['employee_residence']):
    if (len(cost_of_living_df['employee_residence'][idx]) == 1):
        cost_of_living_df['employee_residence'][idx]= value[0]
    else:
        cost_of_living_df['employee_residence'][idx] = None
   
### get stats for each of the five indeces
    
stat_for_cost_of_living = stats_df_creator( cost_of_living_df, 
                                           'employee_residence',
                                           'Cost of Living Index')

stat_for_rent_index = stats_df_creator( cost_of_living_df, 
                                           'employee_residence',
                                           'Rent Index')
stat_for_cost_of_living_plus_rent_index = stats_df_creator( cost_of_living_df, 
                                           'employee_residence',
                                           'Cost of Living Plus Rent Index')
stat_for_groceries_index = stats_df_creator( cost_of_living_df, 
                                           'employee_residence',
                                           'Groceries Index')
stat_for_restaurant_price_index = stats_df_creator( cost_of_living_df, 
                                           'employee_residence',
                                           'Restaurant Price Index')
'''
I reviewed all the stats above and foudn that the values were very close to 
eachother for all three statistics. This implies a very low spread. I've decided
to focus on the median as the measure to use for the indices

To that end the next step is to create a df of just these stats then turn it into a dictionary.

'''

stat_median_index_df = stat_for_cost_of_living.drop(['mean','third_quantile'],axis=1)
stat_median_index_df = stat_median_index_df.rename(columns={"median": "cost_of_living"})
stat_median_index_df['rent_index'] = stat_for_rent_index['median']
stat_median_index_df['cost_of_living_plus_rent_index'] = stat_for_cost_of_living_plus_rent_index['median']
stat_median_index_df['groceries_index'] = stat_for_groceries_index['median']
stat_median_index_df['restuarant_price_index'] = stat_for_restaurant_price_index['median']
stat_median_index_df.reset_index(inplace=True)

index_dict =  defaultdict(def_value,   [(i,[v,w,x,y,z ]) 
                                        for i, v,w,x,y,z 
                                        in zip(stat_median_index_df.employee_residence, 
                                                                stat_median_index_df.cost_of_living, 
                                                                stat_median_index_df.rent_index,
                                                                stat_median_index_df.cost_of_living_plus_rent_index,
                                                                stat_median_index_df.groceries_index,
                                                                stat_median_index_df.restuarant_price_index) ])


'''
Group Salaries by employee_residence(country) and calculate the 75th percentile.
I'm hopeful that I can reach this as a salary within the first fedw years. 
This statitic is also not skewed by outliers as much as the mean.

'''
salary_percentile_df = salary_df.groupby(['employee_residence']).agg(
    first_quantile = ('salary_in_2023' , lambda x: np.percentile(x, q=25)),
    median = ('salary_in_2023' , lambda x: np.percentile(x, q=50)),                  
    third_quantile = ('salary_in_2023' , lambda x: np.percentile(x, q=75))       
    )

salary_percentile_df.reset_index(inplace=True)


'''
get values from index_dict for the countries we have salry data for

Then scale the salary by each "cost of" index. 

the largest of these values indicate were the money will go the farthest in each catergory.
'''
#there is no cost of living data for vietnam, but there is salary data. Removing this row.
index_vietnam =salary_percentile_df[salary_percentile_df['employee_residence'] == 'VN'].index
salary_percentile_df.drop(index_vietnam , inplace=True)


salary_percentile_df['cost_of_values']=''

for idx, salary in enumerate(salary_percentile_df['third_quantile']):
    salary_percentile_df['cost_of_values'][idx] = index_dict.get(salary_percentile_df['employee_residence'][idx])


salary_percentile_df['cost_of_living_scaled_q1']=''
salary_percentile_df['rent_index_scaled_q1']=''
salary_percentile_df['cost_of_living_plus_rent_index_scaled_q1']=''
salary_percentile_df['groceries_index_scaled_q1']=''
salary_percentile_df['restuarant_price_index_q1']=''
salary_percentile_df['cost_of_living_scaled_median']=''
salary_percentile_df['rent_index_scaled_median']=''
salary_percentile_df['cost_of_living_plus_rent_index_scaled_median']=''
salary_percentile_df['groceries_index_scaled_median']=''
salary_percentile_df['restuarant_price_index_median']='' 
salary_percentile_df['cost_of_living_scaled_q3']=''
salary_percentile_df['rent_index_scaled_q3']=''
salary_percentile_df['cost_of_living_plus_rent_index_scaled_q3']=''
salary_percentile_df['groceries_index_scaled_q3']=''
salary_percentile_df['restuarant_price_index_q3']=''     


for idx, salary in enumerate(salary_percentile_df['third_quantile']):
    salary_percentile_df['cost_of_living_scaled_q3'][idx] =salary*100/salary_percentile_df['cost_of_values'][idx][0]
    salary_percentile_df['rent_index_scaled_q3'][idx] = salary*100/salary_percentile_df['cost_of_values'][idx][1]
    salary_percentile_df['cost_of_living_plus_rent_index_scaled_q3'][idx] = salary*100/salary_percentile_df['cost_of_values'][idx][2]
    salary_percentile_df['groceries_index_scaled_q3'][idx] = salary*100/salary_percentile_df['cost_of_values'][idx][3]
    salary_percentile_df['restuarant_price_index_q3'][idx] = salary*100/salary_percentile_df['cost_of_values'][idx][4]
    
    
for idx, salary in enumerate(salary_percentile_df['median']):    
    salary_percentile_df['cost_of_living_scaled_median'][idx] = salary*100/salary_percentile_df['cost_of_values'][idx][0]
    salary_percentile_df['rent_index_scaled_median'][idx] = salary*100/salary_percentile_df['cost_of_values'][idx][1]
    salary_percentile_df['cost_of_living_plus_rent_index_scaled_median'][idx] = salary*100/salary_percentile_df['cost_of_values'][idx][2]
    salary_percentile_df['groceries_index_scaled_median'][idx] = salary*100/salary_percentile_df['cost_of_values'][idx][3]
    salary_percentile_df['restuarant_price_index_median'][idx] = salary*100/salary_percentile_df['cost_of_values'][idx][4]
    
for idx, salary in enumerate(salary_percentile_df['first_quantile']):   
    salary_percentile_df['cost_of_living_scaled_q1'][idx] = salary*100/salary_percentile_df['cost_of_values'][idx][0]
    salary_percentile_df['rent_index_scaled_q1'][idx] = salary*100/salary_percentile_df['cost_of_values'][idx][1]
    salary_percentile_df['cost_of_living_plus_rent_index_scaled_q1'][idx] = salary*100/salary_percentile_df['cost_of_values'][idx][2]
    salary_percentile_df['groceries_index_scaled_q1'][idx] = salary*100/salary_percentile_df['cost_of_values'][idx][3]
    salary_percentile_df['restuarant_price_index_q1'][idx] = salary*100/salary_percentile_df['cost_of_values'][idx][4]
    
    
    
    



salary_percentile_df['cost_of_living_scaled_q1'] = pd.to_numeric(salary_percentile_df['cost_of_living_scaled_q1'], errors='coerce')
salary_percentile_df['rent_index_scaled_q1'] = pd.to_numeric(salary_percentile_df['rent_index_scaled_q1'], errors='coerce')
salary_percentile_df['cost_of_living_plus_rent_index_scaled_q1'] = pd.to_numeric(salary_percentile_df['cost_of_living_plus_rent_index_scaled_q1'], errors='coerce')
salary_percentile_df['groceries_index_scaled_q1'] = pd.to_numeric(salary_percentile_df['groceries_index_scaled_q1'], errors='coerce')
salary_percentile_df['restuarant_price_index_q1'] = pd.to_numeric(salary_percentile_df['restuarant_price_index_q1'], errors='coerce')


salary_percentile_df['cost_of_living_scaled_median'] = pd.to_numeric(salary_percentile_df['cost_of_living_scaled_median'], errors='coerce')
salary_percentile_df['rent_index_scaled_median'] = pd.to_numeric(salary_percentile_df['rent_index_scaled_median'], errors='coerce')
salary_percentile_df['cost_of_living_plus_rent_index_scaled_median'] = pd.to_numeric(salary_percentile_df['cost_of_living_plus_rent_index_scaled_median'], errors='coerce')
salary_percentile_df['groceries_index_scaled_median'] = pd.to_numeric(salary_percentile_df['groceries_index_scaled_median'], errors='coerce')
salary_percentile_df['restuarant_price_index_median'] = pd.to_numeric(salary_percentile_df['restuarant_price_index_median'], errors='coerce')


salary_percentile_df['cost_of_living_scaled_q3'] = pd.to_numeric(salary_percentile_df['cost_of_living_scaled_q3'], errors='coerce')
salary_percentile_df['rent_index_scaled_q3'] = pd.to_numeric(salary_percentile_df['rent_index_scaled_q3'], errors='coerce')
salary_percentile_df['cost_of_living_plus_rent_index_scaled_q3'] = pd.to_numeric(salary_percentile_df['cost_of_living_plus_rent_index_scaled_q3'], errors='coerce')
salary_percentile_df['groceries_index_scaled_q3'] = pd.to_numeric(salary_percentile_df['groceries_index_scaled_q3'], errors='coerce')
salary_percentile_df['restuarant_price_index_q3'] = pd.to_numeric(salary_percentile_df['restuarant_price_index_q3'], errors='coerce')


'''
finding top 5 of each indice for each quantile, which returns all columnns.
so I removed all columns except the residency 
and the column its actually the top 5 of.


'''
# first quantile 
top_5_cost_of_living_q1 = salary_percentile_df.nlargest(5, 'cost_of_living_scaled_q1')    
top_5_cost_of_living_q1 = top_5_cost_of_living_q1[['employee_residence', 'cost_of_living_scaled_q1']]


top_5_rent_index_scaled_q1 = salary_percentile_df.nlargest(5, 'rent_index_scaled_q1') 
top_5_rent_index_scaled_q1  = top_5_rent_index_scaled_q1[['employee_residence', 'rent_index_scaled_q1']]


top_5_cost_of_living_plus_rent_index_scaled_q1= salary_percentile_df.nlargest(5, 'cost_of_living_plus_rent_index_scaled_q1')
top_5_cost_of_living_plus_rent_index_scaled_q1 = top_5_cost_of_living_plus_rent_index_scaled_q1[['employee_residence', 'cost_of_living_plus_rent_index_scaled_q1']]


top_5_groceries_index_scaled_q1 = salary_percentile_df.nlargest(5, 'groceries_index_scaled_q1')
top_5_groceries_index_scaled_q1 = top_5_groceries_index_scaled_q1[['employee_residence', 'groceries_index_scaled_q1']]


top_5_restuarant_price_index_q1 = salary_percentile_df.nlargest(5, 'restuarant_price_index_q1')
top_5_restuarant_price_index_q1 = top_5_restuarant_price_index_q1[['employee_residence', 'restuarant_price_index_q1']]
    

#merging
top_5_merged_q1 = pd.merge(top_5_cost_of_living_q1 , top_5_rent_index_scaled_q1 , how='outer', on='employee_residence')
top_5_merged_q1 = pd.merge(top_5_merged_q1 , top_5_cost_of_living_plus_rent_index_scaled_q1 , how='outer', on='employee_residence')
top_5_merged_q1 = pd.merge(top_5_merged_q1 , top_5_groceries_index_scaled_q1 , how='outer', on='employee_residence')
top_5_merged_q1 = pd.merge(top_5_merged_q1 , top_5_restuarant_price_index_q1 , how='outer', on='employee_residence')
    
top_5_merged_q1['country']=''

for idx, country_code in enumerate(top_5_merged_q1['employee_residence']):
    for key, value in country_code_dict.items():
        if country_code == value:
            top_5_merged_q1['country'][idx] = key
            

top_5_merged_q1 = top_5_merged_q1.drop(['employee_residence'], axis = 1)


# convert to long (tidy) form
top_5_merged_q1_melted = top_5_merged_q1.melt('country', var_name='index_q1d', value_name='scaled_salary')
legend_labels = ['Cost of Living', 'Rent Index', 
        'Cost of Living Plus Rent Index', 
        'Groceries Index', 
        'Restaurant Price Index']

sns.scatterplot(data= top_5_merged_q1_melted, x ='country', y="scaled_salary",
                hue="index_q1d", legend = 'full',  palette=sns.color_palette("Set1", 5))
plt.title('Top 5 Countries using the First Quantile Salaries Scaled to each Cost Index')
plt.xlabel("Country")
plt.xticks(rotation=90)
plt.ylabel("Salary Scaled by Cost of Index")
plt.legend(title='Cost of Index', loc='upper right', 
           labels = legend_labels)                
plt.show()


# print countries of top 5 using print_countries function

print('In terms of the first quantile the following are the lists of countries where salary goes the farthest:\n')
print_countries('Cost of Living', top_5_cost_of_living_q1)
print_countries('Rent', top_5_rent_index_scaled_q1)
print_countries('Cost of Living plus Rent', top_5_cost_of_living_plus_rent_index_scaled_q1)
print_countries('Groceries', top_5_groceries_index_scaled_q1)
print_countries('Restaurant Price', top_5_restuarant_price_index_q1 )

# median 
top_5_cost_of_living_median = salary_percentile_df.nlargest(5, 'cost_of_living_scaled_median')    
top_5_cost_of_living_median = top_5_cost_of_living_median[['employee_residence', 'cost_of_living_scaled_median']]


top_5_rent_index_scaled_median = salary_percentile_df.nlargest(5, 'rent_index_scaled_median') 
top_5_rent_index_scaled_median  = top_5_rent_index_scaled_median[['employee_residence', 'rent_index_scaled_median']]


top_5_cost_of_living_plus_rent_index_scaled_median= salary_percentile_df.nlargest(5, 'cost_of_living_plus_rent_index_scaled_median')
top_5_cost_of_living_plus_rent_index_scaled_median = top_5_cost_of_living_plus_rent_index_scaled_median[['employee_residence', 'cost_of_living_plus_rent_index_scaled_median']]


top_5_groceries_index_scaled_median = salary_percentile_df.nlargest(5, 'groceries_index_scaled_median')
top_5_groceries_index_scaled_median = top_5_groceries_index_scaled_median[['employee_residence', 'groceries_index_scaled_median']]


top_5_restuarant_price_index_median = salary_percentile_df.nlargest(5, 'restuarant_price_index_median')
top_5_restuarant_price_index_median = top_5_restuarant_price_index_median[['employee_residence', 'restuarant_price_index_median']]
    

#merging
top_5_merged_median = pd.merge(top_5_cost_of_living_median , top_5_rent_index_scaled_median , how='outer', on='employee_residence')
top_5_merged_median = pd.merge(top_5_merged_median , top_5_cost_of_living_plus_rent_index_scaled_median , how='outer', on='employee_residence')
top_5_merged_median = pd.merge(top_5_merged_median , top_5_groceries_index_scaled_median , how='outer', on='employee_residence')
top_5_merged_median = pd.merge(top_5_merged_median , top_5_restuarant_price_index_median , how='outer', on='employee_residence')
    
top_5_merged_median['country']=''

for idx, country_code in enumerate(top_5_merged_median['employee_residence']):
    for key, value in country_code_dict.items():
        if country_code == value:
            top_5_merged_median['country'][idx] = key
            

top_5_merged_median = top_5_merged_median.drop(['employee_residence'], axis = 1)


# convert to long (tidy) form
top_5_merged_median_melted = top_5_merged_median.melt('country', var_name='index_mediand', value_name='scaled_salary')
legend_labels = ['Cost of Living', 'Rent Index', 
        'Cost of Living Plus Rent Index', 
        'Groceries Index', 
        'Restaurant Price Index']

sns.scatterplot(data= top_5_merged_median_melted, x ='country', y="scaled_salary",
                hue="index_mediand", legend = 'full',  palette=sns.color_palette("Set1", 5))
plt.title('Top 5 Countries using the Median Salaries Scaled to each Cost Index')
plt.xlabel("Country")
plt.xticks(rotation=90)
plt.ylabel("Salary Scaled by Cost of Index")
plt.legend(title='Cost of Index', loc='upper right', 
           labels = legend_labels)                
plt.show()


# print countries of top 5 using print_countries function

print('In terms of the median the following are the lists of countries where salary goes the farthest:\n')
print_countries('Cost of Living', top_5_cost_of_living_median)
print_countries('Rent', top_5_rent_index_scaled_median)
print_countries('Cost of Living plus Rent', top_5_cost_of_living_plus_rent_index_scaled_median)
print_countries('Groceries', top_5_groceries_index_scaled_median)
print_countries('Restaurant Price', top_5_restuarant_price_index_median )

# third quantile 
top_5_cost_of_living_q3 = salary_percentile_df.nlargest(5, 'cost_of_living_scaled_q3')    
top_5_cost_of_living_q3 = top_5_cost_of_living_q3[['employee_residence', 'cost_of_living_scaled_q3']]


top_5_rent_index_scaled_q3 = salary_percentile_df.nlargest(5, 'rent_index_scaled_q3') 
top_5_rent_index_scaled_q3  = top_5_rent_index_scaled_q3[['employee_residence', 'rent_index_scaled_q3']]


top_5_cost_of_living_plus_rent_index_scaled_q3= salary_percentile_df.nlargest(5, 'cost_of_living_plus_rent_index_scaled_q3')
top_5_cost_of_living_plus_rent_index_scaled_q3 = top_5_cost_of_living_plus_rent_index_scaled_q3[['employee_residence', 'cost_of_living_plus_rent_index_scaled_q3']]


top_5_groceries_index_scaled_q3 = salary_percentile_df.nlargest(5, 'groceries_index_scaled_q3')
top_5_groceries_index_scaled_q3 = top_5_groceries_index_scaled_q3[['employee_residence', 'groceries_index_scaled_q3']]


top_5_restuarant_price_index_q3 = salary_percentile_df.nlargest(5, 'restuarant_price_index_q3')
top_5_restuarant_price_index_q3 = top_5_restuarant_price_index_q3[['employee_residence', 'restuarant_price_index_q3']]
    

#merging
top_5_merged_q3 = pd.merge(top_5_cost_of_living_q3 , top_5_rent_index_scaled_q3 , how='outer', on='employee_residence')
top_5_merged_q3 = pd.merge(top_5_merged_q3 , top_5_cost_of_living_plus_rent_index_scaled_q3 , how='outer', on='employee_residence')
top_5_merged_q3 = pd.merge(top_5_merged_q3 , top_5_groceries_index_scaled_q3 , how='outer', on='employee_residence')
top_5_merged_q3 = pd.merge(top_5_merged_q3 , top_5_restuarant_price_index_q3 , how='outer', on='employee_residence')
    
top_5_merged_q3['country']=''

for idx, country_code in enumerate(top_5_merged_q3['employee_residence']):
    for key, value in country_code_dict.items():
        if country_code == value:
            top_5_merged_q3['country'][idx] = key
            

top_5_merged_q3 = top_5_merged_q3.drop(['employee_residence'], axis = 1)


# convert to long (tidy) form
top_5_merged_q3_melted = top_5_merged_q3.melt('country', var_name='index_q3d', value_name='scaled_salary')
legend_labels = ['Cost of Living', 'Rent Index', 
        'Cost of Living Plus Rent Index', 
        'Groceries Index', 
        'Restaurant Price Index']

sns.scatterplot(data= top_5_merged_q3_melted, x ='country', y="scaled_salary",
                hue="index_q3d", legend = 'full',  palette=sns.color_palette("Set1", 5))
plt.title('Top 5 Countries using the Third Quantile Salaries Scaled to each Cost Index')
plt.xlabel("Country")
plt.xticks(rotation=90)
plt.ylabel("Salary Scaled by Cost of Index")
plt.legend(title='Cost of Index', loc='upper right', 
           labels = legend_labels)                
plt.show()


# print countries of top 5 using print_countries function

print('In terms of the third quantile the following are the lists of contries where salary goes the farthest:\n')
print_countries('Cost of Living', top_5_cost_of_living_q3)
print_countries('Rent', top_5_rent_index_scaled_q3)
print_countries('Cost of Living plus Rent', top_5_cost_of_living_plus_rent_index_scaled_q3)
print_countries('Groceries', top_5_groceries_index_scaled_q3)
print_countries('Restaurant Price', top_5_restuarant_price_index_q3 )


'''
The United States was top 1 or 2 on each index. This was for the US as a whole. 
Now I consider just the US
'''

'''
Go back to salary_df and cost_of_living_df and filter for just US

add quantile to us salary information

'''

salary_us_df = salary_df[salary_df['employee_residence']=='US']

salary_us_quartile_df = salary_us_df.groupby(['city', 'state']).agg(
    first_quantile = ('salary_in_2023' , lambda x: np.percentile(x, q=25)),
    median = ('salary_in_2023' , lambda x: np.percentile(x, q=50)),
    third_quantile = ('salary_in_2023' , lambda x: np.percentile(x, q=75))       
    )

cost_of_living_us_df = cost_of_living_df[cost_of_living_df['employee_residence']=='US']

'''
Note there are no duplicate cities in the cost of living data, 
so unlike when grouped by country there is no measures of central tendency to 
calculate

merge cost of living and salary data, then scale salary by each cost of living 
index
'''

us_salary_cost_of_living_merge_df = pd.merge(salary_us_quartile_df , 
                                             cost_of_living_us_df,
                                             how='outer', on=['city', 'state'])

'''
remove the rank column which is all nan

drops rows that contain nan as they either are missing salary or index data
'''
us_salary_cost_of_living_merge_drop_df= us_salary_cost_of_living_merge_df.drop(['Rank'], axis = 1)

us_salary_cost_of_living_merge_drop_df = us_salary_cost_of_living_merge_drop_df.dropna(axis = 0)

us_salary_cost_of_living_merge_drop_df= us_salary_cost_of_living_merge_drop_df.reset_index(drop=True)

'''
Calculate scaled salaries for each index
'''

us_salary_cost_of_living_merge_drop_df['cost_of_living_scaled_q1']=''
us_salary_cost_of_living_merge_drop_df['rent_index_scaled_q1']=''
us_salary_cost_of_living_merge_drop_df['cost_of_living_plus_rent_index_scaled_q1']=''
us_salary_cost_of_living_merge_drop_df['groceries_index_scaled_q1']=''
us_salary_cost_of_living_merge_drop_df['restuarant_price_index_q1']=''  

us_salary_cost_of_living_merge_drop_df['cost_of_living_scaled_median']=''
us_salary_cost_of_living_merge_drop_df['rent_index_scaled_median']=''
us_salary_cost_of_living_merge_drop_df['cost_of_living_plus_rent_index_scaled_median']=''
us_salary_cost_of_living_merge_drop_df['groceries_index_scaled_median']=''
us_salary_cost_of_living_merge_drop_df['restuarant_price_index_median']='' 


us_salary_cost_of_living_merge_drop_df['cost_of_living_scaled_q3']=''
us_salary_cost_of_living_merge_drop_df['rent_index_scaled_q3']=''
us_salary_cost_of_living_merge_drop_df['cost_of_living_plus_rent_index_scaled_q3']=''
us_salary_cost_of_living_merge_drop_df['groceries_index_scaled_q3']=''
us_salary_cost_of_living_merge_drop_df['restuarant_price_index_q3']='' 

for idx, salary in enumerate(us_salary_cost_of_living_merge_drop_df['first_quantile']):
    us_salary_cost_of_living_merge_drop_df['cost_of_living_scaled_q1'][idx] = salary*100/us_salary_cost_of_living_merge_drop_df['Cost of Living Index'][idx]
    us_salary_cost_of_living_merge_drop_df['rent_index_scaled_q1'][idx] = salary*100/us_salary_cost_of_living_merge_drop_df['Rent Index'][idx]
    us_salary_cost_of_living_merge_drop_df['cost_of_living_plus_rent_index_scaled_q1'][idx] = salary*100/us_salary_cost_of_living_merge_drop_df['Cost of Living Plus Rent Index'][idx]
    us_salary_cost_of_living_merge_drop_df['groceries_index_scaled_q1'][idx] = salary*100/us_salary_cost_of_living_merge_drop_df['Groceries Index'][idx]
    us_salary_cost_of_living_merge_drop_df['restuarant_price_index_q1'][idx] = salary*100/us_salary_cost_of_living_merge_drop_df['Restaurant Price Index'][idx]


for idx, salary in enumerate(us_salary_cost_of_living_merge_drop_df['median']):
    us_salary_cost_of_living_merge_drop_df['cost_of_living_scaled_median'][idx] = salary*100/us_salary_cost_of_living_merge_drop_df['Cost of Living Index'][idx]
    us_salary_cost_of_living_merge_drop_df['rent_index_scaled_median'][idx] = salary*100/us_salary_cost_of_living_merge_drop_df['Rent Index'][idx]
    us_salary_cost_of_living_merge_drop_df['cost_of_living_plus_rent_index_scaled_median'][idx] = salary*100/us_salary_cost_of_living_merge_drop_df['Cost of Living Plus Rent Index'][idx]
    us_salary_cost_of_living_merge_drop_df['groceries_index_scaled_median'][idx] = salary*100/us_salary_cost_of_living_merge_drop_df['Groceries Index'][idx]
    us_salary_cost_of_living_merge_drop_df['restuarant_price_index_median'][idx] = salary*100/us_salary_cost_of_living_merge_drop_df['Restaurant Price Index'][idx]


  
for idx, salary in enumerate(us_salary_cost_of_living_merge_drop_df['third_quantile']):
    us_salary_cost_of_living_merge_drop_df['cost_of_living_scaled_q3'][idx] = salary*100/us_salary_cost_of_living_merge_drop_df['Cost of Living Index'][idx]
    us_salary_cost_of_living_merge_drop_df['rent_index_scaled_q3'][idx] = salary*100/us_salary_cost_of_living_merge_drop_df['Rent Index'][idx]
    us_salary_cost_of_living_merge_drop_df['cost_of_living_plus_rent_index_scaled_q3'][idx] = salary*100/us_salary_cost_of_living_merge_drop_df['Cost of Living Plus Rent Index'][idx]
    us_salary_cost_of_living_merge_drop_df['groceries_index_scaled_q3'][idx] = salary*100/us_salary_cost_of_living_merge_drop_df['Groceries Index'][idx]
    us_salary_cost_of_living_merge_drop_df['restuarant_price_index_q3'][idx] = salary*100/us_salary_cost_of_living_merge_drop_df['Restaurant Price Index'][idx]

us_salary_cost_of_living_merge_drop_df['cost_of_living_scaled_q1'] = pd.to_numeric(us_salary_cost_of_living_merge_drop_df['cost_of_living_scaled_q1'], errors='coerce')
us_salary_cost_of_living_merge_drop_df['rent_index_scaled_q1'] = pd.to_numeric(us_salary_cost_of_living_merge_drop_df['rent_index_scaled_q1'], errors='coerce')
us_salary_cost_of_living_merge_drop_df['cost_of_living_plus_rent_index_scaled_q1'] = pd.to_numeric(us_salary_cost_of_living_merge_drop_df['cost_of_living_plus_rent_index_scaled_q1'], errors='coerce')
us_salary_cost_of_living_merge_drop_df['groceries_index_scaled_q1'] = pd.to_numeric(us_salary_cost_of_living_merge_drop_df['groceries_index_scaled_q1'], errors='coerce')
us_salary_cost_of_living_merge_drop_df['restuarant_price_index_q1'] = pd.to_numeric(us_salary_cost_of_living_merge_drop_df['restuarant_price_index_q1'], errors='coerce')    

us_salary_cost_of_living_merge_drop_df['cost_of_living_scaled_median'] = pd.to_numeric(us_salary_cost_of_living_merge_drop_df['cost_of_living_scaled_median'], errors='coerce')
us_salary_cost_of_living_merge_drop_df['rent_index_scaled_median'] = pd.to_numeric(us_salary_cost_of_living_merge_drop_df['rent_index_scaled_median'], errors='coerce')
us_salary_cost_of_living_merge_drop_df['cost_of_living_plus_rent_index_scaled_median'] = pd.to_numeric(us_salary_cost_of_living_merge_drop_df['cost_of_living_plus_rent_index_scaled_median'], errors='coerce')
us_salary_cost_of_living_merge_drop_df['groceries_index_scaled_median'] = pd.to_numeric(us_salary_cost_of_living_merge_drop_df['groceries_index_scaled_median'], errors='coerce')
us_salary_cost_of_living_merge_drop_df['restuarant_price_index_median'] = pd.to_numeric(us_salary_cost_of_living_merge_drop_df['restuarant_price_index_median'], errors='coerce')    


us_salary_cost_of_living_merge_drop_df['cost_of_living_scaled_q3'] = pd.to_numeric(us_salary_cost_of_living_merge_drop_df['cost_of_living_scaled_q3'], errors='coerce')
us_salary_cost_of_living_merge_drop_df['rent_index_scaled_q3'] = pd.to_numeric(us_salary_cost_of_living_merge_drop_df['rent_index_scaled_q3'], errors='coerce')
us_salary_cost_of_living_merge_drop_df['cost_of_living_plus_rent_index_scaled_q3'] = pd.to_numeric(us_salary_cost_of_living_merge_drop_df['cost_of_living_plus_rent_index_scaled_q3'], errors='coerce')
us_salary_cost_of_living_merge_drop_df['groceries_index_scaled_q3'] = pd.to_numeric(us_salary_cost_of_living_merge_drop_df['groceries_index_scaled_q3'], errors='coerce')
us_salary_cost_of_living_merge_drop_df['restuarant_price_index_q3'] = pd.to_numeric(us_salary_cost_of_living_merge_drop_df['restuarant_price_index_q3'], errors='coerce')    




'''
finding top 5 of each indice for each measure, which returns all columnns.
so I removed all columns except the residency 
and the column its actually the top 5 of.


'''
# first quantile

top_5_cost_of_living_us_q1 = us_salary_cost_of_living_merge_drop_df.nlargest(5, 'cost_of_living_scaled_q1')    
top_5_cost_of_living_us_q1 = top_5_cost_of_living_us_q1[['City', 'cost_of_living_scaled_q1']]


top_5_rent_index_scaled_us_q1 = us_salary_cost_of_living_merge_drop_df.nlargest(5, 'rent_index_scaled_q1') 
top_5_rent_index_scaled_us_q1  = top_5_rent_index_scaled_us_q1[['City', 'rent_index_scaled_q1']]


top_5_cost_of_living_plus_rent_index_scaled_us_q1 = us_salary_cost_of_living_merge_drop_df.nlargest(5, 'cost_of_living_plus_rent_index_scaled_q1')
top_5_cost_of_living_plus_rent_index_scaled_us_q1 = top_5_cost_of_living_plus_rent_index_scaled_us_q1[['City', 'cost_of_living_plus_rent_index_scaled_q1']]


top_5_groceries_index_scaled_us_q1 = us_salary_cost_of_living_merge_drop_df.nlargest(5, 'groceries_index_scaled_q1')
top_5_groceries_index_scaled_us_q1 = top_5_groceries_index_scaled_us_q1[['City', 'groceries_index_scaled_q1']]


top_5_restuarant_price_index_us_q1 = us_salary_cost_of_living_merge_drop_df.nlargest(5, 'restuarant_price_index_q1')
top_5_restuarant_price_index_us_q1 = top_5_restuarant_price_index_us_q1[['City', 'restuarant_price_index_q1']]
    


#merging
top_5_merged_us_q1 = pd.merge(top_5_cost_of_living_us_q1 , top_5_rent_index_scaled_us_q1 , how='outer', on='City')
top_5_merged_us_q1 = pd.merge(top_5_merged_us_q1 , top_5_cost_of_living_plus_rent_index_scaled_us_q1 , how='outer', on='City')
top_5_merged_us_q1 = pd.merge(top_5_merged_us_q1 , top_5_groceries_index_scaled_us_q1 , how='outer', on='City')
top_5_merged_us_q1 = pd.merge(top_5_merged_us_q1 , top_5_restuarant_price_index_us_q1 , how='outer', on='City')


# convert to long (tidy) form
top_5_merged_melted_us_q1 = top_5_merged_us_q1.melt('City', var_name='index_measured', value_name='scaled_salary')


legend_labels = ['Cost of Living', 'Rent Index', 
        'Cost of Living Plus Rent Index', 
        'Groceries Index', 
        'Restaurant Price Index']

sns.scatterplot(data= top_5_merged_melted_us_q1, x ='City', y="scaled_salary",
                hue="index_measured", palette=sns.color_palette("Set1", 5))
plt.title('Top 5 US Cities with First Quantile Salaries Scaled to each Cost Index')
plt.xlabel("City")
plt.xticks(rotation=90)
plt.ylabel("Salary Scaled by Cost of Index")
plt.legend(title='Cost of Index', loc='upper right', 
           labels = legend_labels)                
plt.show()                

# print countries of top 5 using print_countries function

print('The top five cities for each index for the first quantile of salaries are:\n')
print_cities('Cost of Living', top_5_cost_of_living_us_q1)
print_cities('Rent', top_5_rent_index_scaled_us_q1)
print_cities('Cost of Living plus Rent', top_5_cost_of_living_plus_rent_index_scaled_us_q1)
print_cities('Groceries', top_5_groceries_index_scaled_us_q1)
print_cities('Restaurant Price', top_5_restuarant_price_index_us_q1 )

#median
top_5_cost_of_living_us_medain = us_salary_cost_of_living_merge_drop_df.nlargest(5, 'cost_of_living_scaled_medain')    
top_5_cost_of_living_us_medain = top_5_cost_of_living_us_medain[['City', 'cost_of_living_scaled_medain']]


top_5_rent_index_scaled_us_medain = us_salary_cost_of_living_merge_drop_df.nlargest(5, 'rent_index_scaled_medain') 
top_5_rent_index_scaled_us_medain  = top_5_rent_index_scaled_us_medain[['City', 'rent_index_scaled_medain']]


top_5_cost_of_living_plus_rent_index_scaled_us_medain = us_salary_cost_of_living_merge_drop_df.nlargest(5, 'cost_of_living_plus_rent_index_scaled_medain')
top_5_cost_of_living_plus_rent_index_scaled_us_medain = top_5_cost_of_living_plus_rent_index_scaled_us_medain[['City', 'cost_of_living_plus_rent_index_scaled_medain']]


top_5_groceries_index_scaled_us_medain = us_salary_cost_of_living_merge_drop_df.nlargest(5, 'groceries_index_scaled_medain')
top_5_groceries_index_scaled_us_medain = top_5_groceries_index_scaled_us_medain[['City', 'groceries_index_scaled_medain']]


top_5_restuarant_price_index_us_medain = us_salary_cost_of_living_merge_drop_df.nlargest(5, 'restuarant_price_index_medain')
top_5_restuarant_price_index_us_medain = top_5_restuarant_price_index_us_medain[['City', 'restuarant_price_index_medain']]
    


#merging
top_5_merged_us_medain = pd.merge(top_5_cost_of_living_us_medain , top_5_rent_index_scaled_us_medain , how='outer', on='City')
top_5_merged_us_medain = pd.merge(top_5_merged_us_medain , top_5_cost_of_living_plus_rent_index_scaled_us_medain , how='outer', on='City')
top_5_merged_us_medain = pd.merge(top_5_merged_us_medain , top_5_groceries_index_scaled_us_medain , how='outer', on='City')
top_5_merged_us_medain = pd.merge(top_5_merged_us_medain , top_5_restuarant_price_index_us_medain , how='outer', on='City')


# convert to long (tidy) form
top_5_merged_melted_us_medain = top_5_merged_us_medain.melt('City', var_name='index_measured', value_name='scaled_salary')


legend_labels = ['Cost of Living', 'Rent Index', 
        'Cost of Living Plus Rent Index', 
        'Groceries Index', 
        'Restaurant Price Index']

ax = sns.scatterplot(data= top_5_merged_melted_us_medain, x ='City', y="scaled_salary",
                hue="index_measured", palette=sns.color_palette("Set1", 5))
plt.title('Top 5 US Cities with Medain Salaries Scaled to each Cost Index')
plt.xlabel("City")
plt.xticks(rotation=90)
plt.ylabel("Salary Scaled by Cost of Index")
plt.legend(title='Cost of Index', 
           labels = legend_labels)
sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))                
plt.show()                

# print countries of top 5 using print_countries function


print_cities('Cost of Living', top_5_cost_of_living_us_medain)
print_cities('Rent', top_5_rent_index_scaled_us_medain)
print_cities('Cost of Living plus Rent', top_5_cost_of_living_plus_rent_index_scaled_us_medain)
print_cities('Groceries', top_5_groceries_index_scaled_us_medain)
print_cities('Restaurant Price', top_5_restuarant_price_index_us_medain )




#third qunatile
top_5_cost_of_living_us_q3 = us_salary_cost_of_living_merge_drop_df.nlargest(5, 'cost_of_living_scaled_q3')    
top_5_cost_of_living_us_q3 = top_5_cost_of_living_us_q3[['City', 'cost_of_living_scaled_q3']]


top_5_rent_index_scaled_us_q3 = us_salary_cost_of_living_merge_drop_df.nlargest(5, 'rent_index_scaled_q3') 
top_5_rent_index_scaled_us_q3  = top_5_rent_index_scaled_us_q3[['City', 'rent_index_scaled_q3']]


top_5_cost_of_living_plus_rent_index_scaled_us_q3 = us_salary_cost_of_living_merge_drop_df.nlargest(5, 'cost_of_living_plus_rent_index_scaled_q3')
top_5_cost_of_living_plus_rent_index_scaled_us_q3 = top_5_cost_of_living_plus_rent_index_scaled_us_q3[['City', 'cost_of_living_plus_rent_index_scaled_q3']]


top_5_groceries_index_scaled_us_q3 = us_salary_cost_of_living_merge_drop_df.nlargest(5, 'groceries_index_scaled_q3')
top_5_groceries_index_scaled_us_q3 = top_5_groceries_index_scaled_us_q3[['City', 'groceries_index_scaled_q3']]


top_5_restuarant_price_index_us_q3 = us_salary_cost_of_living_merge_drop_df.nlargest(5, 'restuarant_price_index_q3')
top_5_restuarant_price_index_us_q3 = top_5_restuarant_price_index_us_q3[['City', 'restuarant_price_index_q3']]
    


#merging
top_5_merged_us_q3 = pd.merge(top_5_cost_of_living_us_q3 , top_5_rent_index_scaled_us_q3 , how='outer', on='City')
top_5_merged_us_q3 = pd.merge(top_5_merged_us_q3 , top_5_cost_of_living_plus_rent_index_scaled_us_q3 , how='outer', on='City')
top_5_merged_us_q3 = pd.merge(top_5_merged_us_q3 , top_5_groceries_index_scaled_us_q3 , how='outer', on='City')
top_5_merged_us_q3 = pd.merge(top_5_merged_us_q3 , top_5_restuarant_price_index_us_q3 , how='outer', on='City')


# convert to long (tidy) form
top_5_merged_melted_us_q3 = top_5_merged_us_q3.melt('City', var_name='index_measured', value_name='scaled_salary')


legend_labels = ['Cost of Living', 'Rent Index', 
        'Cost of Living Plus Rent Index', 
        'Groceries Index', 
        'Restaurant Price Index']

ax = sns.scatterplot(data= top_5_merged_melted_us_q3, x ='City', y="scaled_salary",
                hue="index_measured", palette=sns.color_palette("Set1", 5))
plt.title('Top 5 US Cities with Third Quantile Salaries Scaled to each Cost Index')
plt.xlabel("City")
plt.xticks(rotation=90)
plt.ylabel("Salary Scaled by Cost of Index")
plt.legend(title='Cost of Index', 
           labels = legend_labels)    
sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))            
plt.show()                

# print countries of top 5 using print_countries function

print('The top five cities for each index for the third quantile of salaries are:\n')
print_cities('Cost of Living', top_5_cost_of_living_us_q3)
print_cities('Rent', top_5_rent_index_scaled_us_q3)
print_cities('Cost of Living plus Rent', top_5_cost_of_living_plus_rent_index_scaled_us_q3)
print_cities('Groceries', top_5_groceries_index_scaled_us_q3)
print_cities('Restaurant Price', top_5_restuarant_price_index_us_q3 )




###############################################################################
'''
Functions
'''

def stats_df_creator (df, grouping, column):
    '''
    Parameters
    ----------
    df : dataframe of data
    grouping : column to group by
    column : column we want stats on
    Returns df with mean, median and third quantile values for column
    '''
    stats_df = df.groupby([grouping]).agg(
        median=(column , np.median),
        mean = (column, np.mean),
        third_quantile = ( column, lambda x: np.percentile(x, q=75))       
        )
    return stats_df


def convert_currency(amount, from_currency):
     
    base_url = "https://v6.exchangerate-api.com/v6/2f3616b696be3fa3d78a6f14/latest/USD"

    response = requests.get(base_url)
    data = response.json()

    if 'conversion_rates' in data:
        rates = data['conversion_rates']
        if from_currency == '':
            return amount

        if from_currency in rates :
            converted_amount = amount / rates[from_currency]
            return converted_amount
        else:
            raise ValueError("Invalid currency!")
    else:
        raise ValueError("Unable to fetch exchange rates!")
    return

def print_countries(index_phrase, df):
    print('The 5 countries in which salary goes the farthest on the ' +str(index_phrase) + ' index are:\n')

    for idx, country_code in enumerate(df['employee_residence']):
        for key, value in country_code_dict.items():
            if country_code == value:
                print(key)
    return


def print_cities(index_phrase, df):
    print('The 5 cities in which salary goes the farthest on the ' +str(index_phrase) + ' index are:')

    for idx, city in enumerate(df['City']):
        print(city)
    return



