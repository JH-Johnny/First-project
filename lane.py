import numpy as np
import cv2
from matplotlib import pyplot as plt
from PIL import Image
import imutils

def invert_img(img):
    img = (255-img)
    return img

def canny(imgray):
    imgray = cv2.GaussianBlur(imgray, (5,5), 200)
    canny_low = 5
    canny_high = 150

    thresh = cv2.Canny(imgray,canny_low,canny_high)
    return thresh

def filtering(imgray):
    thresh = canny(imgray)

    minLineLength = 1
    maxLineGap = 1


    lines = cv2.HoughLines(thresh,1,np.pi/180,0)
    #lines = cv2.HoughLinesP(thresh,2,np.pi/180,100,minLineLength,maxLineGap)

    # Code for HoughLinesP
    '''
    for i in range(0,lines.shape[0]):
        for x1,y1,x2,y2 in lines[i]:
            cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
    '''

    # Code for HoughLines

    for i in range(0,5):
        for rho,theta in lines[i]:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))

            cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)


    return thresh


img = cv2.imread('test.png')


imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

img = imutils.resize(img, height = 500)
imgray = imutils.resize(imgray, height = 500)

thresh = filtering(imgray)

cv2.imshow('original', img)
cv2.imshow('result', thresh)
cv2.waitKey(0)