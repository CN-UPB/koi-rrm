from __future__ import division
from time import *
from math import *
from localcell import *
import sys, random, os
		
try: 
	instance = str(sys.argv[1])
except:
	print("Error: input file missing!")
	exit(1)
	
try: 
	cellsize = int(sys.argv[2])
except:
	cellsize = 50
	
try: 
	num_devices = int(sys.argv[3])
except:
	num_devices = 50
	
schedulings = 10

# initialize
if instance == "generate":
	while True:
		lc = LocalCell(num_devices=num_devices,cellsize=cellsize)
		if lc.non_schedulable_pairs == 0:
			break
	lc.save_to_file("new.dat")
else: 
	lc = LocalCell(filename=instance)
	
#for p in lc.P:
	#print p.output()
#print [(c.name,c.Ksum) for c in lc.C]
#exit(1)
	
trun = 0

print "EDF stream scheduling:"
for i in range(0,schedulings):	
	trun -= time.time()
	lc.schedule_edf_bf(allchans=True)
	trun += time.time()
	if lc.scheduling['success'] == True:
		lc.validate_scheduling()
		#print "Channels used (EDF): " + str(lc.scheduling['num_ch'])
		#print lc.scheduling['ch_used']

print "Successful schedulings: " + str(len(lc.Csets)) + " out of " + str(schedulings)
if len(lc.Csets) > 0:
	print "Average amount of channels per scheduling: " + str(sum(len(cs) for cs in lc.Csets)/len(lc.Csets)) + " (out of " + str(len(lc.C)) + ")"
	print "Average runtime per scheduling: " + str(trun/schedulings)
	all_chans = []
	for cs in lc.Csets:
		all_chans = all_chans + cs
	print "Amount of channels used in all schedulings: " + str(len(set(all_chans)))

lc.Csets = []
trun = 0

print "EDF packetwise scheduling:"
for i in range(0,schedulings):	
	trun -= time.time()
	lc.schedule_edf_packetwise(allchans=True)
	trun += time.time()
	if lc.scheduling['success'] == True:
		lc.validate_scheduling()
		#print "Channels used (EDF): " + str(lc.scheduling['num_ch'])
		#print lc.scheduling['ch_used']

print "Successful schedulings: " + str(len(lc.Csets)) + " out of " + str(schedulings)
if len(lc.Csets) > 0:
	print "Average amount of channels per scheduling: " + str(sum(len(cs) for cs in lc.Csets)/len(lc.Csets)) + " (out of " + str(len(lc.C)) + ")"
	print "Average runtime per scheduling: " + str(trun/schedulings)
	all_chans = []
	for cs in lc.Csets:
		all_chans = all_chans + cs
	print "Amount of channels used in all schedulings: " + str(len(set(all_chans)))