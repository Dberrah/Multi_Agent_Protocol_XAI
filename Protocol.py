import csv
import itertools
from logging import exception
import copy
from pickletools import ArgumentDescriptor
import random
import re
import sys
import os

# formula to extract the inferred score from the inferences
def scoreFromInference(var2):
	ag_score_infered = []
	for ag in var2:
		# the inferred score is the middle of the inferred interval
		ag_score_infered.append((max(ag[0],ag[2]) + min(ag[1],ag[3]))/2.0)
	return ag_score_infered

# return true if an argument attacks the issue
def attackTarget(agentArgs):
	for arg in agentArgs:
		if(arg in attaquants[0]):
			return True
	return False

# computes the score with respect to the h-categorizer semantic
def getScore(graph, firstValuation = []):
	if(firstValuation == []):
		firstValuation = []
		for item in range(len(graph)): # creation of the new valuation
			firstValuation.append(float(1.0))
	newValuation = []
	stable = True
	for item in range(len(graph)): # creation of the new valuation
		newValuation.append(float(1.0))
	i = 0
	for arg,att in graph.items(): # go through the elements of the graph
		sum = 1.0
		j = 0
		for item in graph:
			if(item in graph[arg]):
				sum += float(firstValuation[j])
			j += 1
		newValuation[i] = float(1.0/sum)
		if(abs(firstValuation[i] - newValuation[i]) > 0.0001): # the treshhold is fixed to 0.0001
			stable = False
		i += 1
	if(stable):
		return float(newValuation[0])
	else:
		return getScore(graph, newValuation)

# computes the positive inference
def turnScoreInference(move, previousTurnScore, argsPlayed, agentsInference):
	if(move.__len__() == 2): # if the agent did not play
		return move[0], int(0), [], argsPlayed, previousTurnScore, agentsInference
	elif(move.__len__() == 3): # if the agent played one argument
		newScore = getScore(move[2])
		if(newScore < previousTurnScore): # if the score got closer to zero
			if(((previousTurnScore + newScore)/2.0) < agentsInference[move[0]][1]):
				agentsInference[move[0]][1] = ((previousTurnScore + newScore)/2.0)
		else: # if the score got closer to one
			if(((previousTurnScore + newScore)/2.0) > agentsInference[move[0]][0]): # if it gives new information about the personal score of the agent
				agentsInference[move[0]][0] = ((previousTurnScore + newScore)/2.0)
		return move[0], int(1), [move[1]], argsPlayed+[argToId[move[1]]], newScore, agentsInference
	elif(move.__len__() == 4): # if the agent played two arguments
		newScore = getScore(move[3])
		if(newScore < previousTurnScore):
			if(((previousTurnScore + newScore)/2.0) < agentsInference[move[0]][1]):
				agentsInference[move[0]][1] = ((previousTurnScore + newScore)/2.0)
		else:
			if(((previousTurnScore + newScore)/2.0) > agentsInference[move[0]][0]):
				agentsInference[move[0]][0] = ((previousTurnScore + newScore)/2.0)
		return move[0], int(1), [move[1]]+[move[2]], argsPlayed+[argToId[move[1]]]+[argToId[move[2]]], newScore, agentsInference

# computes the negative inference
def negInference(turnNotPlayed, move, game_att, agentsInference):
	# print('NEGINF1')
	# print(move)
	couldHave = False
	if(move.__len__() == 3): # if the agent played one argument
		# i = 0
		# print('NEGINF3')
			# if(att == 1):
		for turn in turnNotPlayed: # goes through the turns during which the agent did not play
			print(f'{turn} == {move[0]} ?')
			if(turn[0] == move[0]): # if it was the agent's turn to play
				for att in turn[1]: #game_att[argToId[move[1]]]:
				# print(f'NEGINF, turn : {turn}, {att}')
					print(att)
					if(argToId[move[1]] in game_att[att]): # agent could have played
						couldHave = True
						temp = copy.deepcopy(turn[1])
						temp[argToId[move[1]]] = move[2][argToId[move[1]]]
						newScore = getScore(temp)
						if(newScore < turn[2]): # if the score would have gotten closer to zero
							print('NEGINFBS')
							if(((turn[2] + newScore)/2.0) > agentsInference[move[0]][2]):
								agentsInference[move[0]][2] = ((turn[2] + newScore)/2.0)
						else: # closer to one
							print('NEGINFBI')
							if(((turn[2] + newScore)/2.0) < agentsInference[move[0]][3]):
								agentsInference[move[0]][3] = ((turn[2] + newScore)/2.0)
			# i += 1
	elif(move.__len__() == 4): # if the agent played two arguments
		# i = 0
		# print('NEGINF4')
			# if(att == 1):
		for turn in turnNotPlayed:
			print(f'{turn} == {move[0]} ?')
			if(turn[0] == move[0]):
				# print(f'NEGINF, turn : {turn}, {att}')
				for att in turn[1]: #game_att[argToId[move[1]]]:
					if(argToId[move[1]] in game_att[att]): # agent could have played
						couldHave = True
						temp = copy.deepcopy(turn[1])
						temp[argToId[move[1]]] = move[3][argToId[move[1]]]
						temp[argToId[move[2]]] = move[3][argToId[move[2]]]
						newScore = getScore(temp)
						if(newScore < turn[2]):
							print('NEGINF')
							if(((turn[2] + newScore)/2.0) > agentsInference[move[0]][2]):
								agentsInference[move[0]][2] = ((turn[2] + newScore)/2.0)
						else:
							print('NEGINF')
							if(((turn[2] + newScore)/2.0) < agentsInference[move[0]][3]):
								agentsInference[move[0]][3] = ((turn[2] + newScore)/2.0)
			# i += 1
	return agentsInference,couldHave

# this function process the game history to compute the inferences
def gameScoreInference(moves, nbAgent, game_att):
	score = 1
	agentsInference = []
	turnNotPlayed = []
	inferenceHistory = []
	i = 0
	args = [0]
	for a in range(nbAgent): # init the inferred intervals
		agentsInference += [[0,1,0,1]] # positive inference lower and upper bounds and negative inference lower and upper bounds
		inferenceHistory += [[[0,1,0,1]]]
	# print(f'moves : {moves}')
	for move in moves: # goes through the game history
		couldHave = False
		print(f'move : {move}')
		ag, hasPlayed, played, args, score, agentsInference = turnScoreInference(move, score, args, agentsInference) # calls positive inference
		if(hasPlayed == 0): # if the agent did not play
			turnNotPlayed += [[ag,move[1],score]] 
			print(f'Agent {ag} did not play, so we save the game : {[ag,move[1],score]}')# : {turnNotPlayed}')
		else: # if the agent played
			print(f'Agent {ag} did play ',end='')#{played} : {agentsInference}')
			print("{",end='')
			j = 0
			for item in played:
				if(j==0):
					print(f'{item}',end='')
				else:
					print(f', {item}',end='')
				j += 1
			print("} :")
			print(f'\tAgent\'s inference : {agentsInference[ag]}')
			agentsInference, couldHave = negInference(turnNotPlayed, move, game_att, agentsInference) # calls negative inference
			# inferenceHistory[ag].append([agentsInference[ag][0], agentsInference[ag][1], agentsInference[ag][2], agentsInference[ag][3]])
			print(f'\tAgent\'s inference : {agentsInference[ag]}, {couldHave}')
			if(couldHave == True): # if the agent could have make this move before now 
				print(f'Agent {ag} could have played ',end='')#{played} : {agentsInference}')
				print("{",end='')
				j = 0
				for item in played:
					if(j==0):
						print(f'{item}',end='')
					else:
						print(f', {item}',end='')
					j += 1
				print("} earlier :")
				print(f'\tAgent\'s inference : {agentsInference[ag]}')
		inferenceHistory[ag].append([agentsInference[ag][0], agentsInference[ag][1], agentsInference[ag][2], agentsInference[ag][3]])
	print()
	return turnNotPlayed, agentsInference, inferenceHistory

# never called (attempt to improve the inference)
def gameScoreInference2(moves, nbAgent, game_att):
	agentsInference = []
	inferenceHistory = []
	args = [0]
	for a in range(nbAgent):
		agentsInference += [[0,1,0,1]]
		inferenceHistory += [[[0,1,0,1]]]
	
	for ag in range(nb_agents):
		ag_move = []
		for move in moves:
			if(move[0] == ag):
				if(move.__len__() == 3):
					temp = copy.deppcopy(move[2])
					temp = temp.pop(argToId[move[1]])
					ag_move.append(temp)
				if(move.__len__() == 4):
					temp = copy.deepcopy(move[3])
					temp = temp.pop(argToId[move[1]])
					temp = temp.pop(argToId[move[2]])
					ag_move.append(temp)
		i = 0
		for move in moves:
			if(move[0] == ag):
				if(move.__len__() == 3):
					for j in range(i):
						for arg in ag_move[j].keys():
							if(arg in att[argToId[move[1]]]):
								pass # move[1] aurait pu etre played
				if(move.__len__() == 4):
					pass
			i += 1

	return agentsInference, inferenceHistory

# this function runs the protocol
def protocol(agentsOrder, ag_score, agentAF, exception = []):
	# nbArgPlayed = 0
	gameArgs = [int(0)]
	done = False
	argsImpact = {}
	game = []
	game_att = {}
	game_att[0] = []
	# each agent tries every arg not in it yet and plays the best one
	while(not done):
		done = True
		for i in agentsOrder: # for each agent
			game_score = getScore(game_att) # get the game score
			minDiff = abs(ag_score[i] - game_score) # calculate the difference between their own score and the game score
			min_index = -1 # for now no arg is played
			multipleArgs = False
			j = 0
			for arg in agentAF[i]: # for each arg of the agent
				if((arg not in gameArgs) and (arg not in exception)): # if the arg has not been played
					temp = copy.deepcopy(game_att)
					temp[arg] = []
					for k in temp:
						for l in temp:
							if((l in attaquants[k]) and (l not in temp[k])):
								temp[k].append(l)
					new_score = getScore(temp) # score if arg is added
					# print(f'arg : {arg}, new_score : {new_score}')
					if(abs(ag_score[i] - new_score) < minDiff): # if it brings the game score closer to own score
						min_index = j # holds the arg that brings the score closest to own score
						minDiff = abs(ag_score[i] - new_score) # update the score difference
						best_score = new_score
						done = False # an arg is played so the game is not done
						multipleArgs = False
					else:
						for item in attaquants[arg]:
							if((item in agentAF[i]) and (item not in gameArgs) and (item not in exception)):
								temp[item] = []
								for k in temp:
									for l in temp:
										if((l in attaquants[k]) and (l not in temp[k])):
											temp[k].append(l)
								new_score = getScore(temp) # score if arg is added
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
				game += [[int(i), copy.deepcopy(game_att)]]
			elif(multipleArgs == False): # if the agent plays one argument
				# print([key for key in agentAF[i].keys()][min_index])
				print(f'Agent {i} plays argument {idToArg[[key for key in agentAF[i].keys()][min_index]]}')
				# add the argument to the debate graph
				game_att[[key for key in agentAF[i].keys()][min_index]] = []
				for k in game_att:
					for l in game_att:
						if((l in attaquants[k]) and (l not in game_att[k])):
							game_att[k].append(l)
				# add the play to the game history
				game += [[int(i), idToArg[[key for key in agentAF[i].keys()][min_index]], copy.deepcopy(game_att)]]
				# argsPlayedByAgent[int(i)].append(int(agentsArgs[i][min_index]))
				argsImpact[[key for key in agentAF[i].keys()][min_index]] = best_score - game_score # game_score - ag_score[i] + minDiff
				gameArgs.append(int([key for key in agentAF[i].keys()][min_index]))
			else: # if the agent played two arguments
				print(f'Agent {i} plays argument {idToArg[[key for key in agentAF[i].keys()][min_index]]} and {idToArg[multipleArgs[0]]}')
				game_att[[key for key in agentAF[i].keys()][min_index]] = []
				game_att[multipleArgs[0]] = []
				for k in game_att:
					for l in game_att:
						if((l in attaquants[k]) and (l not in game_att[k])):
							game_att[k].append(l)
				game += [[int(i), idToArg[[key for key in agentAF[i].keys()][min_index]], idToArg[multipleArgs[0]], copy.deepcopy(game_att)]]
				# argsPlayedByAgent[int(i)].append(int(agentsArgs[i][min_index]))
				# argsPlayedByAgent[int(i)].append(int(multipleArgs[0]))
				argsImpact[[key for key in agentAF[i].keys()][min_index]] = (best_score - game_score)/2 # game_score - ag_score[i] + minDiff
				gameArgs.append(int([key for key in agentAF[i].keys()][min_index]))
				argsImpact[multipleArgs[0]] = (best_score - game_score)/2 # game_score - ag_score[i] + minDiff
				gameArgs.append(int(multipleArgs[0]))
	print(f'End of the protocol because no agent played during the round')
	print("\n-------------------------------------------------------------------")
	print()
	return game, gameArgs, game_att, argsImpact

argDen = random.randint(4,8)
argDensity = float(argDen/10.0)
nb_agents = random.randint(2,4)
argToId = {}
idToArg = {}
attaquants = {}
att = {}
universeGraph = []
agentAF = []
size_AF = 0
ag_score = []

path = ''
# finds the generated apx file
for file in os.listdir(sys.argv[1]):
	if(re.match("debate_graph_\S+", file)):
		path = sys.argv[1]+file

fileExists = os.path.exists(path)
if(fileExists == False):
	raise Exception("File not Found")
with open(path) as file_object:
	line = file_object.readline()
	while line:
		values = re.split("\\(|\\)|,",line)
		if(line.startswith('arg')): # new argument
			argToId[values[1]] = size_AF
			idToArg[size_AF] = values[1]
			attaquants[size_AF] = [] # attackers dictionnary
			att[size_AF] = [] # attacked dictionnary
			size_AF += 1
		elif((line.startswith('att')) and (values[1] in argToId) and (values[2] in argToId)): # new attack
			attaquants[argToId[values[2]]].append(argToId[values[1]])
			att[argToId[values[1]]].append(argToId[values[2]])
		else:
			raise Exception("Error in File")
		line = file_object.readline()

# creation of the universe graph
for item in range(size_AF):
	universeGraph.append([])
	for j in range(size_AF):
		if(j in att[item]):
			universeGraph[item].append(int(1))
		else:
			universeGraph[item].append(int(0))

# creation of the agent's knowledge base
for ag in range(nb_agents):
	agentAF.append({})
	for i in range(size_AF):
		if(i == 0): # the issue is always part of the knowledge base
			agentAF[ag][i] = []
		elif(random.random() <= argDensity): # each argument has a probability to be part of the knowledge base
			agentAF[ag][i] = []
			#here to get nb args
	if(not attackTarget(agentAF[ag])): # verify that at least one argument attacks the issue
		agentAF[ag] = {}
		while(not attackTarget(agentAF[ag])):
			for i in range(size_AF):
				if(i == 0):
					agentAF[ag][i] = []
				elif(random.random() <= argDensity):
					agentAF[ag][i] = []
	for i in agentAF[ag]:
		for j in agentAF[ag]:
			if(j in attaquants[i]):
				agentAF[ag][i].append(j)

# allows to write the useful information in a file
f = open(sys.argv[1]+'data'+sys.argv[2]+'.csv', 'w', newline='')
f1 = open(sys.argv[1]+'bench'+sys.argv[2]+'.csv', 'w', newline='')
writer = csv.writer(f)
w = csv.writer(f1)
temp = [nb_agents, size_AF]
writer.writerow(temp)
w.writerow([size_AF])
w.writerow([nb_agents])
writer.writerow(argToId.keys())
writer.writerows(universeGraph)
for af in agentAF:
	writer.writerow(af.keys())
	temp = [getScore(af)]
	writer.writerow(temp)
	w.writerow(temp)
	w.writerow([af.__len__()])

agOrder = []
ag_score = []
for i in range(nb_agents):
	agOrder.append(int(i))
	ag_score.append(getScore(agentAF[i]))

agOrder = itertools.permutations(agOrder, nb_agents) # get every possible order 

# use to write the logs
print(f'There are {nb_agents} agents playing.')
print()
print(f'With an argument density of {argDensity}')
print()
print(f'The agents have the following knowledge base : ')
k = 0
for ag in agentAF:
	print(f'Agent {k} knows the argument(s) :\n\t\t',end='')
	j = 0
	for cle, value in ag.items():
		if(j == 0):
			print("{",end='')
		else:
			print(", ",end='')
		print(f'{idToArg[cle]}',end='') #: [', end='')
		j += 1
	print("}\n\tand the relations :\n\t\t",end='')
	i = 0
	print("{", end='')
	for cle, value in ag.items():
		for val in value:
			if(i != 0):
				print(f', ', end='')
			print(f'({val},{cle})',end='')
			i += 1
	print("}",end='')
	print(f'\n\twith a personal score of {getScore(ag)}\n')
	k += 1

for agentsOrder in agOrder: # we run the protocol for every order possible
	print()
	print("-------------------------------------------------------------------")
	print(f'\t\t\tAGENTS ORDER : ',end='')
	i = 0
	for ag in agentsOrder:
		if(i == 0):
			print(f'{ag}',end='')
			i+=1
		else:
			print(f', {ag}',end='')
	print()
	print("-------------------------------------------------------------------")
	print()

	game, gameArgs, game_att, argsImpact = protocol(agentsOrder, ag_score, agentAF)

	print(f'The final graph :\n\t',end='')
	print(f'the argument(s) played are :\n\t\t',end='')
	j = 0
	for cle, value in game_att.items():
		if(j == 0):
			print("{",end='')
		else:
			print(", ",end='')
		print(f'{idToArg[cle]}',end='') #: [', end='')
		j += 1
	print("}\n\tand the relations :\n\t\t",end='')
	i = 0
	print("{", end='')
	for cle, value in game_att.items():
		for val in value:
			if(i != 0):
				print(f', ', end='')
			print(f'({val},{cle})',end='')
			i += 1
	print("}")
	k += 1
	print()
	print(f'\twith a score of {getScore(game_att)}')
	print()
	print(f'The immediate impacts of the arguments when played are :')
	for key, value in argsImpact.items():
		print(f'\tthe impact of the argument {idToArg[key]} equals {value}')
	print()

	print("---------------impact of args based on final outcome---------------\n")

	argsImpactOnFinalOutcome = {}

	for item in gameArgs: # for every argument in the final debate graph
		if(item != 0):
			temp1 = copy.deepcopy(game_att)
			for arg in attaquants[item]:
				if arg in temp1:
					temp1.pop(arg) # remove the direct attackers of item
			temp2 = copy.deepcopy(game_att)
			temp2.pop(item) # remove item
			a = getScore(temp1)
			b = getScore(temp2)
			argsImpactOnFinalOutcome[item] = a - b
		else:
			argsImpactOnFinalOutcome[item] = 0.0

	print(f'The arguments impact based on the final outcome :')
	for key, value in argsImpactOnFinalOutcome.items():
		print(f'\tthe impact of the argument {idToArg[key]} equals {value}')

	print("\n-------------impact of args based on omniscient protocol-------------\n")

	argsImpactOnUniverseProtocol = {}

	gameScore = getScore(game_att)
	for item in gameArgs:
		if((item != 0)):
			print(f'Protocol without the argument {idToArg[item]}\n')
			game2, gameArgs2, game_att2, argsImpact2 = protocol(agentsOrder, ag_score, agentAF, [item])
			newScore = getScore(game_att2)
			argsImpactOnUniverseProtocol[item] = gameScore - newScore
		else:
			argsImpactOnUniverseProtocol[item] = 0.0

	print(f'The arguments impact based on the omniscient protocol :')
	for key, value in argsImpactOnUniverseProtocol.items():
		print(f'\tthe impact of the argument {idToArg[key]} equals {value}')
	print()

	print("--------------impact of args based on observable protocol-------------\n")

	var1, var2, inferenceHistory = gameScoreInference(game, nb_agents, game_att)

	print(f'The saved steps of the game are :')
	for turn in var1:
		print(f'\t{turn} :\n\tAgent {turn[0]}\'s turn, ',end='')
		i = 0
		for item in turn[1]:
			if(i == 0):
				print("{",end='')
				print(f'{item}',end='')
			else:
				print(f', {item}',end='')
			i += 1
		print("}",end='')
		print(f', with a score of {turn[2]}\n')
	print(f'The infered score intervals of the agents are :')
	i = 0
	for item in var2:
		print(f'for agent {i} : [{max(item[0], item[2])}, {min(item[1], item[3])}]')
		i += 1
		print(f'item : {item}')

	argsImpactOnPartialProtocolH1 = {}
	argsImpactOnPartialProtocolH2 = {}
	gameScore = getScore(game_att)
	ag_score_infered = scoreFromInference(var2)

	i = 0
	print(f'\nThe infered score :')
	for item in ag_score_infered:
		print(f'for agent {i} : {item}')
		i += 1

	i = 0
	print(f'\nThe only playable arguments are :')
	for item in gameArgs:
		if(i == 0):
			print("\t{",end='')
			print(f'{item}',end='')
		else:
			print(f', {item}',end='')
		i += 1
	print("}")
	print()
	print("-------------------------------------------------------------------")
	print()

	tempAF2 = []
	for i in range(nb_agents):
		tempAF2.append({})
		tempAF2[i][0] = []
	for move in game:
		if(move.__len__() == 3):
			tempAF2[move[0]][argToId[move[1]]] = []
		elif(move.__len__() == 4):
			tempAF2[move[0]][argToId[move[1]]] = []
			tempAF2[move[0]][argToId[move[2]]] = []
	for ag in tempAF2:
		for key, values in attaquants.items():
			if(key in ag):
				for arg in values:
					if(arg in ag):
						ag[key].append(arg)

	poped = []
	for af in agentAF:
		for arg,value in af.items():
			if(arg not in gameArgs) and (arg not in poped):
				poped.append(arg)

	tempAF = copy.deepcopy(agentAF)
	for ag in tempAF:
		if(item in ag):
			ag.pop(item)
		for arg in poped:
			if(arg in ag):
				ag.pop(arg)

	for item in game_att:
		if(item != 0):
			print(f'Protocol without the argument {idToArg[item]} under hypothesis 1\n')
			game2, gameArgs2, game_att2, argsImpact2 = protocol(agentsOrder, ag_score_infered, tempAF, exception=[item])
			newScore = getScore(game_att2)
			argsImpactOnPartialProtocolH1[item] = gameScore - newScore
			print(f'Protocol without the argument {idToArg[item]} under hypothesis 2\n')
			game3, gameArgs3, game_att3, argsImpact3 = protocol(agentsOrder, ag_score_infered, tempAF2, exception=[item])
			newScore2 = getScore(game_att3)
			argsImpactOnPartialProtocolH2[item] = gameScore - newScore2
		else:
			argsImpactOnPartialProtocolH1[item] = 0.0
			argsImpactOnPartialProtocolH2[item] = 0.0
	
	print(f'The arguments impact based on the observable protocol with hypothesis 1 :')
	for key, value in argsImpactOnPartialProtocolH1.items():
		print(f'\tthe impact of the argument {idToArg[key]} equals {value}')
	print()

	print(f'The arguments impact based on the observable protocol with hypothesis 2 :')
	for key, value in argsImpactOnPartialProtocolH2.items():
		print(f'\tthe impact of the argument {idToArg[key]} equals {value}')
	print()

	writer.writerow([])
	writer.writerow(agentsOrder)
	writer.writerow(gameArgs)
	temp = [game.__len__()]
	writer.writerow(temp)
	w.writerow(temp)
	for move in game:
		writer.writerow(move)
	i = 0
	for ag in inferenceHistory:
		writer.writerow(ag)
		w.writerow(ag)
		writer.writerow([ag_score_infered[i]])
		w.writerow([ag_score_infered[i]])
		i += 1
	argsPlayed = []
	for item in range(nb_agents):
		argsPlayed.append([])
	for move in game:
		if(move.__len__() == 3):
			argsPlayed[move[0]].append(argToId[move[1]])
		elif(move.__len__() == 4):
			argsPlayed[move[0]].append(argToId[move[1]])
			argsPlayed[move[0]].append(argToId[move[2]])

	writer.writerow(argsImpactOnFinalOutcome.values())
	writer.writerow(argsImpactOnUniverseProtocol.values())
	writer.writerow(argsImpactOnPartialProtocolH1.values())
	writer.writerow(argsImpactOnPartialProtocolH2.values())
	w.writerow(argsImpactOnFinalOutcome.values())
	w.writerow(argsImpactOnUniverseProtocol.values())
	w.writerow(argsImpactOnPartialProtocolH1.values())
	w.writerow(argsImpactOnPartialProtocolH2.values())
	w.writerow(argsImpactOnFinalOutcome.keys())
	for item in argsPlayed:
		w.writerow(item)
