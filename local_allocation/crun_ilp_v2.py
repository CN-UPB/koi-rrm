from __future__ import division 
from coopr.pyomo import *
from coopr.opt import *
import sys, os
import time
from lra_ilp_v2 import model

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

filename='Test.dat'
instance = model.create(filename)
tstart = time.time()
results = opt.solve(instance, tee=True)
tend = time.time()
instance.load(results)

if results.solver.termination_condition == TerminationCondition.infeasible:
	print "Instance is infeasible!"
else:
	print " "	
	print "Channels used: "
	total = 0
	out = ""
	for c in instance.C:
		if instance.z[c] == 1:
			total += 1
			out += str(c) + ", "
	print out
	print "Total: " + str(total)
	print "Runtime: " + str(tend-tstart)
	
fout = open('Results_' + filename, "w")
for v in instance.active_components(Var):
	fout.write(str(v) + "\n")
	varobject = getattr(instance, v)
	for index in varobject:
		if varobject[index].value > 0:
			fout.write("   " + str(index) + " " + str(varobject[index].value) + "\n")
	fout.write("\n")
