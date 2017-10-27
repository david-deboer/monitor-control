# monitor-control
To clone the sensor libraries together with code use 'git clone --recursive https://github.com/reeveress/monitor-control.git'

###Usage
import the nodeControlClass into ipython 
instantiate a nodeControl class object: 
n = nodeControlClass.NodeControl() 
Check out the available functions via n.[tab] 
you'll see something like this: 
n.getHumid

n.power_fem         
n.power_snap_relay  
n.power_snapv2_2_3  
n.reset             
n.getTemp           
n.power_pam         
n.power_snapv2_0_1  n.r

The power methods provide the ability to send power commands to Arduino, through the Redis database.
All power methods take the node number and command as arguments. Node number is a digit from 0-29 and command
is string with value 'on' or 'off'.







***You must have the Arduino IDE installed on the computer you're using arduino-mk on or it won't work***
using arduino-mk to create .bin out of .ino file:
go into mc_arduino folder
run make clean to get rid of old versions
run make
build-ethernet folder is created that has the .bin file among others
.bin file is uploaded to the /srv/tftp/arduino directory on the server
.ino file can be directly edited with vim or nano
