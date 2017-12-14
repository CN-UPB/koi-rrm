from __future__ import division 
from coopr.pyomo import *
from coopr.opt import *
import sys, os
import time
from lra_ilp import model
from localcell import *

solver = 'gurobi'
solver_io = 'python'
stream_solver = True

opt = SolverFactory(solver,solver_io=solver_io)
opt.options['MIPGap'] = 0.0
opt.options['Threads'] = 1
opt.options['timelimit'] = 36000
opt.options['PSDTol'] = 0.0

if opt is None:
	print("")
	print("ERROR: Unable to create solver plugin for %s "\
		"using the %s interface" % (solver, solver_io))
	print("")
	exit(1)

test = 3
no_instances = 150

for network in range(1, no_instances + 1):
	filename='Instances/Test_' + str(test) + '/LC_' + str(network) + '.dat'
	
	instance = model.create(filename)
	tstart1 = time.time()
	results = opt.solve(instance)#, tee=True)
	tend1 = time.time()
	rtime1 = tend1 - tstart1
	
	if results.solver.termination_condition == TerminationCondition.infeasible:
		print "Network " + str(network) + " is infeasible!"
		fout = open('Instances/Test_' + str(test) + '/_Results.dat', "a")
		fout.write(str(network) + " 0 0 0 0 0 0\n")
		fout.close()
	else: 
		instance.load(results)
		total1 = 0
		for c in instance.C:
			if instance.z[c] == 1:
				total1 += 1
		print "ILP done for local cell " + str(network)
		print "Total: " + str(total1) + ", Runtime: " + str(rtime1)
		
		lc = LocalCell(filename=filename)
		tstart2 = time.time()
		lc.schedule_edf_bf()
		tend2 = time.time()
		rtime2 = tend2 - tstart2
		total2 = lc.scheduling['num_ch']
		
		print "EDF stream scheduling done for local cell " + str(network)
		print "Total: " + str(total2) + ", Runtime: " + str(rtime2)
		
		lc.Csets = []
		tstart3 = time.time()
		lc.schedule_edf_packetwise()
		tend3 = time.time()
		rtime3 = tend3 - tstart3
		total3 = lc.scheduling['num_ch']
		
		print "EDF packetwise scheduling done for local cell " + str(network)
		print "Total: " + str(total3) + ", Runtime: " + str(rtime3)
					
		fout = open('Instances/Test_' + str(test) + '/_Results.dat', "a")
		fout.write(str(network) + " " + str(total1) + " " + str(rtime1) + " " + str(total2) + " " + str(rtime2) + " " + str(total3) + " " + str(rtime3) + "\n")
		fout.close()