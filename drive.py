#!/usr/bin/env python
# script to listen to ROS joy messages and publish ROS command vel messages


import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy

global mode
mode = 0
global mode_tog
mode_tog = False
num_modes = 3
modes = ['tank', 'arcade', 'rocket']

axes = ['dpad_vert', 'right_horz', 'right_vert', 'right_trig', 'left_vert', 'left_horz', 'dpad_horz', 'left_trig']
buttons = ['a', 'b', 'ls', 'rb', 'start', 'lb', 'rs', 'home', 'x', 'y', 'select']

def read_message(msg):
    global mode
    global mode_tog
    left_vert = msg.axes[axes.index('left_vert')]
    left_horz = msg.axes[axes.index('left_horz')]
    right_vert = msg.axes[axes.index('right_vert')]
    right_horz = msg.axes[axes.index('right_horz')]
    left_trig = msg.axes[axes.index('left_trig')]
    right_trig = msg.axes[axes.index('right_trig')]

    # if this is the first packet time we see the right bumper pushed
	# since the last time it was not pushed, change modes
	if msg.buttons[buttons.index('rb')] == 1 and not mode_tog:
        mode_tog = True
        mode += 1
        if mode >= num_modes:
            mode = 0
        print(modes[mode])
    # mark that the right bumper has been released
	elif msg.buttons[buttons.index('rb')] == 0 and mode_tog:
        mode_tog = False

    twist = Twist()

    if mode == modes.index('tank'):
        twist.linear.x = (-right_vert - left_vert) / 2.
        twist.angular.z = (-right_vert + left_vert) / 2.
    elif mode == modes.index('arcade'):
        twist.linear.x = -left_vert
        twist.angular.z = right_horz
    elif mode == modes.index('rocket'):
        twist.linear.x = (right_trig - left_trig) / 2.
        twist.angular.z = left_horz

    vel_pub.publish(twist)

if __name__ == '__main__':
    try:
        rospy.init_node('drive_node')
        vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        rospy.Subscriber('/joy', Joy, read_message, queue_size=10)
        rospy.sleep(1)
        while(not rospy.is_shutdown()):
            pass
    except rospy.ROSInterruptException:
        pass
