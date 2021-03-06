import sys
import os.path
import argparse, math, random, time
import csv
import numpy as np
import cPickle as pickle
from telescopeclasses import *
from matplotlib import rc
from scipy.optimize import curve_fit

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

data=["36tev-lpdfull", "56tev-lpdfull"]



areas = [108., 614.]

mindensity = 0.1
height = 25000

filepath = "/nfs/astrop/d6/rstein/data/"



cut, ucut, QDCcut, DCcut, signalcut = ic.runforstats()
arcut = ic.runar()



sys.path.append('/nfs/astrop/d6/rstein/Hamburg-Cosmic-Rays/misc')
from progressbar import ProgressBar
custom_options = {
	'end': 100,
	'width': 100,
	'format': '%(progress)s%% [%(fill)s%(blank)s]'
}

for k in range(len(data)):
	jobID=data[k]
	targetfolder = filepath + jobID +"/"
	truesignals1=[[],[]]
	truedistances=[[],[]]
	p = ProgressBar(**custom_options)
	print p
	j=500
	i=0
	while (i < j):
		targetpath = targetfolder +  "run" + str(i) + "/pickle/eventdata.p"
		if (os.path.isfile(targetpath)):
			event = pickle.load(open(targetpath, 'rb'))
			if hasattr(event.simulations, "DC") and hasattr(event.simulations, "full"):
				DCsim =event.simulations.DC
				fullsim = event.simulations.full
				
				IDs=0
			
				for fulltel in fullsim.images:	
					if fulltel.BDTID != None:
						fullBDT = fulltel.getBDTpixel()
									
						simplecandidatesignal = fullBDT.channel1.intensity -fullBDT.nnmean
						
						if float(ucut) > float(fullBDT.bdtscore) > float(cut):
							if float(simplecandidatesignal) > float(signalcut):
								if float(fulltel.hillas.aspect_ratio_) > arcut:
									IDs+=1
			
				if IDs > 3:
	
					for fulltel in fullsim.images:
							
						if fulltel.size == "HESS1":
							plotindex = 0
						elif fulltel.size == "HESS2":
							plotindex = 1
						else:
							raise Exception("Telescope.size error, size is " +fulltel.size)
		
						truedistances[plotindex].append(fulltel.hillas.core_distance_to_telescope)
						truesignals1[plotindex].append(fulltel.hillas.image_size_amplitude_/fulltel.mirrorarea)				
	
		if (int(float(i)*100/float(j)) - float(i)*100/float(j)) ==0:
			print p+1
		i+=1
	
	for index in [0, 1]:
		print "HESS"+str(index+1)
		energy = float(jobID[:jobID.find("tev-lpd")])
		epn=1000 * energy/56
		print energy, "TeV", epn, "GeV per nucleon"
		print height, "m"
		
		figure = plt.gcf() # get current figure
		figure.set_size_inches(20, 20)
		sqarea = math.sqrt(areas[index])
		
		ax1=plt.subplot(2,2,1+index+(k*2))
		
		print len(truedistances[index]), "points"
		print truedistances[index], truesignals1[index]
		
		plt.scatter(truedistances[index], truesignals1[index])
		plt.xlabel("Core distance to telescope (m)")
		plt.ylabel("Photoelectron Density (m^-2)")
		ax1.set_xlim(left=0)
		ax1.set_yscale("log")
		plt.title("True LPD (Amplitude)")
		
		s=[]
	
		for l in range(len(truedistances[index])):
			value = truedistances[index][l]
			expval = truesignals1[index][l]
			s.append(math.log(expval))
				
		A, logC = np.polyfit(truedistances[index], s, 1)
		C = math.exp(logC)
		print A, logC, C, C/(energy**2)
				
		def fit(x):
			return C*np.exp(x*A)
	
		lpd=[]
		u=[]
		l=[]
		pu =[]
		pl = []
	
		diffs = []
		alldistances=[]
		
		for n in range(len(truedistances[index])):
			sig = np.exp(s[n])
			dist = truedistances[index][n]
			fitsig = fit(dist)
			diff = math.fabs((sig-fitsig)/fitsig)
			diffs.append(diff)
	
		diffs.sort()
		nentries = len(diffs)
		distances=truedistances[index]
		distances.sort()
		if nentries > 3:
			halfinteger = int(0.5*nentries)
			lowerinteger = int(0.16*nentries)
			upperinteger = int(0.84*nentries)
			integer68 = int(0.68*nentries)
			
			lower = diffs[lowerinteger]
			upper = diffs[upperinteger]
			
			truesigma = diffs[integer68]
			print "Actual", truesigma, "possonian", 

			psigmas = []
			for dist in distances:
				sig = fit(dist)
				lpd.append(sig)
				ulpd = sig*(1+truesigma)
				u.append(ulpd)
				llpd = sig*(1-truesigma)
				l.append(llpd)
				up = sig + (math.sqrt(sig)/sqarea)
				pu.append(up)
				lp = sig - (math.sqrt(sig)/sqarea)
				pl.append(lp)
				psigmas.append(1./(sqarea*math.sqrt(sig)))
		
			psigmas.sort()
			psigma = psigmas[integer68]
			print psigma
			plt.plot(distances, lpd, color='k')
			plt.fill_between(distances, l, u, color='g', alpha=0.25)
			ax1.fill_between(distances, pl, pu, color='r', alpha=0.25)
			message = "Sigma: " + str('{0:.2f}'.format(truesigma)) + " \n"
			plt.annotate(message, xy=(0.6, 0.8), xycoords="axes fraction",  fontsize=15)
		else:
			print "Nentries < 3"
	
		fd = mpatches.Rectangle((0, 0), 1, 1, fc="g",alpha=0.25)
		pd = mpatches.Rectangle((0, 0), 1, 1, fc="r",alpha=0.25)
		
		figure.legend([fd, pd], ["Fractional Deviation from True Fit","Expected Poissonian Error"], loc="upper right")
		

		title= str(energy)+ " TeV HESS " + str(index+1)
		plt.title(title)
	

saveto = "/nfs/astrop/d6/rstein/Hamburg-Cosmic-Rays/CORSIKA/graphs/fullshowerlpd.pdf"

print "Saving to", saveto

plt.tight_layout()

plt.savefig(saveto)
plt.savefig("/nfs/astrop/d6/rstein/Hamburg-Cosmic-Rays/report/graphs/corsikafullshowerlpd.pdf")
plt.close()
