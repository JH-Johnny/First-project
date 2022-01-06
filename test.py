import numpy as np
import cv2
from matplotlib import pyplot as plt

cap = cv2.VideoCapture(0)

while True :
	_, img = cap.read()
	cv2.imshow("now", img);
