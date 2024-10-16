import socket
import threading
import pickle as pk
from datetime import datetime
from threading import *
import time

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

#print("Your Computer Name is:" + hostname)
#print("Your Computer IP Address is:" + IPAddr)

class mainServer(threading.Thread):
    def __init__(self, max_connection):
        threading.Thread.__init__(self)
        self.host = IPAddr
        self.semaphore = Semaphore(max_connection)
        self.port = 3456
        self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Server is live")
        self.serv.bind((self.host, self.port))
        self.serv.listen(max_connection)
        self.files = []
        self.keys = ['peer_id', 'file_name', 'date_added', 'ip_address', 'last_heartbeat']
        print("Get connected at", self.host, "on port number", self.port)
        self.client_timeout = 300 

    def run(self):
        threading.Thread(target=self.check_timeouts, daemon=True).start()
        while True:
            client, addr = self.serv.accept()
            print("Connected to", addr[0], "Port at", addr[1])

            request = pk.loads(client.recv(1024))

            if request[0] == 1:
                print("Peer", addr[1], "Add new file")
                self.semaphore.acquire()
                self.register(request[1], request[2], str(datetime.now()), addr[0])
                ret = "File Registered Successfully."
                client.send(bytes(ret, 'utf-8'))
                self.semaphore.release()
                client.close()
            elif request[0] == 2:
                print("Peer", addr[1], "Searching for a file")
                self.semaphore.acquire()
                ret_data = pk.dumps(self.search_data(request[1]))
                client.send(ret_data)
                self.semaphore.release()
                client.close()
            elif request[0] == 3:
                print("Peer", addr[1], "Listing all files")
                self.semaphore.acquire()
                ret_data = pk.dumps(self.all_data())
                client.send(ret_data)
                self.semaphore.release()
                client.close()
            elif request[0] == 99:  # Heartbeat update
                self.update_heartbeat(request[1])
            else:
                continue

    def register(self, peer_id, file_name, date, ip_address):
        entry = [str(peer_id), file_name, str(date), str(ip_address), time.time()]
        self.files.insert(0, dict(zip(self.keys, entry)))

    def search_data(self, file_name):
        ret = []
        for item in self.files:
            if item['file_name'] == file_name:
                entry = [item['peer_id'], item['file_name'], item['date_added'], item['ip_address']]
                ret.insert(0, dict(zip(self.keys, entry)))
        return ret, self.keys

    def all_data(self):
        return self.files, self.keys
    
    def update_heartbeat(self, peer_id):
        with self.semaphore:
            for file in self.files:
                if file['peer_id'] == str(peer_id):
                    file['last_heartbeat'] = time.time()
    def send_heartbeat(self):
        while True:
            for server in self.servers:
                if server != self.host:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.connect((server, self.port))
                        sock.send(pk.dumps(('heartbeat', self.server_id)))
                        if(self.leader_id == self.server_id):
                            sock.send(pk.dumps('files', self.files))
            time.sleep(5)  # send heartbeat every 5 seconds
    def initiate_leader_election(self):
        """ Elect the server with the next lowest ID as the new leader and announce it """
        sorted_servers = sorted(self.servers)
        current_index = sorted_servers.index(self.host)
        new_leader_index = (current_index + 1) % len(sorted_servers)
        new_leader = sorted_servers[new_leader_index]
        self.update_leader(new_leader)
        self.announce_new_leader(new_leader)
        print(f"New leader elected: Server {new_leader}")
    
    def announce_new_leader(self, new_leader):
        """ Announce the new leader to all other servers """
        for server in self.servers:
            if server != self.host:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((server, self.port))
                    sock.send(pk.dumps(('new_leader', new_leader)))
        print(f"Announced new leader {new_leader} to all other servers.")

    def update_leader(self, new_leader):
        """ Update the leader information """
        self.leader_id = new_leader
        self.is_leader = (self.host == new_leader)
        print(f"Server {self.server_id} is now the leader: {self.is_leader}")

    def check_timeouts_leader(self):
        """ Check if the current leader has missed sending heartbeats and initiate leader election if necessary. """
        last_leader_heartbeat = time.time()
        while True:
            time.sleep(5)  # Frequency to check leader timeouts
            current_time = time.time()
            # Check only if this server is not the leader
            if not self.is_leader:
                if current_time - last_leader_heartbeat > self.leader_timeout:
                    print(f"Leader timeout detected. Leader {self.leader_id} failed to send heartbeat. Initiating leader election.")
                    self.initiate_leader_election()
                else:
                    print(f"Leader is active; last heartbeat received {current_time - last_leader_heartbeat} seconds ago.")
            else:
                print("This server is the leader, skipping leader timeout check.")
    def check_timeouts(self):
        while True:
            with self.semaphore:
                current_time = time.time()
                self.files = [file for file in self.files if current_time - file['last_heartbeat'] < self.client_timeout]
            time.sleep(60)


# Main
print("Welcome. Server is about to go live")
server = mainServer(5)
server.start()
