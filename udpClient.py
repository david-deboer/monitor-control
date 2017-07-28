
'''
	UDP socket server
'''



#           Redis Monitor Control Database hash structure
#
# key            status:node:<zero indexed node ID>
#
# fields	 temps          <array of sensor temperatures>
#	         humidities     <array of humidities> 
# 	 	 airflow        airflow measured by the node
# 	 	 cpu-uptime     uptime of node CPU, in seconds




import time
import datetime
import struct
import redis
import socket
import sys


PORT = 8888
localAddress = ('10.0.1.224', PORT)   # hera-nuc IP
addressArduino = ('10.1.1.247', PORT)    # arduino IP




# Instantiate a Redis object and bind it to an existing running Redis server
r = redis.StrictRedis()

# Create a UDP socket
try:
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	print('Socket created')
except socket.error, msg:
	print('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + str(msg[1]))
	sys.exit()

#client_socket.settimeout(1)


# Bind socket to local host and port
try: 
	client_socket.bind(localAddress)
	print('Bound socket')
except socket.error , msg:
	print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
	sys.exit()



while 1:
        print("Collecting Data and pushing to Redis...")
	# Receive data continuously from the server (Arduino in this case)
	data, addr =  client_socket.recvfrom(1024)

	# Arduino sends a Struct via UDP so unpacking is needed 
        # struct.unpack returns a tuple with one element
	unpacked_mcptemp = struct.unpack('=f',data[0:4])
	unpacked_htutemp = struct.unpack('=f', data[4:8])
	unpacked_htuhumid = struct.unpack('=f', data[8:12])

#       print('Unpack type: ', type(unpacked_mcptemp))
#	print('MCP9808 Temperature: ' ,unpacked_mcptemp[0])
#	print('HTU21DF Temperature: ', unpacked_htutemp[0])
#	print('HTU21DF Humidity: ', unpacked_htuhumid[0])
        
	# Set hashes in Redis composed of sensor temperature values
	r.hmset('status:node:0', {'tempBot':unpacked_htutemp[0]})
        r.hmset('status:node:0', {'tempMid':unpacked_mcptemp[0]})
	r.hmset('status:node:0', {'humidBot':unpacked_htuhumid[0]})

        # Set timestamp 
        r.hmset('status:node:0', {'timestamp':str(datetime.datetime.now())})

        # Check if getTemps flag is set by a mcNode object
        if (r.hmget('status:node:0', 'getTemps') == "True"):
            print("Inside the if statement")
            try:
                print('getTemps is...',bool(r.hmget('status:node:0', 'getTemps')))
                print('getTemps is...',type(bool(r.hmget('status:node:0', 'getTemps'))))
                
                client_socket.sendto('getTemps', addressArduino)
                
                time.sleep(2)
                # Arduino checks if it received any udp packets and sends a respons back based on request
                debug_data, addr = client_socket.recvfrom(1024)
                
                unpacked_mcptemp_debug = struct.unpack('=f',debug_data[0:4])
                unpacked_htutemp_debug = struct.unpack('=f', debug_data[4:8])

    #               print("Unpacked Response from Arduino:  ", unpacked_mcptemp_debug[0])

                r.hmset('status:node:0', {'tempBotDebug':unpacked_htutemp_debug[0]})
                r.hmset('status:node:0', {'tempMidDebug':unpacked_mcptemp_debug[0]})
    #               print(r.hmget('status:node:0','tempBotDebug'))

                # Set timestamp
                r.hmset('status:node:0', {'timestamp':str(datetime.datetime.now())})

                # Reset the flag for next request 
                r.hmset('status:node:0', {'getTemps':False}) 
                print('getTemps after resetting it is...',r.hget('status:node:0','getTemps')) 
            
            except:

                pass
        print(r.hmget('status:node:0', 'reset'))
        print(type(r.hmget('status:node:0', 'reset')))
        print(len(r.hmget('status:node:0', 'reset')))
        print((r.hmget('status:node:0', 'reset')[0]))
        print(type(r.hmget('status:node:0', 'reset')[0]))
        if (r.hmget('status:node:0', 'reset')[0] == "True"):
            print("inside reset if")            
            # Reset the microcontroller when reset is sent through the mcNode class
            # might remove this functionality in the future; too much power for the mcNode class
            client_socket.sendto('reset', addressArduino)

            time.sleep(2)

            # Reset the flag to False so it's not resetting microcontroller to infinity
            r.hmset('status:node:0', {'reset': False})
            

        # Set delay before receiving more data
        time.sleep(2)


