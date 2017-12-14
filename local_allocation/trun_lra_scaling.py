from __future__ import division
from time import *
from math import *
from localcell import *
import sys, random, os
		
scaling_factors = [1,2,4,5,8]
inst_per_sf = 50
schedulings = 10
num_devices = range(5,61,5)

fout = open("Scaling_results/packetwise.dat","w")
fout.write("scaling devices successes attempts channels bandwidth runtime \n")
fout.close()
fout = open("Scaling_results/stream.dat","w")
fout.write("scaling devices successes attempts channels bandwidth runtime \n")
fout.close()

for sf in scaling_factors:	
	for n in num_devices:
		print "Performing scaling test for factor " + str(sf) + " with " + str(n) + " devices..."
		for i in range(0,inst_per_sf):
			while True:
				lc = LocalCell(num_devices=n,cellsize=n,scaling_factor=sf)
				if lc.non_schedulable_pairs == 0:
					break

			chbw = lc.cm.ch_bandwidth
			
			trun = 0
			for i in range(0,schedulings):	
				trun -= time.time()
				lc.schedule_edf_packetwise(allchans=True)
				trun += time.time()
				
			if len(lc.Csets) > 0:
				av_chs = sum(len(cs) for cs in lc.Csets)/len(lc.Csets)
						
				fout = open("Scaling_results/packetwise.dat","a")
				fout.write(str(sf) + " " + str(n) + " " + str(len(lc.Csets)) + " " + str(schedulings) + " " + str(av_chs) + " " + str(av_chs*chbw) + " " + str(trun/schedulings) + "\n")
				fout.close()
			else:
				fout = open("Scaling_results/packetwise.dat","a")
				fout.write(str(sf) + " " + str(n) + " 0 " + str(schedulings) + "\n")
				fout.close()
			
			if sf > 1:
				lc.Csets = []
				trun = 0
				for i in range(0,schedulings):	
					trun -= time.time()
					lc.schedule_edf_bf(allchans=True)
					trun += time.time()
				
				if len(lc.Csets) > 0:
					av_chs = sum(len(cs) for cs in lc.Csets)/len(lc.Csets)
							
					fout = open("Scaling_results/stream.dat","a")
					fout.write(str(sf) + " " + str(n) + " " + str(len(lc.Csets)) + " " + str(schedulings) + " " + str(av_chs) + " " + str(av_chs*chbw) + " " + str(trun/schedulings) + "\n")
					fout.close()
				else:
					fout = open("Scaling_results/stream.dat","a")
					fout.write(str(sf) + " " + str(n) + " 0 " + str(schedulings) + "\n")
					fout.close()