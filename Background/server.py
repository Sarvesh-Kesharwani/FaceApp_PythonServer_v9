import socket


HOST = '0.0.0.0'
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((HOST, 1234))
s.listen(999)

while True:
    clientsocket, address = s.accept()
    print(f"Connetion from {address} has been established!")
    clientsocket.send(bytes("Welcome to the server!", "utf-8"))
    
    
    message = clientsocket.recv(1024).decode()
    print(message)
        
            
