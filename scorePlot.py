#!/usr/bin/env python
import re
import sys
import matplotlib.pyplot as plt
from scipy import stats
import pandas as pd
import numpy as np

data = []
data2 = []
indexes = []
indexes2 = []
with open(sys.argv[1]) as file_object:
	def predict(x):
		temp = []
		for item in x:
			temp.append(slope * item + intercept)
		return temp
	line = file_object.readline()
	while line:
		temp = re.split(',|\n',line)
		# print(temp)
		indexes.append(float(temp[1]))
		indexes2.append(float(temp[1]))
		data.append(float(temp[0]))
		data2.append(float(temp[0]))
		line = file_object.readline()
		if(data2.__len__()%4 == 0):
			categories = []
			# for item in range(int(data2.__len__()/2)):
			# 	# categories.append(item)
			# 	# categories.append(item)
			# 	categories.append(int(0))
			# 	categories.append(int(1))
			categories = [0,1,2,3]
			# color = np.random.random((int(data.__len__()/2), 4))
			color = np.array(['b','g','r','y'])
			# slope, intercept, r_value, p_value, std_err = stats.linregress(indexes, data)
			plt.figure(figsize=(18,5))
			plt.title(f'{sys.argv[1]}')
			plt.ylabel('mesured var')
			plt.xlabel('interval size')
			# plt.axes().grid()
			plt.scatter(indexes2,data2,20, c=color[categories])
			# fitLine = predict(indexes)
			# plt.plot(indexes, fitLine, c='r')
			# plt.plot(indexes2,indexes2,c='g')
			plt.plot([0,1],[0,1],c='k')
			plt.show()
			data2 = []
			indexes2 = []
	slope, intercept, r_value, p_value, std_err = stats.linregress(data,indexes)
	plt.figure(figsize=(18,5))
	plt.title(f'{sys.argv[1]}')
	plt.xlabel('mesured var')
	plt.ylabel('interval size')
	# plt.axes().grid()
	plt.scatter(data,indexes,10)
	fitLine = predict(data)
	plt.plot(data, fitLine, c='r')
	plt.plot(data,data,c='g')
	plt.show()