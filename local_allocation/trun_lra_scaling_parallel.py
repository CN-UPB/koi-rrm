from __future__ import division
from time import *
from math import *
#from localcell import *
import sys, random, os
from subprocess import Popen, list2cmdline

def exec_commands(cmds,max_task):
	if not cmds: return # empty list

	def done(p):
		return p.poll() is not None
	def success(p):
		return p.returncode == 0
	def fail():
		sys.exit(1)

	processes = []
	while True:
		while cmds and len(processes) < max_task:
			task = cmds.pop(0)
			print list2cmdline(task)
			processes.append(Popen(task))

		for p in processes:
			if done(p):
				if success(p):
					processes.remove(p)
				#else:
					#fail()

		if not processes and not cmds:
			break
		else:
			sleep(0.05)

# bash input
num_task = int(sys.argv[1])
		
scaling_factors = [1,2,4,5,8]
inst_per_sf = 50
schedulings = 10
num_devices = range(5,61,5)

fout = open("Scaling_results/packetwise.dat","w")
fout.write("scaling devices successes attempts channels bandwidth runtime \n")
fout.close()
fout = open("Scaling_results/stream.dat","w")
fout.write("scaling devices successes attempts channels bandwidth runtime \n")
fout.close()

commands = []

for sf in scaling_factors:	
	for n in num_devices:
		for i in range(0,inst_per_sf):
			commands.append(['python','trun_lra_scaling_single.py',str(sf),str(n)])
			
exec_commands(commands,num_task)