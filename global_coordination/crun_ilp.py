from __future__ import division 
from coopr.pyomo import *
from coopr.opt import *
import sys, os
import time
from coloring_ilp import model

solver = 'gurobi'
solver_io = 'python'
stream_solver = True

opt = SolverFactory(solver,solver_io=solver_io)
opt.options['MIPGap'] = 0.0
opt.options['Threads'] = 1
opt.options['timelimit'] = 60
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

# fout = open('Results_' + filename, "w")
# for v in instance.active_components(Var):
	# fout.write(str(v) + "\n")
	# varobject = getattr(instance, v)
	# for index in varobject:
		# if varobject[index].value > 0:
			# fout.write("   " + str(index) + " " + str(varobject[index].value) + "\n")
	# fout.write("\n")
	
if results.solver.termination_condition == TerminationCondition.infeasible:
	print "Instance is infeasible!"
else:
	print " "	
	print "Channels used: "
	total = 0
	for v in instance.V:
		out = "Cell " + str(v) + ": "
		for i in instance.C:
			if instance.x[v,i] == 1:
				total += 1
				out += str(i) + ", "
		print out
	print "Total: " + str(total)
	print "Runtime: " + str(tend-tstart)
