# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 15:06:13 2023

@author: HawthorneR
"""
#Question 1
import random

random.seed(10)

int_list = [random.randint(0, 15) for n in range(50)]

print(int_list)

print(int_list[9])

print(int_list[29])

#question 2

import string

az_upper = string.ascii_uppercase

az_list = []

for i in az_upper:    
    
    az_list.append(i)


print(az_list)


#question 3

set_1 = set(range(1,6))
print('set 1: ', set_1)

set_2 = set(int_list)
print('set 2: ', set_2)

set_3 = set_1.symmetric_difference(set_2)
print('set 3: ', set_3)

print('length of set_1 is ', len(set_1))

print('length of set_2 is ', len(set_2))

print('length of set_3 is ', len(set_3))


#Question 4
#Import default dict and set the default value to 'Not Present'. Call this dict_1.

#Add int_list, set_2, and set_3 to dict_1 using the object names as the key names.

#Create a new dictionary, dict_2, using curly bracket notation with set_1 and 
#az_list as the keys and values.

#Invoke the default value of dict_1 by trying to access the key az_list. 
#Create a new set named set_4 from the value of dict_1['az_list']. 
#What is the lenght of the difference between dict_2['az_list'] and `set_4'?

#Update dict_2 with dict_1. Print the value of the key az_list from dict_2. What happened?




from collections import defaultdict
# Function to return a default
# values for keys that is not
# present
def def_value():
    return "Not Present"
      
# Defining dict_1
dict_1 = defaultdict(def_value)
dict_1['int_list'] = int_list
dict_1['set_2'] = set_2
dict_1['set_3'] = set_3

print(dict_1)

#define dict_2
dict_2={'set_1':set_1, 'az_list':az_list}

print(dict_2)

#call az_list from dict_1
print(dict_1['az_list'])

#create set_4
set_4 = set(dict_1['az_list'])
print(set_4)

#find the length of the difference, had to conver dict_2['az_list] to a set to 
#use differnce function

print(len(set(dict_2['az_list']).difference(set_4)))

#update dict_2 with dict_1

dict_2.update(dict_1)
print(dict_2)
 