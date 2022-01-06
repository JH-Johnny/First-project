import cv2
import numpy as np
from matplotlib import pyplot as plt
import copy
import os, datetime, threading, sys
cap = None

# 100px = 0.3mm

def check_camera() :
	global cap
	call = os.system
	call("sudo modprobe bcm2835-v4l2")

	print("test1")
	if os.path.exists("/dev/video0"):
		call("wget http://www.linux-projects.org/listing/uv4l_repo/lrkey.asc && sudo apt-key add ./lrkey.asc")
		print("test2")
		call("cp ./source_list /etc/apt/sources.list")
		print("test3")
		call("sudo apt-get update")
		print("test4")
		call("sudo apt-get install uv4l uv4l-raspicam")
		print("test5")
		call("uv4l --driver raspicam --auto-video_nr --width 640 --height 480 --encoding jpeg --frame-time 0")
		print("test6")
		call("dd if=/dev/video0 of=snapshot.jpeg bs=11M count=1")
		print("test7")
		if os.path.exists("./snapshot.jpeg"):
			print("[SYSTEM] Now UV4L device driver operated...")
			call("rm lrkey*")
		else :
			print("[SYSTEM] Fail...")
			exit()
			
def test():
	global cap
	if cap.isOpened():
		_, img = cap.read()
		img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		#img = cv2.imread('test1.jpg',0)
		#img = cv2.resize(img, (0,0), fx=0.3, fy=0.3) 
		cv2.imwrite('test_original.jpg', img)
		laplacian = cv2.Laplacian(img,cv2.CV_64F)
		sobelx = cv2.Sobel(img,cv2.CV_64F,1,0,ksize=5)
		cv2.imwrite('test_result64.jpg', laplacian)
		cv2.imwrite('test_resultx.jpg', sobelx)
		ret, thr = cv2.threshold(sobelx, 250, 255, cv2.THRESH_BINARY)
		cv2.imwrite('test_resultw.jpg', thr)
		thr = thr[127:128][:].copy()

		# min 8
		start = False
		inner = False
		bubble_edges_temp = []
		bubble_edges = []
		temp = {}
		index = 0
		for i in thr[0]:
			print(i)
			index = index + 1
			if i == 255 :
				if start == False : 
					start = True
					temp['start'] = index
				else :
					inner = True
			else :
				if start == True :
					temp['end'] = index
					temp['size'] = temp['end'] - temp['start']
					bubble_edges_temp.append(copy.copy(temp))
					inner = start = False
		temp = 0
		for i in bubble_edges_temp :
			if i['size'] > 6 :
				print(i['start'])
				print(i['end'])
				print(i['size'])
				print("BUBBLE_DETECT!!!")
				bubble_edges.append(copy.copy(i))
		
		for idx in range(start, len(bubble_edges), 2):
			print(idx)
			if idx > len(bubble_edges) - 1 : 
				break
			diff = 0
			if idx == (len(bubble_edges) - 2) :
				diff = bubble_edges[idx]['start'] - len(thr[0])
			else :
				diff = bubble_edges[idx + 1]['start'] - bubble_edges[idx]['end']
			mm = (diff/1000.0) * 3
			print("DISTANCE" + str(int(idx + 1) / 2) + " : "); print(repr(mm))
		cv2.imwrite('test_resultwr.jpg', thr)

if __name__ == "__main__":
	global cap
	print("START")
	#check_camera()
	cap = cv2.VideoCapture(0)
	test()
