import face_recognition
import picamera
import pickle
import numpy as np
from google_speech import Speech
import cv2
import os
from datetime import datetime
import time
import RPi.GPIO as GPIO

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

def Face(pirPin):
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

        #print("I see someone named {}!".format(name))

#GPIO.setwarnings(False)
print("Motion Sensor Alarm (CTRL+C to exit)")
time.sleep(.2)
print("Ready")


try:
    GPIO.add_event_detect(pirPin, GPIO.RISING, callback=Face)
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Quit")
    GPIO.cleanup()        

