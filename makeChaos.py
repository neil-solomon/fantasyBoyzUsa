from time import sleep
from random import random

def generateChaos(length,seed):
	with open('C:/Users/NeilS/Desktop/FantasyBoyzUSA/plots/chaosData.txt','w+') as file:
		file.write('')
	x = seed
	for i in range(length):
		with open('C:/Users/NeilS/Desktop/FantasyBoyzUSA/plots/chaosData.txt','a+') as file:
			file.write(str(i)+','+str(x)+'\n')
		x = x**2 - 1.5
		sleep(.25)

seed=random()
print(seed)
generateChaos(1000,float(seed))