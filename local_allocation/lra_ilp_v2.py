from __future__ import division 
from coopr.pyomo import *

model = AbstractModel()

############################################################################
# input parameters:

# set of available wireless channels
model.C = Set() 
# set of communication pairs (within the local cell)
model.P = Set()
# Bit matrix
model.B = Param(model.P, model.C, within=NonNegativeIntegers) 
# amount of available time slots (in the considered time frame)
model.Ns = Param()
# size of a time slot
model.Ts = Param()
# packet size
model.ps = Param(model.P)
# arrival periods
model.per = Param(model.P)
# deadline (starting from arrival time)
model.D = Param(model.P)
# amount of packets in time T
model.n = Param(model.P)
# big-M constant
model.bigM = Param()

# Misc that needs to be read in to prevent errors
model.dur = Param(model.P, model.C, within=NonNegativeIntegers)
model.Tx = Param(model.P)
model.Rx = Param(model.P)
model.Tx_type = Param(model.P)
model.Rx_type = Param(model.P)
model.K = Param(model.P, model.C, within=Binary)
model.M = Param(model.P, model.C, within=NonNegativeIntegers)

# index sets for x variables
def I_init(model):
	I = []
	for p in model.P:
		for i in range(1,model.n[p]+1):
			I.append((p,i))
	return I
model.I = Set(dimen=2, initialize=I_init)

def T_init(model):
	T = range(1,model.Ns+1)
	return T
model.T = Set(initialize=T_init)

def J_init(model):
	J = []
	for (p,i) in model.I:
		for c in model.C:
			if model.K[p,c] == 1:
				for k in model.T:
					if (k - 1) * model.Ts >= (i-1) * model.per[p] and k * model.Ts <= (i-1) * model.per[p] + model.D[p]:
						J.append((p,i,c,k))
	return J
model.J = Set(dimen=4, initialize=J_init)

#######################################################################

# decision variables 
model.x = Var(model.J, within=Binary)
model.z = Var(model.C, within=Binary)
		
################################################################
# objective: minimize overall number of channels used
model.obj = Objective (rule = lambda m: sum(m.z[c] for c in m.C))

###################################################################
# constraints 

## Setting z-variables
model.setz = Constraint (model.C, rule = lambda m, c: sum(m.x[p,i,d,k] for (p,i,d,k) in m.J if d == c) <= m.bigM * m.z[c])

## All packets need to be scheduled exactly once
model.schedule = Constraint (model.I, rule = lambda m, p, i: sum(m.x[q,j,c,k] * m.B[q,c] for (q,j,c,k) in m.J if q == p and j == i) >= m.ps[p])

## Eeach time slot must be scheduled at most once per channel
def timeslotHelp (m, c, k):
	cs = [(p,i,d,l) for (p,i,d,l) in m.J if d == c and l == k]
	if len(cs) > 0:
		return sum(m.x[p,i,d,l] for (p,i,d,l) in cs) <= 1
	else:
		return Constraint.Skip
	
model.timeslot = Constraint (model.C, model.T, rule = timeslotHelp)

## A packet must be scheduled between its arrival time and its scheduling duration must end before its deadline is reached.
#model.arrival = Constraint (model.J, rule = lambda m, p, i, c, k: (1 - m.x[p,i,c,k]) * m.bigM + m.x[p,i,c,k] * (k - 1) * m.Ts >= (i-1) * m.per[p])
#model.deadline = Constraint (model.J, rule = lambda m, p, i, c, k: m.x[p,i,c,k] * k * m.Ts <= (i-1) * m.per[p] + m.D[p])