"""
This class is used for sending UDP commands to Arduino.

Has ability to turn on/off PSU, FEM, PAM and White Rabbit. Could also reset the Arduino so it restarts the bootloader. 
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
PORT = 8888


class UdpClient():


    def __init__(self):

        # define socket address for binding; necessary for receiving data from Arduino 
        self.localSocket = (serverAddress, PORT)


        # Instantiate redis object connected to redis server running on serverAddress
        self.r = redis.StrictRedis(serverAddress)

        # Create a UDP socket
        try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                # Make sure that specify that we want to reuse the socket address
                self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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


        # Make a server object to send alerts by email
        #server = smtplib.SMTP('smtp.gmail.com', 587)
        #server.login('heranodemc@gmail.com','monitorcontrol')
        #server.ehlo()
        #server.starttls()
        

    def reset(self, arduinoAddress):

        # define arduino socket to send requests
        arduinoSocket = (arduinoAddress, PORT)
        self.client_socket.sendto('reset', arduinoSocket)

        # Set delay before receiving more data
        time.sleep(2)
    
    def shutdown(self, arduinoAddress):

        # define arduino socket to send requests
        arduinoSocket = (arduinoAddress, PORT)
        self.client_socket.sendto('shutdown', arduinoSocket)

        # Set delay before receiving more data
        time.sleep(2)

    def start(self, arduinoAddress):

        # define arduino socket to send requests
        arduinoSocket = (arduinoAddress, PORT)
        self.client_socket.sentto('start', arduinoSocket)

        # Set delay before receiving more data
        time.sleep(2)

    def psu(self, arduinoAddress, command):
        
        # define arduino socket to send requests
        arduinoSocket = (arduinoAddress, PORT)
        self.client_socket.sendto('PSU_%s'%command, arduinoSocket)

        # Set delay before receiving more data
        time.sleep(2)

    def whiteRabbit(self, command):
        
        # define arduino socket to send requests
        arduinoSocket = (arduinoAddress, PORT)
        self.client_socket.sendto('wr_%s'%command, arduinoSocket)

        # Set delay before receiving more data
        time.sleep(2)

    def fem(self, command, arduinoAddress):
        
        # define arduino socket to send requests
        arduinoSocket = (arduinoAddress, PORT)
        self.client_socket.sendto('FEM_%s'%command, arduinoSocket)

        # Set delay before receiving more data
        time.sleep(2)

    def pam(self, command, arduinoAddress):
        
        # define arduino socket to send requests
        arduinoSocket = (arduinoAddress, PORT)
        self.client_socket.sendto('PAM_%s'%command, arduinoSocket)

        # Set delay before receiving more data
        time.sleep(2)

    def snapv2_0_1(self, command, arduinoAddress):

        # define arduino socket to send requests
        arduinoSocket = (arduinoAddress, PORT)
        self.client_socket.sendto('snapv2_0_1_%s'%command, arduinoSocket)

        # Set delay before receiving more data
        time.sleep(2)

    def snapv2_2_3(self, command, arduinoAddress):

        # define arduino socket to send requests
        arduinoSocket = (arduinoAddress, PORT)
        self.client_socket.sendto('snapv2_2_3_%s'%command, arduinoSocket)

        # Set delay before receiving more data
        time.sleep(2)

