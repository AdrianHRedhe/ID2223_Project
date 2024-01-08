import tensorflow as tf
import numpy as np
import cv2

# Helper class for visualising the Sim search
class neighbor_info:
    def __init__(self,label,data,distance):
        self.label = label
        self.data = data
        self.distance = distance
        
def GeM(x):
    # Can make this hyper-param trainable but will not for now
    p = 3

    x = tf.math.maximum(x, 1e-6)
    x = tf.pow(x, p)
    x = tf.reduce_mean(x, axis=[1, 2], keepdims=False)
    x = tf.pow(x, 1.0 / p)
    return x

def from_path_to_image(path):
    bgr_image = cv2.imread(path)
    rgb_image = bgr_image[:, :, ::-1]
    return rgb_image
  
def string_row_to_array(string):
    float_list = string.strip('[ ]').split(', ')
    floats = [float(val) for val in float_list]
    return np.array(floats)