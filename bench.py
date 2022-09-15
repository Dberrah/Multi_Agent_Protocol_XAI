#!/usr/bin/env python
import copy
from operator import index, indexOf
import re
import sys
from matplotlib.cbook import index_of
import pandas as pd
from numpy import mean
import matplotlib.pyplot as plt
from sqlalchemy import false
from sympy import ordered

# récup nb agents

# pour chaque ag
	# récup score perso
	# récup évolution inference

data = []
data2 = []
nb_agent = 0
sizeAF = 0
ag_score = []
ag_score_infered = []
last_infered = []
infered = []
argsImpactOnFinalOutcome = []
argsImpactOnUniverseProtocol = []
argsImpactOnPartialProtocolH1 = []
argsImpactOnPartialProtocolH2 = []
impactsByAgent = []
gameSize = []
ag_nbArg = []
percent = []
gu = 0
gameSizeFile = open('gameSize4.data', 'a') # size of interval compared to the game length
scoreFile = open('score4.data', 'a') # size of interval compared to the actual score of the agent
sumFile = open('sum4.data', 'a') # size of interval compared to the sum of the impact
absSumFile = open('absSum4.data', 'a') # size of interval compared to the abs sum of the impact
maxFile = open('max4.data', 'a') # size of interval compared to the max impact of an arg played
minFile = open('min4.data', 'a') # size of interval compared to the min impact of an arg played
guFile = open('gu4.data', 'a') # nb arg dans graph univers/nb agents and mean of interval sizes
# a faire avec 2 et 4 agents fixe
percentFile = open('percent4.data', 'a') # nb arg/agent par rapport au nb d'arg total and interval size
diffFile = open('diff4.data', 'a') # score perso et moyenne interval inferer (score inferer)
with open(sys.argv[1]) as file_object:
	line = file_object.readline()
	sizeAF = int(line)
	line = file_object.readline()
	nb_agent = int(line)
	gu = float(float(sizeAF)/float(nb_agent))
	line = file_object.readline()
	for i in range(nb_agent):
		ag_score_infered.append([])
		impactsByAgent.append([])
	for j in range(nb_agent):
		ag_score.append(float(line))
		line = file_object.readline()
		ag_nbArg.append(int(line))
		percent.append(float(float(line)/float(sizeAF)))
		line = file_object.readline()
	while line:
		indexes = []
		ind = 0
		gameSize.append(int(line))
		line = file_object.readline()
		for j in range(nb_agent):
			inf = re.split('\"|,\S|\",\"',line)
			i = 0
			while i<inf.__len__()-1:
				i += 1
				inf2 = re.split('\[|\]|\, ',inf[i])
				indexes.append(ind)
				ind += 1
				i += 1
				row = {
					'inf_pos_BI': float(inf2[1]),
					'inf_pos_BS': float(inf2[2]),
					'ag_score': float(ag_score[j])
				}
				row2 = {
					'inf_neg_BI': float(inf2[3]),
					'inf_neg_BS': float(inf2[4]),
					'ag_score': float(ag_score[j])
				}
				last_infered = [max(float(inf2[1]), float(inf2[3])), min(float(inf2[2]), float(inf2[4]))]
				data.append(row)
				data2.append(row2)
			line = file_object.readline()
			infered += [last_infered]
			ag_score_infered[j].append(float(line))
			line = file_object.readline()
			data = pd.DataFrame(data, columns=['inf_pos_BI', 'inf_pos_BS', 'ag_score'])
			data2 = pd.DataFrame(data2, columns=['inf_neg_BI', 'inf_neg_BS', 'ag_score'])
			data.index = indexes
			data2.index = indexes
			data = data.T
			data2 = data2.T
			plt.figure(figsize=(18, 5))
			plt.plot(data.iloc[0], label='inf_pos_BI', color='blue')
			plt.plot(data.iloc[1], label='inf_pos_BS', color='green')
			plt.plot(data.iloc[2], label='ag_score', color='black')
			plt.legend()
			plt.title(f'agent {j}')
			plt.ylabel('score value')
			plt.xlabel('turn')
			# plt.show()
			plt.figure(figsize=(18, 5))
			plt.plot(data2.iloc[0], label='inf_neg_BI', color='red')
			plt.plot(data2.iloc[1], label='inf_neg_BS', color='orange')
			plt.plot(data2.iloc[2], label='ag_score', color='black')
			plt.legend()
			plt.title(f'agent {j}')
			plt.ylabel('score value')
			plt.xlabel('turn')
			# plt.show()
			data = []
			data2 = []
			indexes = []
			ind = 0
		temp = re.split(',',line)
		for item in temp:
			argsImpactOnFinalOutcome.append(float(item))
		line = file_object.readline()
		temp = re.split(',',line)
		for item in temp:
			argsImpactOnUniverseProtocol.append(float(item))
		line = file_object.readline()
		temp = re.split(',',line)
		for item in temp:
			argsImpactOnPartialProtocolH1.append(float(item))
		line = file_object.readline()
		temp = re.split(',',line)
		for item in temp:
			argsImpactOnPartialProtocolH2.append(float(item))
		line = file_object.readline()
		# print('coucou')
		# print(argsImpactOnFinalOutcome)
		# print(argsImpactOnUniverseProtocol)
		# print(argsImpactOnPartialProtocolH1)
		# print(argsImpactOnPartialProtocolH2)
		orderedArgs = []
		temp = re.split(',',line)
		for item in temp:
			orderedArgs.append(int(item))
		print(orderedArgs)
		argsPlayed = []
		for i in range(nb_agent):
			argsPlayed.append([])
			line = file_object.readline()
			temp = re.split(',',line)
			for item in temp:
				argsPlayed[i].append(int(item))
		line = file_object.readline()
		print(argsPlayed)
		
		agentsImpact = []
		for i in range(nb_agent):
			agentsImpact.append([[],[],[],[]])
		print(f'agentsImpact : {agentsImpact}')
		j = 0
		for item in orderedArgs:
			i = 0
			for ag in argsPlayed:
				if(item in ag):
					agentsImpact[i][0].append(argsImpactOnFinalOutcome[j])
					agentsImpact[i][1].append(argsImpactOnUniverseProtocol[j])
					agentsImpact[i][2].append(argsImpactOnPartialProtocolH1[j])
					agentsImpact[i][3].append(argsImpactOnPartialProtocolH2[j])
				i += 1
			j += 1
		print(f'agentsImpact : {agentsImpact}\n\n')
		i = 0
		for ag in agentsImpact:
			for item in ag:
				temp = []
				sum = 0
				absSum = 0
				for imp in item:
					temp.append(abs(imp))
					sum += imp
					absSum += abs(imp)
				max_ind = temp.index(max(temp))
				min_ind = temp.index(min(temp))
				impactsByAgent[i].append([sum, absSum, item[max_ind], item[min_ind]])
			print(f'impactsByAgent : {impactsByAgent}\n')
			i += 1

		argsImpactOnFinalOutcome = []
		argsImpactOnUniverseProtocol = []
		argsImpactOnPartialProtocolH1 = []
		argsImpactOnPartialProtocolH2 = []

	i = 0
	for item in ag_score_infered:
		for score in item:
			diffFile.write(f'{ag_score[i]},{score}\n')
		i += 1
	print(ag_score_infered)
	print()
	print(ag_score)
	print()
	intervalSize = []
	for i in range(nb_agent):
		intervalSize.append([])
	i = 0
	for item in infered:
		temp = int(i%nb_agent)
		intervalSize[temp].append(abs(item[1] - item[0]))
		i += 1
	print(f'intervalSize : {intervalSize}')
	for item in intervalSize:
		k = 0
		for i in gameSize:
			gameSizeFile.write(f'{i},{item[k]}\n')
			k += 1
	means = []
	for i in range(nb_agent):
		means.append(float(0))
	i = 0
	mean = 0
	sum = 0
	sum1 = 0
	n = 0
	for item in intervalSize:
		j = 0
		for size in item:
			sum += size
			sum1 += size
			scoreFile.write(f'{ag_score[i]},{size}\n')
			for k in range(4):
				sumFile.write(f'{impactsByAgent[i][j+k][0]},{size}\n')
				absSumFile.write(f'{impactsByAgent[i][j+k][1]},{size}\n')
				maxFile.write(f'{impactsByAgent[i][j+k][2]},{size}\n')
				minFile.write(f'{impactsByAgent[i][j+k][3]},{size}\n')
			j += 1
		means[i] = float(sum1/j)
		n += j
		i += 1
	mean = float(float(sum)/float(n))
	guFile.write(f'{gu},{mean}\n')
	for i in range(means.__len__()):
		percentFile.write(f'{percent[i]},{means[i]}\n')
	print()
	print(infered)
	distinct = False
	if(nb_agent == 2):
		if((infered[0][0] > infered[1][1]) or (infered[1][0] > infered[0][1])):
			print(f'Game order 0,1 : distinct interval')
			distinct = True
		if((infered[2][0] > infered[3][1]) or (infered[3][0] > infered[2][1])):
			print(f'Game order 1,0 : distinct interval')
			distinct = True
		if(distinct):
			distinctFile = open('distinct.data', 'a')
			distinctFile.write(sys.argv[1])
			distinctFile.write('\n')