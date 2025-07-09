import rospy
from std_msgs.msg import String
from darknet_ros_msgs.msg import BoundingBoxes
import subprocess
import os 
import time
global i
i = 0

def listener2():
    rospy.Subscriber("finishCmd", String, callback2)
    rospy.spin()

def callback2(data2):
    if(data2.data == "reached goal"):
	i = 0
        listener()
def listener():
    pub5_.publish("start stream")
    rospy.Subscriber("/darknet_ros/bounding_boxes", BoundingBoxes, callback)
    
    #proc = subprocess.Popen(['roslaunch darknet_ros dndoors.launch'], shell=True)

def callback(data):
    #i = 0
    global i
    for box in data.bounding_boxes:
        stored = box.Class
	print(stored)
	print(box)
	if(stored == "closed" or stored == "opened" or stored == "semi"):
	    if(i==0):
	        pub4_.publish("door "+stored)
	    	i = i+1
	    	break 

if __name__=="__main__":
    pub4_ = rospy.Publisher('doorReport', String, queue_size=10)
    pub5_ = rospy.Publisher('openStream', String, queue_size=10)
    i = 0
    try:
        print("Connecting to VisualBot ROSCORE")
        rospy.init_node('doorListen', anonymous=False)
        print("Connected to VisualBot Correctly")
        listener2()
	#proc = subprocess.Popen(['roslaunch darknet_ros dndoors.launch'], shell=True)
    except rospy.ROSInterruptException:
        rospy.loginfo("Ctrl-C caught. Quitting")   
