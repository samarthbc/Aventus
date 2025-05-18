import os
import tensorflow as tf
from tensorflow.keras.layers import Dropout  # type: ignore
from tensorflow.keras.utils import custom_object_scope  # type: ignore
import numpy as np
from tensorflow.keras.preprocessing import image  # type: ignore

# Define the FixedDropout layer
class FixedDropout(Dropout):
    def __init__(self, rate, **kwargs):
        super().__init__(rate, **kwargs)
        self.rate = rate

    def call(self, inputs):
        if self.rate > 0:
            return tf.nn.dropout(inputs, rate=self.rate)
        return inputs

# Load model with custom layer
# with custom_object_scope({'FixedDropout': FixedDropout}):
#     model = tf.keras.models.load_model('steganography_detection_model.h5')

model = tf.keras.models.load_model('steganography_detection_model.h5')

# Get directory path from user
folder_path = input("Enter directory path containing images: ")

# Loop through all files in directory
for filename in os.listdir(folder_path):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
        img_path = os.path.join(folder_path, filename)
        print(f"Processing {img_path}...")

        # Load & preprocess image
        img = image.load_img(img_path, target_size=model.input_shape[1:3])
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = tf.keras.applications.efficientnet.preprocess_input(img_array)

        # Predict
        predictions = model.predict(img_array)
        predicted_class = np.argmax(predictions, axis=1)

        print(f"File: {filename} | Predicted class: {predicted_class[0]} | Raw predictions: {predictions[0]}")
