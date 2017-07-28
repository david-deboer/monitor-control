import redis
import mcNode

m = mcNode.mcNode()
print("getTemp method output: ", m.getTemp(0))
#print("getTempDebug method ouput: ", m.getTempDebug(0))
m.reset(0)
