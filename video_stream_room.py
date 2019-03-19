import socket
import threading
import sys
import zmq
import base64
import numpy as np
import cv2

class ChatServer:
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    connections=[]

    def __init__(self):
        self.sock.bind(('0.0.0.0',10000))
        self.sock.listen(1)
        print("Server running on: ")
        print((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0])


    def handler(self,c,a):
        while True:
            data=c.recv(1024)
            for connection in self.connections:
                if(connection!=c):
                    connection.send(data)
            if not data:
                print(str(a[0])+':'+str(a[1]),"disconnected")
                self.connections.remove(c)
                c.close()
                break

    def run(self):
        while True:
            c,a=self.sock.accept()
            cThread=threading.Thread(target=self.handler,args=(c,a))
            cThread.daemon=True
            cThread.start()
            self.connections.append(c)
            print(str(a[0])+':'+str(a[1]),"connected")

class ChatClient:
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    user_name=""
    def sendMsg(self):
        while True:
            msg=input("")
            self.sock.send(bytes(self.user_name+"\t: "+msg,'utf-8'))
    def __init__(self,address,user_name):
        self.user_name=user_name
        self.sock.connect((address,10000))
        iThread=threading.Thread(target=self.sendMsg)
        iThread.daemon=True
        iThread.start()

        while True:
            data=self.sock.recv(1024)
            if not data:
                break
            print(str(data,'utf-8'))

class Streamer:
    context = zmq.Context()
    footage_socket = context.socket(zmq.PUB)
    camera = cv2.VideoCapture(0)

    def __init__(self):
        self.footage_socket.bind('tcp://*:5555')

    def video(self):
        while True:
            try:
                grabbed, frame = self.camera.read()  # grab the current frame
                frame = cv2.resize(frame, (640, 480))  # resize the frame
                encoded, buffer = cv2.imencode('.jpg', frame)
                jpg_as_text = base64.b64encode(buffer)
                self.footage_socket.send(jpg_as_text)

            except KeyboardInterrupt:
                self.camera.release()
                cv2.destroyAllWindows()
                break

    def run(self):
        videoThread=threading.Thread(target=self.video)
        videoThread.daemon=True
        videoThread.start()

class Viewer:
    context = zmq.Context()
    footage_socket = context.socket(zmq.SUB)

    def __init__(self,address):
        self.footage_socket.connect('tcp://'+address+':5555')
        self.footage_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))

    def video(self):
        while True:
            try:
                frame = self.footage_socket.recv_string()
                img = base64.b64decode(frame)
                npimg = np.fromstring(img, dtype=np.uint8)
                source = cv2.imdecode(npimg, 1)
                cv2.imshow("Stream", source)
                cv2.waitKey(1)

            except KeyboardInterrupt:
                cv2.destroyAllWindows()
                break

    def run(self):
        videoThread=threading.Thread(target=self.video)
        videoThread.daemon=True
        videoThread.start()

if(len(sys.argv)>1):
    viewer=Viewer(sys.argv[1])
    viewer.run()
    client=ChatClient(sys.argv[1],sys.argv[2])
else:
    streamer=Streamer()
    streamer.run()
    server=ChatServer()
    server.run()