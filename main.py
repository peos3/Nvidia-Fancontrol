#!/usr/bin/python3

from nvfan import *
import atexit
from math import sqrt

#Some default stuff so you can use this script out-of-the-box
defaultFanCurve = [
	(40, 30),
	(50, 45),
	(60, 55),
	(70, 65),
	(80, 75)
]

lastTemp = -1
changeFactor = 1

if(__name__ == '__main__'):
	import sys
	if "-v" in sys.argv:
		setVerboseExecution(True)
		print("\x1b[01;33mVerbose execution enabled!\x1b[0m")
	try:
		print("\x1b[01;34mTesting fan control\x1b[0m")
		res = trySetFanControlEnabled(True)
		if(not res[0]):
			print("\x1b[01;31mUnable to enable fan control!\x1b[0m")
			print("\x1b[01;31mReason: %s != %s %s\x1b[0m" % (res[1], res[2], res[3]));
			quit(1)
		legacyFanSpeed = shouldUseLegacyFanSpeed()
		if(legacyFanSpeed):
			print("\x1b[01;33mUsing legacy fan speed!\x1b[0m")
		res = trySetFanSpeed(30, legacy=legacyFanSpeed)
		if(not res[0]):
			print("\x1b[01;31mUnable to set fan speed!\x1b[0m")
			print("\x1b[01;31mReason: %s != %s\x1b[0m" % (res[1], res[2]));
			trySetFanControlEnabled(False)
			quit(1)
	except FileNotFoundError:
		print("\x1b[01;31m;NVIDIA drivers are not installed, this tool only works with the proprietary NVIDIA drivers\x1b[0m")
		quit(1)
	print("\x1b[01;32mFan control works\x1b[0m")
	lastTemp = getGpuTemp() + 1
	def shutdownHook():
		print("\x1b[01;33mShutting down!\x1b[0m")
		res = trySetFanControlEnabled(False)
		if(not res[0]):
			print("\x1b[01;31mUnable to disable fan control\x1b[0m")
			print("\x1b[01;31mReason: %s != %s\x1b[0m" % (res[1], res[2]));
		else:
			print("\x1b[01;32mDisabled fan control\x1b[0m")
	atexit.register(shutdownHook)
	try:
		while True:
			temp = getGpuTemp()
			if(temp != lastTemp):
				change = temp - lastTemp
				col = "\x1b[01;31m"
				if(change < 0):
					col = "\x1b[01;34m"
					estNextTemp = temp
					speed = interpFanCurve(defaultFanCurve, estNextTemp, incMode=False)
				print(col + "Temperature changed by " + str(change) + " deg. C\x1b[0m")
				if(change > 0):
					estNextTemp = temp + sqrt(change) * changeFactor
					speed = interpFanCurve(defaultFanCurve, estNextTemp, incMode=True)
				print("\x1b[01;33mFan speed thus changed to " + str(speed) + "% ("+ str(temp) + " deg C, " + str(estNextTemp) + " estimated next)\x1b[0m")
				if(speed != -1):
					res = trySetFanSpeed(speed, fan=0, legacy=legacyFanSpeed)
					if(not res[0]):
						print("\x1b[01;31mFailed to set fan speed, exiting!\x1b[0m")
						print("\x1b[01;31mReason: %s != %s\x1b[0m" % (res[1], res[2]));
						quit(-1)

					res = trySetFanSpeed(speed, fan=1, legacy=legacyFanSpeed)
					if(not res[0]):
						print("\x1b[01;31mFailed to set fan speed, exiting!\x1b[0m")
						print("\x1b[01;31mReason: %s != %s\x1b[0m" % (res[1], res[2]));
						quit(-1)
				lastTemp = temp
			sleep(4)
	except KeyboardInterrupt:
		print("\x1b[01;31mExiting now!\x1b[0m")
		quit(1)
