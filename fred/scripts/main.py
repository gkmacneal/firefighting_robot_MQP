#! /usr/bin/env/python

# main script for firefighting robot MQP
# WPI Robotics Engineering 2019
# Gavin MacNeal

import rospy
from sensor_msgs.msg import Joy

class Robot:
	
	def __init__(self):
		# class constructor
		# initialize pubs

		# initialize subs
		rospy.Subscriber('/joy', Joy, self.drive, queue_size=1)
		