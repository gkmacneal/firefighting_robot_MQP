#!/usr/bin/env python
# script to compare output of thermal arrays

import rospy
from std_msgs.msg import UInt8MultiArray
import numpy as np
from glumpy import app, gl, gloo
import struct
# makes it so numpy arrays get fully printed
np.set_printoptions(threshold=np.inf)

# glumpy shader setup
vertex = """
         attribute vec2 position;
         void main()
         {
             gl_Position = vec4(position, 0.0, 1.0);
         } """

fragment = """
           uniform vec4 color;
           void main() {
               gl_FragColor = color;
           } """

# array of temp ints coming from ROS
data = np.zeros((3, 768), dtype=np.uint8)

# glumpy window
window = app.Window(720, 320)

# initialize a square for each pixel for each sensor
quads = []
for i in range(0, 72*32):
	quad = gloo.Program(vertex, fragment, count=4)

	quads.append(quad)

# init quad positions
for i in range(72):
	for j in range(0, 32):
            quads[i*32+j]["position"] = [((float(i-36) / 38.0)-0.05, (float(j-16) / -17.0)-0.05),
        					           ((float(i-36) / 38.0)+0.05, (float(j-16) / -17.0)-0.05),
        							   ((float(i-36) / 38.0)-0.05, (float(j-16) / -17.0)+0.05),
        							   ((float(i-36) / 38.0)+0.05, (float(j-16) / -17.0)+0.05)]

# redraws each "pixel"
@window.event
def on_draw(dt):
	window.clear()
	for quad in quads:
		quad.draw(gl.GL_TRIANGLE_STRIP)

# ros subscriber callback
def get_data(msg, args):
    # which sensor sent the message
    sensor = args
    # where in the thermal array we are
    offset = msg.layout.data_offset
    # how many pixels we're getting at a time
    size = msg.layout.dim[0].size
    # copy data in from packet
    for i in range(len(msg.data)):
        data[sensor][offset+i] = struct.unpack("B", msg.data[i])[0]
    # puts the values from data into a format for glumpy
    temp_pixels = np.reshape(data, (72, 32))
    # update all the glumpy pixel colors we recieved
    for i in range(24*sensor, 24*sensor+24):
        for j in range(0, 32):
            # color of each pixel
            flt_col = float(temp_pixels[i,j]) / 255.0
            r = flt_col
            g = flt_col - 0.5
            g = 0.0 if (g < 0.0) else g
            b = 1.0 - flt_col
            quads[i*32+j]["color"] = (r, g, b, 1.0)



if __name__ == "__main__":
	try:
        # init node
		rospy.init_node('thermal_unit_test')
        # init subscribers
		rospy.Subscriber('/thermal_0u',  UInt8MultiArray, get_data, callback_args=(0), queue_size=10)
		rospy.Subscriber('/thermal_1u',  UInt8MultiArray, get_data, callback_args=(1), queue_size=10)
		rospy.Subscriber('/thermal_2u',  UInt8MultiArray, get_data, callback_args=(2), queue_size=10)
		rospy.sleep(1)
        # init glumpy app
		app.run()
		while(not rospy.is_shutdown()):
			pass
	except rospy.ROSInterruptException:
		pass
