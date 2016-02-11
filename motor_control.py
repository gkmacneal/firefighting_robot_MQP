#!/usr/bin/env python

import RPi.GPIO as GPIO
import rospy
from geometry_msgs.msg import Twist

leftMotor = 18
leftDir = 17
rightMotor = 19
rightDir = 20
freq = 1000


def drive_motors(msg):
	vel = msg.linear.x * 100.0
	omega = msg.angular.z / 1.1
	length = 241.3

	# if abs(omega) >= 0.05:
	# 	radius = vel / omega
	# else:
	# 	radius = 0.0
	# Vr = omega * (radius + length / 2.0)
	# Vl = omega * (radius - length / 2.0)

	# omega = (Vr - Vl) / length
	# Vr = omega * length + Vl
	# vel = (Vr + Vl) / 2.0
	# Vl = 2.0 * vel - Vr
	# Vr = omega * length + 2.0 * vel - Vr
	Vr = (omega * length) / 2.0 + vel
	Vl = 2.0 * vel - Vr
	if Vr >=  0:
		GPIO.output(rightDir, GPIO.LOW)
	else:
		GPIO.output(rightDir, GPIO.HIGH)
	if Vl >=  0:
		GPIO.output(leftDir, GPIO.LOW)
	else:
		GPIO.output(leftDir, GPIO.HIGH)
	rightDuty = abs(Vr)
	if rightDuty > 100.0:
		rightDuty = 100.0
	leftDuty = abs(Vl)
	if leftDuty > 100.0:
		leftDuty = 100.0
	rightPWM.ChangeDutyCycle(rightDuty)
	leftPWM.ChangeDutyCycle(leftDuty)

if __name__ == '__main__':
    try:
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(leftMotor, GPIO.OUT)
	GPIO.setup(leftDir, GPIO.OUT)
	GPIO.setup(rightMotor, GPIO.OUT)
	GPIO.setup(rightDir, GPIO.OUT)
	leftPWM = GPIO.PWM(leftMotor, freq)
	rightPWM = GPIO.PWM(rightMotor, freq)
	leftPWM.start(0)
	rightPWM.start(0)
        rospy.init_node('motor_node')
        rospy.Subscriber('/cmd_vel2', Twist, drive_motors, queue_size=10)
        rospy.sleep(1)
        while(not rospy.is_shutdown()):
            pass
	leftPWM.stop()
	rightPWM.stop()
    except rospy.ROSInterruptException:
        pass