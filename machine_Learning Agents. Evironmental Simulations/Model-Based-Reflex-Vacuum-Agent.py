#!/usr/bin/env python3

import random
class environment(object):
	def __init__(self):
		self.location = ["A","B"] #locations 
		self.locationcondition = {"A": 0,"B": 0} 
		self.locationcondition["A"] = random.randint(0,1) 
		self.locationcondition["B"] = random.randint(0,1) 
		self.vacuumlocation = random.choice(self.location) 
		self.mode = ["T","L"]
		#Assume past record is A=T and B=T 
		self.cleaningmethod = {"A":"T","B":"T"}
		#Randomly generate intial cleaning history 
		self.cleaningmethod["A"] = random.choice (self.mode) 
		self.cleaningmethod["B"] = random.choice (self.mode)
		
class agent(environment):
	def __init__(self,environment):
#Randomly generate status
		print("Environment condition", environment.locationcondition,"Vacuum location", environment.vacuumlocation, "cleaning method",environment.cleaningmethod)
		count = 0
		while count<2:
			if environment.locationcondition[environment.vacuumlocation] == 1: 
				print (environment.vacuumlocation, " is dirty, ")
		
	#check status, suck, mark clean, record status
				if environment.cleaningmethod[environment.vacuumlocation] == "T":
					environment.cleaningmethod[environment.vacuumlocation] = "L"
				else:
					environment.cleaningmethod[environment.vacuumlocation] = "T" 
				environment.locationcondition[environment.vacuumlocation] = 0
				print(environment.vacuumlocation, "Has been cleaned")
	
			else:
				print(environment.vacuumlocation, "Is clean")
			newindex = environment.location.index(environment.vacuumlocation) + 1
			if newindex == 2:
				newindex = 0
			environment.vacuumlocation = environment.location[newindex]
			count += 1
		print("new conditions",environment.locationcondition) 
		print("updated history",environment.cleaningmethod)
e1 = environment()
a1 = agent(e1)

	