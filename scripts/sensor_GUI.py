#!/usr/bin/env python
import rospy
from sensor_msgs.msg import Temperature, RelativeHumidity
import Tkinter as tk
import tkFont

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.configure(background='#383838')
        self.createWidgets()

    def createWidgets(self):
        labelFont = tkFont.Font(family='Ubuntu', size=24)
        self.bmeTempLabel = tk.Label(self, text='BME Temp ', font=labelFont, fg='#e0e0e0', bg='#383838')
        self.bmeTempLabel.grid(row=0, column = 0)
        self.bmeTempDisplay = tk.Label(self, text='   N/A   ', font=labelFont, bg='#d0d0d0')
        self.bmeTempDisplay.grid(row=0, column=1)

        self.humidLabel = tk.Label(self, text='Humidity ', font=labelFont, fg='#e0e0e0', bg='#383838')
        self.humidLabel.grid(row=2, column = 0)
        self.humidDisplay = tk.Label(self, text='   N/A   ', font=labelFont, bg='#d0d0d0')
        self.humidDisplay.grid(row=2, column=1)


    def intern_temp(self, msg):
        temp = msg.temperature
        self.bmeTempDisplay.config(text=str(temp))
        if temp >= 35.0 and temp < 45.0:
            self.bmeTempDisplay.config(bg='#f0f000')
        elif temp >= 45.0 and temp < 60.0:
            self.bmeTempDisplay.config(bg='#e09000')
        elif temp >= 60.0:
            self.bmeTempDisplay.config(bg='#f00000')
        else:
            self.bmeTempDisplay.config(bg='#00f000')


    def humidity(self, msg):
        humid = msg.relative_humidity
        self.humidDisplay.config(text=str(humid))
        if humid >= .55 and humid < .65:
            self.humidDisplay.config(bg='#f0f000')
        elif humid >= .65 and humid < .80:
            self.humidDisplay.config(bg='#e09000')
        elif humid >= .80:
            self.humidDisplay.config(bg='#f00000')
        else:
            self.humidDisplay.config(bg='#00f000')


if __name__ == "__main__":
    try:
        app = Application()
        app.master.title('Internal Status')
        rospy.init_node('internal_status')
        rospy.Subscriber('/intern_temp', Temperature, app.intern_temp, queue_size=10)
        rospy.Subscriber('/intern_humidity', RelativeHumidity, app.humidity, queue_size=10)
        rospy.sleep(1)
        app.mainloop()
        while(not rospy.is_shutdown()):
            pass
    except rospy.ROSInterruptException:
        pass
