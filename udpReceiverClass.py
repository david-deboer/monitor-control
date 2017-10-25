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
PORT = 8889
sendPort = 8888

class UdpClient():


    def __init__(self):

        # define socket address for binding; necessary for receiving data from Arduino 
        self.localSocket = (serverAddress, PORT)


        # Instantiate redis object connected to redis server running on serverAddress
        self.r = redis.StrictRedis(serverAddress)

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

        # Make a server object to send alerts by email
        #server = smtplib.SMTP('smtp.gmail.com', 587)
        #server.login('heranodemc@gmail.com','monitorcontrol')
        #server.ehlo()
        #server.starttls()


    def __poke(self):

        print('Poking..')
        self.client_socket.sendto('poke',self.arduinoSocket) 
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
            data, addr =  self.client_socket.recvfrom(1024)

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
            self.r.hmset('status:node:%d'%node, {'tempHumid':unpacked_htutemp[0]})
            self.r.hmset('status:node:%d'%node, {'humid':unpacked_htuhumid[0]})
            
            # Set timestamp 
            self.r.hmset('status:node:%d'%node, {'timestamp':datetime.datetime.now()})
            self.r.hmset('status:node:%d'%node, {'power_snap_relay': bin(unpacked_snap_relay[0])})
            self.r.hmset('status:node:%d'%node, {'power_fem': bin(unpacked_fem[0])})
            self.r.hmset('status:node:%d'%node, {'power_pam': bin(unpacked_pam[0])})
            self.r.hmset('status:node:%d'%node, {'power_snapv2_0_1': bin(unpacked_snapv2_0_1[0])})
            self.r.hmset('status:node:%d'%node, {'power_snapv2_2_3': bin(unpacked_snapv2_2_3[0])})


            # Check if Redis flags were set through the nodeControlClass

            if ((self.r.hmget('status:node:%d'%node, 'power_snap_relay_ctrl')[0]) == "True"):
                if ((self.r.hmget('status:node:%d'%node, 'power_snap_relay_cmd')[0]) == 'on'):
                    self.client_socket.sendto("snapRelay_on",self.arduinoSocket) 
                else: 
                    self.client_socket.sendto('snapRelay_off',self.arduinoSocket) 
                self.r.hmset('status:node:%d'%node, {'power_snap_relay_ctrl': False})
            
            if ((self.r.hmget('status:node:%d'%node, 'power_snapv2_0_1_ctrl')[0]) == "True"):
                if (self.r.hmget('status:node:%d'%node, 'power_snapv2_0_1_cmd')[0] == 'on'):
                    self.client_socket.sendto('snapv2_0_1_on',self.arduinoSocket) 
                else:
                    self.client_socket.sendto('snapv2_0_1_off',self.arduinoSocket) 
                self.r.hset('status:node:%d'%node, 'power_snapv2_0_1_ctrl', False)

            if ((self.r.hmget('status:node:%d'%node, 'power_snapv2_2_3_ctrl')[0]) == "True"):
                if (self.r.hmget('status:node:%d'%node, 'power_snapv2_2_3_cmd')[0] == 'on'):
                    self.client_socket.sendto('snapv2_2_3_on',self.arduinoSocket)
                else:
                    self.client_socket.sendto('snapv2_2_3_off',self.arduinoSocket)
                self.r.hset('status:node:%d'%node, 'power_snapv2_2_3_ctrl', False)

            if (self.r.hmget('status:node:%d'%node, 'power_fem_ctrl')[0] == "True"):
                if (self.r.hmget('status:node:%d'%node, 'power_fem_cmd')[0] == 'on'):
                    self.client_socket.sendto('FEM_on',self.arduinoSocket) 
                else:
                    self.client_socket.sendto('FEM_off',self.arduinoSocket) 
                self.r.hset('status:node:%d'%node, 'power_fem_ctrl', False)

            if (self.r.hmget('status:node:%d'%node, 'power_pam_ctrl')[0] == "True"):
                if (self.r.hmget('status:node:%d'%node, 'power_pam_cmd')[0] == 'on'):
                    self.client_socket.sendto('PAM_on',self.arduinoSocket) 
                else:
                    self.client_socket.sendto('PAM_off',self.arduinoSocket) 
                self.r.hset('status:node:%d'%node, 'power_pam_ctrl', False)




            print(self.r.hgetall('status:node:%d'%node))





















