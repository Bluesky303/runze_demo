from PumpControl import *

pump = PumpControl("COM19")

pump.pull(5, 0.5)
pump.push(2, 1)

pump.close()