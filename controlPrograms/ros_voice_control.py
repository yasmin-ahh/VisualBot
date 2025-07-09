#!/usr/bin/env python

"""This module is a simple demonstration of voice control
for ROS turtlebot using pocketsphinx
"""

import argparse
import roslib
import rospy
import pyttsx3
import os
import time
from std_msgs.msg import String

engine = pyttsx3.init()
from geometry_msgs.msg import Twist

from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *
import pyaudio
global i
global concat 
global count


def tts(text):
      return os.system("espeak  -s 155 -a 200 "+text+" " )

def processString(word):
	goTo = False
	RooM = False
	NuM = 0
	cmds = ["cmd1", "cmd2", "cmd3", "cmd4", "cmd5", "cmd6", "cmd7", "cmmd8", "cmd9", "cmd10", "cmd11"]
	current = "none"
	if (("go to" in word) or ("take me" in word)):
		goTo = True 
		if ("room" in word):
			RooM = True 
			if("four" in word):
				NuM = 4 
				current = cmds[3]
			elif("five" in word):
				NuM = 5
				current = cmds[4]
			elif("six" in word):
				NuM = 6
				current = cmds[5]
			elif("seven" in word):
				NuM = 7
				current = cmds[6]
			elif("eight" in word):
				NuM = 8
				current = cmds[7]
			elif("one" in word):
				NuM = 1
				current = cmds[0]
			elif("two" in word):
				NuM = 2
				current = cmds[1]
			elif("three" in word):
				NuM = 3
				current = cmds[2]
		elif ("exit door" in word):
			NuM = 9
			current = cmds[8]      
		elif ("door lab" in word):
			NuM = 10
			current = cmds[9] 
		elif ("vending machine" in word):
			NuM = 11
			current = cmds[10] 
	if(goTo == True and RooM == True and NuM != 0) or (goTo == True and NuM>=9): 
		return current 
      

class ASRControl(object):
    """Simple voice control interface for ROS turtlebot

    Attributes:
        model: model path
        lexicon: pronunciation dictionary
        kwlist: keyword list file
        pub: where to send commands (default: 'mobile_base/commands/velocity')

    """
    def __init__(self, model, lexicon, kwlist, pub):
        # initialize ROS
        self.speed = 0.2
        self.msg = Twist()

        rospy.init_node('voice_cmd')
        rospy.on_shutdown(self.shutdown)

        # you may need to change publisher destination depending on what you run
        self.pub_ = rospy.Publisher('voice', String, queue_size=10)

        # initialize pocketsphinx
        config = Decoder.default_config()
        config.set_string('-hmm', model)
        config.set_string('-dict', lexicon)
        config.set_string('-kws', kwlist)

        stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1,
                        rate=16000, input=True, frames_per_buffer=1024)
        stream.start_stream()

        self.decoder = Decoder(config)
        self.decoder.start_utt()
	i = 0
	concat = ""
	count = 0
        while not rospy.is_shutdown():
	    while (i<=7):
		    buf = stream.read(1024)
		    if buf:
		        self.decoder.process_raw(buf, False, False)
		    else:
		        break
		    #self.parse_asr_result(0)
		
		    i, concat, count = self.parse_asr_result(i, concat, count)
		    #print ("num = ", count)
		    print("concat =", concat)
		    #print("i = ", i)

    def parse_asr_result(self, i, concat, count):
        """
        move the robot based on ASR hypothesis
        """
	concat1 = ""
        if self.decoder.hyp() != None:
            print ([(seg.word, seg.prob, seg.start_frame, seg.end_frame)
                for seg in self.decoder.seg()])
	    
	 
	    #concat = concat + seg.word
	    #concat = ""
	    #if(seg.word.find("visual ")) > -1:
		#i = i+5
		#print(i)
	    if (seg.word.find("bot ")) > -1 and (count==0):
		print("found")
		#engine.say("hello there")
   		#engine.runAndWait()
   		#engine.stop()
		tts("'Hello There'")
		count = 1
	    	self.decoder.end_utt()
	    	self.decoder.start_utt()
	    elif (count ==1): 
		print ("New word")
		self.decoder.end_utt()
	        self.decoder.start_utt()
		seg.word = seg.word.lower()
	        concat = concat + seg.word
		if (i==7):
			#count = 0 
			#i = 0
			concat1 = processString(concat)
			print(concat1)
			concat = ""
			#time.sleep(10)
		#j = 6
            i = i+1
            #seg.word = seg.word.lower()
	    #concat = concat + seg.words
	    #self.decoder.end_utt()
	    #self.decoder.start_utt()


            # you may want to modify the main logic here
        return i, concat, count

        self.pub_.publish(concat)

    def shutdown(self):
        """
        command executed after Ctrl+C is pressed
        """
        rospy.loginfo("Stop ASRControl")
        #self.pub_.publish(Twist())
        rospy.sleep(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Control ROS turtlebot using pocketsphinx.')
    parser.add_argument('--model', type=str,
        default='.local/lib/python2.7/site-packages/pocketsphinx/model/en-us',
        help='''acoustic model path
        (default: .local/lib/python2.7/site-packages/pocketsphinx/model/en-us)''')
    parser.add_argument('--lexicon', type=str,
        default='.local/lib/python2.7/site-packages/pocketsphinx/model/cmudict-en-us.dict',
        help='''pronunciation dictionary
        (default: .local/lib/python2.7/site-packages/pocketsphinx/model/cmudict-en-us.dict)''')
    parser.add_argument('--kwlist', type=str,
        default='voice_cmd.kwlist',
        help='''keyword list with thresholds
        (default: voice_cmd.kwlist)''')
    parser.add_argument('--rospub', type=str,
        default='mobile_base/commands/velocity',
        help='''ROS publisher destination
        (default: mobile_base/commands/velocity)''')

    args = parser.parse_args()
    ASRControl(args.model, args.lexicon, args.kwlist, args.rospub)
