import numpy as np
import pickle
import socket
import os
##import face_recognition
import os
import pickle
from PIL import Image
import cv2
from glob import glob

######################

import RPi.GPIO as GPIO
import time
#GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers

GPIO.setwarnings(False)

RELAIS_1_GPIO = 17
RELAIS_2_GPIO = 27
RELAIS_3_GPIO = 5
RELAIS_4_GPIO = 6


GPIO.setup(RELAIS_1_GPIO, GPIO.OUT) # GPIO Assign mode
GPIO.setup(RELAIS_2_GPIO, GPIO.OUT)
GPIO.setup(RELAIS_3_GPIO, GPIO.OUT)
GPIO.setup(RELAIS_4_GPIO, GPIO.OUT)

######################

##########################################################
##########################################################
# Creating Common Connection Settings for all Connection made in this script.

IP = "localhost"  # localhost
Port = 1998

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((IP, Port))
# print(str(s.gettimeout()))

# Resources Used:
DatabaseFile = "/home/pi/python_server/dataset_faces.dat"  # "dataset_faces_copy.dat"  # '/home/pi/python_server/dataset_faces.dat'          /home/pi/python_server/dataset_faces.dat
imageDir = "/home/pi/python_server/Photos/"  # "Photos/"  # "/home/pi/python_server/Photos/"            /home/pi/python_server/Photos/
unknown_images = "/home/pi/python_server/Unknown_People/"  # "Unknown_People_test/"          /home/pi/python_server/Unknown_People/
LentghOfUnknonImagesPath = len(unknown_images)
VehicleDatabase = "/home/pi/python_server/VehicleDatabase.txt"
VehicleNameDatabase = "/home/pi/python_server/VehicleNameDatabase.txt"


##########################################################
##########################################################


def NewServer():
    # start listening for any operations from client.
    global all_face_encodings
    s.listen(10)
    print("socket is listening...")

    # Always looking to connections.
    while True:
        print("Waiting for next operation...")
        clientsocket, address = s.accept()
        print("Server Connected With Client...")

        #############Update#######################
        OpCode = clientsocket.recv(7).decode("utf-8", errors="replace")
        if OpCode == "?UPDATE":
            # reading name length
            name_length = clientsocket.recv(2).decode()
            print("Name_length is:" + name_length)
            # reading name
            name = clientsocket.recv(int(name_length)).decode()
            print("Name is :" + name)

            # reading photo length
            photo_length_list = []
            while True:
                tempbyte = clientsocket.recv(1).decode()
                print(tempbyte)
                if tempbyte != '$':
                    photo_length_list.append(tempbyte)
                else:
                    break
            photo_length = np.array(photo_length_list)
            photo_length_string = ''.join(photo_length)
            photo_length_int = int(photo_length_string)
            print("Photo_length is :" + photo_length_string)

            # check if image dir exist
            if not os.path.exists(imageDir):
                print("Dir not found creating dir...")
                os.mkdir(imageDir)

            # reading photo
            length = 0
            with open(imageDir + name + ".png", 'wb') as file:
                while length < photo_length_int:
                    bytes = clientsocket.recv(min(1024, (photo_length_int - length)))
                    length = length + len(bytes)
                    file.write(bytes)
                    print("Byte Length is: " + str(len(bytes)))
                    # print("Image Wrote Successfully.")
                file.close()
                print("Photo&Name wrote successfully.")

            # send ACK
            print("Photo&Name ACK sent. ")
            clientsocket.sendall("?SYNC_DONE\n".encode('utf-8'))

            # update person
            imageFile = imageDir + name + ".png"
            signal = BakeFaceEncoding(name, imageFile)

            if signal == 1:
                clientsocket.sendall("Member Added Successfully.\n".encode('utf-8'))
                os.system('reboot')
            if signal == 0:
                clientsocket.sendall("No Faces Found, Take Clear Photo of Member's Face\n".encode('utf-8'))
            if signal == 2:
                clientsocket.sendall("Multiple Faces Found, Take one member photo at a time.\n".encode('utf-8'))
            if signal == -1:
                clientsocket.sendall("Database is Busy!\n".encode('utf-8'))

            clientsocket.close()

        #############Delete#######################
        if OpCode == "?DELETE":
            # reading name length
            name_length = clientsocket.recv(2).decode()
            print("Name_length is:" + name_length)
            # reading name
            name = clientsocket.recv(int(name_length)).decode()
            print("Name is :" + name)

            # send ACK
            print("Name ACK sent. ")
            clientsocket.sendall("?SYNC_DONE\n".encode('utf-8'))

            # delete person from dataset
            signal, PoppedName = DeletePerson(name)
            if PoppedName is None:
                print("bhuchal")
            if signal == 2:
                clientsocket.sendall((PoppedName + " has been Blocked\n").encode('utf-8'))
                print(PoppedName + " has been Blocked.")

            if signal == 3:
                clientsocket.sendall(("Member is Blocked already\n").encode('utf-8'))
                print("Member is Blocked already.")

            clientsocket.close()

        if OpCode == "?RETREV":
            print("grab started...")

            try:
                f = open(DatabaseFile, 'rb')
                all_face_encodings = pickle.load(f)
            except IOError:
                clientsocket.sendall("Database is busy!".encode('utf-8'))

            known_face_names = list(all_face_encodings.keys())

            NoOfPeople = str(len(known_face_names)) + "\n"
            print("NoOfPeople is:" + NoOfPeople)
            clientsocket.sendall(NoOfPeople.encode('utf-8'))

            Names = []
            PhotoSizes = []
            Photos = []
            for name in known_face_names:
                ReadyName = str(name) + "\n"
                Names.append(ReadyName)
                try:
                    # if person_photo available
                    imageFile = open(imageDir + "/" + name + ".png", 'rb')

                except IOError:
                    # if person_photo not available
                    imageFile = open(imageDir + "/" + "unknown_person" + ".png", 'rb')
                    print("Image is not available!")

                ImageContent = imageFile.read()
                imageFile.close()
                imageSize = len(ImageContent)
                imageSize_str = str(imageSize) + "\n"
                PhotoSizes.append(imageSize_str)
                Photos.append(ImageContent)

            print("Names are:" + str(Names))
            print("Photo Sizes are:" + str(PhotoSizes))

            for name in Names:
                clientsocket.sendall(name.encode('utf-8'))
            for PhotoSize in PhotoSizes:
                clientsocket.sendall(PhotoSize.encode('utf-8'))

            i = 1
            for Photo in Photos:
                print("Waiting for connection " + str(i))
                clientsocket, address = s.accept()
                print("Connection " + str(i))
                clientsocket.sendall(Photo)
                print("Photo sent.")
                i += 1
                # print("Photos are:" + str(Photo)+"\n")
            clientsocket.close()

        if OpCode == "?UNKNON":
            ImageFileNames = []
            PhotoSizes = []
            Photos = []

            # getting files's names inside unknown_dir
            NoOfCharInUnknownFolder = LentghOfUnknonImagesPath
            path = unknown_images
            for file in glob(path + "*"):
                ImageFileNames.append((str(file).split("\ ")[-1])[NoOfCharInUnknownFolder:])
                # print(files)

            # sending no-of-images************************
            NoOfUnknownPhotos = len(ImageFileNames)
            print("length of imagefileNames is: " + str(NoOfUnknownPhotos))
            clientsocket.sendall((str(NoOfUnknownPhotos) + "\n").encode('utf-8'))
            print("No of Unknon Images are: " + str(NoOfUnknownPhotos))

            # sending all ImageFileNames******************
            for onefilename in ImageFileNames:
                clientsocket.sendall((onefilename + "\n").encode('utf-8'))
            print("Files are: " + str(ImageFileNames))

            # Making files & it's sizes ready to send
            for eachFile in ImageFileNames:
                try:
                    # if person_photo available
                    imageFile = open(unknown_images + eachFile, 'rb')

                except IOError:
                    # if person_photo not available
                    imageFile = open(imageDir + "/" + "unknown_person" + ".*", 'rb')
                    print("Image is not available!")

                ImageContent = imageFile.read()
                imageFile.close()

                imageSize = len(ImageContent)
                imageSize_str = str(imageSize) + "\n"

                PhotoSizes.append(imageSize_str)
                Photos.append(ImageContent)

            print("Photo Sizes are:" + str(PhotoSizes))
            print("Photos are: " + str(Photos))
            # all file sizes and file itself are in RAM now
            # now send these to client

            # sending all photoSizes******************
            for PhotoSize in PhotoSizes:
                clientsocket.sendall(PhotoSize.encode('utf-8'))

            # sending all photos******************
            i = 1
            for eachPhotoFile in Photos:
                print("Waiting for connection " + str(i))
                clientsocket, address = s.accept()
                print("Connection " + str(i))
                clientsocket.sendall(eachPhotoFile)
                print("Photo sent.")
                i += 1
                # print("Photos are:" + str(Photo)+"\n")
            clientsocket.close()

        if OpCode == "?FREESV":
            # deleting all photos in unknown_images directory.
            try:
                # counting no of files in unknown_images directory.
                path, dirs, files = next(os.walk(unknown_images))
                NoOfFilesBeingDeleted = len(files)

                # deleting all files in unknown_images directory.
                print("No of files are: " + str(NoOfFilesBeingDeleted))
                filelist = [f for f in os.listdir(unknown_images)]
                for f in filelist:
                    os.remove(os.path.join(unknown_images, f))

                # sending no of files deleted and ACK message.
                clientsocket.sendall(
                    (str(NoOfFilesBeingDeleted) + " Files Were Deleted Successfully\n").encode('utf-8'))
                print("FreeSv ACK sent successfully.")

            except OSError:
                clientsocket.sendall("Failed to delete photos!\n".encode('utf-8'))
                print("Can't Free the server!")

        if OpCode == "?EMEGNC":
            GateOP = clientsocket.recv(9).decode("utf-8", errors="replace")
            if (GateOP == "OPEN_GATE"):
                clientsocket.sendall("Opening Gate\n".encode('utf-8'))
                print("Opening Gate...")
                OpenGate()
                clientsocket.sendall("Gate is Open\n".encode('utf-8'))
            if (GateOP == "CLOSEGATE"):
                clientsocket.sendall("Closing Gate\n".encode('utf-8'))
                print("Closing Gate...")
                OpenGate()
                clientsocket.sendall("Gate is close\n".encode('utf-8'))
            if (GateOP == "TIMEDOPEN"):
                clientsocket.sendall("OpeningGate for small duration\n".encode('utf-8'))
                print("TimedOpening Gate...")
                OpenGateForLimitedTime()
                clientsocket.sendall("Gate has been closed\n".encode('utf-8'))

        if OpCode == "?VCLDEL":
            # receive vehicle_number
            vehicle_number_length = clientsocket.recv(2).decode()
            vehicle_number = str(clientsocket.recv(int(vehicle_number_length)).decode())

            vehicle_name_length = clientsocket.recv(2).decode()
            vehicle_name = str(clientsocket.recv(int(vehicle_name_length)).decode())

            # check if VehicleDatabase exist
            if not os.path.exists(VehicleDatabase):
                print("Dir not found creating dir...")
                os.mkdir(VehicleDatabase)

            file = open(VehicleDatabase, "r")
            VehNumbers = file.readlines()
            file.close()

            numberDeleted = False
            i = 0
            while i <= len(VehNumbers):
                OneNumber = VehNumbers[i]
                if OneNumber == vehicle_number:
                    DeletedVehicleNumber = VehNumbers.pop(i)
                    print("Vehicle Number: " + str(DeletedVehicleNumber) + " has been deleted successfully.")
                    numberDeleted = True
                    break
                i += 1

            # check if VehicleDatabase exist
            if not os.path.exists(VehicleNameDatabase):
                print("Dir not found creating dir...")
                os.mkdir(VehicleNameDatabase)

            if numberDeleted:
                file = open(VehicleNameDatabase, "r")
                VehNames = file.readlines()
                file.close()

                nameDeleted = False
                i = 0
                while i <= len(VehNames):
                    OneName = VehNames[i]
                    if OneName == vehicle_name:
                        DeletedVehicleName = VehNames.pop(i)
                        print("Vehicle Name: " + str(DeletedVehicleName) + " has been deleted successfully.")
                        nameDeleted = True
                        break
                    i += 1

                file = open(VehicleDatabase, "w")
                file.writelines(VehNumbers)
                file.close()

                file = open(VehicleNameDatabase, "w")
                file.writelines(VehNames)
                file.close()

                clientsocket.sendall("?SYNC_DONE".encode("utf-8"))
                clientsocket.sendall("Vehicle Has Been Blocked Successfully".encode("utf-8"))
            else:
                clientsocket.sendall("?SYNC_DONE".encode("utf-8"))
                clientsocket.sendall("Vehicle Was Never Registered".encode("utf-8"))

        if OpCode == "?VCLUPD":
            # receive vehicle_number
            vehicle_number_length = clientsocket.recv(2).decode()
            vehicle_number = str(clientsocket.recv(int(vehicle_number_length)).decode())

            vehicle_name_length = clientsocket.recv(2).decode()
            vehicle_name = str(clientsocket.recv(int(vehicle_name_length)).decode())

            # check if VehicleDatabase exist
            if not os.path.exists(VehicleDatabase):
                print("Dir not found creating dir...")
                os.mkdir(VehicleDatabase)

            # check if it exits already or not
            file = open(VehicleDatabase, "r")
            VehNumbers = file.readlines()
            file.close()

            numberFound = False
            for OneNumber in VehNumbers:
                if OneNumber == vehicle_number:
                    numberFound = True
                    break

            if numberFound:
                clientsocket.sendall("?SYNC_DONE".encode("utf-8"))
                clientsocket.sendall("Member is Already Added!\n".encode("utf-8"))
            else:
                file = open(VehicleDatabase, "a")
                file.write("\n" + vehicle_number)
                file.close()

                # check if VehicleDatabase exist
                if not os.path.exists(VehicleNameDatabase):
                    print("Dir not found creating dir...")
                    os.mkdir(VehicleNameDatabase)

                file1 = open(VehicleNameDatabase, "a")
                file1.write("\n" + vehicle_name)
                file1.close()
                clientsocket.sendall("?SYNC_DONE".encode("utf-8"))
                clientsocket.sendall("Member has been added successfully!\n".encode("utf-8"))

        if OpCode == "?RECVDB":

            # check if VehicleDatabase exist
            if not os.path.exists(VehicleDatabase):
                print("Dir not found creating dir...")
                os.mkdir(VehicleDatabase)

            file = open(VehicleDatabase, "r")
            VehNumbers = file.readlines()
            file.close()

            NoOfVehicles = len(VehNumbers) + "\n"
            clientsocket.sendall(NoOfVehicles.encode("utf-8"))

            for eachNumber in VehNumbers:
                readyNumber = eachNumber + "\n"
                clientsocket.sendall(readyNumber.encode("utf-8"))

            # check if VehicleDatabase exist
            if not os.path.exists(VehicleNameDatabase):
                print("Dir not found creating dir...")
                os.mkdir(VehicleNameDatabase)

            file = open(VehicleNameDatabase, "r")
            VehNames = file.readlines()
            file.close()

            for eachName in VehNames:
                readyName = eachName + "\n"
                clientsocket.sendall(readyName.encode("utf-8"))

            clientsocket.send("VehicleDatabase Received Successfully".encode("utf-8"))


def extendActuator():
    print("Extneding")
    GPIO.output(RELAIS_1_GPIO, GPIO.HIGH)
    GPIO.output(RELAIS_2_GPIO, GPIO.LOW)
    GPIO.output(RELAIS_3_GPIO, GPIO.HIGH)
    GPIO.output(RELAIS_4_GPIO, GPIO.LOW)


def retractActuator():
    print("Retracting")
    GPIO.output(RELAIS_1_GPIO, GPIO.LOW)
    GPIO.output(RELAIS_2_GPIO, GPIO.HIGH)
    GPIO.output(RELAIS_3_GPIO, GPIO.LOW)
    GPIO.output(RELAIS_4_GPIO, GPIO.HIGH)


def stopActuator():
    print("Stop")
    GPIO.output(RELAIS_1_GPIO, GPIO.LOW)
    GPIO.output(RELAIS_2_GPIO, GPIO.LOW)
    GPIO.output(RELAIS_3_GPIO, GPIO.LOW)
    GPIO.output(RELAIS_4_GPIO, GPIO.LOW)


def OpenGate():
    retractActuator()
    time.sleep(32)
    stopActuator()


def CloseGate():
    extendActuator()
    time.sleep(32)
    stopActuator()


def OpenGateForLimitedTime():
    retractActuator()
    time.sleep(15)

    stopActuator()
    time.sleep(2)

    extendActuator()
    time.sleep(15)

    stopActuator()
    time.sleep(2)


def DeletePerson(name):
    signal = 0
    DeletedName = ""
    try:
        f = open(DatabaseFile, 'rb')
        all_face_encodings = pickle.load(f)
        f.close()
        # print(str(all_face_encodings))

        try:
            PoppedName = all_face_encodings.pop(name)
            signal = 2
            DeletedName = PoppedName
        except KeyError:
            signal = 3
            DeletedName = None

        try:
            with open(DatabaseFile, 'wb') as f1:
                pickle.dump(all_face_encodings, f1)
        except IOError:
            signal = -1
            DeletedName = None
    except IOError:
        signal = -1
        DeletedName = None

    return signal, DeletedName


def BakeFaceEncoding(name, imageFile):
    print("image dir to find face is: " + imageFile)
    print(f"Backing Face-Encoding with Received photo & name.")
    dir = imageFile
    person = name

    face_encodings = {}
    face = face_recognition.load_image_file(dir)
    # calculate no. of face in sample-image
    face_bounding_boxes = face_recognition.face_locations(face)
    no_of_faces = len(face_bounding_boxes)

    if no_of_faces == 0:
        print("No Faces Found!")
        return 0
    if no_of_faces == 1:
        if not os.path.exists(DatabaseFile):
            print("DatabaseFile not found creating it...")
            os.mkdir(DatabaseFile)
        try:
            with open(DatabaseFile, 'rb') as f:
                loaded_encodings = pickle.load(f)
        except IOError:
            return -1
        try:
            with open(DatabaseFile, 'wb') as f:
                loaded_encodings[person] = face_recognition.face_encodings(face)[0]
                pickle.dump(loaded_encodings, f)
                return 1
        except IOError:
            return -1
    else:
        print(person + "_img contains multiple faces!")
        return 2


def SendNamePhoto(name):
    s.listen(999)
    print("socket is listening...")
    clientsocket, address = s.accept()
    print(f"Connection from {address} has been established!")

    # send name_delimeter
    clientsocket.sendall("?name\n".encode('utf-8'))
    # send name
    name1 = name + "\n"
    print("Name was sent succesfully.")
    clientsocket.sendall(name1.encode('utf-8'))

    # send image_delimeter
    clientsocket.sendall("?start\n".encode('utf-8'))
    # send image
    imageFile = open("hand.jpg", 'rb')
    Imagecontent = imageFile.read()
    imageSize = len(Imagecontent)
    print("ImageSize is:" + str(imageSize))

    # send imageSize
    imageSize_str = str(imageSize) + "\n"
    clientsocket.sendall(imageSize_str.encode('utf-8'))
    # send imageFile_delimeter
    clientsocket.sendall("?imageFile\n".encode('utf-8'))
    clientsocket.close()

    # Creating new Connetion to send music
    s.listen(999)
    print("socket is listening...")
    clientsocket, address = s.accept()
    print(f"Connection from {address} has been established!")
    print("Ready to receive Image....")

    # send imageFile
    clientsocket.sendall(Imagecontent)
    print("Content type is :" + str(type(Imagecontent)))
    print("Image File Content is : " + str(Imagecontent))
    print("Image was sent succesfully.")

    # receive success ACK


def GrabCards():
    """
def Server():
    jump = False


    # Always looking to connections.
    while True:
        if jump == False:
            print("Waiting for next operations...")
            clientsocket, address = s.accept()
            print("Server Connected With Client...")

            # operation delimiter
            sayit = False
            if not clientsocket.recv(4).decode('utf-8') == "?OPE":
                sayit = True
                continue
            sayit = False
            print("Received ?OPE delimiter.")

            received_op = clientsocket.recv(1).decode('utf-8')
            print("Operation is : " + received_op)

            if sayit == True:
                clientsocket.sendall("Select a Operation\n".encode('utf-8'))
                print("Select a Operation!")
            else:
                clientsocket.sendall("Operation Selected Successfully.\n".encode('utf-8'))
                print("sending Operation Selected Successfully.....")
            clientsocket.close()
            jump = False

        # if operation is APPEND
        if SelectOp(received_op) == "APPEND":
            print("Append-Operation is being done...")
            result = BakeFaceEncoding()

            #create connection for sending ACK
            #Warning! hide the navMenu in app until this connection successfully sends ACK
            # or closes connection otherwise it will stuck here for making a connection to send ack
            #and no one will listen in app
            #recieveACK function handles this connection in APP
            s.listen(999)
            print("socket is listening...")
            CSckt, CAddress = s.accept()
            print(f"Connection from {address} has been established!")


            CSckt.sendall("?ACK\n".encode('utf-8'))
            if result == 3:
                # it means user didn't ADD any person,
                # just went to some other menu option so continue server loop
                # for listning to next operation sent by user.
                continue
            if result == -1:
                CSckt.sendall("Database-Resource is not available!\n".encode('utf-8'))
                continue
            if result == 0:
                CSckt.sendall("No Faces Found!\n".encode('utf-8'))
                jump = True
                received_op = '1'
                continue
            if result == 1:
                CSckt.sendall("Person Added Successfully.\n".encode('utf-8'))
                print("Person Added Successfully.")
                continue
            if result == 2:
                CSckt.sendall("Multiple Faces Found!\n".encode('utf-8'))
                jump = True
                received_op = '1'
                continue
            CSckt.close()

        # if operation is DELETE
        if SelectOp(received_op) == "DELETE":
            print("Delete-Operation is being done...")
            result = DeleteOP()

            clientsocket.sendall("?ACK\n".encode('utf-8'))
            if result == -1:
                clientsocket.sendall("Database-Resource is not available!\n".encode('utf-8'))
                continue
            if result == 1:
                clientsocket.sendall("Person Removed Successfully.\n".encode('utf-8'))
                print("Delete-Operation is done successfully.")
                continue


def SelectOp(op):
    switcher = {
        '1': "APPEND",
        '2': "DELETE",
    }
    return (switcher.get(op, "INVALID_OP!"))

# File Transfer
def RecieveNamePhoto():
    print("Reading Name & Photo...")
    # Reading Op byte

    # Reading name in pure python
    ############################################################1st python's socket connection.
    s.listen(999)
    print("socket is listening...")
    clientsocket, address = s.accept()
    print(f"Connection from {address} has been established!")

    # checking name delimeter
    temp = str(clientsocket.recv(5).decode())
    print("Temp is: "+temp)
    if (temp != "?NAME") and (str(temp[4]) != "1"):
        	return None, None
    else:
      print("switching back to reciving name & photo option.")

    # reads first 2 bytes for name's length in bytes
    name_length = clientsocket.recv(2).decode()
    print("Name_length is:" + name_length)
    # recieve name
    name = clientsocket.recv(int(name_length)).decode()
    print("Name is :" + name)
    clientsocket.close()

    ################################################################2nd python's socket connection.
    s.listen(999)
    print("socket is listening...")
    clientsocket, address = s.accept()
    print(f"Connection from {address} has been established!")

    # reading photo delimeter
    if not str(clientsocket.recv(6).decode()) == "?IMAGE":
        return None, None
    print("IMAGE delimiter recieved successfully.")

    # reading photo length
    photo_length_list = []
    while True:
        tempbyte = clientsocket.recv(1).decode()
        print(tempbyte)
        if tempbyte != '$':
            photo_length_list.append(tempbyte)
        else:
            break
    photo_length = np.array(photo_length_list)
    photo_length_string = ''.join(photo_length)
    photo_length_int = int(photo_length_string)
    print("Photo_length is :" + photo_length_string)
    clientsocket.close()

    ################################################################3rd python's socket connection.
    s.listen(999)
    print("socket is listening...")
    clientsocket3, address = s.accept()
    print(f"Connection from {address} has been established!")

    #delimter for receiving photo
    temp = clientsocket3.recv(6).decode()
    if not temp == "?image":
        return None, None
    print("Image delimiter recieved successfully.")
    print("Image delimiter is:"+str(temp))

    if not os.path.exists(imageDir):
        print("Dir not found creating dir...")
        os.mkdir(imageDir)

    # reading photo
    length = 0
    with open(imageDir + name + ".png", 'wb') as file:
        while length < photo_length_int:
            bytes = clientsocket3.recv(min(1024, (photo_length_int - length)))
            length = length+len(bytes)
            file.write(bytes)
            print("Byte Length is: "+str(len(bytes)))
            #print("Image Wrote Successfully.")
        file.close()
        print("Photo wrote successfully.")
    clientsocket3.close()
    # s.close()

    imageFile = imageDir + name + ".png"
    return name, imageFile
def DeleteOP():
    # Reading Op byte
    print("Delete-Operation is being done...")

    # Read name to delete
    s.listen(999)
    print("socket is listening...")
    clientsocket, address = s.accept()
    print(f"Connection from {address} has been established!")

    # receive name delimeter
    #-------------------------------------#
    # reads first 2 bytes for name's length in bytes
    name_length = clientsocket.recv(2).decode()
    print("DeleteName_length is:" + name_length)

    # recieve name
    delete_name = clientsocket.recv(int(name_length)).decode()
    print("DeleteName is :" + delete_name)
    clientsocket.close()

    DeletePerson(delete_name)
# RecieveNamePhoto()
# SendNamePhoto("sarvesh")
"""
    """
                    if imageSize > 10000:
                        #then compress image first
                        temp_image = Image.open(imageDir + "/" + name + ".png")
                        temp_image = temp_image.resize((240, 320), Image.ANTIALIAS)
                        temp_image.save(imageDir + "/" + name + ".png", "PNG")
                        temp_image.close()
                        imageFile = open(imageDir + "/" + name + ".png", 'rb')
                        ImageContent = imageFile.read()
                        imageSize = len(ImageContent)
                        imageFile.close()
    """


NewServer()
