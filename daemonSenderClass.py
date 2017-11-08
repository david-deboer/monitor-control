
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
    """
    This class received UDP packets from Arduino containing sensor data and misc node metadata.
    Class goes into an infinite loop when receiveUDP method is called.

    """

    def __init__(self):
        self.localSocket = (serverAddress, PORT)

        # Instantiate redis object connected to redis server running on serverAddress
        self.r = redis.StrictRedis(serverAddress)

        # Create a UDP socket
        try:
                self.client_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                # Set these options so multiple processes can connect to this socket
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


    def __poke(self):

        print('Poking..')
        self.client_socket.sendto('poke',self.arduinoSocket) 
        t = threading.Timer(3,self.__poke)
        print("Timer Set.")
        t.daemon = True
        t.start()





    def sender(self, arduinoAddress):
        """
        Captures UDP packets sent by Arduino an pushes to Redis. 
        Sends poke signal to Arduino every 3 seconds.
        Checks for control flags in Redis database set by the nodeControlClass.
        """

        # define socket necessary for sending poke command to Arduino
        self.arduinoSocket = (arduinoAddress, sendPort)
        
        # Start the timer to send poke command to the Arduino
        self.__poke()

        # Loop to grap UDP packets from Arduino and push to Redis
        while True:
            
            

            # Check if Redis flags were set through the nodeControlClass

            if ((self.r.hmget('status:node:%d'%node, 'power_snap_relay_ctrl')[0]) == 'True'):
                if ((self.r.hmget('status:node:%d'%node, 'power_snap_relay_cmd')[0]) == 'on'):
                    self.client_socket.sendto("snapRelay_on",self.arduinoSocket) 
                else: 
                    self.client_socket.sendto('snapRelay_off',self.arduinoSocket) 
                self.r.hmset('status:node:%d'%node, {'power_snap_relay_ctrl': False})
            
            if ((self.r.hmget('status:node:%d'%node, 'power_snapv2_0_1_ctrl')[0]) == 'True'):
                if (self.r.hmget('status:node:%d'%node, 'power_snapv2_0_1_cmd')[0] == 'on'):
                    self.client_socket.sendto('snapv2_0_1_on',self.arduinoSocket) 
                else:
                    self.client_socket.sendto('snapv2_0_1_off',self.arduinoSocket) 
                self.r.hset('status:node:%d'%node, 'power_snapv2_0_1_ctrl', False)

            if ((self.r.hmget('status:node:%d'%node, 'power_snapv2_2_3_ctrl')[0]) == 'True'):
                if (self.r.hmget('status:node:%d'%node, 'power_snapv2_2_3_cmd')[0] == 'on'):
                    self.client_socket.sendto('snapv2_2_3_on',self.arduinoSocket)
                else:
                    self.client_socket.sendto('snapv2_2_3_off',self.arduinoSocket)
                self.r.hset('status:node:%d'%node, 'power_snapv2_2_3_ctrl', False)

            if (self.r.hmget('status:node:%d'%node, 'power_fem_ctrl')[0] == 'True'):
                if (self.r.hmget('status:node:%d'%node, 'power_fem_cmd')[0] == 'on'):
                    self.client_socket.sendto('FEM_on',self.arduinoSocket) 
                else:
                    self.client_socket.sendto('FEM_off',self.arduinoSocket) 
                self.r.hset('status:node:%d'%node, 'power_fem_ctrl', False)

            if (self.r.hmget('status:node:%d'%node, 'power_pam_ctrl')[0] == 'True'):
                if (self.r.hmget('status:node:%d'%node, 'power_pam_cmd')[0] == 'on'):
                    self.client_socket.sendto('PAM_on',self.arduinoSocket) 
                else:
                    self.client_socket.sendto('PAM_off',self.arduinoSocket) 
                self.r.hset('status:node:%d'%node, 'power_pam_ctrl', False)




            print(self.r.hgetall('status:node:%d'%node))





















