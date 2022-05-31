from logging import exception
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

def getAttackers(targetIndex, graph, args):
	attackers = []
	for item in args:
		if(int(graph[item][targetIndex]) == 1):
			attackers.append(int(item))
	return attackers

def getAgentAttackers(targetIndex, graph, args):
	attackers = []
	for item in args:
		if(item in argsPlayedByAgent[targetIndex]):
			# print(f'item = {item}')
			for index in args:
				if((int(graph[index][item]) == 1) and (item not in argsPlayedByAgent[targetIndex]) and (item not in attackers)):
					# print(f'{index} attaque {item}')
					attackers.append(int(index))
	return attackers

def getComplementScore(targetIndex, graph, args, firstValuation, ignoredArgs):
	newValuation = []
	stable = True
	for item in range(graph.__len__()):
		newValuation.append(float(1.0))
	for index in args:
		sum = 1.0
		for item in args:
			if(item not in ignoredArgs):
				sum += (float(graph[item][index])*float(firstValuation[item]))
		newValuation[index] = float(1.0/sum)
		if(abs(firstValuation[index] - newValuation[index]) > 0.0001):
			stable = False
	if(stable):
		return float(newValuation[targetIndex])
	else:
		return getComplementScore(targetIndex, graph, args, newValuation, ignoredArgs)

def turnScoreInference(move, previousTurnScore, argsPlayed, agentsInference):
	if(move.__len__() == 1):
		return move[0], int(0), argsPlayed, previousTurnScore, agentsInference
	elif(move.__len__() == 2):
		newScore = getScore(targetIndex, universeGraph, argsPlayed+[move[1]], firstValuation)
		if(newScore < previousTurnScore):
			if(((previousTurnScore + newScore)/2.0) < agentsInference[move[0]][1]):
				agentsInference[move[0]][1] = ((previousTurnScore + newScore)/2.0)
		else:
			if(((previousTurnScore + newScore)/2.0) > agentsInference[move[0]][1]):
				agentsInference[move[0]][1] = ((previousTurnScore + newScore)/2.0)
		return move[0], int(1), argsPlayed+[move[1]], newScore, agentsInference
	elif(move.__len__() == 3):
		newScore = getScore(targetIndex, universeGraph, argsPlayed+[move[1]]+[move[2]], firstValuation)
		if(newScore < previousTurnScore):
			if(((previousTurnScore + newScore)/2.0) < agentsInference[move[0]][1]):
				agentsInference[move[0]][1] = ((previousTurnScore + newScore)/2.0)
		else:
			if(((previousTurnScore + newScore)/2.0) > agentsInference[move[0]][1]):
				agentsInference[move[0]][1] = ((previousTurnScore + newScore)/2.0)
		return move[0], int(1), argsPlayed+[move[1]]+[move[2]], newScore, agentsInference

def gameScoreInference(moves, nbAgent):
	pass

graphSize = 0
nbAgents = 0
targetIndex = 0
universeGraph = []
gameArgs = []
universeArgs = []
agentsArgs = []
argsImpact = []
argsImpactOnFinalOutcome = []
argsImpactOnPartialProtocol = []
argsImpactOnUniverseProtocol = []
agentsImpactOnFinalOutcome = []
agentsImpactOnPartialProtocol = []
agentsImpactOnUniverseProtocol = []
save = False
fileToSave = 'save.txt'
fileExists = False
game = []

argvIndex = 0
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

firstValuation = []
for item in range(graphSize):
	universeArgs.append(item)
	firstValuation.append(float(1.0))
	argsImpact.append(float(0.0))
	argsImpactOnFinalOutcome.append(float(0.0))
	argsImpactOnPartialProtocol.append(float(0.0))
	argsImpactOnUniverseProtocol.append(float(0.0))

ag_score = []
argsPlayedByAgent = []
for i in range(nbAgents):
	ag_score.append(getScore(targetIndex, universeGraph, agentsArgs[i], firstValuation))
	agentsImpactOnFinalOutcome.append(float(0.0))
	agentsImpactOnPartialProtocol.append(float(0.0))
	agentsImpactOnUniverseProtocol.append(float(0.0))
	argsPlayedByAgent.append([])

score = getScore(targetIndex, universeGraph, universeArgs, firstValuation)

print(f'\nagentsArgs = {agentsArgs}')
print(f'targetIndex = {targetIndex}\n')

for i in range(nbAgents):
	print(f'agent {i} score : {ag_score[i]}')
print(f'score : {score}\n')

def protocol(game=[], gameArgs=[targetIndex]):
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
					# print(f'arg : {arg}, new_score : {new_score}')
					if(abs(ag_score[i] - new_score) < minDiff): # if it brings the game score closer to own score
						min_index = j # holds the arg that brings the score closest to own score
						minDiff = abs(ag_score[i] - new_score) # update the score difference
						best_score = new_score
						done = False # an arg is played so the game is not done
						multipleArgs = False
					else:
						for item in range(universeGraph[agentsArgs[i][j]].__len__()):
							if(universeGraph[agentsArgs[i][j]][item] == 1):
								# print(f'else : {item}, {item in agentsArgs[i]}, {item not in gameArgs}, {agentsArgs[i][j]}')
								# print(universeGraph[agentsArgs[i][j]])
								if((item in agentsArgs[i]) and (item not in gameArgs)):
									new_score = getScore(targetIndex, universeGraph, gameArgs+[arg]+[item], firstValuation) # score if arg is added
									# print(f'item : {item}, new_score : {new_score}')
									if(abs(ag_score[i] - new_score) < minDiff): # if it brings the game score closer to own score
										min_index = j # holds the arg that brings the score closest to own score
										minDiff = abs(ag_score[i] - new_score) # update the score difference
										best_score = new_score
										done = False # an arg is played so the game is not done
										multipleArgs = [item]
				j += 1 # update index for next loop
			if(min_index == -1):
				print(f'Agent {i} doesn\'t play this round')
				game += [[int(i)]]
			elif(multipleArgs == False):
				print(f'Agent {i} plays argument {agentsArgs[i][min_index]}')
				game += [[int(i), int(agentsArgs[i][min_index])]]
				argsPlayedByAgent[int(i)].append(int(agentsArgs[i][min_index]))
				argsImpact[agentsArgs[i][min_index]] = best_score - game_score # game_score - ag_score[i] + minDiff
				gameArgs.append(int(agentsArgs[i][min_index]))
			else:
				print(f'Agent {i} plays argument {agentsArgs[i][min_index]} and {multipleArgs[0]}')
				game += [[int(i), int(agentsArgs[i][min_index]), int(multipleArgs[0])]]
				argsPlayedByAgent[int(i)].append(int(agentsArgs[i][min_index]))
				argsPlayedByAgent[int(i)].append(int(multipleArgs[0]))
				argsImpact[agentsArgs[i][min_index]] = (best_score - game_score)/2 # game_score - ag_score[i] + minDiff
				gameArgs.append(int(agentsArgs[i][min_index]))
				argsImpact[multipleArgs[0]] = (best_score - game_score)/2 # game_score - ag_score[i] + minDiff
				gameArgs.append(int(multipleArgs[0]))
			print(f'gameArgs, score : {gameArgs}, {getScore(targetIndex, universeGraph, gameArgs, firstValuation)}\n')
	return game, gameArgs

game, gameArgs = protocol()

def partialProtocol(game=[], gameArgs=[targetIndex], playable=universeArgs, exception=[]):
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
				# print(f'arg : {arg}, {arg not in gameArgs}, {arg in playable}, {arg not in exception}')
				if((arg not in gameArgs) and (arg in playable) and (arg not in exception)): # if the arg has not been played
					new_score = getScore(targetIndex, universeGraph, gameArgs+[arg], firstValuation) # score if arg is added
					if(abs(ag_score[i] - new_score) < minDiff): # if it brings the game score closer to own score
						min_index = j # holds the arg that brings the score closest to own score
						minDiff = abs(ag_score[i] - new_score) # update the score difference
						done = False # an arg is played so the game is not done
						multipleArgs = False
					else:
						for item in range(universeGraph[agentsArgs[i][j]].__len__()):
							if(universeGraph[agentsArgs[i][j]][item] == 1):
								if((item in agentsArgs[i]) and (item in playable) and (item not in exception) and (item not in gameArgs)):
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
				# argsImpact[agentsArgs[i][min_index]] = game_score - ag_score[i] + minDiff
				gameArgs.append(int(agentsArgs[i][min_index]))
			else:
				print(f'Agent {i} plays argument {agentsArgs[i][min_index]} and {multipleArgs[0]}')
				game += [[int(i), int(agentsArgs[i][min_index]), int(multipleArgs[0])]]
				# argsImpact[agentsArgs[i][min_index]] = game_score - ag_score[i] + minDiff
				gameArgs.append(int(agentsArgs[i][min_index]))
				# argsImpact[multipleArgs[0]] = game_score - ag_score[i] + minDiff
				gameArgs.append(int(multipleArgs[0]))
			print(f'gameArgs, score : {gameArgs}, {getScore(targetIndex, universeGraph, gameArgs, firstValuation)}\n')
	return game, gameArgs

# calculate metrics

# impact of args based on final outcome

print("impact of args based on final outcome\n\n")

for item in universeArgs:
	if((item != targetIndex) and (item in gameArgs)):
		a = getComplementScore(targetIndex, universeGraph, gameArgs, firstValuation, getAttackers(item, universeGraph, universeArgs))
		b = getComplementScore(targetIndex, universeGraph, gameArgs, firstValuation, [item])
		# print(f'arg {item} is attacked by {getAttackers(item, universeGraph, universeArgs)} with an impact of {a-b}')
		argsImpactOnFinalOutcome[item] = a - b
	else:
		argsImpactOnFinalOutcome[item] = 0.0

# impact of args based on partial protocol

print("impact of args based on partial protocol\n\n")

gameScore = getScore(targetIndex, universeGraph, gameArgs, firstValuation)
for item in universeArgs:
	# print(f'gameArgs : {gameArgs}, item : {item}\n')
	if((item != targetIndex) and (item in gameArgs)):
		game2, gameArgs2 = partialProtocol(game=[], gameArgs=[targetIndex], playable=gameArgs, exception=[item])
		newScore = getScore(targetIndex, universeGraph, gameArgs2, firstValuation)
		# print(f'game : {game2}, score : {newScore}, impact : {gameScore - newScore}')
		argsImpactOnPartialProtocol[item] = gameScore - newScore
	else:
		argsImpactOnPartialProtocol[item] = 0.0

# impact of args based on universe protocol

print("impact of args based on universe protocol\n\n")

gameScore = getScore(targetIndex, universeGraph, gameArgs, firstValuation)
for item in universeArgs:
	# print(f'gameArgs : {gameArgs}, item : {item}\n')
	if((item != targetIndex)):
		game2, gameArgs2 = partialProtocol(game=[], gameArgs=[targetIndex], playable=universeArgs, exception=[item])
		newScore = getScore(targetIndex, universeGraph, gameArgs2, firstValuation)
		# print(f'game : {game2}, score : {newScore}, impact : {gameScore - newScore}')
		argsImpactOnUniverseProtocol[item] = gameScore - newScore
	else:
		argsImpactOnUniverseProtocol[item] = 0.0

# impact of agents based on final outcome

# item = 0
# for i in agentsArgs:
# 	a = getComplementScore(targetIndex, universeGraph, gameArgs, firstValuation, getAgentAttackers(item, universeGraph, universeArgs))
# 	b = getComplementScore(targetIndex, universeGraph, gameArgs, firstValuation, i)
# 	# print(f'agent {item} is attacked by {getAgentAttackers(item, universeGraph, universeArgs)} with an impact of {a}-{b}')
# 	agentsImpactOnFinalOutcome[item] = a - b
# 	item += 1

# score inferrance



# print metrics

print(f'\ngameArgs = {gameArgs}')
print(f'argsPlayedByAgent = {argsPlayedByAgent}')
print(f'argsImpact = {argsImpact}')
print(f'argsImpactOnFinalOutcome = {argsImpactOnFinalOutcome}')
print(f'argsImpactOnPartialProtocol = {argsImpactOnPartialProtocol}')
print(f'argsImpactOnUniverseProtocol = {argsImpactOnUniverseProtocol}')
# print(f'agentsImpactOnFinalOutcome = {agentsImpactOnFinalOutcome}')
# print(f'agentsImpactOnPartialProtocol = {agentsImpactOnPartialProtocol}')
# print(f'agentsImpactOnUniverseProtocol = {agentsImpactOnUniverseProtocol}')

# to save the game

# if(save != True):
# 	choice = '2'
# 	while(choice != '0' and choice != '1'):
# 		choice = input(f'Do you want to save the game and metrics ?\n\t0 : No\n\t1 : Yes\n')
# 		if(choice != '0' and choice != '1'):
# 			print(f'Incorrect input...\n')
# 	if(int(choice) == 1):
# 		save = True
# 		saveToFile = input(f'Enter path to save file : \n')

# if(save == True):
# 	with open(saveToFile, 'w') as f:
# 		for item in game:
# 			if(item.__len__() == 2):
# 				f.write(f'Agent {item[0]} plays {item[1]}\n')
# 			elif(item.__len__() == 3):
# 				f.write(f'Agent {item[0]} plays {item[1]} and {item[2]}\n')
# 		f.write(f'universeGraph :')
# 		for item in universeGraph:
# 			f.write(f'\n\t\t{item}')
# 		f.write(f'\ngameArgs :')
# 		for item in gameArgs:
# 			f.write(f' {item}')
# 		f.write(f'\ngame score : {getScore(targetIndex, universeGraph, gameArgs, firstValuation)}')