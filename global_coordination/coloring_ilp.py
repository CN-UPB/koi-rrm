from __future__ import division 
from coopr.pyomo import *

model = AbstractModel()

############################################################################
# input parameters:

# set of nodes (equaling local cells)
model.V = Set()
# set of conflict links with significant interference
model.E = Set (within=model.V*model.V) 
# set of available wireless channels
model.C = Set() 
# potential channel sets
model.C_pot = Set(dimen=3) 

# indexset for z variables
def I_init(model):
	I = []
	for S in model.C_pot:
		if not (S[0],S[1]) in I:
			I.append((S[0],S[1]))
	return I
model.I = Set(dimen=2, initialize=I_init)

#######################################################################

# decision variables 
model.x = Var(model.V, model.C, within=Binary)
model.z = Var(model.I, within=Binary)
		
################################################################
# objective: minimize overall number of channels used
model.obj = Objective (rule = lambda m: sum(sum(m.x[v,i] for i in m.C) for v in m.V))

###################################################################
# constraints 

## Neighboring nodes must not use the same channel
model.neighbors = Constraint (model.E, model.C, rule = lambda m, v, w, i: m.x[v,i] + m.x[w,i] <= 1)

## potential sets must only be realized if all channels of the list are used by a node
model.setlower = Constraint (model.C_pot, rule = lambda m, v, k, i: m.z[v,k] <= m.x[v,i])

## at least one potential set must be realized by node
model.setmin = Constraint (model.V, rule = lambda m, v: sum(m.z[v,k] for (w,k) in m.I if w == v) >= 1)