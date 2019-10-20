import datetime
import imutils
import time
import cv2
import numpy as np
import sys
import time


def current_milli_time(): return int(round(time.time() * 1000))


class Robot():
    FRAME_WIDTH = 400

    def __init__(self):
        self.vs = cv2.VideoCapture(0)
        self.width = self.vs.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vs.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print(self.width, self.height)
        ret, frame = self.vs.read()
        self.firstFrame = None
        self.thresh = np.zeros_like(frame)
        self.frameDelta = np.zeros_like(frame)
        self.gray = None
        self.status = "SEARCHING"

        self.firstLockFrame = None
        self.locked = False

        self.target = None
        self.targetbounds = None
        self.lasttargetbounds = None
        self.didntmoveframes = 0

        self.tracker = None
    def updateframe(self):
        _, self.frame = self.vs.read()
        if self.frame is None:
            print("Failed to read frame!")
            return

        # resize the frame, convert it to grayscale, and blur it
        self.frame = imutils.resize(
            self.frame, width=self.FRAME_WIDTH, height=self.FRAME_WIDTH)
        self.rawframe = self.frame.copy()
    def reset(self):
        self.firstFrame = self.gray
        self.firstLockFrame = None
        self.locked = False
        self.status = "SEARCHING"
        self.tracker = None
        self.lasttargetbounds = None
        self.didntmoveframes = 0

    def make_tracker(self):
        tracker_type = "CSRT"
        if tracker_type == 'BOOSTING':
            tracker = cv2.TrackerBoosting_create()
        if tracker_type == 'MIL':
            tracker = cv2.TrackerMIL_create()
        if tracker_type == 'KCF':
            tracker = cv2.TrackerKCF_create()
        if tracker_type == 'TLD':
            tracker = cv2.TrackerTLD_create()
        if tracker_type == 'MEDIANFLOW':
            tracker = cv2.TrackerMedianFlow_create()
        if tracker_type == 'GOTURN':
            tracker = cv2.TrackerGOTURN_create()
        if tracker_type == 'MOSSE':
            tracker = cv2.TrackerMOSSE_create()
        if tracker_type == "CSRT":
            tracker = cv2.TrackerCSRT_create()
        # bbox = cv2.selectROI(self.rawframe, self.targetbounds)
        tracker.init(self.rawframe, self.targetbounds)
        return tracker

    def runLoop(self):
        self.updateframe()
        if self.status == "SEARCHING":
            # dont move
            self.get_initial_target()
        elif self.status == "LOCKED":
            self.find_locked_target()

        # draw the text and timestamp on the frame
        cv2.putText(self.frame, "Room Status: {}".format(self.status), (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(self.frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                    (10, self.frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
        cv2.imshow("Front camera", self.frame)
        if (self.locked):
            cv2.imshow("target reference", self.target)

        # show the frame and record if the user presses a key
        # cv2.imshow("Thresh", self.thresh)
        # cv2.imshow("Frame Delta", self.frameDelta)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            self.cleanup()
            sys.exit(0)
        if (key == ord("r")):
            self.reset()
            # pass
        if key == ord('p'):
            key = cv2.waitKey(0)  # wait, as a pause

    def cleanup(self):
        self.vs.release()
        cv2.destroyAllWindows()

    def find_locked_target(self):
        if (self.tracker == None):
            self.tracker = self.make_tracker()
            print("init tracker")
        else:
            status, self.targetbounds = self.tracker.update(self.frame)
            self.targetbounds = tuple([int(x) for x in self.targetbounds])
            if (self.lasttargetbounds):
                dx = abs(self.targetbounds[0] - self.lasttargetbounds[0])
                dy = abs(self.targetbounds[1] - self.lasttargetbounds[1])
                if (dx <= 6 and dy <= 6):
                    self.didntmoveframes += 1
                else:
                    self.didntmoveframes = max(self.didntmoveframes-1, 0)
                if (self.didntmoveframes > 5):
                    print("didnt move!")
                    self.reset()
                
        
            self.lasttargetbounds = self.targetbounds
            # print(self.targetbounds)
            if (not status):
                self.reset()
            x, y, w, h = self.targetbounds
            cv2.rectangle(self.frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            xpos = ((2 * x + w) / 2)# / self.width
            ypos = ((2 * y + h) / 2)# / self.height
            print(xpos, ypos)
            print(status)

    def get_initial_target(self):
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        blur_rad = 21
        gray = cv2.GaussianBlur(gray, (blur_rad, blur_rad), 0)

        # if the first frame is None, initialize it
        if self.firstFrame is None:
            self.firstFrame = gray
            return
        # compute the absolute difference between the current frame and
        # first frame
        frameDelta = cv2.absdiff(self.firstFrame, gray)
        THRESHOLD = 50
        thresh = cv2.threshold(frameDelta, THRESHOLD,
                               255, cv2.THRESH_BINARY)[1]

        # dilate the thresholded image to fill in holes, then find contours
        # on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        C_AREA = 500
        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < C_AREA:
                continue

            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(self.frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(self.frame, str(cv2.contourArea(c)), (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            # self.status = "MOTION"
            # TODO: wait a few frames, and grab the image
            if (self.firstLockFrame == None):
                # first time we've seen something, lets wait and see
                self.firstLockFrame = current_milli_time()
        if (self.firstLockFrame and len(cnts) > 0 and (current_milli_time() - self.firstLockFrame) > 750 and not self.locked):

            # a whole second
            # grab the largest frame
            maxIndx = 0
            maxVal = 0
            for i, c in enumerate(cnts):
                area = cv2.contourArea(c)
                if area > maxVal:
                    maxIndx = i
                    maxVal = area
            if (maxVal>C_AREA):
                largestSection = cnts[maxIndx]
                (x, y, w, h) = cv2.boundingRect(largestSection)

                self.target = self.rawframe[y:y + h, x:x + w]
                self.targetbounds = (x, y, w, h)
                self.locked = True
                self.status = "LOCKED"
            else:
                self.firstLockFrame = None
        # cv2.imshow("Frame Delta", frameDelta)
        self.thresh = thresh
        self.frameDelta = frameDelta
        self.gray = gray


if __name__ == "__main__":
    robot = Robot()
    while True:
        robot.runLoop()
