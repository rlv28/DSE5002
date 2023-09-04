# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 13:43:39 2022

@author: jlowh
"""

def factorial(num=5):#function definition, default value of 5
    #code block that calculates a factorial and assigns it to fact
   """
   this function computes a factorial.
   Arguments:
       num: number to compute factorial. default value is 5
   """
   if isinstance(num, int) & (num > 1):
        fact=1
        for i in range(1, num+1):#for loop for finding factorial
            fact=fact*i
        #return statement that returns an object from your function
   elif (num == 0) or (num == 1):
        fact = 1
   else:
        fact = "Factorial does not exist for negative or non-integer values."
    
   return fact    #return factorial 

print("function execution with default value: "+ str(factorial()))
print("function execution with argument provided: "+ str(factorial(num=4)))
factorial(num=-10)