#!/usr/bin/env python
# script to compare output of thermal arrays

import rospy
from std_msgs.msg import Int16MultiArray
import numpy as np
from glumpy import app, gl, gloo
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

# array of raw ints coming from ROS
data = np.zeros((4, 834), dtype=np.uint16)
# to be used when converting to celsius
celsius = np.zeros((4, 32, 24), dtype=np.float)

# tracks which sections of which sensors have been read at least once
read = np.zeros((4, 6), dtype=np.uint8)

# glumpy window
window = app.Window(1280, 240)

# initialize a square for each pixel for each sensor
quads = []
for i in range(0, 128*24):
	quad = gloo.Program(vertex, fragment, count=4)
	quads.append(quad)

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
	data[sensor][offset:offset+size] = msg.data
    # mark that we recieved a packet for this section of this sensor
	read[sensor][int(offset/834)] = 1
    # puts the values from raw data into a format for glumpy
    temp_pixels = np.reshape(data[:,:768], (128, 24))
    # update all the glumpy pixel colors we recieved
    for i in range(32*sensor, 32*sensor+32):
		for j in range(0, 24):
            # position is constant, move this outside get_data() to improve performance
			quads[i*24+j]["position"] = [((float(i-64) / 68.0)-0.05, (float(j-12) / -13.0)-0.05),
								((float(i-64) / 68.0)+0.05, (float(j-12) / -13.0)-0.05),
								((float(i-64) / 68.0)-0.05, (float(j-12) / -13.0)+0.05),
								((float(i-64) / 68.0)+0.05, (float(j-12) / -13.0)+0.05)]
            # color of each pixel
            quads[i*24+j]["color"] = float(temp_pixels[i,j]) / 65535.0

    # convert to celsius
	'''
	if np.sum(read[sensor]) == 6:
		to_celsius(sensor)
		print(str(sensor) + ":")
		print(celsius[sensor])
		print("")
	'''

'''
# converts sensor data to degrees C
# based on MLX90640_API.cpp MLX90640_CalculateTo
def to_celsius(sensor):
	# approximate values of mlx sensor params needed for conversion to celsius
	emissivity = 0.95
	vdd = 2.75
	ta = 25.0
	tr = ta - 8.0
	ta4 = (ta + 273.15)**4.
	tr4 = (tr + 273.15)**4.
	taTr = tr4 - (tr4-ta4)/emissivity
	ksTo = [0., -0.000198, -0.000900, -0.001495]
	ct = [-40, 0, 100, 200]
	gainEE = [5981, 5786, 5743, 5678]
	cpOffset = [[-84, -79],
				[-59, -54],
				[-64, -60],
				[-71, -66]]
	cpKta = [0.005127, 0.004028, 0.004639, 0.004761]
	cpKv = 0.25
	ilChessC = [[-0.125, 3.5, 0.],
				[0.375, 3.5, 0.],
				[0.625, 3., 0.125],
				[1.25, 3., -0.125]]

	alphaCorrR = [1, 1, 1, 1]
	alphaCorrR[0] = 1 / (1 + ksTo[0] * 40)
	alphaCorrR[2] = 1 + ksTo[2] * ct[2]
	alphaCorrR[3] = alphaCorrR[2] * (1 + ksTo[3] * (ct[3] - ct[2]))

	gain = data[sensor][778]
	if gain > 32767:
		gain = gain - 65536
	gain = gainEE[sensor] / gain

	irDataCP = [data[sensor][776], data[sensor][808]]
	for i in range(len(irDataCP)):
		if irDataCP[i] > 32767:
			irDataCP[i] = irDataCP[i] - 65536
		irDataCP[i] = irDataCP[i] * gain

	irDataCP[0] = irDataCP[0] - cpOffset[sensor][0] * (1 + cpKta[sensor] * (ta - 25)) * (1 + cpKv * (vdd - 3.3))
	irDataCP[1] = irDataCP[1] - (cpOffset[sensor][1] + ilChessC[sensor][0]) * (1 + cpKta[sensor] * (ta - 25)) * (1 + cpKv * (vdd - 3.3))

	result = np.zeros((768), dtype=float)
	for i in range(0, 768):
		ilPattern = i / 32 - (i / 64) * 2
		chessPattern = ilPattern ^ (i - (i / 2) * 2)
		conversionPattern = ((i + 2) / 4 - (i + 3) / 4 + (i + 1) / 4 - i / 4) * (1 - 2 * ilPattern)
		pattern = chessPattern
		if pattern == data[sensor][833]:
			irData = data[sensor][i]
			if irData > 32767:
				irData = irData - 65536
			irData = irData * gain
			irData = irData -
	celsius[sensor] = np.reshape(result, (32, 24))
'''

if __name__ == "__main__":
	try:
        # init node
		rospy.init_node('thermal_unit_test')
        # init subscribers
		rospy.Subscriber('/thermal_0i',  Int16MultiArray, get_data, callback_args=(0), queue_size=10)
		rospy.Subscriber('/thermal_1i',  Int16MultiArray, get_data, callback_args=(1), queue_size=10)
		rospy.Subscriber('/thermal_2i',  Int16MultiArray, get_data, callback_args=(2), queue_size=10)
		rospy.Subscriber('/thermal_3i',  Int16MultiArray, get_data, callback_args=(3), queue_size=10)
		rospy.sleep(1)
        # init glumpy app
		app.run()
		while(not rospy.is_shutdown()):
			pass
	except rospy.ROSInterruptException:
		pass
