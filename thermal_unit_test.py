#!/usr/bin/env python
# script to compare output of thermal arrays

import rospy
from std_msgs.msg import Int16MultiArray
import numpy

data = np.zeros((4, 834))

def get_data(msg, args):
	sensor = args[0]
	offset = msg.layout.data_offset
	size = msg.layout.dim.size
	data[sensor][offset:offset+size-1] = msg.data
	print(data)
	
if __name__ == "__main__":
	try:
		rospy.init_node('thermal_unit_test')
		rospy.Subscriber('/thermal_0i',  Int16MultiArray, get_data, callback_args=(0), queue_size=10)
		rospy.Subscriber('/thermal_1i',  Int16MultiArray, get_data, callback_args=(1), queue_size=10)
		rospy.Subscriber('/thermal_2i',  Int16MultiArray, get_data, callback_args=(2), queue_size=10)
		rospy.Subscriber('/thermal_3i',  Int16MultiArray, get_data, callback_args=(3), queue_size=10)
		rospy.sleep(1)
		while(not rospy.is_shutdown()):
			pass
	except rospy.ROSInterruptException:
		pass