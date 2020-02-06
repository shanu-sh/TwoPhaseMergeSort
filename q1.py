#!/usr/bin/env python3

import sys
import math
import csv

colmapping={}
colindexing={}
mainmemorysize=0
chunksize=0

class Node:
	def __init__():
		self.data=''
		self.fp=-1

def readfile(filename):
    lines=[]
    f1=open(filename)
    lines=f1.readlines()
    f1.close()
    return lines

def readmetadata(filename):
	lines=readfile(filename)
	j=0
	for i in lines:
		a,b=i.split(",")
		colmapping[a]=int(b)
		colindexing[a]=j
		j+=1

		
def readwordfromlines(line):
	words=[]
	offset=0
	for i in colmapping.values():
		words.append(line[offset:offset+i])
		offset=offset+i+2
	return words

def parseinput(cmddata):
	input_file=cmddata[1]
	output_file=cmddata[2]
	size=int(cmddata[3])*1024*1024
	nthread=int(cmddata[4])
	code=cmddata[5]
	columns=[]
	i=6
	while(i<len(cmddata)):
		columns.append(cmddata[i])
		i+=1

	return input_file,output_file,size,nthread,code,columns

def printstats(nooflines):
	print('size of 1 tuple in bytes is',sizeoftuple())
	print('size of input file in bytes',sizeofinputfile(len(lines)))
	print('main memory allowed in bytes ',mainmemorysize)
	print('size of chunk size is ',chunksize)

def sizeoftuple():
	return sum(colmapping.values())

def sizeofinputfile(nooflines):
	return nooflines*sizeoftuple()

def calcchunksize():
	return math.floor(mainmemorysize/sizeoftuple())

def writelistoflist(f,result):
	writer=csv.writer(f)
	writer.writerows(result)

def readlistoflist(f):
	reader=csv.reader(f)
	for lines in reader:
		print(lines)

def keyindices(x,columns):
	a=[]
	for i in columns:
		a.append(x[colindexing[i]])
	return a

def sortdata(lines,columns):
	#lines=sorted(lines,key=lambda l:(len(l),l))
	lines=sorted(lines,key=lambda x: keyindices(x,columns))
	# print(lines1)
	return lines

def splitdata_sorted(filename,columns):
	filearray=[]
	findex=0
	f1=open(filename)
	line=f1.readline()

	tempresult=[]
	count=0
	f2=open('temp'+str(findex)+'.txt','w')
	while(line):

		if(count==chunksize):

			#Sort the sublist and store in memory
			filearray.append('temp'+str(findex)+'.txt')
			t=filearray[findex]
			print(t)
			f2=open(t,'w')
			tempresult=sortdata(tempresult,columns)
			writelistoflist(f2,tempresult)
			tempresult=[]
			count=0
			findex+=1
			f2.close()
		else:
			words=readwordfromlines(line)
			tempresult.append(words)
		line=f1.readline()
		count+=1
		

	if(count>0):
		filearray.append('temp'+str(findex)+'.txt')
		f2=open(filearray[findex],'w')
		tempresult=sortdata(tempresult,columns)
		writelistoflist(f2,tempresult)
		f2.close()
		findex+=1
	f1.close()

cmddata=sys.argv
if(len(cmddata)<6):
	print('PLease enter all parameter')
else:
	input_file,output_file,mainmemorysize,nthread,code,columns=parseinput(cmddata)
	readmetadata('metadata.txt')
	chunksize=calcchunksize()

	lines=readfile(input_file)
	printstats(len(lines))
	
	splitdata_sorted(input_file,columns)

	f=open("temp0.txt")
	readlistoflist(f)
	# print(lines)
	# print(lines[len(lines)-1])
	# t=lines[len(lines)-1]

# print(readwordfromlines(t))
# for i in readwordfromlines(t):
# 	print(len(i))
