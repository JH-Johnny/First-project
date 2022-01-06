import cv2
import numpy as np

img = cv2.imread('pattern.jpg',cv2.IMREAD_COLOR)
print("read!!")
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imwrite('result_pattern.jpg', img)
print("DONE!")

