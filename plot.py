#!/usr/bin/env python
import re
import sys
import matplotlib.pyplot as plt
from scipy import stats
import pandas as pd

data = []
indexes = []
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
		data.append(float(temp[0]))
		line = file_object.readline()
	# indexes = pd.DataFrame(indexes)
	# data = pd.DataFrame(data)
	slope, intercept, r_value, p_value, std_err = stats.linregress(indexes, data)
	plt.figure(figsize=(18,5))
	plt.title(f'{sys.argv[1]}')
	plt.ylabel('mesured var')
	plt.xlabel('interval size')
	# plt.axes().grid()
	plt.scatter(indexes,data,10)
	fitLine = predict(indexes)
	plt.plot(indexes, fitLine, c='r')
	# plt.plot(data,data,c='k')
	plt.show()
	slope, intercept, r_value, p_value, std_err = stats.linregress(data,indexes)
	plt.figure(figsize=(18,5))
	plt.title(f'{sys.argv[1]}')
	plt.xlabel('mesured var')
	plt.ylabel('interval size')
	# plt.axes().grid()
	plt.scatter(data,indexes,10)
	fitLine = predict(data)
	plt.plot(data, fitLine, c='r')
	# plt.plot(data,data,c='k')
	plt.show()