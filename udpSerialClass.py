"""
This class is used for receiving the UDP packets from the Arduino.

It goes into an infinite while loop so has only the packet receiving functionality. 
"""


import time
import datetime
import struct
import redis
import socket
import sys
import smtplib

# Define IP address of the Redis server host machine
serverAddress = '10.1.1.1'

# Define PORT for socket creation
PORT = 8889
sendPort = 8888
serialPort = 8890

class UdpClient():


    def __init__(self):

        # define socket address for binding; necessary for receiving data from Arduino 
        self.localSocket = (serverAddress, serialPort)



        # Create a UDP socket
        try:
                self.client_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                # Set these options so multiple processes can connect to this socket
                # self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                print('Socket created')
        except socket.error, msg:
                print('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + str(msg[1]))
                sys.exit()


        # Bind socket to local host and port
        try:
                self.client_socket.bind(self.localSocket)
                print('Bound socket')
        except socket.error , msg:
                print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
                sys.exit()



    def serialUdp(self):
        """
        Goes into an infinite while loop to grab UDP packets.
        """


        # Loop to grap UDP packets from Arduino and push to Redis
        while True:
            
            
            # Receive data continuously from the server (Arduino in this case)
            data, addr =  self.client_socket.recvfrom(2048)
            print(data)
            print(datetime.datetime.now())
