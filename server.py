import socket
import pickle
import signal
import sys
import control
from thread import *
import time
import rospy
from std_msgs.msg import Empty
from std_msgs.msg import Float32MultiArray
from std_msgs.msg import MultiArrayDimension

class Server(object):
    def __init__(self):
        rospy.init_node('server')
        self.executing = False
        self.setup_done = False
	self.f = False
        self.cmd = control.Commands()
        self.cmd.setup()
        self.testCommands()
        self.pub = rospy.Publisher('done', Empty, queue_size=1)
        rospy.Subscriber('route2', Float32MultiArray, self.move)
        rospy.Subscriber('setup', Float32MultiArray, self.setup)
    def testCommands(self):
        self.cmd.move(-100, 0)
        time.sleep(0.1)
        self.cmd.move(-100, 1)
        time.sleep(0.1)
        self.cmd.move(-100, 0)
        time.sleep(0.1)
        self.cmd.move(-100, 1)
        time.sleep(0.1)
    def move(self, msgs):
        if not self.setup_done or self.executing:
            return
        self.executing = True

        for i in range(len(msgs.data)/4):
	    self.cmd.solenoid2(bool(msgs.data[4*i+2]))
	    time.sleep(0.01)
            self.cmd.move(int(msgs.data[4*i]), 0)
            self.cmd.move(int(msgs.data[4*i+1]), 1)
            if int(msgs.data[4*i]):
    	        if self.f or abs(msgs.data[4*i]) > 15000:
		    control.busydelay(msgs.data[4*i+3], 0)
		else:
		    time.sleep(0.25)
            if int(msgs.data[4*i+1]):
                if self.f or abs(msgs.data[4*i+1]) > 15000:
		    control.busydelay(msgs.data[4*i+3], 1)
		else:
		    time.sleep(0.25)
            self.cmd.solenoid2(bool(msgs.data[4*i+2]))
            if not int(msgs.data[4*i]) and not int(msgs.data[4*i+1]):
                if self.f:
		    time.sleep(msgs.data[4*i+3])
		else:
		    time.sleep(0.2)
        self.cmd.reset()
        self.executing = False
        self.pub.publish()
    def setup(self, msgs):
        if self.setup_done:
            return
	self.f = True
        self.setup_done = True
        self.move(msgs)
	self.f = False
    def run(self):
        r = rospy.Rate(10)
        while not rospy.is_shutdown():
            r.sleep()
def main():
    server = Server()
    server.run()
if __name__ == "__main__":
    main()
