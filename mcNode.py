'''
	monitor control database class
'''
import redis
import time
        
HOST = '10.0.1.224'
PORT = 6379



class mcNode():
    def __init__(self):
            
            
    # Class object init makes a connection with our 1U server to grap redis database values
    # Redis bind to port 6379 by default
	self.r = redis.StrictRedis(host = HOST)

    # Returns a dict of temperature sensors
    def getTemp(self,node):
        
        redistime = self.r.hmget("status:node:%d"%node, "timestamp")[0] 
        timestamp = {'timestamp': redistime}
        tempBot = float((self.r.hmget("status:node:%d"%node,"tempBot"))[0])
        tempMid = float((self.r.hmget("status:node:%d"%node,"tempMid"))[0])
        temps = {'timestamp':timestamp,'tempBot':tempBot,'tempMid':tempMid}
        return temps



    def getHumid(self,node):
        return self.r.hmget("status:node:%d"%node,"humidities")




    def getAir(self,node):
        return self.r.hmget("status:node:%d"%node,"airflow")




#    def getTempDebug(self,node):
#        # Set getTemps hash field to True. 
#        self.r.hset("status:node:%d"%node,"getTemps",True)
#        time.sleep(5)
#        tempBotDebug = float(self.r.hmget("status:node:%d"%node, "tempBot")[0])
#        tempMidDebug = float(self.r.hmget("status:node:%d"%node, "tempMidDebug")[0])
#        timestampDebug = self.r.hmget("status:node:%d"%node, "timestampDebug")[0]
#                
#        # Return a dictionary of float values and string timestamp
#        tempsDebug = {'timestamp':timestampDebug,'tempBotDebug':tempBotDebug, 'tempMidDebug':tempMidDebug}
#        return tempsDebug
#
#    def reset(self,node):
#        self.r.hset("status:node:%d"%node,"reset",True)
#        print("Set reset flag to True")
#        return 
#    #def accumulate(self):
	# accumulates specified number of data or for specified period of time, saves to a file, maybe a plot script. Would be cool if I had a real time data upload to a server with cool graphix. 
