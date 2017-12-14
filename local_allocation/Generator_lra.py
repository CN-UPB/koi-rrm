from __future__ import division
from time import *
from math import *
from localcell import *
import sys, random, os
		
try: 
	cellsize = int(sys.argv[1])
except:
	print("Error: cell size missing!")
	exit(1)

try: 
	num_devices = int(sys.argv[2])
except:
	print("Error: amount of devices missing!")
	exit(1)
	
try: 
	instance = str(sys.argv[3])
except:
	instance = str(time()) + '.dat'

try:
	if not os.path.exists(os.path.dirname(instance)):
		os.makedirs(os.path.dirname(instance))
except:
	pass
	
d2d = False
	
# initialize
lc = LocalCell(num_devices=num_devices,cellsize=cellsize,d2d=d2d)

# generate output
lc.save_to_file(instance)

print "Generated: " + instance