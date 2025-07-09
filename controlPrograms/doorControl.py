
import rospy
from std_msgs.msg import String
from darknet_ros_msgs.msg import BoundingBoxes
import subprocess
import os 
import time

def executeProc():
    proc = subprocess.Popen(['roslaunch darknet_yolo dndoors.launch'], shell=True)
    time.sleep(12)
    proc.terminate()

def listener():
    rospy.Subscriber("/darknet_ros/bounding_boxes", String, callback)
    rospy.Subscriber("finishCmd", BoundingBoxes, callback)
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()


def callback(data):
    rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
    if (data.data == "reached goal"):
	#executeProc()
	proc = subprocess.Popen(['roslaunch darknet_yolo dndoors.launch'], shell=True)
	#os.system("roslaunch darknet_yolo dndoors.launch")
    	for box in data.bounding_boxes:
		stored = box.Class
		print(stored)
		if(stored == "Closed door"):
			pub4_.publish("door closed")
			proc.terminate()
			break
		elif(stored == "Open door"):
			pub4_.publish("door open")
			proc.terminate()
			break 
        	#rospy.loginfo("Xmin: {}, Xmax: {} Ymin: {}, Ymax: {}".format(box.xmin, box.xmax, box.ymin, box.ymax))


if __name__=="__main__":
    pub4_ = rospy.Publisher('doorReport', String, queue_size=10)
    try:
        print("Connecting to VisualBot ROSCORE")
        rospy.init_node('doorListen', anonymous=False)
        print("Connected to VisualBot Correctly")
        listener()
    except rospy.ROSInterruptException:
        rospy.loginfo("Ctrl-C caught. Quitting")    

