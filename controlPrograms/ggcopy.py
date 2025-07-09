#!/usr/bin/env python


import rospy
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import actionlib
from actionlib_msgs.msg import *
from geometry_msgs.msg import Pose, Point, Quaternion
from std_msgs.msg import String

SeniorLabX = -6.55
SeniorLabY = 0.531
DoorLabX = -20.84
DoorLabY = -0.847
VendingMachX = -18.065
VendingMachY = 3.454
Room1X = -4.785
Room1Y = 2.144
Room2X = -3.618
Room2Y = 2.548 
Room3X = -0.765
Room3Y = 2.577 
Room4X = 6.29
Room4Y = 1.927 
Room5X = 7.904
Room5Y = 1.97 
Room6X = 2.735
Room6Y = 2.163
Room7X = 4.27
Room7Y = 1.40
EXitDoorX = 9.604
EXitDoorY = 1.41 
class GoToPose():
    def __init__(self):

        self.goal_sent = False

	# What to do if shut down (e.g. Ctrl-C or failure)
        rospy.on_shutdown(self.shutdown)
	
	# Tell the action client that we want to spin a thread by default
        self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        rospy.loginfo("Wait for the action server to come up")

	# Allow up to 5 seconds for the action server to come up
        self.move_base.wait_for_server(rospy.Duration(5))

    def goto(self, pos, quat, checkBool):

        # Send a goal
        self.goal_sent = True
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = 'map'
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose = Pose(Point(pos['x'], pos['y'], 0.000),
                                     Quaternion(quat['r1'], quat['r2'], quat['r3'], quat['r4']))

	# Start moving
        #self.move_base.send_goal(goal)

	# Allow TurtleBot up to 60 seconds to complete task
	if (checkBool == True):
            self.move_base.send_goal(goal)
            success = self.move_base.wait_for_result(rospy.Duration(6000)) 
	elif(checkBool == False):
	    success = False
        state = self.move_base.get_state()
        result = False

        if success and state == GoalStatus.SUCCEEDED:
            # We made it!
            result = True
        else:
            self.move_base.cancel_goal()

        self.goal_sent = False
        return result

    def shutdown(self):
        if self.goal_sent:
            self.move_base.cancel_goal()
        rospy.loginfo("Stop")
        rospy.sleep(1)
def funcDecide(data):
    x = 0
    y = 0
    if (data == "cmd1"):
        x,y = Room1X, Room1Y
    elif (data == "cmd2"):
        x,y = Room2X, Room2Y
    elif (data == "cmd3"):
        x,y = Room3X, Room3Y
    elif (data == "cmd4"):
        x,y = Room4X, Room4Y
    elif (data == "cmd5"):
        x,y = Room5X, Room5Y
    elif (data == "cmd6"):
        x,y = Room6X, Room6Y
    elif (data == "cmd7"):
        x,y = Room7X, Room7Y
    #elif (data == "cmd8"):
        #x,y = Room8X, Roo8Y
    elif (data == "cmd9"):
        x,y = EXitDoorX, EXitDoorY
    elif (data == "cmd10"):
        x,y = DoorLabX, DoorLabY
    elif (data == "cmd11"):
        x,y = VendingMachX, VendingMachY
    elif (data == "cmd12"):
	#move_base.cancel_goal()
	x = -100 
	y = -100 
    return x,y

def callback(data):
    #rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
    navigator = GoToPose()
    x,y = funcDecide(data.data)
    print("x and y", x, y)
    if (x!=0 and y!=0):
	    position = {'x': x, 'y' : y}
	    quaternion = {'r1' : 0.000, 'r2' : 0.000, 'r3' : 0.000, 'r4' : 1.000}

	    rospy.loginfo("Go to (%s, %s) pose", position['x'], position['y'])
	    if(x == -100 and y ==-100):
		print("yes i saw that")
	    	success = navigator.goto(position, quaternion, False)
	    else:
		success = navigator.goto(position, quaternion, True)
	   
	    if success:
		rospy.loginfo("Reached {} and {} Successfully".format(x,y))
		pub_.publish("reached goal")
		
	    else:
		rospy.loginfo("The base failed to reach the desired pose")

		# Sleep to give the last log messages time to be sent
		rospy.sleep(1)
    

def listener():

    rospy.Subscriber("voicecmd", String, callback)
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    pub3_ = rospy.Publisher('finishCmd', String, queue_size=10)
    try:
        print("Connecting to VisualBot ROSCORE")
        rospy.init_node('nav_test2', anonymous=True)
        print("Connected to VisualBot Correctly")
	listener()

    except rospy.ROSInterruptException:
        rospy.loginfo("Ctrl-C caught. Quitting")



