import pickle


f = open("/home/pi/python_server/dataset_faces.dat", 'rb')
all_face_encodings = pickle.load(f)
#all_face_encodings.pop(name)
print(str(all_face_encodings))