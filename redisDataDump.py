import os 
import time
while True:
    os.system("redis-cli hgetall status:node:0 >> dataset091817.txt")
    time.sleep(300)

    
