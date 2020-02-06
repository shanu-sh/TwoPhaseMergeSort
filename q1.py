#!/usr/bin/env python3

import sys
import math
import csv

colmapping={}
colindexing={}
mainmemorysize=0
chunksize=0
heap=[]

class Node:
	def __init__(self):
		#data will be a list
		self.data=[]
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

	columns=columns[0].split(',')
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
	for i in result:
		t=""
		for j in i:
			t=t+j+"  "
		t=t[:-1]
		t=t+'\n'
		f.write(t)

def readoneline(f):
	line=f.readline()
	if(line):
		return readwordfromlines(line)
	else:
		return []

def keyindices(x,columns):
	a=[]
	for i in columns:
		a.append(x[colindexing[i]])
	return a

def sortdata(lines,columns):
	lines=sorted(lines,key=lambda x: keyindices(x,columns))
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
	return filearray

def lessthan(l1,l2,columns):
	for j in columns:
		i=colindexing[j]
		if(l1[i]<l2[i]):
			return True
		elif(l1[i]==l2[i]):
			continue
		else:
			return False
	return False

def minheapify(i,columns):
	temp=Node()

	l=2*i+1
	r=2*i+2
	small=-1
	if(l<len(heap) and lessthan(heap[l].data,heap[i].data,columns)):
		small=l
	else:
		small=i

	if(r<len(heap) and lessthan(heap[r].data,heap[small].data,columns)):
		small=r

	if(small!=i):
		temp=heap[small]
		heap[small]=heap[i]
		heap[i]=temp
		minheapify(small,columns)

def buildminheap(columns):
	i=len(heap)-1
	while(i>=0):
		minheapify(i,columns)
		i-=1

def adjust(pos,columns):
	child=pos
	parent=math.floor((child-1)/2)

	while(parent>=0 and lessthan(heap[child].data,heap[parent].data,columns)):
		temp=heap[child]
		heap[child]=heap[parent]
		heap[parent]=temp

		child=parent
		parent=math.floor((child-1)/2)

def removemin(columns):
	temp=heap[0]
	
	heap[0]=heap[len(heap)-1]
	heap.pop()

	minheapify(0,columns)
	return temp

def mergesplittedfiles(filearray,columns):
	print(len(filearray))
	
	filepointer=[None]*len(filearray)

	for i in range(len(filearray)):
		filepointer[i]=open(filearray[i])
		data=readoneline(filepointer[i])
		temp=Node()
		temp.fp=i
		temp.data=data
		heap.append(temp)

	buildminheap(columns)

	fpwrite=open('tempoutput.txt','w')
	fileclosecount=0

	while(fileclosecount!=len(filearray)):
		temp=removemin(columns)
		result=[]
		result.append(temp.data)
		writelistoflist(fpwrite,result)

		data=readoneline(filepointer[temp.fp])
		if(len(data)!=0):
			temp.data=data
			heap.append(temp)
			adjust(len(heap)-1,columns)
		else:
			fileclosecount+=1

	for i in range(len(filearray)):
		filepointer[i]=open(filearray[i])
	return 1

#execution begins here
cmddata=sys.argv
if(len(cmddata)<6):
	print('PLease enter all parameter')
else:
	input_file,output_file,mainmemorysize,nthread,code,columns=parseinput(cmddata)
	readmetadata('metadata.txt')
	chunksize=calcchunksize()

	lines=readfile(input_file)
	printstats(len(lines))
	
	filearray=splitdata_sorted(input_file,columns)
	mergesplittedfiles(filearray,columns)

