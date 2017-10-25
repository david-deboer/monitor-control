'''
	monitor control database class
'''
import redis
import time
        
PORT = 6379
serverAddress = '10.1.1.1'


class mcNode():
    def __init__(self):
            
            
    # Class object init makes a connection with our 1U server to grap redis database values
    # Redis bind to port 6379 by default
	self.r = redis.StrictRedis(serverAddress)

    # Redis key values/status methods
    def getTemp(self,node):
        
        redistime = self.r.hmget("status:node:%d"%node, "timestamp")[0] 
        timestamp = {'timestamp': redistime}
        tempMid = float((self.r.hmget("status:node:%d"%node,"tempMid"))[0])
        tempTop = float((self.r.hmget("status:node:%d"%node,"tempTop"))[0])
        temps = {'timestamp':timestamp,'tempTop':tempTop,'tempMid':tempMid}
        return temps


    def getHumid(self,node):
        return self.r.hmget("status:node:%d"%node,"humidities")


    # Power Control Methods 
    
    def power_snap_relay(self, node, command):
        self.r.hset("status:node:%d"%node,"power_snap_relay_ctrl",True)
        self.r.hset("status:node:%d"%node,"power_snap_relay_cmd",command)
        print("Snap relay power is %s"%command)


    def power_snapv2_0_1(self, node, command):
        self.r.hset("status:node:%d"%node,"power_snapv2_0_1_ctrl",True)
        self.r.hset("status:node:%d"%node,"power_snapv2_0_1_cmd",command)
        print("SNAPv2_0_1 power is %s"%command)


    def power_snapv2_2_3(self, node, command):
        self.r.hset("status:node:%d"%node,"power_snapv2_2_3_ctrl",True)
        self.r.hset("status:node:%d"%node,"power_snapv2_2_3_cmd",command)
        print("SNAPv2_2_3 power is %s"%command)


    def power_fem(self, node, command):
        self.r.hset("status:node:%d"%node,"power_fem_ctrl",True)
        self.r.hset("status:node:%d"%node,"power_fem_cmd",command)
        print("FEM power is %s"%command)


    def power_pam(self, node, command):
        self.r.hset("status:node:%d"%node,"power_pam_ctrl",True)
        self.r.hset("status:node:%d"%node,"power_pam_cmd",command)
        print("PAM power is %s"%command)


    def reset(self,node):
        self.r.hset("status:node:%d"%node,"reset",True)
        print("Set reset flag to True")
         

