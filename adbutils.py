#! /usr/bin/python

import sys
import time
import datetime
from subprocess import call, Popen, PIPE

############################
# Class AdbRobot
############################

class AdbRobot():

##########
# Tables #
##########
    touchActions    =   {}
    androidActions  =   {   "powerKey" : "KEYCODE_POWER",
                            "menuKey"  : "KEYCODE_MENU",
                            "homeKey"  : "KEYCODE_HOME",
                            "backKey"  : "KEYCODE_BACK",
                            "volumeUp" : "KEYCODE_VOLUME_UP",
                            "volumeDown" : "KEYCODE_VOLUME_DOWN"
                        }
    swipeActions    =   {}
    adbActions      =   {   "screenCap"  : "screencap -p /sdcard/screen_%s.png",
                            "pullLog"  : "adb pull /data/logs log_%s"
                        }

    timestamp_format_commands = ("screenCap", "pullLog", "other_command")

    actions = []
    ACTION_TABLES = ((touchActions, "input tap"), (adbActions, ""), (androidActions,"input keyevent"), (swipeActions,"input swipe"))
#################
# Function Part #
#################
    def __init__(self):
        self.touchActionTableName = "touchActions.tab"
        self.swipeActionTableName = "swipeActions.tab"
        self.repeatProcedureName = ""
        self.cmdInterval = 2
        self.repeatCount = 1
        self.readTable(self.touchActionTableName, self.touchActions)
        self.readTable(self.swipeActionTableName, self.swipeActions)
        self.device = None
        self.cmds = []
        self.names = []
        self.cmd_timings = []

    def setDevice(self, device):
        self.device = device

    def getDevice(self):
        return self.device

    def setTouchActionTable(self, table_name):
        self.touchActionTableName = table_name
        self.readTable(table_name, self.touchActions)

    def setSwipeActionTable(self, table_name):
        self.swipeActionTableName = table_name
        self.readTable(table_name, self.swipeActions)

    def setRepeatProcedure(self, procedure_name):
        self.repeatProcedureName = procedure_name
        self.readProcedure()

    def setCmdInterval(self, t_interval):
        self.cmdInterval = t_interval

    def getRepeatCound(self):
        return self.repeatCount

    def setRepeatCount(self, count):
        self.repeatCount = count

    def doAction(self, actions):
        self.device.adbAction(actions)

    def getScreenShot(self, store_path):
        self.device.getScreenShot(store_path)

    def dumpTable(self, table):
        for k,v in table.iteritems():
            print k + ": " + v

    def readTable(self, filename, table):
        table.clear()
        with open(filename) as fd:
            table.update(dict([line.strip().split(": ", 1) for line in fd]))

    def readProcedure(self):
        if self.repeatProcedureName != "" and self.repeatProcedureName != None:
	    with open(self.repeatProcedureName) as f:
		self.setActions(f.read().splitlines())
    
    def setActions(self, actions):
        self.actions = actions

    def getCmds(self):
        return self.cmds

    def convertActionsToCmds(self):
        for action in self.actions:
            if action == "":
        	continue
            cmd = None;
            timing = self.cmdInterval;
            if "," in action:
                action_list = action.split(",")
                action = action_list[0]
                timing = action_list[1]
            
            for table,prefix in self.ACTION_TABLES:
                cmd = table.get(action,None)
                if cmd != None:
                    cmd = prefix + " " + cmd
                    self.cmds.append(cmd)
                    self.names.append(action)
                    self.cmd_timings.append(str(timing))
                    break
                if cmd == None:
                    print "%s is not existed in action tables, it will be igonre" % action

    def doWork(self):
        for i in xrange(0, self.repeatCount):
            print "looptimes: " + str(i)
            timeStamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
            for name,cmd,timing in zip(self.names, self.cmds, self.cmd_timings) :
        	if name in self.timestamp_format_commands:
       		    cmd = cmd % timeStamp
       	        print name + ": " + cmd
       	        print "sleep " + timing
       	        self.doAction(cmd.split(" "));
       	        call(["sleep", timing]);

############################
# Class AdbDevice
############################

class AdbDevice():

    nonShellCmds = {"root", "remount", "devices", "kill-server", "wait-for-device", "bugreport", "pull", "push"}
    TEMP_SCREENCAP_PATH = "/sdcard/temp_screen.png"

    def __init__(self):
        self.serial = None
        
    def setSerial(self, serial):
        self.serial = serial
    
    def getSerial(self):
        return self.serial

    def getDevices(self):
	adbStdout, err = Popen(["adb", "devices"], stdout=PIPE).communicate()
	adbStdoutList = adbStdout.splitlines()
	adbDevices = []
	for item in adbStdoutList:
		temp = item.split('\t')
		if len(temp) == 2 and temp[1] == "device":
			adbDevices.append(temp[0])
			
	if len(adbDevices) > 1:
		while(1):
			for device in adbDevices:
				print adbDevices.index(device)+1, ")" , device
			deviceInput = sys.stdin.readline()
			if int(deviceInput) < len(adbDevices)+1 and int(deviceInput) >= 1:
				break	
		return adbDevices[int(deviceInput)-1]
	elif len(adbDevices) == 1:
		return adbDevices[0]
	else:
		#print "No devices is connected."
		#exit()
		return None

    def adbAction(self, action):
        cmd = ["adb"]
	if self.serial != None:
	        cmd.extend(["-s", self.serial])
        if self.isNeedShell(action):
            cmd.append("shell")
        cmd.extend(action)
        print cmd
        call(cmd)
    
    def isNeedShell(self, action):
        print action
        for cmd in self.nonShellCmds:
            if cmd in action:  # find a cmd without "shell" prefix
                print False
                return False
        print True
        return True
    
    def getScreenShot(self, store_path):
        self.adbAction(["screencap -p", self.TEMP_SCREENCAP_PATH])
        self.pull(self.TEMP_SCREENCAP_PATH, store_path)
        self.adbAction(["rm", self.TEMP_SCREENCAP_PATH])

    def pull(self, stuff_path, local_path):
        self.adbAction(["pull", stuff_path, local_path])

    def push(self, stuff, device_path):
        self.adbAction(["push", stuff_path, device_path])
