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

engine = pyttsx3.init()
from geometry_msgs.msg import Twist

from std_msgs.msg import String

from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *
import pyaudio
global i
global concat 
global count

def tts(text):
      return os.system("espeak  -s 155 -a 200 "+text+" " )

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

        rospy.init_node('voice_cmd_vel')
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
	concat = "ss"
	count = 0
        while not rospy.is_shutdown():
	    buf = stream.read(1024)
	    if buf:
	        self.decoder.process_raw(buf, False, False)
	    else:
	        break
	    #self.parse_asr_result(0)
	
	    self.parse_asr_result(concat)

    def parse_asr_result(self, concat):
        """
        move the robot based on ASR hypothesis
        """
	#concat = ""
        if self.decoder.hyp() != None:
            print ([(seg.word, seg.prob, seg.start_frame, seg.end_frame)
                for seg in self.decoder.seg()])
	    

            seg.word = seg.word.lower()
	    #concat = concat + seg.words
	    self.decoder.end_utt()
	    self.decoder.start_utt()
	    if (seg.word.find("hello robot ")) > -1:
		print("found yay")
		#engine.say("hello there")
   		#engine.runAndWait()
   		#engine.stop()
		tts("'Hello There'")
		#count = 1
	    	#self.decoder.end_utt()
		concat = "start to send"
                self.pub_.publish(concat)
	    #self.decoder.end_utt()
	    #time.sleep(60) 

	#concat = ""

    def shutdown(self):
        """
        command executed after Ctrl+C is pressed
        """
        rospy.loginfo("Stop ASRControl")
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
