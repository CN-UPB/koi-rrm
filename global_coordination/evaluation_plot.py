from __future__ import division
import sys
import math
#from pprint import pprint

import pylab as P

from matplotlib.transforms import Bbox
from matplotlib.font_manager import FontProperties

from collections import defaultdict

from ci import calc_sample_mean

labels = {}
labels["nodes"] = "Number of local cells" 
labels["rt"] = "Runtime" 
labels["sq"] = "% of optimal solution"
labels["tot"] = "Channels used (total)"
labels["fs"] = "Feasibility"
labels["i"] = "ILP"
labels["g"] = "Greedy"

manual_input = False

tests = [11,12]

for test in tests:
	filename = "Instances\Test_" + str(test) + "\_Results.dat"
	results = []
	xvalues = []

	fin = open(filename, "r")
	while True:
		tmp = fin.readline().split(" ")
		try:
			r = {}
			n = 5 * math.ceil(int(tmp[0])/25)
			if not n in xvalues:
				xvalues.append(n)
			r["nodes"] = n
			r["toti"] = float(tmp[1])
			r["rti"] = float(tmp[2])
			r["totg"] = float(tmp[3]) 
			r["rtg"] = float(tmp[4])
			if float(tmp[1]) > 0.5:
				r["fsi"] = True
			else:
				r["fsi"] = False
			if float(tmp[3]) > 0.5:
				r["fsg"] = True
				r["sqg"] = float(tmp[3]) / float(tmp[1])
				r["sqi"] = 1.0
			else:
				r["fsg"] = False
			results.append(r)
		except:
			break
				
	obj = ["rt","sq","fs","tot"]	
	alllines = [("i","rt"),("g","rt"),("i","fs"),("g","fs"),("i","sq"),("g","sq"),("i","tot"),("g","tot")]	

	for o in obj:
				
		x_label = labels["nodes"]
		y_label = labels[o]

		lines = [l for l in alllines if l[1] == o]

		plotdata = {}
		plotconfidence = {}
		xaxis = {}

		for l in lines:
			di = []
			ci = []
			for x in xvalues:
				values = []
				for r in results:
					if x == r["nodes"] and (o == "fs" or r["fsg"] == True):
						values.append(r[l[1]+l[0]])
				if len(values) > 1:
					(xd,xc) = calc_sample_mean(values, 0.95)
					di.append(xd)
					ci.append(xc)
					
			plotdata[l] = di
			plotconfidence[l] = ci

		#colors = ['#FF0000','#00FF00','#0000FF','#FFFF00','#FF00FF','#00FFFF','#800000','#008000','#000080','#808000','#800080','#008080','#808080','#FFFFFF']
		markers = ['^','*','o','v']

		font = FontProperties(size=24)
		font_smaller = FontProperties(size=18)

		F = P.figure()
		AX1 = F.add_subplot(111)
		plotlines = []
		plotlabels = []
		for i,l in enumerate(lines):
			if o == "fs":
				pl = AX1.errorbar(xvalues[:len(plotdata[l])], plotdata[l], label=(l), lw=2, marker=markers[i], markersize=12, elinewidth=2,ls="--")
			else:
				pl = AX1.errorbar(xvalues[:len(plotdata[l])], plotdata[l], yerr=plotconfidence[l], label=(l), lw=2, marker=markers[i], markersize=12, elinewidth=2,ls="--")
			plotlines.append(pl[0])
			plotlabels.append(labels[l[0]])
		AX1.set_xlabel(x_label, fontproperties=font)
		AX1.set_ylabel(y_label, fontproperties=font)
		AX1.set_xlim(0, 52)
		
		if o == "rt":
			AX1.set_yscale('log')
		elif o == "sq":
			AX1.set_ylim(ymin=0.995)
		elif o == "fs":
			AX1.set_ylim(ymax=1.02,ymin=0.0)
		elif o == "tot":
			AX1.set_ylim(ymax=350)
			#plotlines.append(AX1.plot((0, 166), (52, 166), 'k-'))
			plotlines.append(AX1.axhline(y=166, xmin=0, xmax=1, color='r', linewidth=1.5, linestyle='-'))
			
		for tick in AX1.xaxis.get_major_ticks():
			tick.label1.set_fontsize(18)
		for tick in AX1.yaxis.get_major_ticks():
			tick.label1.set_fontsize(18)
			
		P.savefig('plots/plot_Test_' + str(test) + '_' + str(l[1]) + '.pdf', bbox_inches='tight')
		F = P.figure(2)
		F.legend(plotlines, plotlabels, loc='upper left', shadow=False, fancybox=True, prop=font_smaller, ncol=2)
		bb = Bbox.from_bounds(0, 0, 6.4, 4)
		P.savefig('plots/plot_legend.pdf', bbox_inches=bb)
