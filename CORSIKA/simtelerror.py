import sys
import os.path
import argparse, math, random, time
import csv
import numpy as np
import cPickle as pickle
from telescopeclasses import *
from matplotlib import rc

parser = argparse.ArgumentParser()
parser.add_argument("-jid", "--jobID", default="double-no-shower")

cfg = parser.parse_args()

filepath = "/nfs/astrop/d6/rstein/data/"
i = 1
j = 2000
one=[[],[]]
two=[[],[]]
diff=[[],[]]

targetfolder = filepath + cfg.jobID +"/"

sys.path.append('/nfs/astrop/d6/rstein/Hamburg-Cosmic-Rays/misc')
from progressbar import ProgressBar
custom_options = {
	'end': 100,
	'width': 100,
	'format': '%(progress)s%% [%(fill)s%(blank)s]'
}

p = ProgressBar(**custom_options)
print p

while (i < j):
	targetpath = targetfolder +  "run" + str(i) + "/pickle/eventdata.p"
	if (os.path.isfile(targetpath)):
		event = pickle.load(open(targetpath, 'rb'))
		if hasattr(event.simulations, "DC") and hasattr(event.simulations, "full"):
			DCsim =event.simulations.DC
			fullsim = event.simulations.full
			
			for index in DCsim.triggerIDs:
				DCtel = DCsim.images[index]
				fulltel =  fullsim.images[index]
				
				trueID = DCtel.trueDC
				DCtrue = DCtel.getpixel(trueID)
				DCcount = DCtrue.channel1.intensity
				
				if fulltel.size == "HESS1":
					plotindex = 0
				elif fulltel.size == "HESS2":
					plotindex = 1
				else:
					raise Exception("Telescope.size error, size is " +fulltel.size) 
				
				fullBDT = fulltel.getpixel(trueID)
											
				candidatesignal = fullBDT.channel1.intensity
				
				if (candidatesignal != None) and (DCcount != None):
							
					difference = (DCcount - candidatesignal)/DCcount
					
					one[plotindex].append(DCcount)
					two[plotindex].append(candidatesignal)
					diff[plotindex].append(difference)

	if (int(float(i)*100/float(j)) - float(i)*100/float(j)) ==0:
		print p+1
	i+=1
	
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

for i in [0, 1]:

	ax2 = plt.subplot(2,1,2)
	plt.scatter(one[i], two[i], color='g')
	plt.xlabel("Intensity")
	plt.ylabel("Intensity")
	plt.plot([0,2500], [0, 2500], color="k")
	ax2.set_xlim(left=0)
	ax2.set_ylim(bottom=0)
	
	ax1 = plt.subplot(2,1,1)
	plt.hist(diff[i], bins=50)
	plt.title("Difference in count")
	
	allevents = diff[i]
	allevents.sort()
	
	nentries = len(allevents)
	halfinteger = int(0.5*nentries)
	lowerinteger = int(0.16*nentries)
	upperinteger = int(0.84*nentries)
	integer68 = int(0.68*nentries)
	
	lower = allevents[lowerinteger]
	upper = allevents[upperinteger]
	
	toprint= "Mean = " + str('{0:.1f}'.format(np.mean(allevents)))
	toprint += ". Median = " + str('{0:.1f}'.format(allevents[halfinteger])) + "\n"
	toprint += "Lower = " + str('{0:.1f}'.format(lower))
	toprint += ". Upper = " + str('{0:.1f}'.format(upper)) + "\n"
	toprint += "Sigma = " + str('{0:.1f}'.format(0.5*(upper-lower))) + "\n"
	
	ax1.annotate(toprint, xy=(0.02, 0.75), xycoords='axes fraction',  fontsize=10)
	
	print toprint
	
	figure = plt.gcf() # get current figure
	figure.set_size_inches(20, 20)
	
	saveto = "/nfs/astrop/d6/rstein/Hamburg-Cosmic-Rays/CORSIKA/graphs/simtelerror" + str(i+1)+".pdf"
	
	print "Saving to", saveto
	
	plt.savefig(saveto)
	plt.close()
	
