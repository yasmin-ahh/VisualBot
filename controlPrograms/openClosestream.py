import rospy
from std_msgs.msg import String
from darknet_ros_msgs.msg import BoundingBoxes
import subprocess
import os 
import time
import psutil

def listener():
    rospy.Subscriber("openStream", String, callback)
    rospy.spin()

def callback(data):
    if(data.data == "start stream"):
    	#proc = subprocess.Popen(['roslaunch darknet_ros dndoors.launch'], shell=True)
	#time.sleep(25)
	#proc.terminate()
	os.system("gnome-terminal -e \"timeout 40 roslaunch darknet_ros dndoors.launch\"")
	print("after close")
	#p = psutil.Process(proc.pid)
	#try: 
	#    p.wait(timeout = 20)
	#except psutil.TimeoutExpired:
	#    p.kill()
	#    proc.terminate()
	#    raise 
if __name__=="__main__":
    try:
        print("Connecting to VisualBot ROSCORE")
        rospy.init_node('streamListen', anonymous=False)
        print("Connected to VisualBot Correctly")
        listener()
    except rospy.ROSInterruptException:
        rospy.loginfo("Ctrl-C caught. Quitting")   
