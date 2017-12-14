from __future__ import division
import math, sys, random
import numpy as np
#import matlab.engine

matlab_path = '../../Simulator/scm-11-01-2005'
spectrum_lbound = 5.725e9
spectrum_ubound = 5.875e9
#spectrum_ubound = 5.75e9 # for testing only.
transmit_power_dbm = {"LRC": 30, "device": 23}
antenna_gain_dbi = {"LRC": 0, "device": 0}
antennas = {"LRC": 2, "device": 1}
type_code = {"LRC": 1, "device": 2}
code_type = {1: "LRC", 2: "device"}
# values by Shehzad from WP2_M3 document
MCSfile = 'koi_mcs.dat'
symbols_per_slot = 7*2*12 # 7 OFDM symbols * 2 RBs * 12 sub-carriers (LTE frame structure)
coding_rate = {1: 1/3, 2: 1/2, 3: 1/3, 4: 1/2, 5: 1/3, 6: 1/2, 7: 1/3, 8: 1/2}
coding_factor = {1: 2, 2: 2, 3: 4, 4: 4, 5: 6, 6: 6, 7: 8, 8: 8} # QPSK, 16QAM, 64QAM, 256QAM
chGainMode = 3
chGainFile = 'chGains.dat'

class ChModel:

	def __init__(self, sf=5):
		self.scaling_factor = sf # must be a factor that devides 1 without a continuous period, e.g. 1,2,4,5,8,...; not 3,6,7,...
		self.TTI_length = 1e-3 / self.scaling_factor # LTE numerology scaled by scaling factor
		self.ch_bandwidth = 1.8e5 * self.scaling_factor # LTE numerology scaled by scaling factor
		self.num_channels = int((spectrum_ubound - spectrum_lbound) / self.ch_bandwidth)
		self.chGainsImported = []
		self.MCS = {}

	def w2db(self, watts): # also used for "linear" to dB
		return 10 * math.log(watts, 10)

	def db2w(self, db):
		return math.pow(10, db / 10)
		
	def dbm2w(self, dbm):
		return math.pow(10, (dbm - 30) / 10)
		
	def transmit_power_watts(self, x):
		return self.dbm2w(transmit_power_dbm[x])

	def path_loss_db(self, distance,Tx="LRC",Rx="device"):	
		# values from Tanghe channel model
		d0 = 15			# reference distance
		PL_d0 = 81.01	# path loss of reference distance
		n = 0.91		# path loss exponent
		
		pl = PL_d0 + n * self.w2db(distance/d0)
		
		return pl
		
	def shadowing_db(self):	
		# values from Tanghe channel model
		sigma = 4.79	# SD for lognormal shadowing
		sh = random.normalvariate(0, sigma)
		return sh
		
	def ricean_fading_db(self, distance,Tx="LRC",Rx="device"): # not used currently
		# values from Tanghe channel model
		k_factor_mean = 12.3
		k_factor_sd = 5.4
		
		K = self.db2w(random.normalvariate(k_factor_mean, k_factor_sd))
		omega = self.db2w(self.w2db(self.dbm2w(transmit_power_dbm[Tx])) + antenna_gain_dbi[Tx] + antenna_gain_dbi[Rx] - self.path_loss_db(distance,Tx,Rx)) # estimated local mean power
		v = math.sqrt(K*omega/(K+1))
		sigma = math.sqrt(omega/(2*(K+1)))
		
		# approximation of ricean distribution by normal variate, which works for K >> 1
		rf = self.w2db(random.normalvariate(v, sigma))
		
		return rf	
		
	def channel_gain_watts(self, distance,Tx="LRC",Rx="device",slots=1):
		try:
			eng
		except:
			eng = matlab.engine.start_matlab()
			eng.cd(matlab_path,nargout=0)
			
		eng.rng('shuffle')
		gain = eng.chGain(distance,self.num_channels,antennas[Tx],antennas[Rx],slots)

		return gain[0]
		
	def channel_gain_watts2(self):
		try:
			eng
		except:
			eng = matlab.engine.start_matlab()
			eng.cd(matlab_path,nargout=0)
			
		eng.rng('shuffle')
		gain = eng.chGain2(self.num_channels)

		return gain[0]
		
	def import_chGains(self):
		try:
			fin = open(chGainFile, "r")
			while True:
				tmp = fin.readline()
				if len(tmp) > 0:
					chGtmp = [float(n) for n in tmp.split(" ")]
					self.chGainsImported.append(chGtmp)
				else:
					break
		except:
			print "Error: Could not import chGains from file!"
			exit(1)
		
	def get_chgain(self, distance,Tx="LRC",Rx="device",slots=1):
		random.seed()
		if chGainMode == 1:
			chgain = self.channel_gain_watts(distance,Tx,Rx)
		elif chGainMode == 2:
			chgain = self.channel_gain_watts2()
		elif chGainMode == 3:
			chgain = [random.expovariate(1) for i in range(0,self.num_channels)]
		elif chGainMode == 4:
			if len(self.chGainsImported) == 0:
				self.import_chGains()
			chgain = []
			while True:
				g_rand = random.randint(1,len(self.chGainsImported))
				for i in range(0,len(self.chGainsImported[g_rand-1])):
					chgain.append(self.chGainsImported[g_rand-1][i])
					if len(chgain) == self.num_channels:
						return chgain

		return chgain
		
	def received_signal_power_db(self, distance,Tx="LRC",Rx="device",shad=None):
		if shad is None:
			s_power = self.w2db(self.transmit_power_watts(Tx)) + antenna_gain_dbi[Tx] + antenna_gain_dbi[Rx] - self.path_loss_db(distance,Tx,Rx) - self.shadowing_db() #- ricean_fading_db(distance,Tx,Rx)
		else:
			s_power = self.w2db(self.transmit_power_watts(Tx)) + antenna_gain_dbi[Tx] + antenna_gain_dbi[Rx] - self.path_loss_db(distance,Tx,Rx) - shad
		return s_power
		
	def base_test(self, distance,Tx="LRC",Rx="device"): # for testing only
		return self.w2db(self.transmit_power_watts(Tx) / self.noise_watts()) + antenna_gain_dbi[Tx] + antenna_gain_dbi[Rx] - self.path_loss_db(distance,Tx,Rx)

	def received_signal_power_watts(self, distance,Tx="LRC",Rx="device",shad=None):
		return self.db2w(self.received_signal_power_db(distance,Tx,Rx,shad))

	def noise_dbm(self):
		# Johnson-Nyquist noise, Boltzmann constant, Temperature: 300 Kelvin
		return -174 + self.w2db(self.ch_bandwidth)
		
	def noise_watts(self):
		return self.dbm2w(self.noise_dbm())
		
	def interference_watts(self):
		# not considered for now
		return 0

	def sinr(self, distance,Tx="LRC",Rx="device"):
		chg = self.get_chgain(distance,Tx,Rx)
		return self.w2db(self.received_signal_power_watts(distance,Tx,Rx) * chg[0] / (self.interference_watts() + self.noise_watts()))
		
	def sinr_list(self, distance,Tx="LRC",Rx="device",shad=None,chgain=None):
		rspw = self.received_signal_power_watts(distance,Tx,Rx,shad)
		int_noise = self.interference_watts() + self.noise_watts()
		if chgain is None:
			chg = self.get_chgain(distance,Tx,Rx)
		else:
			chg = chgain
		sl = [self.w2db(rspw * chg[i] / (int_noise)) for i in range(0,self.num_channels)] 
		return sl
		
	def shannon_capacity(self, distance,Tx="LRC",Rx="device"):
		return self.ch_bandwidth * math.log( 1 + self.received_signal_power_watts(distance,Tx,Rx) / (self.interference_watts() + self.noise_watts()), 2)  # bit/s
		
	def import_MCS(self):
		try:
			fin = open(MCSfile, "r")
			tmp = fin.readline()
			self.MCS['refps'] = int(tmp)
			tmp = fin.readline()
			self.MCS['reftti'] = float(tmp)
			tmp = fin.readline()
			self.MCS['refbw'] = {}
			while True:
				tmpl = fin.readline()
				if len(tmpl) > 0:
					tmp = tmpl.split("\t")
					if (int(tmp[0]),int(tmp[1])) not in self.MCS:
						self.MCS[(int(tmp[0]),int(tmp[1]))] = {}
					self.MCS[(int(tmp[0]),int(tmp[1]))][int(tmp[2])] = float(tmp[3])
					self.MCS['refbw'][int(tmp[2])] = float(tmp[4])
				else:
					break
		except:
			print "Error: Could not import MCS from file!"
			exit(1)
			
	def sinr_th(self, mcs,tx="LRC",rx="device"):
		if len(self.MCS) == 0:
			self.import_MCS()
		return self.MCS[(antennas[tx],antennas[rx])][mcs] - self.w2db(self.ch_bandwidth) + self.w2db(self.MCS['reftti']/self.TTI_length) 
		
	def get_mcs(self, sinr,tx="LRC",rx="device"):
		if len(self.MCS) == 0:
			self.import_MCS()
		mcs = 8
		while True:
			if sinr >= self.sinr_th(mcs,tx,rx):
				return mcs
			else:
				mcs -= 1
			if mcs == 0:
				return 0
				
	def get_bits_per_slot(self, mcs):
		if len(self.MCS) == 0:
			self.import_MCS()
		if mcs == 0:
			return 0
		else:
			return int(coding_rate[mcs] * coding_factor[mcs] * symbols_per_slot)
		
	def get_duration(self, ps,mcs):
		if len(self.MCS) == 0:
			self.import_MCS()
		if mcs == 0:
			return 0
		else:
			return int(math.ceil(ps / self.get_bits_per_slot(mcs)))