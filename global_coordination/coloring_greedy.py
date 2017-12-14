from __future__ import division
import networkx as nx
import sys, math, random, time, copy
from igraph import *
import pdb
#pdb.set_trace()

class ColoringGreedy:

	def __init__(self, filename=None, lra=False, cells=25):		
		self.ig = igraph()
		if filename is None:
			if lra == False:
				print "Error: Set either filename or lra!"
				exit(1)
			else:
				self.ig.generate_lra(cells)
				self.state = "NOT SOLVED"
		else:
			valid_igraph = self.ig.generate_from_file(filename)
			if valid_igraph:
				self.state = "NOT SOLVED"
			else:
				print "Error: Invalid interference graph!"
				exit(1)
		self.Scheduled = []
		self.option = "neighbors2"
		self.obj = 0

	def cg(self):					
		while len(self.Scheduled) < len(self.ig.V):
			tmp = self.scheduleNextNode(self.option)
			if len(self.Scheduled) == len(self.ig.V):
				self.state = "Solved"
				self.obj = sum(len(self.ig.G.node[v]['C_assigned']) for v in self.ig.V)
				break
			if not tmp:
				break
			
	def scheduleNextNode(self,option):
		candidates = list(set(self.ig.V) - set(self.Scheduled))
		
		if option == "neighbors":
			ctmp = [(k,len(set(self.ig.G.neighbors(k)) - set(self.Scheduled))) for k in candidates]
			ctmp.sort(key=lambda x: x[1], reverse=True)
			c = ctmp[0][0] 
			cpot = [self.ig.G.node[c]['C_pot'][k] for k in self.ig.G.node[c]['C_pot']]
			cpot.sort(key=len)
			for l in cpot:
				iflag = False
				for w in set(self.ig.G.neighbors(c)) & set(self.Scheduled):
					if len(set(l) & set(self.ig.G.node[w]['C_assigned'])) > 0:
						iflag = True
						break
				if not iflag:
					self.ig.G.node[c]['C_assigned'] = l
					self.Scheduled.append(c)
					return True
			if iflag:
				return False
				
		elif option == "sets":	
			ctmp = [(k,len(self.ig.G.node[k]['C_pot'])) for k in candidates]
			ctmp.sort(key=lambda x: x[1])
			c = ctmp[0][0] 
			cpot = [self.ig.G.node[c]['C_pot'][k] for k in self.ig.G.node[c]['C_pot']]
			cpot.sort(key=len)
			for l in cpot:
				iflag = False
				for w in list(set(self.ig.G.neighbors(c)) & set(self.Scheduled)):
					if len(set(l) & set(self.ig.G.node[w]['C_assigned'])) > 0:
						iflag = True
						break
				if not iflag:
					self.ig.G.node[c]['C_assigned'] = l
					self.Scheduled.append(c)
					return True
			if iflag:
				return False
				
		elif option == "neighbors2":
			ctmp = [(k,len(set(self.ig.G.neighbors(k)) - set(self.Scheduled)),len(self.ig.G.node[k]['C_pot'])) for k in candidates]
			ctmp.sort(key=lambda x: x[2])
			ctmp.sort(key=lambda x: x[1], reverse=True)
			c = ctmp[0][0] 
			cpot = [self.ig.G.node[c]['C_pot'][k] for k in self.ig.G.node[c]['C_pot']]
			cpot.sort(key=len)
			c_good = []
			for l in cpot:
				iflag = False
				for w in set(self.ig.G.neighbors(c)) & set(self.Scheduled):
					if len(set(l) & set(self.ig.G.node[w]['C_assigned'])) > 0:
						iflag = True
						break
				if not iflag:
					max_min = len(self.ig.C)+1
					total_dis = 0
					for w in set(self.ig.G.neighbors(c)) - set(self.Scheduled):
						tmp_dis = 0
						for k in self.ig.G.node[w]['C_pot']:
							if len(set(self.ig.G.node[w]['C_pot'][k]) & set(l)) == 0:
								tmp_dis +=1
						total_dis += tmp_dis
						max_min = min(max_min, tmp_dis)
					c_good.append((l,max_min,total_dis))
			if len(c_good) == 0:
				return False
			else: 
				c_good.sort(key=lambda x: x[2], reverse=True)
				c_good.sort(key=lambda x: x[1], reverse=True)
				self.ig.G.node[c]['C_assigned'] = c_good[0][0]
				self.Scheduled.append(c)
				return True	