import argparse, math, random
import csv
import numpy as np
import matplotlib.pyplot as plt

def run(source, detectorcount, mindetections, graph, llcuts):
	fullcount=[]
	labels=[]
	info = ""
	k=0
	for j in range (detectorcount, mindetections -1, -1):
		specificcount=[]
		with open("/afs/desy.de/user/s/steinrob/Documents/DESY/positioning/reconstructeddata/"+ str(source) +".csv", 'rb') as csvfile:
			reader = csv.reader(csvfile, delimiter=',', quotechar='|')
			i = 0
			upperll=llcuts[k]
			for row in reader:
				if i == 0:
					i = 1
				else:
					detections = row[0]
					reconx = float(row[1])
					recony = float(row[2])
					reconEPN = float(row[3])
					reconZ = row[4]
					reconHeight = row[5]
					truex = float(row[6])
					truey = float(row[7])
					trueEPN = float(row[8])
					trueZ = row[9]
					trueHeight = row[10]
					likelihood = row[13]
					
					if int(detections) == int(j):
						if float(likelihood) < float(upperll):
							difference = (reconEPN-trueEPN)/trueEPN
							specificcount.append(difference)

		fullcount.append(specificcount)
		label = str(j) + " detections"
		labels.append(label)
		
		total = len(specificcount)
		
		if float(total) > float(0):
		
			specificcount.sort()
		
			lower = int(total*0.16)
			mid = int(total*0.5)
			upper = int(total*0.84)
			
			lowerz = specificcount[lower]
			meanz = specificcount[mid]
			upperz = specificcount[upper]
			sigma = (upperz-lowerz) * 0.5
			
			info += str("For N = " + str(j) + " \n ")
			info += ('Lower bound = ' + str(lowerz) + " \n")
			info += ('Upper bound = ' + str(upperz) + " \n")
			info += ('Mean = ' + str(meanz) + " \n")
			info += ('Sigma = ' + str(sigma) + "\n \n")
	
	plt.annotate(info, xy=(0.05, 0.4), xycoords="axes fraction",  fontsize=10)
			
	n, bins, _ = plt.hist(fullcount, bins=14, range=[-0.7,0.7], label=labels, histtype='bar', stacked=True)
	
	mid = (bins[1:] + bins[:-1])*0.5
	if isinstance(n[0], np.ndarray):
		errors = np.zeros(len(n[0]))
		for i in range(0, len(n)):
			array = n[i]
			old = errors
			errors = []
			for j in range(0, len(array)):
				count = array[j]
				oldcount = old[j]
				delta = count-oldcount
				errors.append(math.sqrt(delta))
			
			plt.errorbar(mid, n[i], yerr=errors, fmt='kx')
	
	nmax = np.amax(n)
	
	uplim = nmax + 2*(math.sqrt(nmax))
	
	plt.ylim(0, uplim)

	plt.ylabel("Count")
	plt.xlabel("Fractional diference from True EPN")
	plt.title("Reconstruction of Energy per Nucleon")
	plt.legend()
	plt.savefig('/afs/desy.de/user/s/steinrob/Documents/DESY/positioning/graphs/epn.pdf')
	
	
	if graph:
		plt.show()
		
	else:
		plt.close()
