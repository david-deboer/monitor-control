import matplotlib.pyplot as plt
import numpy as np
import datetime

f = open("dataset091517.txt")
dataList = f.readlines()

with open("dataset091517.txt") as f:
    dataListStp = [word.strip() for word in f]


tempTop = dataListStp[1::20]
tempMid = dataListStp[3::20]
humidTemp = dataListStp[5::20]
timeStamp = dataListStp[9::20]
print(len(timeStamp))

print(tempTop)
print(timeStamp)
for i,val in enumerate(tempTop):
    val = float(val)




timeStamp = [datetime.datetime.strptime(elem, '%Y-%m-%d %H:%M:%S.%f') for elem in timeStamp]

plt.plot(timeStamp,tempTop)
plt.plot(timeStamp,tempMid)
plt.plot(timeStamp,humidTemp)
plt.show()
