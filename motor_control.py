import RPi.GPIO as GPIO
import rospy
from geometry_msgs.msg import Twist

leftMotor = 18
leftDir = 17
rightMotor = 19
rightDir = 20
freq = 1000

def drive_motors(msg):
	vel = msg.linear.x
	omega = msg.angular.z
	radius = vel / omega
	length = 241.3
	# omega = (Vr - Vl) / length
	# Vr = omega * length + Vl
	# vel = (Vr + Vl) / 2.0
	# Vl = 2.0 * vel - Vr
	# Vr = omega * length + 2.0 * vel - Vr
	Vr = (omega * length) / 2.0 + vel
	Vl = 2.0 * vel - Vr
	if Vr >=  0:
		GPIO.output(rightDir, GPIO.HIGH)
	else:
		GPIO.output(rightDir, GPIO.LOW)
	if Vl >=  0:
		GPIO.output(leftDir, GPIO.HIGH)
	else:
		GPIO.output(leftDir, GPIO.LOW)
	rightPWM.ChangeDutyCycle(int(Vr * 100))
	leftPWM.ChangeDutyCycle(int(Vl * 100))

if __name__ == '__main__':
    try:
        rospy.init_node('motor_node')
        rospy.Subscriber('/cmd_vel', Twist, drive_motors, queue_size=10)
        rospy.sleep(1)
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(leftMotor, GPIO.OUT)
		GPIO.setup(leftDir, GPIO.OUT)
		GPIO.setup(rightMotor, GPIO.OUT)
		GPIO.setup(rightDir, GPIO.OUT)
		leftPWM = GPIO.PWM(leftMotor, freq)
		rightPWM = GPIO.PWM(rightMotor, freq)
		leftPWM.start(0)
		rightPWM.start(0)
        while(not rospy.is_shutdown()):
            pass
		leftPWM.stop()
		rightPWM.stop()
    except rospy.ROSInterruptException:
        pass