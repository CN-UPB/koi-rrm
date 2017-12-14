from __future__ import division
import networkx as nx
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import math, sys, copy, random, os
sys.path.insert(0, os.path.dirname(__file__) + '/../local_allocation')
from ChModel_KoI import *
from localcell import *

class igraph:

	def __init__(self):
		self.G = nx.Graph()
		
	def generate_lra(self, cells, edfm="stream", dc=True):
		
		self.LCs = {}
		self.hall_size = 1000
		#self.int_th = -80
		self.int_dist = 200
		self.EDF_calls = 15
		self.EDF_mode = edfm
		self.dualcalc_mode = dc
		self.min_cellsize = 10
		self.max_cellsize = 30
		self.V = range(0,cells)		
		for v in self.V:
			d = random.randint(self.min_cellsize,self.max_cellsize)
			valid_pos = False
			while valid_pos == False:
				valid_pos = True
				xpos = random.uniform(d,self.hall_size - d)
				ypos = random.uniform(d,self.hall_size - d)
				for w in range(0,v):
					if sqrt(pow(xpos - self.G.node[w]['x'], 2) + pow(ypos - self.G.node[w]['y'], 2)) <= self.G.node[w]['cs'] + d:
						valid_pos = False
						
			self.LCs[v] = LocalCell(num_devices=d,cellsize=d)
			if self.EDF_mode == "stream":
				self.LCs[v].schedule_edf_bf(amount=self.EDF_calls,dualcalc=self.dualcalc_mode)
			elif self.EDF_mode == "packetwise":
				self.LCs[v].schedule_edf_packetwise(amount=self.EDF_calls,dualcalc=self.dualcalc_mode)
			else:
				print "Error: Invalid EDF mode!"
				exit(1)
			self.G.add_node(v, C_pot={}, C_assigned=None, x=xpos, y=ypos, cs=d)
			for i in range(0,len(self.LCs[v].Csets)):
				self.G.node[v]['C_pot'][i] = list(self.LCs[v].Csets[i])
			
		# generate channels
		self.C = range(0,num_channels)
		
		# generate interference edges
		for v in range(0, len(self.V)):
			for w in range(v+1, len(self.V)):
				dist = sqrt(pow(self.G.node[v]['x'] - self.G.node[w]['x'], 2) + pow(self.G.node[v]['y'] - self.G.node[w]['y'], 2))
				#int_val = received_signal_power_db(dist)
				#if int_val >= self.int_th:
				if dist <= self.int_dist:
					self.G.add_edge(v,w)
		# feasibility fix: ILP needs at least one edge
		if len(self.G.edges()) == 0:
			self.G.add_edge(0,1)
		
	def generate_generic(self, cells):
	
		self.V = range(0,cells)
		for v in self.V:
			self.G.add_node(v, C_pot={}, C_assigned=None)
		# generate channels
		self.C = range(0,num_channels)

		f = random.uniform(1,2)
		p = f*log(cells)/cells

		# generate edges			
		for v in range(0, len(self.V)):
			for w in range(v+1, len(self.V)):                                                                                                                                                                                                      
				c=random.random()
				if c < p:
					self.G.add_edge(v,w)	
			
		# generate potential channel sets
		Csets = {}
		for v in self.V:
			ctmp = []
			#number = min(10,int(random.expovariate(0.25)) + 2)
			number = random.randint(10,20)
			load = random.uniform(3,6)
			while len(ctmp) < number:
				#length = min(10, len(self.C), int(random.expovariate(0.25)) + 1)
				length = max(1,int(random.gauss(load,0.5)))
				tmp = random.sample(self.C,length)
				if not tmp in ctmp:
					ctmp.append(tmp)
			for i in range(0,len(ctmp)):
				self.G.node[v]['C_pot'][i] = ctmp[i]
	
	def save_to_file(self, filename):
					
		# new representation of Csets for data output
		Cout = []
		for c in self.V:
			for k in self.G.node[c]['C_pot']:
				S = self.G.node[c]['C_pot'][k]
				for i in S:
					Cout.append((c,k,i))

		# generate output
		fout = open(filename, "w")	
		fout.write("set V := ")
		for v in self.V:
			fout.write(str(v) + " ")
		fout.write(";\n")

		fout.write("set E := ")
		for l in self.G.edges():
			fout.write(str(l).replace(" ","") + " ")
		fout.write(";\n")

		fout.write("set C := ")
		for c in self.C:
			fout.write(str(c) + " ")
		fout.write(";\n")

		fout.write("set C_pot := ")
		for S in Cout: 
			fout.write(str(S).replace(" ","") + " ")
		fout.write(";\n")

		fout.close()
	
	def generate_from_file(self, filename):
		
		# read input file
		try:
			fin = open(filename, "r")
			tmp = fin.readline()
			self.V = [int(n) for n in tmp[tmp.find("=")+2:tmp.find(";")-1].split(" ")]
			if len(self.V) == 0:
				print("Error: Empty network!")
				exit(1)
				
			for v in self.V:
				self.G.add_node(v, C_pot={}, C_assigned=None)

			tmp = fin.readline()
			for n in tmp[tmp.find("=")+2:tmp.find(";")-1].split(" "):
				self.G.add_edge(int(n[n.find("(")+1:n.find(",")]),int(n[n.find(",")+1:n.find(")")]))
			
			tmp = fin.readline()
			self.C = [int(n) for n in tmp[tmp.find("=")+2:tmp.find(";")-1].split(" ")]
			if len(self.C) == 0:
				print("Error: No channels!")
				exit(1)

			# generate back real potential channel sets
			tmp = fin.readline()
			for n in tmp[tmp.find("=")+2:tmp.find(";")-1].split(" "):
				v = int(n[n.find("(")+1:n.find(",")])
				k = int(n[n.find(",")+1:n.rfind(",")])
				i = int(n[n.rfind(",")+1:n.find(")")])
				if not k in self.G.node[v]['C_pot']:
					self.G.node[v]['C_pot'][k] = []
				self.G.node[v]['C_pot'][k].append(i)
					
			return True			
		except:		
			return False
			
	def check_consistency(self):
		for e in self.G.edges():
			a = list(self.G.node[e[0]]['C_assigned'])
			b = list(self.G.node[e[1]]['C_assigned'])
			if len(set(a) & set(b)) > 0:
				return False
		return True
			
		
	def output(self,filename="graph.pdf"):
		loc = {}
		labellist = {}
		for n in self.V:
			loc[n] = (self.G.node[n]['x'],self.G.node[n]['y'])
			labellist[n] = str(n)
		plt.axis('off')
		nx.draw_networkx(self.G,pos=loc,labels=labellist,font_size=8)
		plt.tight_layout()
		plt.savefig(filename)
		plt.close()