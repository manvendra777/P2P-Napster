# Peer to Peer File Sharing System

## Minimum Requirements
* Windows/Ubuntu Operating System
* Python3
* AWS EC2 Servers.

## Setup
* To setup intially, we need to .
* Create multiple AWS EC2 instances with Ubuntu and configure the network settings by adding a security rule.
* This will allow all the EC2 instances to communicate among each other using Python socket programming
* Create a Shared Files folder which will have two sub folders. One to upload files and another to download files
* Remember the path of the Shared Files directory.
* Upload all the code files and shared folders to all of the EC2 instances. 
* Also update your server ip in the new_client.py file

## Usage
* In the terminal of the first EC2 instance:
    * ```python3 new_server.py```
* This will start the super peer server.
* Then start another server super peer to provide fault tolerance to the primary server in another EC2 instance.
* Then start multiple peers for efficient file sharing among the peers. 
    * ```python3 new_client.py```
* Once the client code is running:
    * ```Select 1 to register the files and the peer to the network```
    * ```Select 2 to query and search the files in the network```
    * ```Select 3 to view the list of files available in the network```
    * ```Select 4 to download the file after viewing the list of files. Enter the peer id, ip address and filename```
    * ```Select 5 to exit the network```

## Contributions
* System Design Research 
* Setting up the AWS Ec2 instances and the cloud environment
* Leader Election Algorithm 
* Resource Discovery Algorithm
* Multicast for super peer server failure Algorithm (Gossip)
* Research Analysis (Leader Election Algorithm and P2P systems) 

