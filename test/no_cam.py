import cv2
import numpy as np
from matplotlib import pyplot as plt
import copy
import os, datetime, threading, sys

# 100px = 0.3mm
def pattern(img_rgb, template):
	img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
	#template = cv2.imread('pattern.jpg',0)
	w, h = template.shape[::-1]

	res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
	threshold = 0.8
	loc = np.where( res >= threshold)
	for pt in zip(*loc[::-1]):
	    cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
	cv2.imwrite('res.png',img_rgb)

def test():
	img = cv2.imread('test1.jpg',0)
	#img = cv2.resize(img, (0,0), fx=0.3, fy=0.3)
	cv2.imwrite('test_original.jpg', img)
	laplacian = cv2.Laplacian(img,cv2.CV_64F)
	sobelx = cv2.Sobel(img,cv2.CV_64F,1,0,ksize=5)
	cv2.imwrite('test_result64.jpg', laplacian)
	cv2.imwrite('test_resultx.jpg', sobelx)
	ret, thr = cv2.threshold(sobelx, 250, 255, cv2.THRESH_BINARY)
	cv2.imwrite('test_resultw.jpg', thr)
	thr = cv2.imread('test_resultw.jpg')
	pattern_img = cv2.imread('pattern.jpg', 0)
	pattern(thr, pattern_img)

if __name__ == "__main__":
	print("START")
	test()
