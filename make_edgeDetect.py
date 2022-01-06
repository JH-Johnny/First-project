import cv2
import numpy as np

def make_edge(cap):
    ret, frame = cap.read()

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    img = clahe.apply(frame)

    edges = cv2.Canny(img, 127, 225)
    return edges
