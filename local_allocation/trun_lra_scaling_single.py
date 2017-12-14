from __future__ import division
from time import *
from math import *
from localcell import *
import sys, random, os
		
schedulings = 10

# bash input
sf = int(sys.argv[1])
n = int(sys.argv[2])

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