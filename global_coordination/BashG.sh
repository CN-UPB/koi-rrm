#!/bin/bash

test=6
k=20

for i in {0..4}
do
  for j in {1..20}
  do
    dim=$(( 5 * $i + 10 ))
	number=$(( $k * $i + $j ))
    buff=`echo "python Generator_col.py "$dim" Instances/Test_"$test"/Network_"$number".dat lra"`
    $buff
  done
done
