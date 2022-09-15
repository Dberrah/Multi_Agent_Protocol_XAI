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
	# nbArgs=$((75 * $i))
	# mkdir test_R-CDisc_${now}/tests_${nbArgs}args
	# for ((j = 0; 50 - $j; j++)); do
		# java -cp ./AFGen.jar net.sf.jAFBenchGen.jAFBenchGen.Generator -numargs $nbArgs -type ErdosRenyi -ER_probAttacks 0.9 >test_R-CDisc_${now}/tests_${nbArgs}args/graph$j.apx
		# { time java -cp ./target/solver-1.0-SNAPSHOT.jar com.bf.solver.App -p R-CDisc -f test_R-CDisc_${now}/tests_${nbArgs}args/graph$j.apx -fo apx >test_R-CDisc_${now}/tests_${nbArgs}args/results_graph$j.txt 2>stderr; } 2>>test_R-CDisc_${now}/benchtime.txt
	# done
# rm stderr
# ./bench.py test_R-CDisc_${now}/benchtime.txt CDiscussion_Based_ErdosRenyi_0.9 CDiscussion_Based_ErdosRenyi_9