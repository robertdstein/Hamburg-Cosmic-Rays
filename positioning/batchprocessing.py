import argparse, math, random
import csv
import numpy as np

def run(source, outputfile, mincount, detectorcount):
	with open("data/" + str(outputfile) + ".csv", 'wb') as csvout:
		writer = csv.writer(csvout, delimiter=',', quotechar='|')
		writer.writerow("a")
	
		with open("output/"+ str(source) +".csv", 'rb') as csvfile:
			reader = csv.reader(csvfile, delimiter=',', quotechar='|')
			i = 0
			j = 0
			detections = 0
			a=[]
			for row in reader:
				if i > 0:
					event = row[0]
					category = row[1]
					xpos = float(row[2])
					ypos = float(row[3])
					sigcount = row[4]
					bkgcount = row[5]
					siglitarea = row[6]
					bkglitarea=row[7]
					
					j+=1
				
					if (int(event) == int(i)):
						a += [[xpos, ypos, sigcount, bkgcount, siglitarea, bkglitarea]]
						if ((int(sigcount) == int(0)) & (int(bkgcount) == int(0))):
							pass
						else:
							detections += 1
						
					if j == detectorcount:
						print "Total detections:", detections
						if detections >= float(mincount):
							writer.writerow(a)
						a=[]
						detections=0
						j = 0
						i +=1			
				else:
					i +=1
