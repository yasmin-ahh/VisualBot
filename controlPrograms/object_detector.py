'''
Example usage:
    python object_detector.py \
        --input_cam=0

'''
import tensorflow.compat.v1 as tf
import numpy as np
import os
import sys
import time
import cv2
from gtts import gTTS
import playsound
import subprocess as sp

# Here are the imports from the object detection module.
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

###ADDED INPUT STREAM FROM RPI########

FFMPEG_BIN = "ffmpeg" # on Linux ans Mac OS
#-i tcp://192.168.0.15:2222
command = [ FFMPEG_BIN,
                        '-i', 'tcp://raspberrypi:2222',
                #       '-f', 'image2pipe',
                        '-f', 'rawvideo',
                        '-tune', 'zerolatency',
                        '-fflags', 'nobuffer',
                        '-preset','ultrafast',
                        '-pix_fmt', 'rgb24',
                        '-vcodec', 'rawvideo', '-']
pipe = sp.Popen(command, stdout = sp.PIPE, bufsize=10**8)

# read 420*360*3 bytes (= 1 frame)
width = 640
height = 480


#######DONE#######

flags = tf.app.flags
flags.DEFINE_integer('input_cam', 0, 'Cam Number.')
FLAGS = flags.FLAGS

# Model preparation
MODEL_NAME = 'object_detection/ssd_mobilenet_v1_coco_11_06_2017'

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join('object_detection/data', 'mscoco_label_map.pbtxt')

NUM_CLASSES = 90

# Load a (frozen) Tensorflow model into memory.
detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.GraphDef()
  with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
    serialized_graph = fid.read()
    od_graph_def.ParseFromString(serialized_graph)
    tf.import_graph_def(od_graph_def, name='')

# Loading label map
'''
Label maps map indices to category names, so that when our convolution network predicts `5`, we know that this corresponds to `airplane`.  Here we use internal utility functions, but anything that returns a dictionary mapping integers to appropriate string labels would be fine
'''
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

#add Voice System:
buf_name=""
def found(self):
    text="There is a {} in front of you".format(self)
    filename="voice.mp3"
    tts = gTTS(text=text, lang='en')
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)



# Helper code
def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)

# Detection
with detection_graph.as_default():
  with tf.Session(graph=detection_graph) as sess:
    # Opencv, Video capture
    input_cam = FLAGS.input_cam
    cap = cv2.VideoCapture(input_cam)
    if cap.isOpened() == False:
      print('Can\'t open the CAM(%d)' % (input_cam))
      exit()

    prevTime = 0  # Frame time variable

    # Recording Video
    fps = 30.0
    width = int(cap.get(3))
    height = int(cap.get(4))
    fcc = cv2.VideoWriter_fourcc('D', 'I', 'V', 'X')
    out = cv2.VideoWriter("save_video.avi", fcc, fps, (width, height))

    while True:
      # Opencv, Video capture
      raw_image = pipe.stdout.read(width*height*3) #takes 0.15 secs per call.  
        # transform the byte read into a numpy array
      image_np =  np.fromstring(raw_image, dtype='uint8')
      image_np = image_np.reshape((height,width,3))
        # throw away the data in the pipe's buffer.
      pipe.stdout.flush()
      # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
      image_np_expanded = np.expand_dims(image_np, axis=0)
      image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
      # Each box represents a part of the image where a particular object was detected.
      boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
      # Each score represent how level of confidence for each of the objects.
      # Score is shown on the result image, together with the class label.
      scores = detection_graph.get_tensor_by_name('detection_scores:0')
      classes = detection_graph.get_tensor_by_name('detection_classes:0')
      num_detections = detection_graph.get_tensor_by_name('num_detections:0')
      # Actual detection.
      (boxes, scores, classes, num_detections) = sess.run(
          [boxes, scores, classes, num_detections],
          feed_dict={image_tensor: image_np_expanded})
      # Visualization of the results of a detection.
      vis_util.visualize_boxes_and_labels_on_image_array(
          image_np,
          np.squeeze(boxes),
          np.squeeze(classes).astype(np.int32),
          np.squeeze(scores),
          category_index,
          use_normalized_coordinates=True,
          min_score_thresh=.5,
          line_thickness=4)
    
      ################### Data analysis ###################
      print("")
      final_score = np.squeeze(scores)  # scores
      r_count = 0  # counting
      r_score = []  # temp score, <class 'numpy.ndarray'>
      final_category = np.array([category_index.get(i) for i in classes[0]]) # category
      r_category = np.array([])  # temp category
      
      for i in range(100):
        if scores is None or final_score[i] > 0.7:
          r_count = r_count + 1
          r_score = np.append(r_score, final_score[i])
          r_category = np.append(r_category, final_category[i])
      
      if r_count > 0:
        print("Number of bounding boxes: ", r_count)
        print("")
      else:
        print("Not Detect")
        print("")
      for i in range(len(r_score)):  # socre array`s length
        print("Object Num: {} , Category: {} , Score: {}%".format(i+1, r_category[i]['name'], 100*r_score[i]))
        
        if buf_name!=r_category[i]['name']:

            print("Voice output expected")
            print("")
            buf_name=r_category[i]['name']
        final_boxes = np.squeeze(boxes)[i]  # ymin, xmin, ymax, xmax
        xmin = final_boxes[1]
        ymin = final_boxes[0]
        xmax = final_boxes[3]
        ymax = final_boxes[2]
        location_x = (xmax+xmin)/2
        location_y = (ymax+ymin)/2
        # print("final_boxes [ymin xmin ymax xmax]")
        # print("final_boxes", final_boxes)
        print("Location x: {}, y: {}".format(location_x, location_y))
        print("")
      print("+ " * 30 ) 
      #####################################################        

      # Frame
      curTime = time.time()
      sec = curTime - prevTime
      prevTime = curTime
      fps = 1/(sec)
      str = "FPS : %0.1f" % fps

      # Display
      display_model_name = MODEL_NAME.split('/')[1]
      cv2.putText(image_np, display_model_name, (5, 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0))
      cv2.putText(image_np, str, (5, 40), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0))
      cv2.imshow('Object Detection', cv2.resize(image_np, (1300,800)))

      # Recording Video
      out.write(image_np)

      if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
