import cv2
import numpy as np
import copy
import os, datetime, threading, sys
import RPi.GPIO as GPIO

from matplotlib import pyplot as plt
from datetime import datetime

cap = None
timeout = 0
LED_PIN = 4
timer = None
# 100px = 0.3mm
size_x = None

def detect_bubble():
	now = str(datetime.now()).replace(' ', '_')
	os.system('cp res.png ' + now + '_detect.png')
	os.system('cp test_original.jpg ' + now + '_original.jpg')

def led_thread():
	global timeout
	global LED_PIN
	global timer
	if timeout > 0 :
		timeout = timeout - 1
		GPIO.output(LED_PIN, True)
		print('led high')
	else :
		GPIO.output(LED_PIN, False)
		print('led low')
	timer = threading.Timer(0.5, led_thread)

def pattern(img_rgb):
	bubble_list = []

	#img_rgb = cv2.imread('test_resultw.jpg')
	img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
	template = cv2.imread('pattern.png',0)
	end_template = cv2.imread('y_pattern.png', 0)
	w, h = template.shape[::-1]
	we, he = end_template.shape[::-1]

	res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
	res_end = cv2.matchTemplate(img_gray, end_template, cv2.TM_CCOEFF_NORMED)
	threshold = 0.8
	threshold_end = 0.7
	loc = np.where( res >= threshold)
	loc_end = np.where(res_end >= threshold_end)
	img_copy = cv2.imread('test_resultx.jpg', 1)
	for pt in zip(*loc_end[::-1]):
		cv2.rectangle(img_copy, pt, (pt[0] + w, pt[1] + h), (0,255,0), 2)
		pt = pt + ('end',)
		bubble_list.append(pt)
	for pt in zip(*loc[::-1]):
		cv2.rectangle(img_copy, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
		pt = pt + ('start',)
		bubble_list.append(pt)
	cv2.imwrite('res_copy.png', img_copy)
	before = (0,0)
	for pt in zip(*loc_end[::-1]):
		if pt[0] - before[0] > 20 :
			cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,255,0), 2)
		before = pt

	before = (0,0)
	for pt in zip(*loc[::-1]):
		if pt[0] - before[0] > 20:
			cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
		before = pt
	cv2.imwrite('res.png',img_rgb)
	bubble_list = sorted(bubble_list, key=lambda bubble: bubble[0])
	print("SAVE")
	return bubble_list

def bubble_fillter(bubble_list):
	result = []
	last_append = None
	before = (0, 0)
	for pt in bubble_list :
		if pt[0] - before[0] > 30 or pt[2] != last_append :
			print('row : ' + str(pt))
			if last_append != pt[2]:
				result.append(pt)
				last_append = pt[2]
		before = pt
	distance = detect_distance(result)

	print("=====DISTANCE=====")
	for dis in distance :
		print(str(dis))
	draw_distance(distance)
	return result

def detect_distance(bubble_list):
	result = []
	global size_x
	'''거품별 거리를 측정하는 함수'''
	for idx in range(0, len(bubble_list)):
		print(idx)
		if idx < len(bubble_list) :
			print('in')
			if bubble_list[idx][2] == 'end' and bubble_list[idx + 1][2] == 'start':
				dis = (bubble_list[idx + 1][0] - bubble_list[idx][0]) / 100 * 0.3
				start = (bubble_list[idx][0], bubble_list[idx][1])
				end =  (bubble_list[idx + 1][0], bubble_list[idx + 1][1])
				result.append((dis, start, end))
				print("DIFF : " + str((bubble_list[idx + 1][0] - bubble_list[idx][0]) / 100 * 0.3))
			elif bubble_list[idx][2] == 'start':
				if idx == 0 :
					dis = bubble_list[idx][0] / 100 * 0.3
					start = (0, bubble_list[idx][1])
					end = (bubble_list[idx][0], bubble_list[idx][1])
					result.append((dis, start, end))
					print("DIFF : " + str(bubble_list[idx][0]))
			elif bubble_list[idx][2] == 'end':
				if idx == 0:
					dis = (size_x - bubble_list[idx][0]) / 100 * 0.3
					start = (bubble_list[idx][0], bubble_list[idx][1])
					end = (size_x, bubble_list[idx][1])
					result.append((dis, start, end))
					print("DIFF : " + str(size_x - bubble_list[idx][0]))
	return result

def draw_distance(distance_list):
	img = cv2.imread('res.png', 1)
	catch = False
	for distance in distance_list:
		x = int((distance[2][0] + distance[1][0]) / 2)
		y = int((distance[2][1] + distance[1][1]) / 2)
		dis = '{:.3f}'.format(distance[0])+"cm"
		print(dis)
		cv2.line(img, distance[1], distance[2], (0,255,255), 1)
		cv2.putText(img, dis, (x, y), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 255, 255), thickness=1)
		catch = True
	cv2.imwrite('res.png', img)
	if catch == True :
		timeout = 6
		detect_bubble()


def calcu_lux(y):
	temp = []
	for row in y:
		temp.append(np.mean(row))
	return np.mean(temp)

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
	global size_x
	global cap
	while cap.isOpened():
		_, img = cap.read()
		img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		#img = cv2.imread('test1.jpg',0)
		#img = cv2.resize(img, (0,0), fx=0.3, fy=0.3)
		cv2.imwrite('test_original.jpg', img)
		height, size_x = img.shape[:2]
		original_img = cv2.imread('test_original.jpg', 1)
		yuv_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2YUV)
		y, u, v = cv2.split(yuv_img)
		img_lux = calcu_lux(y)
		print('lux : ' + str(img_lux))
		if img_lux > 60 :
			laplacian = cv2.Laplacian(img,cv2.CV_64F)
			sobelx = cv2.Sobel(img,cv2.CV_64F,1,0,ksize=5)
			sobely = cv2.Sobel(img,cv2.CV_64F,0,1,ksize=5)
			cv2.imwrite('test_result64.jpg', laplacian)
			cv2.imwrite('test_resultx.jpg', sobelx)
			#ret, thr = cv2.threshold(sobelx, 200, 255, cv2.THRESH_BINARY)
			#cv2.imwrite('test_resultw.jpg', thr)
			#ret, thr = cv2.threshold(sobely, 200, 255, cv2.THRESH_BINARY)
			cv2.imwrite('test_resulty.jpg', sobely)
			thr = cv2.imread('test_resultx.jpg', 1)
			bubbles = pattern(thr)
			bubbles = bubble_fillter(bubbles)
			for pt in bubbles:
				print(str(pt[0]) + '\t' + str(pt[1]) + '\t' + pt[2])
		else :
			'''빛이 적을때의 처리'''
			print("LUX....")

if __name__ == "__main__":
	global cap
	print("START")
	try:
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(LED_PIN, GPIO.OUT)
		check_camera()
		cap = cv2.VideoCapture(0)
		global timer
		timer = threading.Timer(0.5, led_thread)
		timer.start()
		test()
	except Exception as err:
		print(str(err))
	finally :
		GPIO.cleanup()
