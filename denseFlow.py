import numpy as np
import cv2 as cv
import argparse
import signal
import sys

# parser = argparse.ArgumentParser(description='This sample demonstrates Lucas-Kanade Optical Flow calculation. \
#                                               The example file can be downloaded from: \
#                                               https://www.bogotobogo.com/python/OpenCV_Python/images/mean_shift_tracking/slow_traffic_small.mp4')
# parser.add_argument('image', type=str, help='path to image file')
# args = parser.parse_args()
# cap = cv.VideoCapture(args.image)
cap = cv.VideoCapture(0)

ret, frame1 = cap.read()
scale_percent = 25 # percent of original size
width = int(frame1.shape[1] * scale_percent / 100)
height = int(frame1.shape[0] * scale_percent / 100)
dim = (width, height) 
fourcc = cv.VideoWriter_fourcc(*'DIVX')
out = cv.VideoWriter('out.avi',fourcc,20.0, dim)

frame1 = cv.resize(frame1, dim, interpolation = cv.INTER_AREA) 
prvs = cv.cvtColor(frame1,cv.COLOR_BGR2GRAY)

hsv = np.zeros_like(frame1)
hsv[...,1] = 255
frame = 1

def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        out.release()
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

while(1):
    ret, frame2 = cap.read()
    try:
        frame2 = cv.resize(frame2, dim, interpolation = cv.INTER_AREA) 
    except Exception as e:
        break
    next = cv.cvtColor(frame2,cv.COLOR_BGR2GRAY)
    flow = cv.calcOpticalFlowFarneback(prvs,next, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    mag, ang = cv.cartToPolar(flow[...,0], flow[...,1])
    # hsv[...,0] = ang*180/np.pi/2
    # hsv[...,2] = cv.normalize(mag,None,0,255,cv.NORM_MINMAX)
    hsv[..., 2] = cv.normalize(mag, None, 0, 255, cv.NORM_MINMAX)
    bgr = cv.cvtColor(hsv,cv.COLOR_HSV2BGR)
    # cv.namedWindow('image',cv.WINDOW_NORMAL)
    # cv.imshow('image',bgr)
    out.write(bgr)
    # cv.resizeWindow('image', 600,600)
    # k = cv.waitKey(30) & 0xff
    prvs = next
    print(frame)
    frame = frame+1
out.release()
