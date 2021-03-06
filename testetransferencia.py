
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.python.keras.models import load_model
import numpy as np
import cv2, os, glob

classes = ['cats','dogs']
model = load_model("model.h5")

caminho = "/content/test"

for arquivo in glob.glob(os.path.join(caminho, "*")):
  image = tf.keras.preprocessing.image.load_img(r''+arquivo, target_size = (224,224))
  image = tf.keras.preprocessing.image.img_to_array(image)
  image = np.expand_dims(image, axis=0)

  image = tf.keras.applications.resnet50.preprocess_input(image)

  predictions = model.predict(image)

  prediction = classes[np.argmax(predictions[0])]
  print(prediction)
  print(arquivo)
