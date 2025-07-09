#engine.say("hello there")
#engine.runAndWait()
#engine.stop()

from gtts import gTTS
import pyttsx3
import os
import time
import rospy
import datetime
from geometry_msgs.msg import Twist

from std_msgs.msg import String

global i

i = 0
engine = pyttsx3.init()
#voices = engine.getProperty('voices')
#engine.setProperty('voice', voices[1].id)


def tts(text):
      return os.system("espeak  -s 155 -a 150 "+text+" " )

def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour>= 0 and hour<12 and (i==0):
        tts("'Good Morning '")
	tts("'I am your robot Assistant'")
	firstTime()
  
    elif hour>= 12 and hour<18 and (i==0):
        tts("'Good Afternoon '")
	tts("'I am your robot Assistant'") 
	firstTime() 
  
    else:
	if i==0:
            tts("'Good Evening '") 
	    tts("'I am your robot Assistant'")
	    firstTime()
  
    tts("'Please Tell me where to go  '")
def firstTime():
    tts("'Since this is the first time, I will give you some guidance'")
    tts("'In order to use me, tell me which location to go to'")
    tts("'There are eight different rooms here'")

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def listener():
    #rospy.init_node('voiceListener', anonymous=True)

    rospy.Subscriber("voice", String, callback)
    rospy.Subscriber("replyCmd", String, callback)
    rospy.Subscriber("finishCmd", String, callback)
    rospy.Subscriber("doorReport", String, callback)
    rospy.spin()

def callback(data):
    global i
    rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
    if(data.data == "start to send"):
	wishMe()  
	i = i+1
	#tts("hello there mate")
	
    elif(data.data == "exit door" or data.data == "laboratory door" or data.data == "vending machine"):
	text = "'Going to "+data.data + "'" 
        tts(text)
    elif(data.data == "stop"):
	tts("'I will Stop now'")
    elif(data.data == "no room"):
	tts("'Sorry, could not recognize room number'")
    elif(data.data == "reached goal"):
	tts("'I reached my goal'")
    elif(data.data == "door open"):
	tts("'I can see that the door is open'")
    elif(data.data == "door closed"):
	tts("'I can see that the door is closed'")
    else: 
	text = "'Going to room "+data.data + "'" 
        tts(text)

if __name__=="__main__":
    try:
        print("Connecting to VisualBot ROSCORE")
        rospy.init_node('voiceListen', anonymous=False)
        print("Connected to VisualBot Correctly")
	i = 0
        listener()
    except rospy.ROSInterruptException:
        rospy.loginfo("Ctrl-C caught. Quitting")    
	#main()
