#! /usr/bin/python

import sys
import time
import datetime
from subprocess import call, Popen, PIPE
import argparse


"""
Tables
"""
cameraActions = {}

androidActions = { "powerKey" : "KEYCODE_POWER",
                   "menuKey"  : "KEYCODE_MENU",
                   "homeKey"  : "KEYCODE_HOME",
                   "backKey"  : "KEYCODE_BACK",
                   "volumeUp" : "KEYCODE_VOLUME_UP",
                   "volumeDown" : "KEYCODE_VOLUME_DOWN"
                   }

screenActions = {}

adbActions = 	{ "screenCap"  : "screencap -p /sdcard/screen_%s.png",
                  "pullLog"  : "adb pull /data/logs log_%s"
                  }


"""
Function Part 
"""
def getDevices():
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
				print adbDevices.index(device), ")" , device
			deviceInput = sys.stdin.readline()
			if int(deviceInput) < len(adbDevices) and int(deviceInput) >= 0:
				break	
		return adbDevices[int(deviceInput)]
	elif len(adbDevices) == 1:
		return adbDevices[0]
	else:
		print "No devices is connected."
		exit()


def adbAction(serial, action):
	if serial != None:
		call(["adb", "-s", serial, "shell", action])
	else:
		call(["adb", "shell", action])

def dumpTable(table):
    for k,v in table.iteritems():
        print k + ": " + v

def readTable(filename, table):
    with open(filename) as fd:
        table.update(dict([line.strip().split(": ", 1) for line in fd]))

"""
Main Script
"""
serial = None

args = [ str(argv) for argv in sys.argv ]
default_timing = 2
cmds_timing = []
cmds = []
names = []
repeatCount = 10

touchActionTableName = "touchActions.tab"
swipeActionTableName = "swipeActions.tab"

timestamp_format_commands = ("screenCap", "pullLog", "other_command")
tables = ((cameraActions, "input tap"), (adbActions, ""), (androidActions,"input keyevent"), (screenActions,"input swipe"))


__author__ = 'Balaji Muhammad'

#configure parser
parser = argparse.ArgumentParser(description='This is broken from Baliji, but crashed by Muhammand')
parser.add_argument('actions',metavar='ACTION', nargs='*', help='actions to be performed in a single flow. Format: action_name,delay_ms', default='')
parser.add_argument('-s','--serial', help='serial# of the device, use this argument if you have 2+ devices', required=False, dest='serial', default=None)
parser.add_argument('--touch-table', metavar='TOUCH_ACTION_TABLE', help='the name of touch action table. default: touchActions.tab', required=False, dest='touchTable', default='touchActions.tab')
parser.add_argument('--swipe-table',metavar='SWIPE_ACTION_TABLE', help='the name of swipe action table. default: swipeActions.tab', required=False, dest='swipeTable', default='swipeActions.tab')
parser.add_argument('--interval', metavar='ACTION_INTERVAL', help='the internal between two actions. default: 2s', required=False, dest='interval', default='2')
parser.add_argument('-t', '--repeat', metavar='REPEAT_COUNT', help='the number of times to repeat assigned actions. default: 10', required=False, dest='repeatCount', default=10, type=int)
parser.add_argument('-p', metavar='PROCEDURE', help='the name of repeat procedure. ex: example.procedure', required=False, dest='repeatProcedure', default='')

args = parser.parse_args()

#print args
 
touchActionTableName = args.touchTable
swipeActionTableName = args.swipeTable
repeatProcedureName = args.repeatProcedure

default_timing = args.interval
serial = args.serial
if serial == None:
	serial = getDevices()
repeatCount = args.repeatCount
## show values ##
#print args

readTable(touchActionTableName, cameraActions)
readTable(swipeActionTableName, screenActions)
#dumpTable(cameraActions)
#dumpTable(screenActions)

if repeatProcedureName != "":
	with open(repeatProcedureName) as f:
		args.actions = f.read().splitlines();

#show procedure actions
#print args.actions
for action in args.actions:
	
        if action == "":
		continue
	cmd = None;
	timing = default_timing;
	if "," in action:
		action_list = action.split(",")
		action = action_list[0]
		timing = action_list[1]

	for table,prefix in tables:
		cmd = table.get(action,None)
		if cmd != None:
			cmd = prefix + " " + cmd
			cmds.append(cmd)
			names.append(action)
			cmds_timing.append(str(timing))
			break
	if cmd == None:
	    print "%s is not existed in action tables, it will be igonre" % action

if cmds == []:
	parser.print_help()
	exit()

for i in xrange(0, repeatCount):
	print "looptimes: " + str(i)
	timeStamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
	for name,cmd,timing in zip(names,cmds,cmds_timing) :

		if name in timestamp_format_commands:
			cmd = cmd % timeStamp

		print name + ": " + cmd
		print "sleep " + timing
		adbAction(serial, cmd);
		call(["sleep", timing]);
