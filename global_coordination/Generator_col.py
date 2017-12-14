from __future__ import division
from time import *
from math import *
import sys, random, os
from igraph import *

# initialize

try: 
	dim = int(sys.argv[1])
except:
	print("Error: dimension missing!")
	exit(1)
	
try: 
	instance = str(sys.argv[2])
except:
	instance = str(time()) + '.dat'
	
try: 
	option = str(sys.argv[3])
except:
	option = 'lras'

try:
	if not os.path.exists(os.path.dirname(instance)):
		os.makedirs(os.path.dirname(instance))
except:
	pass
	
ig = igraph()
if option == 'lras':
	ig.generate_lra(cells=dim,edfm="stream",dc=True)
elif option == 'lrap':
	ig.generate_lra(cells=dim,edfm="packetwise",dc=True)
elif option == 'generic':
	ig.generate_generic(cells=dim)
else:
	print "Error: Invalid generator option!"
	exit(1)
	
ig.save_to_file(instance)

print "Generated: " + instance