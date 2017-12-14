from __future__ import division
import sys
import math
import random
from coloring_greedy import *
import time

filename = 'Test.dat'
cg = ColoringGreedy(filename)

tstart = time.time()
cg.cg()
tend = time.time()

print "State: " + cg.state
if cg.state == "NOT SOLVED":
	print "Remaining nodes: " + str([i for i in cg.ig.V if not i in cg.Scheduled])
print "Channels used: "
total = 0
for v in cg.ig.V:
	if cg.state == "Solved":
		total += len(cg.ig.G.node[v]['C_assigned'])
	print "Cell " + str(v) + ": " + str(cg.ig.G.node[v]['C_assigned'])
if cg.state == "Solved":
	print "Total: " + str(total)
print "Runtime: " + str(tend-tstart)

#print cg.ig.check_consistency()
#cg.ig.output()