#!/bin/bash
# This script will create graphs and run our solver to get the execution times
# Accepts parameters to configure the graph generation
# Usage:        $./bench.sh

for ((j = 1; 5 - $j; j++)); do
now=$(date +"%Y-%m-%d_%X")

	mkdir test4_${now}
	python3 ./debategraph_generation.py -p ./test4_${now}
	for ((i = 1; 11 - $i; i++)); do
		python3 ./Protocol.py ./test4_${now}/ ${i} > ./test4_${now}/run_${i}.txt
		./bench.py ./test4_${now}/bench${i}.csv
	done
done
