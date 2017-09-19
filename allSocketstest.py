"""
This class is used for receiving the UDP packets from the Arduino.

It goes into an infinite while loop so has only the packet receiving functionality. 
"""


import threading
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
rcvPort = 8889
sendPort = 8888
serialPort = 8890
class UdpClient():


    def __init__(self):

        # define socket address for binding; necessary for receiving data from Arduino 
        self.rcvSocket = (serverAddress, rcvPort)
        self.sendSocket = (serverAddress, sendPort)
        self.serialSocket = (serverAddress, serialPort)


        # Instantiate redis object connected to redis server running on serverAddress
        self.r = redis.StrictRedis(serverAddress)

        # Create a UDP socket
        try:
                self.rcv_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.send_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.serial_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                # Set these options so multiple processes can connect to this socket
                # self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                print('Sockets created')
        except socket.error, msg:
                print('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + str(msg[1]))
                sys.exit()


        # Bind socket to local host and port
        try:
                self.rcvSocket.bind(self.rcvSocket)
                self.send_socket.bind(self.sendSocket)
                self.serial_socket.bind(self.serialSocket)
                print('Bound sockets')
        except socket.error , msg:
                print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
                sys.exit()

        # Make a server object to send alerts by email
        #server = smtplib.SMTP('smtp.gmail.com', 587)
        #server.login('heranodemc@gmail.com','monitorcontrol')
        #server.ehlo()
        #server.starttls()


    def __poke(self):

        print('Poking..')
        self.send_socket.sendto('poke',self.arduinoSocket) 
        t = threading.Timer(5,self.__poke)
        print("Timer Set.")
        t.daemon = True
        t.start()





    def receiveUDP(self, arduinoAddress):
        """
        Goes into an infinite while loop to grab UDP packets.
        """

        # define socket necessary for sending poke command to Arduino
        self.arduinoSocket = (arduinoAddress, sendPort)
        
        # Start the timer to send poke command to the Arduino
        self.__poke()

        # Loop to grap UDP packets from Arduino and push to Redis
        while True:
            
            
            # Receive data continuously from the server (Arduino in this case)
            data, addr =  self.rcv_socket.recvfrom(1024)

            # Arduino sends a Struct via UDP so unpacking is needed 
            # struct.unpack returns a tuple with one element
            # Each struct element is 4 Bytes (c floats are packed as 4 byte strings)

            unpacked_nodeID = struct.unpack('=f',data[0:4])
            unpacked_mcptemp_top = struct.unpack('=f',data[4:8])
            unpacked_mcptemp_mid = struct.unpack('=f',data[8:12])
            unpacked_htutemp = struct.unpack('=f', data[12:16])
            unpacked_htuhumid = struct.unpack('=f', data[16:20])
            #unpacked_windspeed_mph = struct.unpack('=f', data[20:24])
            #unpacked_tempCairflow = struct.unpack('=f', data[24:28])
            unpacked_serial = struct.unpack('=B',data[20])
            unpacked_snap_relay = struct.unpack('=?',data[21])
            unpacked_fem = struct.unpack('=?',data[22])
            unpacked_pam = struct.unpack('=?',data[23])
            unpacked_snapv2_0_1 = struct.unpack('=?',data[24])
            unpacked_snapv2_2_3 = struct.unpack('=?',data[25])

            node = int(unpacked_nodeID[0])

            # if (unpacked_mcptemp_top > 27 && unpacked_mcptemp_mid > 27 && unpacked_htutemp > 27):
               #server.send('heranodemc@gmail.com','recipientemail@gmail.com','The temperature values are approaching critical levels, shutdown sequence initiated') 
            # Set hashes in Redis composed of sensor temperature values
            self.r.hmset('status:node:%d'%node, {'tempTop':unpacked_mcptemp_top[0]})
            self.r.hmset('status:node:%d'%node, {'tempMid':unpacked_mcptemp_mid[0]})
            self.r.hmset('status:node:%d'%node, {'humidTemp':unpacked_htutemp[0]})
            self.r.hmset('status:node:%d'%node, {'humid':unpacked_htuhumid[0]})
            #self.r.hmset('status:node:%d'%node, {'windSpeed_mph':unpacked_windspeed_mph[0]})
            #self.r.hmset('status:node:%d'%node, {'tempCairflow':unpacked_tempCairflow[0]})
            
            # Set timestamp 
            self.r.hmset('status:node:%d'%node, {'timestamp':datetime.datetime.now()})
            self.r.hmset('status:node:%d'%node, {'snap_relay': bin(unpacked_snap_relay[0])})
            self.r.hmset('status:node:%d'%node, {'fem': bin(unpacked_fem[0])})
            self.r.hmset('status:node:%d'%node, {'pam': bin(unpacked_pam[0])})
            self.r.hmset('status:node:%d'%node, {'snapv2_0_1': bin(unpacked_snapv2_0_1[0])})
            self.r.hmset('status:node:%d'%node, {'snapv2_2_3': bin(unpacked_snapv2_2_3[0])})
            print('status:node:%d'%node,self.r.hgetall('status:node:%d'%node))


    def serialUDP(self):
        """
        Goes into an infinite while loop to grab UDP packets.
        """


        # Loop to grap UDP packets from Arduino and push to Redis
        while True:


            # Receive data continuously from the server (Arduino in this case)
            data, addr =  self.serial_socket.recvfrom(2048)

            print(data)


    def reset(self, arduinoAddress):

        # define arduino socket to send requests
        arduinoSocket = (arduinoAddress, sendPort)
        self.send_socket.sendto('reset', arduinoSocket)

        # Set delay before receiving more data
        time.sleep(2)

    def shutdown(self, arduinoAddress):

        # define arduino socket to send requests
        arduinoSocket = (arduinoAddress, sendPort)
        self.send_socket.sendto('shutdown', arduinoSocket)

        # Set delay before receiving more data
        time.sleep(2)

    def start(self, arduinoAddress):

        # define arduino socket to send requests
        arduinoSocket = (arduinoAddress, sendPort)
        self.send_socket.sentto('start', arduinoSocket)

        # Set delay before receiving more data
        time.sleep(2)



    def snapRelay(self, command, arduinoAddress):

        # define arduino socket to send requests
        arduinoSocket = (arduinoAddress, sendPort)
        self.send_socket.sendto('snapRelay_%s'%command, arduinoSocket)

        # Set delay before receiving more data
        time.sleep(2)

    def fem(self, command, arduinoAddress):

        # define arduino socket to send requests
        arduinoSocket = (arduinoAddress, sendPort)
        self.send_socket.sendto('FEM_%s'%command, arduinoSocket)

        # Set delay before receiving more data
        time.sleep(2)

    def pam(self, command, arduinoAddress):

        # define arduino socket to send requests
        arduinoSocket = (arduinoAddress, sendPort)
        self.send_socket.sendto('PAM_%s'%command, arduinoSocket)

        # Set delay before receiving more data
        time.sleep(2)

    def snapv2_0_1(self, command, arduinoAddress):

        # define arduino socket to send requests
        arduinoSocket = (arduinoAddress, sendPort)
        self.send_socket.sendto('snapv2_0_1_%s'%command, arduinoSocket)

        # Set delay before receiving more data
        time.sleep(2)

    def snapv2_2_3(self, command, arduinoAddress):

        # define arduino socket to send requests
        arduinoSocket = (arduinoAddress, sendPort)
        self.send_socket.sendto('snapv2_2_3_%s'%command, arduinoSocket)

        # Set delay before receiving more data
        time.sleep(2)


