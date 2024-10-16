import os
import pickle
import threading
import socket
from threading import *
from peerShare import *
import time


class peerServer:
    def __init__(self):
        print("Welcome to peer to peer file sharing system")
        self.file_name = ""
        self.peer_port = 0
        self.server_ip = '192.168.0.211'
        self.server_port = 3456
        threading.Thread(target=self.send_heartbeat, daemon=True).start()

    def send_heartbeat(self):
        while True:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((self.server_ip, self.server_port))
                    # Assuming the peer ID is related to the peer_port
                    heartbeat_message = pickle.dumps([99, self.peer_port])
                    sock.send(heartbeat_message)
                time.sleep(60)  # Send heartbeat every 60 seconds
            except Exception as e:
                print(f"Error sending heartbeat: {e}")
    
    def start_server(self):
        while True:
            choice = input("Menu \n(1) Register\n(2) Search\n(3) List all files\n(4) Download\n(5) Exit server\n")
            choice = int(choice)
            if choice == 1:
                peer_id = input("Enter the 4 digit peer id: ")
                self.file_name = input("Enter file name: ")
                self.peer_port = int(peer_id)
                self.register()
                start_sharing(self.peer_port, '192.168.0.74')

            elif choice == 2:
                self.search()

            elif choice == 3:
                self.list_all()

            elif choice == 4:
                peer_id = input("Enter the 4 digit peer id: ")
                file_name = input("Enter file name: ")
                ip_address = input("Enter peer ip_address: ")
                self.download(int(peer_id), file_name, ip_address)

            elif choice == 5:
                break

            else:
                continue

    def register(self):
        client = socket.socket()
        client.connect(('192.168.0.211', 3456))
        register_data = [1, self.peer_port, self.file_name]
        data = pickle.dumps(register_data)
        client.send(data)
        state = client.recv(1024)
        print(state.decode('utf-8'))
        client.close()

    def search(self):
        client = socket.socket()
        client.connect(('192.168.0.211', 3456))
        file_name = input("Enter file name: ")
        register_data = [2, file_name]
        data = pickle.dumps(register_data)
        client.send(data)
        state = pickle.loads(client.recv(1024))
        self.print_list(state[0], state[1])
        client.close()

    def list_all(self):
        client = socket.socket()
        client.connect(('192.168.0.211', 3456))
        data = pickle.dumps([3])
        client.send(data)
        state = pickle.loads(client.recv(1024))
        self.print_list(state[0], state[1])
        client.close()

    def print_list(self, files, keys):
        if len(files) == 0:
            print("There is no file available")
        else:
            print("Peer ID  File Name    Date Added                        IP Address")
            for item in files:
                print(item[keys[0]],"  ",item[keys[1]], "    ", item[keys[2]], "    ", item[keys[3]])

    def download(self, peer_id, file_name, ip_address):
        client = socket.socket()
        client.connect((ip_address, peer_id))
        list_data = [4, str(file_name)]
        data = pickle.dumps(list_data)
        client.send(data)

        # file_path = os.path.join(, '..')
        file_path = os.path.join(os.getcwd(), 'SharingFiles')
        file_path = os.path.join(file_path, 'Downloads')

        with open(os.path.join(file_path, file_name), 'wb') as myfile:
            while True:
                data = client.recv(1024)
                print(data.decode("utf-8"))
                if not data:
                    myfile.close()
                    break
                myfile.write(data)
        client.close()
        print('File is downloaded successfully.')


peer = peerServer()
peer.start_server()
