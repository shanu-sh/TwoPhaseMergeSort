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
	if(code=='dsc'):
		flag=True
	elif(code=='asc'):
		flag=False
	else:
		print('PLease specify the correct sorting order')
		exit()
	columns=[]
	i=6
	while(i<len(cmddata)):
		columns.append(cmddata[i])
		i+=1

	columns=columns[0].split(',')
	return input_file,output_file,size,nthread,flag,columns

def printstats():
	print('size of 1 tuple in bytes is',sizeoftuple())
	print('main memory allowed in bytes ',mainmemorysize)
	print('size of chunk size is ',chunksize)

def sizeoftuple():
	return sum(colmapping.values())

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

def sortdata(lines,columns,flag):
	if(flag==True):
		return sorted(lines,key=lambda x: keyindices(x,columns),reverse=True)
	else:
		return sorted(lines,key=lambda x: keyindices(x,columns))

def splitdata_sorted(filename,columns,flag):
	filearray=[]
	findex=0
	f1=open(filename)
	line=f1.readline()

	tempresult=[]
	count=0
	f2=open('temp'+str(findex)+'.txt','w')
	while(line):

		if(count==chunksize):

			filearray.append('temp'+str(findex)+'.txt')
			t=filearray[findex]
			f2=open(t,'w')
			tempresult=sortdata(tempresult,columns,flag)
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
		tempresult=sortdata(tempresult,columns,flag)
		writelistoflist(f2,tempresult)
		f2.close()
		findex+=1
	f1.close()
	return filearray

def compare(l1,l2,columns,flag):
	if(flag):
		for j in columns:
			i=colindexing[j]
			if(l1[i]>l2[i]):
				return True
			elif(l1[i]==l2[i]):
				continue
			else:
				return False
		return False
	else:
		for j in columns:
			i=colindexing[j]
			if(l1[i]<l2[i]):
				return True
			elif(l1[i]==l2[i]):
				continue
			else:
				return False
		return False

def minheapify(i,columns,flag):
	temp=Node()

	l=2*i+1
	r=2*i+2
	small=-1
	if(l<len(heap) and compare(heap[l].data,heap[i].data,columns,flag)):
		small=l
	else:
		small=i

	if(r<len(heap) and compare(heap[r].data,heap[small].data,columns,flag)):
		small=r

	if(small!=i):
		temp=heap[small]
		heap[small]=heap[i]
		heap[i]=temp
		minheapify(small,columns,flag)

def buildminheap(columns,flag):
	i=len(heap)-1
	while(i>=0):
		minheapify(i,columns,flag)
		i-=1

def adjust(pos,columns,flag):
	child=pos
	parent=math.floor((child-1)/2)

	while(parent>=0 and compare(heap[child].data,heap[parent].data,columns,flag)):
		temp=heap[child]
		heap[child]=heap[parent]
		heap[parent]=temp

		child=parent
		parent=math.floor((child-1)/2)

def removemin(columns,flag):
	temp=heap[0]
	
	heap[0]=heap[len(heap)-1]
	heap.pop()

	minheapify(0,columns,flag)
	return temp

def mergesplittedfiles(filearray,columns,flag):

	filepointer=[None]*len(filearray)
	for i in range(len(filearray)):
		filepointer[i]=open(filearray[i])
		data=readoneline(filepointer[i])
		temp=Node()
		temp.fp=i
		temp.data=data
		heap.append(temp)

	buildminheap(columns,flag)

	fpwrite=open('tempoutput.txt','w')
	fileclosecount=0

	while(fileclosecount!=len(filearray)):
		temp=removemin(columns,flag)
		result=[]
		result.append(temp.data)
		writelistoflist(fpwrite,result)

		data=readoneline(filepointer[temp.fp])
		if(len(data)!=0):
			temp.data=data
			heap.append(temp)
			adjust(len(heap)-1,columns,flag)
		else:
			fileclosecount+=1

	for i in range(len(filearray)):
		filepointer[i]=open(filearray[i])
	return 1

cmddata=sys.argv
if(len(cmddata)<6):
	print('PLease enter all parameter')
else:
	input_file,output_file,mainmemorysize,nthread,flag,columns=parseinput(cmddata)
	readmetadata('metadata.txt')
	chunksize=calcchunksize()

	printstats()
	
	filearray=splitdata_sorted(input_file,columns,flag)
	mergesplittedfiles(filearray,columns,flag)
