import os
import pickle
import threading
import socket
from threading import *

class peerShare(threading.Thread):
    def __init__(self, port, host, max_connection):
        threading.Thread.__init__(self)
        self.host = host
        self.semaphore = Semaphore(max_connection)
        self.port = port
        self.clnt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clnt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Set SO_REUSEADDR
        self.clnt.bind((self.host, self.port))
        self.clnt.listen(max_connection)

    def run(self):
        print("Now this peer is ready to share the files")
        while True:
            try:
                client, addr = self.clnt.accept()
                print("Got connection from", addr[0], " port at", addr[1])
                request = pickle.loads(client.recv(1024))
                if request[0] == 4:
                    file_path = os.path.join(os.getcwd(), 'SharingFiles', 'Uploads')
                    file_name = request[1]
                    full_path = os.path.join(file_path, file_name)
                    self.semaphore.acquire()
                    with open(full_path, "rb") as myfile:
                        rd = myfile.read(1024)
                        while rd:
                            client.send(rd)
                            rd = myfile.read(1024)
                    print('File Sent Successfully')
                self.semaphore.release()
            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                client.close()


def start_sharing(port, host):
    peer = peerShare(port, host, 5)
    peer.start()
