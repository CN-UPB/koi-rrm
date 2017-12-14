from __future__ import division
import networkx as nx
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ChModel_KoI import *
import sys, copy, random, time
from math import *
import pdb
#pdb.set_trace()

class Pair:
	def __init__(self, name, tx, rx, tx_type, rx_type, ps, per, dl):
		self.name = name
		self.Tx = tx
		self.Rx = rx
		self.Tx_type = tx_type
		self.Rx_type = rx_type
		self.ps = ps
		self.per = per # milliseconds
		self.dl = dl # milliseconds
		self.dur = []
		self.n = 0
		self.K = []
		self.Ksum = 0
		self.M = []
		self.Msum = 0
		self.B = []
		self.Bsum = 0
	def __repr__(self):
		return str(self.name)
	def __str__(self):
		return str(self.name)
	def output(self):
		out = "Pair: " + str(self.name) + ", (" + str(self.Tx) + "," + str(self.Rx) + "), ps: " + str(self.ps) + ", per: " + str(self.per)
		out += ", DL: " + str(self.dl) + ", Ksum: " + str(self.Ksum) + ", Msum: " + str(self.Msum) + ", Bsum: " + str(self.Bsum)
		return out
	
class Channel:
	def __init__(self, name):
		self.name = name
		self.Ksum = 0
	def __repr__(self):
		return str(self.name)
	def __str__(self):
		return str(self.name)
		
def gcd(a, b):
    while b:      
        a, b = b, a % b
    return a

def lcms(a, b):
    return a * b // gcd(a, b)

def lcm(l):
    return reduce(lcms, l)
	

class LocalCell:

	def __init__(self, num_devices=None, cellsize=None, d2d=False, filename=None, scaling_factor=5):
		self.G = nx.DiGraph()
		self.cm = ChModel(sf=scaling_factor)
		self.scheduling = None
		self.Csets = []
		self.d2d_mode = d2d
		self.p_d2d = 0.5
		self.periods = [1,2,3,4,6,8] # milliseconds
		self.default_packetsize = 1000 # bits
		self.static_ps = True
		self.non_schedulable_pairs = 0
		self.num_devices = num_devices
		self.cs = cellsize
		self.monitoring = False
			
		if filename is None:
			if num_devices is None or cellsize is None:
				print "Error: amount of devices and cell size required!"
				exit(1)
			self.generate_cell()
		else:
			self.generate_from_file(filename)
	
	def generate_cell(self):
	
		# add LRC first
		self.G.add_node(0, isLRC=True, d2d=False, x=self.cs/2, y=self.cs/2)
				
		for i in range(1,self.num_devices+1):
			xpos = random.uniform(0,self.cs)
			ypos = random.uniform(0,self.cs)
			c=random.random()
			if c < self.p_d2d:
				self.G.add_node(i, isLRC=False, d2d=True, x=xpos, y=ypos)
			else: 
				self.G.add_node(i, isLRC=False, d2d=False, x=xpos, y=ypos)
			dist = sqrt(pow(xpos - self.cs/2, 2) + pow(ypos - self.cs/2, 2))
			ps,per,dl = self.get_traffic_characteristics(static_ps=self.static_ps)
			self.G.add_edge(0, i, Tx_type="LRC", Rx_type="device", packetsize=ps, period=per, deadline=dl, distance=dist)
			ps,per,dl = self.get_traffic_characteristics(static_ps=self.static_ps)
			self.G.add_edge(i, 0, Tx_type="device", Rx_type="LRC", packetsize=ps, period=per, deadline=dl, distance=dist)
			
		if self.d2d_mode == True:
			for i in range(1,self.num_devices + 1):
				for j in range(i+1,self.num_devices + 1):
					dist = sqrt(pow(self.G.node[i]['x'] - self.G.node[j]['x'], 2) + pow(self.G.node[i]['y'] - self.G.node[j]['y'], 2))
					if dist <= 5 and self.G.node[i]['d2d'] and self.G.node[j]['d2d']:
						ps,per,dl = self.get_traffic_characteristics()
						self.G.add_edge(i, j, Tx_type="device", Rx_type="device", packetsize=ps, period=per, deadline=dl, distance=dist)
						ps,per,dl = self.get_traffic_characteristics()
						self.G.add_edge(j, i, Tx_type="device", Rx_type="device", packetsize=ps, period=per, deadline=dl, distance=dist)
		
		# generate channels
		self.num_channels = self.cm.num_channels
		self.C = []
		for i in range(0,self.num_channels):
			ch = Channel(name=i)
			self.C.append(ch)
		
		# generate LCM and number of time slots in major cycle
		a = list(set([e[2]['period'] for e in self.G.edges(data=True)]))
		T = lcm(a)
		self.Ts = self.cm.TTI_length*1000 # from seconds to milliseconds
		self.Ns = int(T / self.Ts)
			
		# generate Pairs
		self.P = []
		shadowing = {}
		channel_gain = {}
		self.num_pairs = 0
		mt=[0,0,0,0,0,0,0,0,0] # just for monitoring
		for e in self.G.edges(data=True):
			#sys.stdout.write('.')
			dist = sqrt(pow(self.G.node[e[0]]['x'] - self.G.node[e[1]]['x'], 2) + pow(self.G.node[e[0]]['y'] - self.G.node[e[1]]['y'], 2))
			if (e[1],e[0]) in shadowing:
				shad = shadowing[(e[1],e[0])]
				chg = channel_gain[(e[1],e[0])]
			else:
				shad = self.cm.shadowing_db()
				chg = self.cm.get_chgain(dist,e[2]['Tx_type'],e[2]['Rx_type'])
				# Feasibility-fix: retrieve chGain with a least one non-deep fading channel
				# while True:
					# chg = get_chgain(dist,e[2]['Tx_type'],e[2]['Rx_type'])
					# if len([i for i in chg if i >= 1]) > 0:
						# break
				shadowing[(e[0],e[1])] = shad
				channel_gain[(e[0],e[1])] = chg
			sl = self.cm.sinr_list(dist,e[2]['Tx_type'],e[2]['Rx_type'],shad,chg)
			
			p = Pair(self.num_pairs, e[0], e[1], e[2]['Tx_type'], e[2]['Rx_type'], e[2]['packetsize'], e[2]['period'], e[2]['deadline'])	
			
			for ch in self.C:
				mcs = self.cm.get_mcs(sl[ch.name],p.Tx_type,p.Rx_type)
				if mcs > 0:
					p.K.append(1)
				else:
					p.K.append(0)
				p.M.append(mcs)
				p.B.append(self.cm.get_bits_per_slot(mcs))
				p.dur.append(self.cm.get_duration(p.ps,mcs))
				mt[mcs] +=1 # just for monitoring

			p.n = int(T/p.per)
			p.Ksum = sum(i for i in p.K)
			#if p.Ksum == 0:
				#print "Warning: No available channel for Pair " + str(p.name) + "!"
			p.Msum = sum(i for i in p.M)
			p.Bsum = sum(i for i in p.B)
				
			self.P.append(p)
			self.num_pairs += 1
		
		for ch in self.C:
			ch.Ksum = sum(p.K[ch.name] for p in self.P) 
		
		# monitoring
		if self.monitoring == True:
			print "MCS distribution: " + str(mt)	
			Knone = [p for p in self.P if p.Ksum == 0]
			self.non_schedulable_pairs = len(Knone)
			if len(Knone) > 0:
				print "Feasibility warning: " + str(len(Knone)) + " out of " + str(self.num_pairs) + " pairs have no channels available!"
			Kfew = [p for p in self.P if p.Ksum < self.num_channels/10]
			if len(Knone) > 0:
				print "Feasibility warning 2: " + str(len(Kfew)) + " out of " + str(self.num_pairs) + " pairs have less than 10% of all channels available!"
			Kall = [p for p in self.P if p.Ksum == self.num_channels]
			if len(Kall) > 0:
				print "Triviality warning: " + str(len(Kall)) + " out of " + str(self.num_pairs) + " pairs have all channels available!"
			Mall = [p for p in self.P if len([i for i in p.M if i == 8]) == self.num_channels]
			if len(Mall) > 0:
				print "Triviality warning 2: " + str(len(Mall)) + " out of " + str(self.num_pairs) + " pairs have best MCS for all channels available!"
			
		# temporary feasibility fix
		#for p in self.P:
			#if p.Ksum == 0:
				#p.K = [random.choice([0,1]) for c in self.C]
				
					
	def generate_from_file(self, filename):
		
		# read input file
		try:
			fin = open(filename, "r")
			tmp = fin.readline()
			self.C = [Channel(name=int(n)) for n in tmp[tmp.find("=")+2:tmp.find(";")-1].split(" ")]
			if len(self.C) == 0:
				print("Error: No channels!")
				exit(1)
			self.num_channels = len(self.C)
				
			tmp = fin.readline()
			Pairs = [int(n) for n in tmp[tmp.find("=")+2:tmp.find(";")-1].split(" ")]
			if len(Pairs) == 0:
				print("Error: No pairs!")
				exit(1)
			self.num_pairs = len(Pairs)
				
			tmp = fin.readline()
			self.Ns = int(tmp[tmp.find("=")+2:tmp.find(";")])
			tmp = fin.readline()
			self.Ts = float(tmp[tmp.find("=")+2:tmp.find(";")])
			tmp = fin.readline()
			tmp = fin.readline()

			# generate back pairs
			self.P = []
			self.num_devices = 0
			for i in range(0, self.num_pairs):
				tmp = fin.readline().split(" ")
				Tx = int(tmp[5])
				Rx = int(tmp[6])
				p = Pair(int(tmp[0]), Tx, Rx, code_type[int(tmp[7])], code_type[int(tmp[8])], int(tmp[4]), int(tmp[1]), int(tmp[2]))
				p.n = int(tmp[3])
				self.P.append(p)
				
				# generate back graph
				if not Tx in self.G.nodes():
					if p.Tx_type == "LRC":
						self.G.add_node(Tx, isLRC=True)
					else: 
						self.G.add_node(Tx, isLRC=False)
						self.num_devices += 1
				if not Rx in self.G.nodes():
					if p.Rx_type == "LRC":
						self.G.add_node(Rx, isLRC=True)
					else: 
						self.G.add_node(Rx, isLRC=False)
						self.num_devices += 1
				self.G.add_edge(Tx, Rx, Tx_type=p.Tx_type, Rx_type=p.Rx_type, packetsize=p.ps, period=p.per, deadline=p.dl)
			
			# generate back durations
			tmp = fin.readline()
			tmp = fin.readline()
			for p in self.P:
				for j in range(0, self.num_channels):
					tmp = fin.readline().split(" ")
					p.dur.append(int(tmp[2]))
				
			# generate back K matrix and channel Ksums
			tmp = fin.readline()
			tmp = fin.readline()
			for p in self.P:
				for j in range(0, self.num_channels):
					tmp = fin.readline().split(" ")
					p.K.append(int(tmp[2]))
					if int(tmp[2]) == 1:
						self.C[j].Ksum += 1
				p.Ksum = sum(i for i in p.K)
				
			Knone = [p for p in self.P if p.Ksum == 0]
			self.non_schedulable_pairs = len(Knone)
			
			# generate back M matrix
			tmp = fin.readline()
			tmp = fin.readline()
			for p in self.P:
				for j in range(0, self.num_channels):
					tmp = fin.readline().split(" ")
					p.M.append(int(tmp[2]))
				p.Msum = sum(i for i in p.M)
			
			# generate back B matrix
			tmp = fin.readline()
			tmp = fin.readline()
			for p in self.P:
				for j in range(0, self.num_channels):
					tmp = fin.readline().split(" ")
					p.B.append(int(tmp[2]))
				p.Bsum = sum(i for i in p.B)

			return True			
		except:		
			print "Error: generating local cell from " + filename + " failed!"
			return False
		
	def get_traffic_characteristics(self,static_ps=True):
		if static_ps:
			ps = self.default_packetsize
		else:
			ps = random.randint(1,10) * 100 # 100 - 1000 bits
		per = random.choice(self.periods) # milliseconds
		dl = random.randint(1,per) # milliseconds
		
		return [ps,per,dl]
		
	def util_edf(self,plist,c):
		return sum(p.dur[c.name]*self.Ts/min(p.dl, p.per) for p in plist)
		
	def test_edf(self,plist,c):
		util = self.util_edf(plist,c)
		if util > 1:
			return False
		#plist.sort(key=lambda p: p.dl)
		#for i in range(0,len(plist)):
			# bt = (max([p.dur[c.name] for p in plist[:i+1]]) * self.Ts) - self.Ts
			# util = self.util_edf(plist[:i+1],c) + bt/min(plist[i].dl, plist[i].per)
			# if util > 1:
				# return False
		
		return True
		
	def schedule_edf_bf(self, amount=1, dualcalc=False, allchans=False):
		if dualcalc:	
			endrange = 2*amount
		else:
			endrange = amount
		for scheds in range(0, endrange):
			self.scheduling = {}
			self.scheduling['mode'] = "edf_bf"
			self.scheduling['type'] = "stream"
			self.scheduling['ch_used'] = []
			self.scheduling['success'] = True
			for c in self.C:
				self.scheduling[c.name] = {}
				self.scheduling[c.name]['pairs'] = []
				self.scheduling[c.name]['util'] = 0
			
			if len(self.Csets) == 0 or allchans == True:
				C_used = list(self.C)
			elif len(self.Csets) < amount: 
				tsl = random.randint(1,int(len(self.C)/2))
				tmpban = random.sample(self.C,tsl)
				C_used = list(set(self.C) - set(tmpban))
			else: 
				C_used = list(set(self.C) - set(self.Csets[scheds-amount]))
			
			random.shuffle(C_used)
			C_used.sort(key=lambda c: c.Ksum, reverse=True)
			
			to_schedule = list(self.P)
			to_schedule.sort(key=lambda p: sum(p.K[c.name] for c in C_used))
			
			while len(to_schedule) > 0:
				#pdb.set_trace()
				tmp = len(to_schedule)
				p = to_schedule[0]
				Kp = [c for c in C_used if p.K[c.name] == 1]
				#Kp.sort(key=lambda c: sum(q.K[c.name] for q in to_schedule), reverse=True)
				#Kp.sort(key=lambda c: c.Ksum, reverse=True)
				Kp.sort(key=lambda c: p.M[c.name], reverse=True)
				Kp.sort(key=lambda c: self.scheduling[c.name]['util'], reverse=True)
				for c in Kp:
					plist = list(self.scheduling[c.name]['pairs'] + [p])
					if self.test_edf(plist,c) == True:
						self.scheduling[c.name]['pairs'].append(p)
						self.scheduling[c.name]['util'] = self.util_edf(plist,c)
						to_schedule.remove(p)
						if not c in self.scheduling['ch_used']:
							self.scheduling['ch_used'].append(c)
						break
				if tmp == len(to_schedule):
					self.scheduling['success'] = False
					break
			if self.scheduling['success'] == True:
				self.scheduling['num_ch'] = len(self.scheduling['ch_used'])		
				self.Csets.append([c.name for c in self.scheduling['ch_used']])
			else: 
				self.scheduling['ch_used'] = []
				self.scheduling['num_ch'] = 0
				print "EDF scheduling attempt unsuccessful."
		
	def schedule_edf_packetwise(self, amount=1, dualcalc=False, allchans=False):
		if dualcalc:	
			endrange = 2*amount
		else:
			endrange = amount
		for scheds in range(0, endrange):
			self.scheduling = {}
			self.scheduling['mode'] = "edf_pw"
			self.scheduling['type'] = "packetwise"
			self.scheduling['ch_used'] = []
			self.scheduling['success'] = True
			for c in self.C:
				self.scheduling[c.name] = {}
				self.scheduling[c.name]['used'] = [0 for k in range(0,self.Ns)]
				self.scheduling[c.name]['sched'] = [0 for k in range(0,self.Ns)]
				self.scheduling[c.name]['util'] = 0
	
			if len(self.Csets) == 0 or allchans == True:
				C_used = list(self.C)
			elif len(self.Csets) < amount: 
				tsl = random.randint(1,int(len(self.C)/2))
				tmpban = random.sample(self.C,tsl)
				C_used = list(set(self.C) - set(tmpban))
			else: 
				C_used = list(set(self.C) - set(self.Csets[scheds-amount]))
				
			random.shuffle(C_used)
			C_used.sort(key=lambda c: c.Ksum, reverse=True)
			
			to_schedule = []
			for p in self.P:
				for i in range(0,p.n):
					to_schedule.append((p,i,i*p.per,i*p.per+p.dl))
			to_schedule.sort(key=lambda ts: sum(ts[0].K[c.name] for c in C_used))
			to_schedule.sort(key=lambda ts: ts[3])

			while len(to_schedule) > 0:
				ts = to_schedule[0]
				suitable_timeslots = range(int(ts[2]/self.Ts),int(ts[3]/self.Ts))
				Kp_cand = [c for c in C_used if ts[0].K[c.name] == 1]
				rel_util = {}
				for c in Kp_cand:
					rel_util[c.name] = sum(self.scheduling[c.name]['used'][k] for k in suitable_timeslots) 
				Kp = [c for c in Kp_cand if rel_util[c.name] < len(suitable_timeslots)]
				#Kp.sort(key=lambda c: sum(q[0].K[c.name] for q in to_schedule), reverse=True)
				Kp.sort(key=lambda c: p.M[c.name], reverse=True)
				Kp.sort(key=lambda c: rel_util[c.name], reverse=True)
				
				bits_scheduled = 0
				for c in Kp:
					for j in suitable_timeslots:
						if self.scheduling[c.name]['used'][j] == 0:
							self.scheduling[c.name]['used'][j] = 1
							self.scheduling[c.name]['sched'][j] = (ts[0],ts[1])
							self.scheduling[c.name]['util'] += 1/self.Ns
							if not c in self.scheduling['ch_used']:
								self.scheduling['ch_used'].append(c)
							bits_scheduled += ts[0].B[c.name]
						if bits_scheduled >= ts[0].ps:
							break
					if bits_scheduled >= ts[0].ps:
						break
				if bits_scheduled >= ts[0].ps:			
					to_schedule.remove(ts)
				else:
					self.scheduling['success'] = False
					break

			if self.scheduling['success'] == True:
				self.scheduling['num_ch'] = len(self.scheduling['ch_used'])		
				self.Csets.append([c.name for c in self.scheduling['ch_used']])
			else: 
				self.scheduling['ch_used'] = []
				self.scheduling['num_ch'] = 0
				print "EDF scheduling attempt unsuccessful."
				
	def extent_stream_to_packetwise(self):
		if not self.scheduling['type'] == "stream":
			print "Error: Stream type scheduling required for extending to packetwise!"
			return False
			
		for c in self.scheduling['ch_used']:
			self.scheduling[c.name]['used'] = [0 for k in range(0,self.Ns)]
			self.scheduling[c.name]['sched'] = [0 for k in range(0,self.Ns)]
			self.scheduling[c.name]['util'] = 0
			
			to_schedule = []
			for p in self.scheduling[c.name]['pairs']:
				for i in range(0,p.n):
					to_schedule.append((p,i,i*p.per,i*p.per+p.dl))
			to_schedule.sort(key=lambda ts: ts[3])
			
			while len(to_schedule) > 0:
				ts = to_schedule[0]
				suitable_timeslots = range(int(ts[2]/self.Ts),int(ts[3]/self.Ts))

				bits_scheduled = 0
				for j in suitable_timeslots:
					if self.scheduling[c.name]['used'][j] == 0:
						self.scheduling[c.name]['used'][j] = 1
						self.scheduling[c.name]['sched'][j] = (ts[0],ts[1])
						self.scheduling[c.name]['util'] += 1/self.Ns
						bits_scheduled += ts[0].B[c.name]
					if bits_scheduled >= ts[0].ps:
						break
				if bits_scheduled >= ts[0].ps:			
					to_schedule.remove(ts)
				else:
					#pdb.set_trace()
					self.scheduling['success'] = False
					print "Critical Error: Extending to packetwise scheduling failed due to insufficient capacity!"
					return False
		
		#print "Successfully extended stream scheduling to packetwise scheduling."
		return True
	
	def validate_scheduling(self):
		if not (self.scheduling['type'] == "stream" or self.scheduling['type'] == "packetwise"):
			print "Error: Scheduling type not supported by validation."
			return False
	
		if self.scheduling['type'] == "stream":
			self.extent_stream_to_packetwise()
		
		Bcheck = {}
		for p in self.P:
			for i in range(0,p.n):
				Bcheck[(p,i)] = p.ps
				
		for c in self.scheduling['ch_used']:
			for j in range(0,len(self.scheduling[c.name]['sched'])):
				if self.scheduling[c.name]['sched'][j] <> 0:
					s = self.scheduling[c.name]['sched'][j]
					p = s[0]
					i = s[1]
					Bcheck[(p,i)] -= p.B[c.name]
					if i*p.per > j*self.Ts:
						print "Scheduling validation failed: " + str(i) + "-th packet of stream " + str(p) + " scheduled prior to arrival!"
						return False
					if i*p.per + p.dl < (j+1)*self.Ts:
						print "Scheduling validation failed: " + str(i) + "-th packet of stream " + str(p) + " scheduled after deadline!"
						return False
			
		for x in Bcheck:
			if Bcheck[x] > 0:
				print "Scheduling validation failed: " + str(x[1]) + "-th packet of stream " + str(x[0]) + "not fully scheduled!"
				return False
		
		#print "Scheduling validation succeeded!"
		return True
		
	def save_to_file(self,instance):
		fout = open(instance, "w")	

		fout.write("set C := ")
		for c in self.C:
			fout.write(str(c.name) + " ")
		fout.write(";\n")

		fout.write("set P := ")
		for p in self.P:
			fout.write(str(p.name) + " ")
		fout.write(";\n")

		fout.write("param : Ns := "+ str(self.Ns) + ";\n")
		fout.write("param : Ts := "+ str(self.Ts) + ";\n") 
		fout.write("param : bigM := 1e6;\n")

		fout.write("param : per D n ps Tx Rx Tx_type Rx_type :=\n") # Tx_xpos Tx_ypos Rx_xpos Rx_ypos
		for p in self.P:
			fout.write(str(p.name) + " " + str(p.per) + " " + str(p.dl) + " " + str(p.n) + " " + str(p.ps) + " ")
			fout.write(str(p.Tx) + " " + str(p.Rx) + " " + str(type_code[p.Tx_type]) + " " + str(type_code[p.Rx_type]) + "\n")
		fout.write(";\n")

		fout.write("param : dur :=\n")
		for p in self.P:
			for c in self.C:
				fout.write(str(p.name) + " " + str(c.name) + " " + str(p.dur[c.name])  + "\n")
		fout.write(";\n")

		fout.write("param : K :=\n")
		for p in self.P:
			for c in self.C:
				fout.write(str(p.name) + " " + str(c.name) + " " + str(p.K[c.name])  + "\n")
		fout.write(";\n")

		fout.write("param : M :=\n")
		for p in self.P:
			for c in self.C:
				fout.write(str(p.name) + " " + str(c.name) + " " + str(p.M[c.name])  + "\n")
		fout.write(";\n")

		fout.write("param : B :=\n")
		for p in self.P:
			for c in self.C:
				fout.write(str(p.name) + " " + str(c.name) + " " + str(p.B[c.name])  + "\n")
		fout.write(";\n")

		fout.close()
	
	def output(self,filename="graph.pdf"):
		loc = {}
		labellist = {}
		for n in range(0,self.num_devices+1):
			loc[n] = (self.G.node[n]['x'],self.G.node[n]['y'])
			labellist[n] = str(n)
		plt.axis('off')
		nx.draw_networkx(self.G,pos=loc,labels=labellist,font_size=8)
		plt.tight_layout()
		plt.savefig(filename)
		plt.close()