import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import RPi.GPIO as GPIO
import os, datetime, threading, sys

#물방울 감지시 사진이 찍히는 최소 간격?
TIMEDIFF_SECOND = 1

BUZZER_PIN = 4
timeout = 0

def sort_contours(cnts, method="left-to-right"):
    # initialize the reverse flag and sort index
    reverse = False
    i = 0
    
    # handle if we need to sort in reverse
    if method == "right-to-left" or method == "bottom-to-top":
        reverse = True
        
    # handle if we are sorting against the y-coordinate rather than
    # the x-coordinate of the bounding box
    if method == "top-to-bottom" or method == "bottom-to-top":
        i = 1
        
    # construct the list of bounding boxes and sort them from top to
    # bottom
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
        key=lambda b:b[1][i], reverse=reverse))
    
    # return the list of sorted contours and bounding boxes
    return (cnts, boundingBoxes)


def get_centres(cnts):
    centres = []
    
    for i in range(len(cnts)):
        moments = cv2.moments(cnts[i])
        if moments['m10'] == 0 or moments['m00'] == 0 or moments['m01'] == 0:
            continue
            
        centres.append((int(moments['m10']/moments['m00']), 
                        int(moments['m01']/moments['m00'])))
    
    return centres


def find_bubble(img):
    _, cnts, _ = cv2.findContours(img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_KCOS)
    
    if(len(cnts) > 0):
        cnts, _ = sort_contours(cnts, method="left-to-right")
        cnts = [cv2.approxPolyDP(cnt, 1, True) for cnt in cnts] #default 4
        centres = get_centres(cnts)

    else:
        centres = []

    return centres


def preprocess_img(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.resize(img, (0,0), fx=0.3, fy=0.3)
    edges = cv2.Canny(img, 57, 142)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (21,21)))
    # edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (21,21)))
    # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

    # img = clahe.apply(img)
    # img = cv2.Canny(img, 127, 225)
    # res = cv2.resize(img, None,fx=2, fy=2, interpolation = cv2.INTER_CUBIC)
    # res = res[220:430][:].copy() # ROI
	
    return edges

def buzzer_off():
    global timeout
    global BUZZER_PIN
    print("Now timeout : " + str(timeout))
    if timeout == 0 :
        GPIO.output(BUZZER_PIN, False)
    else :
        timeout = timeout - 1
    threading.Timer(1, buzzer_off).start()


tempImg = False
before = datetime.datetime.now()
def visualize(img, centres):
    global timeout
    global before
    global tempImg
    now = datetime.datetime.now()
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    count = len(centres)
	# 감지된 외곽선이 2개 이상일 경우에는 공기층이 있는 것으로 판단하여 저장
    if count > 1 :
        print("SAVE_PROCESSING")
        GPIO.output(BUZZER_PIN, True)
		#1초가 지난 후면
        if before + datetime.timedelta(seconds=TIMEDIFF_SECOND) < now :
            cv2.imwrite(str(now) + '_processing.png', img)
            cv2.imwrite(str(now) + '_unmark.png', tempImg)
        timeout = 10
		
    for idx in range(1, len(centres), 2):  
        length = np.array(centres[idx]) - np.array(centres[idx-1])
        if length[0] < 0:
            continue

        cv2.circle(img, centres[idx-1], 1, (0,255,0), 5)
        cv2.circle(img, centres[idx], 1, (0,255,0), 5)
        cv2.line(img, centres[idx-1], centres[idx], (0,255,0), 1)

        point = centres[idx-1]
        cv2.putText(img, str(length[0]*0.008)+"cm", tuple([point[0], point[1]+50]), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), thickness=1)
    if count > 1 :
		#1초가 지난 후면
        if before + datetime.timedelta(seconds=TIMEDIFF_SECOND) < now :
            print("SAVE_MARK")
            cv2.imwrite(str(now) + '_mark.png', img)
    cv2.imshow("mark", img)
    return img
 

def check_camera() :
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

if __name__ == "__main__":
    global tempImg
    try :
        if "-f" not in sys.argv :
            check_camera()
        timeout = 0
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BUZZER_PIN, GPIO.OUT)
        cap = cv2.VideoCapture(0)
        # threading.Timer(1, buzzer_off).start()        
        while cap.isOpened():
            _, img = cap.read()
            tempImg = img
            cv2.imshow("original", img)
            cv2.imwrite("test_raw.png", img)
            img = preprocess_img(img)
            centres = find_bubble(img)
        
            for idx in range(1, len(centres), 2):
                length = np.array(centres[idx]) - np.array(centres[idx-1])
        
                if length[0] < 0:
                    continue
        
                print(length[0] * 0.008) 
            
            cv2.imwrite("test.png", visualize(img, centres))
        
            if cv2.waitKey(1) & 0xff == ord('q'):
                break
                
    except Exception as e :
        print(e)
    finally :    
        GPIO.cleanup()