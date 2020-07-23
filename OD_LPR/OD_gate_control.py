# USAGE
# python real_time_object_detection.py --prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel

import argparse
import difflib
import time
import cv2
import imutils
import numpy as np
import pytesseract
from imutils.video import FPS
from imutils.video import VideoStream
import face_recognition
import picamera
import pickle
from google_speech import Speech
import os
from datetime import datetime
import time
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

pirPin = 26
RELAIS_1_GPIO = 17
RELAIS_2_GPIO = 27
RELAIS_3_GPIO = 5
RELAIS_4_GPIO = 6
GPIO.setup(pirPin, GPIO.IN) # GPIO Assign mode
GPIO.setup(RELAIS_1_GPIO, GPIO.OUT)
GPIO.setup(RELAIS_2_GPIO, GPIO.OUT)
GPIO.setup(RELAIS_3_GPIO, GPIO.OUT)
GPIO.setup(RELAIS_4_GPIO, GPIO.OUT)

def extendActuator(person):
    print("Extneding")
    GPIO.output(RELAIS_1_GPIO, GPIO.HIGH)
    GPIO.output(RELAIS_2_GPIO, GPIO.LOW)
    GPIO.output(RELAIS_3_GPIO, GPIO.HIGH)
    GPIO.output(RELAIS_4_GPIO, GPIO.LOW)
    time.sleep(person*7)

def retractActuator(person):
    print("Retracting")
    GPIO.output(RELAIS_1_GPIO, GPIO.LOW)
    GPIO.output(RELAIS_2_GPIO, GPIO.HIGH)
    GPIO.output(RELAIS_3_GPIO, GPIO.LOW)
    GPIO.output(RELAIS_4_GPIO, GPIO.HIGH)
    time.sleep(person*7)

def stopActuator():
    print("Stop")
    GPIO.output(RELAIS_1_GPIO, GPIO.LOW)
    GPIO.output(RELAIS_2_GPIO, GPIO.LOW)
    GPIO.output(RELAIS_3_GPIO, GPIO.LOW)
    GPIO.output(RELAIS_4_GPIO, GPIO.LOW)
    time.sleep(2)

def Face():
    #don't render frame.
    #uses picamera library to capture frames. 

    #Get a reference to the Raspberry Pi camera.
    camera = None
    while not camera:
        camera = picamera.PiCamera()
            
    camera.resolution = (320, 240)
    output = np.empty((240, 320, 3), dtype=np.uint8)

    #path to save unknown person's photos
    path = '/home/pi/python_server/Unknown_People/'

    #load known faces
    print("Loading known face image(s)")
    # Load face encodings
    while True:
        try:    
    	    with open(r'/home/pi/python_server/dataset_faces.dat', 'rb') as f:
                all_face_encodings = pickle.load(f)
                break
        except IOError:
            continue

    # Grab the list of names and the list of encodings
    known_face_names = list(all_face_encodings.keys())
    known_face_encodings = np.array(list(all_face_encodings.values()))

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    t_end = time.time() + 20*1
    while time.time() <= t_end:
        print("Capturing image.")
        # Grab a single frame of video from the RPi camera as a numpy array
        camera.capture(output, format="rgb")

        # Loop over each face found in the frame to see if it's someone we know.
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(output)
            print("Found {} faces in image.".format(len(face_locations)))

            face_encodings = face_recognition.face_encodings(output, face_locations)

            face_names = []
            known = False
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    known = True
                else:
                    name = "भवानी सेवा दल मेें आपका स्वागत है, आपकी एंट्री नहीं है, कृपया अपनी एंट्री कराये।"
                    now = datetime.now()
                    dt_string = now.strftime("%d-%m-%Y, %H-%M-%S")
                    cv2.imwrite(path + dt_string + '.jpg', output)
                face_names.append(name)

        print(*face_names, sep = ", ")
    
        #play names of detected people
        lang = "hi"
        sox_effects = ("speed", "1.0")
        for name in face_names:
            speech = Speech(name, lang)
            speech.play(sox_effects)
        
        if known == True:
            retractActuator(person=len(face_locations))
            stopActuator()
            extendActuator(person=len(face_locations))
            stopActuator()
            known = False

        #toggle process_this_frame var to run FR on alternate frames
        process_this_frame = not process_this_frame


        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    #release picamera resource
    if time.time() >= t_end:
        if camera:
           camera.close()
           
def LPR():
    def remove(string):
        return string.replace(" ", "")

    def check_if_string_in_file(file_name, string_to_search):
        """ Check if any line in the file contains given string """
        # Open the file in read only mode
        with open(file_name, 'r') as read_obj:
            # Read all lines in the file one by one
            for line in read_obj:
                # For each line, check if line contains the string
                if string_to_search in line:
                    return True
        return False


    img = cv2.imread('LP.jpg', cv2.IMREAD_COLOR)

    img = cv2.resize(img, (620, 480))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # convert to grey scale
    gray = cv2.bilateralFilter(gray, 11, 17, 17)  # Blur to reduce noise
    edged = cv2.Canny(gray, 30, 200)  # Perform Edge detection

    # find contours in the edged image, keep only the largest
    # ones, and initialize our screen contour
    cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]
    screenCnt = None

    # loop over our contours
    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)

        # if our approximated contour has four points, then
        # we can assume that we have found our screen
        if len(approx) == 4:
            screenCnt = approx
            break

    if screenCnt is None:
        detected = 0
        print("No contour detected")
    else:
        detected = 1

    if detected == 1:
        cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 3)

        # Masking the part other than the number plate
        mask = np.zeros(gray.shape, np.uint8)
        new_image = cv2.drawContours(mask, [screenCnt], 0, 255, -1, )
        new_image = cv2.bitwise_and(img, img, mask=mask)

        # Now crop
        (x, y) = np.where(mask == 255)
        (topx, topy) = (np.min(x), np.min(y))
        (bottomx, bottomy) = (np.max(x), np.max(y))
        Cropped = gray[topx:bottomx + 1, topy:bottomy + 1]

        # Read the number plate
        text = pytesseract.image_to_string(Cropped, config='--psm 11')
        print("Detected Number is:", text)
        string = text
        whitelist = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        filtered_text = ''.join(filter(whitelist.__contains__, text))
        print(filtered_text)

        cv2.imshow('image', img)
        cv2.imshow('Cropped', Cropped)

        if check_if_string_in_file('sample.txt', filtered_text):
            print('Registered')
        else:
            print('Not Registered')

        # print(''.join(open('sample.txt').read().split(",")))

        with open('sample.txt', 'r') as read_obj:
            # Read all lines in the file one by one
            for line in read_obj:
                if (difflib.SequenceMatcher(None, filtered_text, line).ratio()) > .75:
                    print("Registered")
                    print(difflib.SequenceMatcher(None, filtered_text, line).ratio())
                    break
                else:
                    print("Not Registered")

    # cv2.waitKey(0)
    cv2.destroyAllWindows()

def OD(pirPin):
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--confidence", type=float, default=0.2,
                    help="minimum probability to filter weak detections")
    args = vars(ap.parse_args())

    # initialize the list of class labels MobileNet SSD was trained to
    # detect, then generate a set of bounding box colors for each class
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
               "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
               "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
               "sofa", "train", "tvmonitor"]
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

    # load our serialized model from disk
    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe('MobileNetSSD_deploy.prototxt.txt', 'MobileNetSSD_deploy.caffemodel')

    # initialize the video stream, allow the cammera sensor to warmup,
    # and initialize the FPS counter
    print("[INFO] starting video stream...")
    vs = VideoStream(src=0).start()
    # vs = VideoStream(usePiCamera=True).start()
    time.sleep(2.0)
    fps = FPS().start()

    # loop over the frames from the video stream
    while True:
        # grab the frame from the threaded video stream and resize it
        # to have a maximum width of 400 pixels
        frame = vs.read()
        frame = imutils.resize(frame, width=400)

        # grab the frame dimensions and convert it to a blob
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                     0.007843, (300, 300), 127.5)

        # pass the blob through the network and obtain the detections and
        # predictions
        net.setInput(blob)
        detections = net.forward()

        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with
            # the prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence > args["confidence"]:
                # extract the index of the class label from the
                # `detections`, then compute the (x, y)-coordinates of
                # the bounding box for the object
                idx = int(detections[0, 0, i, 1])
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # draw the prediction on the frame
                label = "{}: {:.2f}%".format(CLASSES[idx],
                                             confidence * 100)
                cv2.rectangle(frame, (startX, startY), (endX, endY),
                              COLORS[idx], 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(frame, label, (startX, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
                if CLASSES[idx] == "person":
                    print("Person is Detected")
                    vs.stop()
                    Face()
                elif CLASSES[idx] == "car":
                    print("Car is detected")
                    i = 0
                    t_end = time.time() + .4
                    while time.time() < t_end:
                        frame = vs.read()
                        cv2.imwrite('LP' + str(i) + '.jpg', frame)
                        i += 1
                    LPR()

        # show the output frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

        # update the FPS counter
        fps.update()

    # stop the timer and display FPS information
    fps.stop()
    print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    # do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()
    
print("Motion Sensor Alarm (CTRL+C to exit)")
time.sleep(.2)
print("Ready")


try:
    GPIO.add_event_detect(pirPin, GPIO.RISING, callback=OD)
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Quit")
    GPIO.cleanup()
