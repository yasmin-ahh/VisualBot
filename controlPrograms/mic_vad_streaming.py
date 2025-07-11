import time, logging
from datetime import datetime
import threading, collections, queue, os, os.path
from std_msgs.msg import String
import deepspeech
import numpy as np
import rospy
import pyaudio
import wave
import webrtcvad
from halo import Halo
from scipy import signal

logging.basicConfig(level=20)

class Audio(object):
    """Streams raw audio from microphone. Data is received in a separate thread, and stored in a buffer, to be read from."""

    FORMAT = pyaudio.paInt16
    # Network/VAD rate-space
    RATE_PROCESS = 16000
    CHANNELS = 1
    BLOCKS_PER_SECOND = 50

    def __init__(self, callback=None, device=None, input_rate=RATE_PROCESS, file=None):
        def proxy_callback(in_data, frame_count, time_info, status):
            #pylint: disable=unused-argument
            if self.chunk is not None:
                in_data = self.wf.readframes(self.chunk)
            callback(in_data)
            return (None, pyaudio.paContinue)
        if callback is None: callback = lambda in_data: self.buffer_queue.put(in_data)
        self.buffer_queue = queue.Queue()
        self.device = device
        self.input_rate = input_rate
        self.sample_rate = self.RATE_PROCESS
        self.block_size = int(self.RATE_PROCESS / float(self.BLOCKS_PER_SECOND))
        self.block_size_input = int(self.input_rate / float(self.BLOCKS_PER_SECOND))
        self.pa = pyaudio.PyAudio()

        kwargs = {
            'format': self.FORMAT,
            'channels': self.CHANNELS,
            'rate': self.input_rate,
            'input': True,
            'frames_per_buffer': self.block_size_input,
            'stream_callback': proxy_callback,
        }

        self.chunk = None
        # if not default device
        if self.device:
            kwargs['input_device_index'] = self.device
        elif file is not None:
            self.chunk = 320
            self.wf = wave.open(file, 'rb')

        self.stream = self.pa.open(**kwargs)
        self.stream.start_stream()

    def resample(self, data, input_rate):
        """
        Microphone may not support our native processing sampling rate, so
        resample from input_rate to RATE_PROCESS here for webrtcvad and
        deepspeech

        Args:
            data (binary): Input audio stream
            input_rate (int): Input audio rate to resample from
        """
        data16 = np.fromstring(string=data, dtype=np.int16)
        resample_size = int(len(data16) / self.input_rate * self.RATE_PROCESS)
        resample = signal.resample(data16, resample_size)
        resample16 = np.array(resample, dtype=np.int16)
        return resample16.tostring()

    def read_resampled(self):
        """Return a block of audio data resampled to 16000hz, blocking if necessary."""
        return self.resample(data=self.buffer_queue.get(),
                             input_rate=self.input_rate)

    def read(self):
        """Return a block of audio data, blocking if necessary."""
        return self.buffer_queue.get()

    def destroy(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

    frame_duration_ms = property(lambda self: 1000 * self.block_size // self.sample_rate)

    def write_wav(self, filename, data):
        logging.info("write wav %s", filename)
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        # wf.setsampwidth(self.pa.get_sample_size(FORMAT))
        assert self.FORMAT == pyaudio.paInt16
        wf.setsampwidth(2)
        wf.setframerate(self.sample_rate)
        wf.writeframes(data)
        wf.close()


class VADAudio(Audio):
    """Filter & segment audio with voice activity detection."""

    def __init__(self, aggressiveness=3, device=None, input_rate=None, file=None):
        super().__init__(device=device, input_rate=input_rate, file=file)
        self.vad = webrtcvad.Vad(aggressiveness)

    def frame_generator(self):
        """Generator that yields all audio frames from microphone."""
        if self.input_rate == self.RATE_PROCESS:
            while True:
                yield self.read()
        else:
            while True:
                yield self.read_resampled()

    def vad_collector(self, padding_ms=300, ratio=0.75, frames=None):
        """Generator that yields series of consecutive audio frames comprising each utterence, separated by yielding a single None.
            Determines voice activity by ratio of frames in padding_ms. Uses a buffer to include padding_ms prior to being triggered.
            Example: (frame, ..., frame, None, frame, ..., frame, None, ...)
                      |---utterence---|        |---utterence---|
        """
        if frames is None: frames = self.frame_generator()
        num_padding_frames = padding_ms // self.frame_duration_ms
        ring_buffer = collections.deque(maxlen=num_padding_frames)
        triggered = False

        for frame in frames:
            if len(frame) < 640:
                return

            is_speech = self.vad.is_speech(frame, self.sample_rate)

            if not triggered:
                ring_buffer.append((frame, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                if num_voiced > ratio * ring_buffer.maxlen:
                    triggered = True
                    for f, s in ring_buffer:
                        yield f
                    ring_buffer.clear()

            else:
                yield frame
                ring_buffer.append((frame, is_speech))
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                if num_unvoiced > ratio * ring_buffer.maxlen:
                    triggered = False
                    yield None
                    ring_buffer.clear()
    

def listener():
    #rospy.init_node('listener', anonymous=True)

    rospy.Subscriber("voice", String, callback)
    rospy.spin()

def processString(word):
	goTo = False
	RooM = False
	finishbool = False
	NuM = 0
	#cmds = ["cmd1", "cmd2", "cmd3", "cmd4", "cmd5", "cmd6", "cmd7", "cmmd8", "cmd9", "cmd10", "cmd11", "cmd12"]
	current = "none"
	fullCmd = "none"
	if (("go to" in word) or ("take me" in word) or ("i want to go" in word) or ("go" in word) or ("let's go" in word)):
		goTo = True 
		if (("location" in word) or ("place" in word) or ("room" in word)):
			RooM = True 
			if("one two three four" in word):
				NuM = 1 
				fullCmd = "one two three four"
				#current = cmds[0]
			elif("one two three seven" in word):
				NuM = 2
				fullCmd = "one two three seven"
				#current = cmds[1]
			elif("one four five seven" in word):
				NuM = 3
				fullCmd = "one four five seven"
				#current = cmds[2]
			elif("one four five nine" in word):
				NuM = 4
				fullCmd = "one four five nine"
				#current = cmds[3]
			elif("one six five nine" in word):
				NuM = 5
				fullCmd = "one six five nine"
				#current = cmds[4]
			elif("one six seven eight" in word):
				NuM = 6
				fullCmd = "one six seven eight"
				#current = cmds[5]
			elif("three four five eight" in word):
				NuM = 7
				fullCmd = "three four five eight"
				#current = cmds[6]
			elif("five four three six" in word):
				NuM = 8
				fullCmd = "five four three six"
				#current = cmds[7]
			else: 
				fullCmd = "no room"
		elif ("exit door" in word or ("end of hall" in word) or ("stairs" in word)):
			NuM = 9
			fullCmd = "exit door"
			#current = cmds[8]      
		elif ("laboratory door" in word or ("lab door" in word) ):
			NuM = 10
			fullCmd = "laboratory door"
			#current = cmds[9] 
		elif ("vending machine" in word):
			NuM = 11
			fullCmd = "vending machine"
			#current = cmds[10]
	if ("stop" in word):
                finishbool = True
                NuM = 12 
                fullCmd = "stop"
                #current = cmds[11] 
	#if(goTo == True and RooM == True and NuM != 0) or (goTo == True and NuM>=9) or (finishbool == True): 
	current = "cmd"+str(NuM)
	return current, fullCmd 
                #finishbool = False
      


def main(ARGS):
    # Load DeepSpeech model
    if os.path.isdir(ARGS.model):
        model_dir = ARGS.model
        ARGS.model = os.path.join(model_dir, 'output_graph.pb')
        ARGS.scorer = os.path.join(model_dir, ARGS.scorer)

    print('Initializing model...')
    logging.info("ARGS.model: %s", ARGS.model)
    model = deepspeech.Model(ARGS.model)
    if ARGS.scorer:
        logging.info("ARGS.scorer: %s", ARGS.scorer)
        model.enableExternalScorer(ARGS.scorer)

    # Start audio with VAD
    vad_audio = VADAudio(aggressiveness=ARGS.vad_aggressiveness,
                         device=ARGS.device,
                         input_rate=ARGS.rate,
                         file=ARGS.file)
    
    print("Listening (ctrl-C to exit)...")
    frames = vad_audio.vad_collector()

    # Stream from microphone to DeepSpeech using VAD
    spinner = None
    if not ARGS.nospinner:
        spinner = Halo(spinner='line')
    stream_context = model.createStream()
    wav_data = bytearray()
    for frame in frames:
        if frame is not None:
            if spinner: spinner.start()
            logging.debug("streaming frame")
            stream_context.feedAudioContent(np.frombuffer(frame, np.int16))
            if ARGS.savewav: wav_data.extend(frame)
        else:
            if spinner: spinner.stop()
            logging.debug("end utterence")
            if ARGS.savewav:
                vad_audio.write_wav(os.path.join(ARGS.savewav, datetime.now().strftime("savewav_%Y-%m-%d_%H-%M-%S_%f.wav")), wav_data)
                wav_data = bytearray()
            newcon = "none"
            cmdTosend = "none"
            text = stream_context.finishStream()
            newcon, cmdTosend = processString(text)
            if( (newcon != "none" and newcon != "cmd0") or (newcon == "cmd0" and cmdTosend != "none")):
                pub_.publish(newcon)
                pub2_.publish(cmdTosend)
            print("Recognized: %s" % text)
            if 'finish' in text:
                vad_audio.destroy()
                newcon = "none"
                cmdTosend = "none"
                #break
                return 1
            stream_context = model.createStream()

if __name__ == '__main__':
    DEFAULT_SAMPLE_RATE = 16000
    pub_ = rospy.Publisher('voicecmd', String, queue_size=10)
    pub2_ = rospy.Publisher('replyCmd', String, queue_size=10)
    import argparse
    parser = argparse.ArgumentParser(description="Stream from microphone to DeepSpeech using VAD")

    parser.add_argument('-v', '--vad_aggressiveness', type=int, default=3,
                        help="Set aggressiveness of VAD: an integer between 0 and 3, 0 being the least aggressive about filtering out non-speech, 3 the most aggressive. Default: 3")
    parser.add_argument('--nospinner', action='store_true',
                        help="Disable spinner")
    parser.add_argument('-w', '--savewav',
                        help="Save .wav files of utterences to given directory")
    parser.add_argument('-f', '--file',
                        help="Read from .wav file instead of microphone")

    parser.add_argument('-m', '--model', required=True,
                        help="Path to the model (protocol buffer binary file, or entire directory containing all standard-named files for model)")
    parser.add_argument('-s', '--scorer',
                        help="Path to the external scorer file.")
    parser.add_argument('-d', '--device', type=int, default=None,
                        help="Device input index (Int) as listed by pyaudio.PyAudio.get_device_info_by_index(). If not provided, falls back to PyAudio.get_default_device().")
    parser.add_argument('-r', '--rate', type=int, default=DEFAULT_SAMPLE_RATE,
                        help="Input device sample rate. Default: {DEFAULT_SAMPLE_RATE}. Your device may require 44100.")
    ARGS = parser.parse_args()
    if ARGS.savewav: os.makedirs(ARGS.savewav, exist_ok=True)
    #main(ARGS)
    def callback(data):
        rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
        main(ARGS)
    try:
        print("Connecting to VisualBot ROSCORE")
        rospy.init_node('nav_test', anonymous=False)
        print("Connected to VisualBot Correctly")
        listener()
    except rospy.ROSInterruptException:
        rospy.loginfo("Ctrl-C caught. Quitting")
    #listener()
