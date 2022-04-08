import re
import sys
import os.path

def getScore(targetIndex, graph, args, firstValuation):
	newValuation = []
	stable = True
	for item in range(graph.__len__()):
		newValuation.append(float(1.0))
	for index in args:
		sum = 1.0
		for item in args:
			sum += (float(graph[item][index])*float(firstValuation[item]))
		newValuation[index] = float(1.0/sum)
		if(abs(firstValuation[index] - newValuation[index]) > 0.0001):
			stable = False
	if(stable):
		return float(newValuation[targetIndex])
	else:
		return getScore(targetIndex, graph, args, newValuation)

graphSize = 0
nbAgents = 0
targetIndex = 0
universeGraph = []
gameArgs = []
universeArgs = []
agentsArgs = []
argsImpact = []
save = False
fileToSave = 'save.txt'
fileExists = False
game = []

argvIndex = 0
# print(sys.argv[])
for item in sys.argv:
	if(sys.argv[argvIndex] == '-f' and sys.argv.__len__() > (argvIndex+1)):
		fileExists = os.path.exists(sys.argv[(argvIndex+1)])
		if(fileExists == False):
			raise Exception("File not Found")
		with open(sys.argv[(argvIndex+1)]) as file_object:
			# reads nb of agents
			line = file_object.readline()
			values = re.split(' ', line)
			nbAgents = int(values[0])

			# reads graph size
			line = file_object.readline()
			values = re.split(' ', line)
			graphSize = int(values[0])

			# reads target index
			line = file_object.readline()
			values = re.split(' ', line)
			targetIndex = int(values[0])
			gameArgs.append(int(values[0]))

			# skips blank line
			line = file_object.readline()
			line = file_object.readline()

			# reads universe graph
			for i in range(graphSize):
				values = re.split(' ', line)
				argRelations = []
				for item in values:
					argRelations.append(int(item))
				universeGraph.append(argRelations)
				line = file_object.readline()

			# skips blank line
			line = file_object.readline()
			values = re.split(' ', line)
			if(int(values[0]) == 1): # if there is agents graphs
				# skips blank line
				line = file_object.readline()
				line = file_object.readline()
				# reads agents graphs
				for i in range(nbAgents):
					values = re.split(' ', line)
					argslist = []
					for item in values:
						argslist.append(int(item))
					agentsArgs.append(argslist)
					line = file_object.readline()
	elif(sys.argv[argvIndex] == '-s' and sys.argv.__len__() > (argvIndex+1)):
		save = True
		saveToFile = sys.argv[(argvIndex+1)]
	argvIndex += 1



for item in range(graphSize):
	universeArgs.append(item)

firstValuation = []
for item in range(graphSize):
	firstValuation.append(float(1.0))
	argsImpact.append(float(0.0))

ag_score = []
for i in range(nbAgents):
	ag_score.append(getScore(targetIndex, universeGraph, agentsArgs[i], firstValuation))

score = getScore(targetIndex, universeGraph, agentsArgs[0]+[int(1)], firstValuation)

print(f'graphSize = {universeGraph.__len__()}')
print(f'agentsArgs = {agentsArgs}')
print(f'targetIndex = {targetIndex}')
print(f'universeArgs len = {universeArgs.__len__()}')

for i in range(nbAgents):
	print(f'agent {i} score : {ag_score[i]}')
print(f'score : {score}')

# each agent tries every arg not in it yet and plays the best one

done = False
while(not done):
	done = True
	for i in range(nbAgents): # for each agent
		game_score = getScore(targetIndex, universeGraph, gameArgs, firstValuation) # get the game score
		minDiff = abs(ag_score[i] - game_score) # calculate the difference between their own score and the game score
		min_index = -1 # for now no arg is played
		multipleArgs = False
		j = 0
		for arg in agentsArgs[i]: # for each arg of the agent
			if(arg not in gameArgs): # if the arg has not been played
				new_score = getScore(targetIndex, universeGraph, gameArgs+[arg], firstValuation) # score if arg is added
				if(abs(ag_score[i] - new_score) < minDiff): # if it brings the game score closer to own score
					min_index = j # holds the arg that brings the score closest to own score
					minDiff = abs(ag_score[i] - new_score) # update the score difference
					done = False # an arg is played so the game is not done
					multipleArgs = False
				else:
					for item in range(universeGraph[j].__len__()):
						if(universeGraph[j][item] == 1):
							if(item in agentsArgs[i]):
								new_score = getScore(targetIndex, universeGraph, gameArgs+[arg]+[item], firstValuation) # score if arg is added
								if(abs(ag_score[i] - new_score) < minDiff): # if it brings the game score closer to own score
									min_index = j # holds the arg that brings the score closest to own score
									minDiff = abs(ag_score[i] - new_score) # update the score difference
									done = False # an arg is played so the game is not done
									multipleArgs = [item]
			j += 1 # update index for next loop
		if(min_index == -1):
			print(f'Agent {i} doesn\'t play this round')
		elif(multipleArgs == False):
			print(f'Agent {i} plays argument {agentsArgs[i][min_index]}')
			game += [[int(i), int(agentsArgs[i][min_index])]]
			argsImpact[agentsArgs[i][min_index]] = game_score - ag_score[i] + minDiff
			gameArgs.append(int(agentsArgs[i][min_index]))
		else:
			print(f'Multiple args : {multipleArgs}')
			print(f'Agent {i} plays argument {agentsArgs[i][min_index]} and {multipleArgs[0]}')
			game += [[int(i), int(agentsArgs[i][min_index]), int(multipleArgs[0])]]
			argsImpact[agentsArgs[i][min_index]] = game_score - ag_score[i] + minDiff
			gameArgs.append(int(agentsArgs[i][min_index]))
			argsImpact[multipleArgs[0]] = game_score - ag_score[i] + minDiff
			gameArgs.append(int(multipleArgs[0]))
		print(f'gameArgs, score : {gameArgs}, {getScore(targetIndex, universeGraph, gameArgs, firstValuation)}')

print(f'gameArgs = {gameArgs}')
print(f'argsImpact = {argsImpact}')

if(save != True):
	choice = '2'
	while(choice != '0' and choice != '1'):
		choice = input(f'Do you want to save the game and metrics ?\n\t0 : No\n\t1 : Yes\n')
		if(choice != '0' and choice != '1'):
			print(f'Incorrect input...\n')
	if(int(choice) == 1):
		save = True
		saveToFile = input(f'Enter path to save file : \n')

if(save == True):
	with open(saveToFile, 'w') as f:
		for item in game:
			if(item.__len__() == 2):
				f.write(f'Agent {item[0]} plays {item[1]}\n')
			elif(item.__len__() == 3):
				f.write(f'Agent {item[0]} plays {item[1]} and {item[2]}\n')
		f.write(f'universeGraph :')
		for item in universeGraph:
			f.write(f'\n\t\t{item}')
		f.write(f'\ngameArgs :')
		for item in gameArgs:
			f.write(f' {item}')
		f.write(f'\ngame score : {getScore(targetIndex, universeGraph, gameArgs, firstValuation)}')