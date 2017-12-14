from __future__ import division 
from coopr.pyomo import *
from coopr.opt import *
from coopr.opt.parallel import SolverManagerFactory
import sys, os, math, random, time
from coloring import model
from coloring_greedy import *

solver = 'gurobi'
solver_io = 'python'
stream_solver = True

opt = SolverFactory(solver,solver_io=solver_io)
opt.options['MIPGap'] = 0.0
opt.options['Threads'] = 1
opt.options['timelimit'] = 3600
opt.options['PSDTol'] = 0.0

if opt is None:
	print("")
	print("ERROR: Unable to create solver plugin for %s "\
		"using the %s interface" % (solver, solver_io))
	print("")
	exit(1)
	
test = 11
no_instances = 250

for network in range(1, no_instances + 1):
	filename='Instances/Test_' + str(test) + '/Network_' + str(network) + '.dat'
	
	instance = model.create(filename)
	tstart1 = time.time()
	results = opt.solve(instance)#, tee=True)
	tend1 = time.time()
	rtime1 = tend1 - tstart1
	
	if results.solver.termination_condition == TerminationCondition.infeasible:
		print "Network " + str(network) + " is infeasible!"
		fout = open('Instances/Test_' + str(test) + '/_Results.dat', "a")
		fout.write(str(network) + " 0 0 0 0\n")
		fout.close()
	else: 
		instance.load(results)
		total1 = 0
		for v in instance.V:
			for i in instance.C:
				if instance.x[v,i] == 1:
					total1 += 1
		print "ILP done for network " + str(network)
		print "Total: " + str(total1) + ", Runtime: " + str(rtime1)
		
		cg = ColoringGreedy(filename)
		tstart2 = time.time()
		cg.cg()
		tend2 = time.time()
		rtime2 = tend2 - tstart2
		total2 = cg.obj
		
		print "Greedy done for network " + str(network)
		print "Total: " + str(total2) + ", Runtime: " + str(rtime2)
					
		fout = open('Instances/Test_' + str(test) + '/_Results.dat', "a")
		fout.write(str(network) + " " + str(total1) + " " + str(rtime1) + " " + str(total2) + " " + str(rtime2) + "\n")
		fout.close()



