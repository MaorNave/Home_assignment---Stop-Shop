#import relevent Libraries
import csv
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd
from geopy import distance
import statistics as sa

#Custom functions:
#Custom function for creating a bar graph:
def bar_plot(axis_x, axis_y, xlabel, ylabel, title, figsize=(10,5), width=0.8, color='#3399FF', ticks=None, labels=None):
    plt.figure(figsize=figsize)
    plt.bar(axis_x, axis_y, color=color, width=width)
    if ticks is not None and labels is not None:
        plt.xticks(ticks, labels)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.show()

#Custom function for build_ranges_for bar graphs -
#Create a list that holds the end values for grouping the ranges
#Enter the amount of the device_id count in the DataFrame for each range
#Enter new values for the X-axis labels in the graph to display the existing ranges in the data
def build_ranges(df_1, column_1, df_2, column_2):
    limits = list(df_1.index)
    for index in range(len(limits)):
        lower_lim = limits[index]
        upper_lim = float('inf') if index == (len(limits) - 1) else limits[index + 1]
        df_1.loc[lower_lim][column_1] = len(df_2.loc[df_2[column_2] < upper_lim][df_2[column_2] > lower_lim])
    y = list()
    for index in range(len(limits)):
        lower_lim = str(limits[index])
        upper_lim = '+' if index == (len(limits) - 1) else str('-') + str(limits[index + 1] - 1)
        limit_label = lower_lim + upper_lim
        y.append(limit_label)
    return y

#Custom function for calc loyal grades for customers:
def calc_grades(cor_df, device_visits_counter):
    for index in cor_df.index:
        if cor_df.loc[index]['Avg_distance_to_store'] > 50:
            grade = 0.999*device_visits_counter[index] - 0.001*cor_df.loc[index]['Avg_distance_to_store']
            loyalty_Grade_df.loc[index]['Grade'] = grade
        else:
            grade = 0.95*device_visits_counter[index] - 0.05*cor_df.loc[index]['Avg_distance_to_store']
            loyalty_Grade_df.loc[index]['Grade'] = grade
            
#Custom function for checking loyal customers:
def is_loyal(loyalty_Grade_df, grades_mean):
    for index in loyalty_Grade_df.index:
        if loyalty_Grade_df.loc[index]['Grade'] > grades_mean:
            loyalty_df.loc[index]['Loyal'] = True
        else:
            loyalty_df.loc[index]['Loyal'] = False

""" Question 1 """
#read csv
reader = csv.reader(open('activeness.csv'))
#Creating the dictionary and normalizing the data of the values according to  the question 
#- the coverage can only be between zero and one
activeness_dict = {}
for row in reader:
    key = (row[0], row[1])
    try:
        value = float(row[2])
        if value > 1:
            value = 1.0
        activeness_dict[key] = value
    except:
        pass
# Create a list to find the number of times device_id appears whose coverage value is greater than 0.75
active_devices = list()
for key in activeness_dict.keys():
    if activeness_dict[key] >= 0.75:
        active_devices.append(key[1])
        

# Counter Dictionary - Grouping the number of times device_id in the list we prepared above
active_counter = Counter(active_devices)
# Convert the dictionary to a csv file in order to visualize the data on tableau
a_file = open("Q1\Active_Devices.csv", "w", newline='')
writer = csv.DictWriter(a_file, fieldnames=["Device_ID", "Count_Active"])
writer.writeheader()
writer = csv.writer(a_file)
for key, value in active_counter.items():
    writer.writerow([key, value])
a_file.close()

# Visualization - checking the number of times each device_id appears and issuing a value to the 
#quantity based on a counter dictionary in order to display the graph for the number of days
#of active -  and the quantity of the device_id accordingly.
active_dist = active_counter.values()
dist_counter = Counter(active_dist)
 
#Visualization graph:
bar_plot(dist_counter.keys(), dist_counter.values(), 'number of active days', 'number of users',
             'Bar of count active days for num of users' ,(15,5))   


""" Question 2 """
#Creating a new dictionary that contains values from the active_counter
#dictionary by filtering the value of  number of active times over 90
active_visits_dict = {}
for key in active_counter.keys():
    if active_counter[key] > 90:
        active_visits_dict.update({int(key): active_counter[key]})
#Reading the file visits_Stop _ & _ Shop.csv and changing the guiding index in the table
#to visit_id
visits_DF = pd.read_csv('visits_Stop_&_Shop.csv')
visits_DF.set_index('visit_id', inplace=True, drop=True) 
      
#Create a DataFrame named weight_df with a leading index which is device_id and weight_sum column,
#Upload values to the DataFrame based on the sum of the device_id weight_visit values
weight_df = pd.DataFrame(index=active_visits_dict.keys(), columns=['weight_sum'])
for device_id in weight_df.index:
        device_weight = sum(visits_DF.loc[visits_DF['device_id'] == device_id]['visit_weight'])
        weight_df.loc[device_id]['weight_sum'] = device_weight
# Convert the DataFrame to a csv file in order to visualize the data on tableau     
weight_df.to_csv('Q2\weight_df.csv')     

#Visualization - Creating a DataFrame called weights_range_counter with a 
#leading index that is grouping the amount of device_id in value ranges.
weights_range_counter = pd.DataFrame(index=[0, 100, 500, 1000], columns=['decives_count'])
#Graph Visualization:
bar_plot(weights_range_counter.index, weights_range_counter['decives_count'], 'sum of weight by groups',
             'count of devices in the group', 'Bar of count users for sum weight', width=10,  ticks=weights_range_counter.index, 
                 labels=build_ranges(weights_range_counter, 'decives_count', weight_df, 'weight_sum'))


""" Question 3 """
#A. distance customer home location prosess:
#Build a set that contains the unique_device_id for use as a guiding index in DataFrames later in the program.
#Enter the location of the store for the variable
unique_device_id = set(visits_DF['device_id'])
shop_cor = (41.3723654,-72.9141964)
#Build a DataFrame called cor_df that will hold the average home point location of each device_id
#to the store and upload the data to it
cor_df = pd.DataFrame(index=unique_device_id, columns=['Avg_Home_Point_lat', 'Avg_Home_Point_long','Avg_distance_to_store'])
cor_df.index = cor_df.index.astype('int64')
for device_id in cor_df.index:
    cor_df.loc[device_id]['Avg_Home_Point_lat'] = (visits_DF.loc[visits_DF['device_id'] == device_id]['user_home_lat'].mean())
    cor_df.loc[device_id]['Avg_Home_Point_long'] = (visits_DF.loc[visits_DF['device_id'] == device_id]['user_home_long'].mean())
    Home_avg_cor = (cor_df.loc[device_id]['Avg_Home_Point_lat'], cor_df.loc[device_id]['Avg_Home_Point_long'])
    cor_df.loc[device_id]['Avg_distance_to_store'] = distance.great_circle(shop_cor, Home_avg_cor).km

# Convert the DataFrame to a csv file in order to visualize the data on tableau     
cor_df.to_csv('Q3\distance_df.csv')     

#Visualization - Creating a DataFrame called distance_range_counter with a 
#leading index that is grouping the amount of device_id in value ranges - by distance from the store in KM.
distance_range_counter = pd.DataFrame(index=[0, 5, 10, 20, 50, 100], columns=['decives_count'])


#Graph Visualization:
bar_plot(distance_range_counter.index, distance_range_counter['decives_count'], 'distance from store by groups',
             'count of devices in the group', 'Bar of count users for distance groups', width=10,
                 ticks=distance_range_counter.index, labels=build_ranges(distance_range_counter, 'decives_count', cor_df, 'Avg_distance_to_store'))

#B.Loyal Customers process
#Creates a variable that contains a counter of the number of times device_id appears 
#in visits_DF in order to calculate the number of visits made to each device_id.
#Creating two new DataFrames called loyalty_Grade_df that holds the loyalty grade for each device_id 
#and loyalty_df that holds true or false value for each device_id for the question of whether the customer is loyal or not,
device_visits_counter = Counter(visits_DF['device_id'])
loyalty_Grade_df = pd.DataFrame(index=unique_device_id, columns=['Grade'])
loyalty_df = pd.DataFrame(index=unique_device_id, columns=['Loyal'])
#Build custom functions to calculate the loyal score for each device_id and respectively to calculate 
#the overall average grade in order to determine whether a customer is loyal or not

calc_grades(cor_df, device_visits_counter)
grades_mean = sa.mean(loyalty_Grade_df['Grade'])
is_loyal(loyalty_Grade_df, grades_mean)

# Convert the DataFrame to a csv file in order to visualize the data on tableau     
loyalty_df.to_csv('Q3\Loyalty_df.csv')     
#Visualization - Creating a counter called count_loyalty with a 
#leading index that is grouping the amount of device_id in value ranges.
count_loyalty = Counter(loyalty_df['Loyal'])
#Graph Visualization,
#Enter new values for the X-axis labels in the graph to display the existing ranges in the data
z = list(('not_loyal', 'loyal'))
bar_plot(count_loyalty.keys(), count_loyalty.values(), 'Loyal / not Loyal', 'count of devices in the group',
             'Bar of count Loyal/not Loyal by groups', ticks=list(count_loyalty.keys()), labels=z)


""" Bonus Q """
#A
#Creating a new DataFrame called Venue_loc_df that holds raw data about a specific store along with the exact
#location of the store (depending on the data in question).
#Convert the DataFrame to a csv file in order to visualize the data on Kepler.gl
venue_loc_df = pd.DataFrame(columns=['Venue_id','Venue_name' ,'Venue_lat' ,'Venue_long' ])
venue_loc_df['Venue_id'] = visits_DF['venue_id'].unique()
venue_loc_df['Venue_name'] = "Stop&Shop"
venue_loc_df['Venue_lat'] = 41.3723654
venue_loc_df['Venue_long'] = -72.9141964
venue_loc_df.to_csv('Bonus Q\Venue_loc_df.csv')
#B
#Adding a new column to cor_df called Loyal and adding the values for each customer in 
#order to filter with the Kepler.gl tool for customers who are loyal only
cor_df['Loyal'] = ""
for index in loyalty_df.index:
    cor_df.loc[index]['Loyal'] = loyalty_df.loc[index]['Loyal']

# Convert the DataFrame to a csv file in order to visualize the data on Kepler.gl     
cor_df.to_csv('Bonus Q\distance&loyal_df.csv')     


        



















        