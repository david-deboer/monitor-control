import os 
import time
while True:
    os.system("redis-cli hgetall status:node:0 >> dataset112117.txt")
    time.sleep(300)

    
