import tensorflow as tf
from tensorflow.keras.layers import Dropout # type: ignore
from tensorflow.keras.utils import custom_object_scope # type: ignore
import numpy as np
from tensorflow.keras.preprocessing import image # type: ignore

# Define the FixedDropout layer (common in EfficientNet models)
class FixedDropout(Dropout):
    def __init__(self, rate, **kwargs):
        super().__init__(rate, **kwargs)
        self.rate = rate

    def call(self, inputs):
        if self.rate > 0:
            return tf.nn.dropout(inputs, rate=self.rate)
        return inputs


with custom_object_scope({'FixedDropout': FixedDropout}):
    model = tf.keras.models.load_model('effnetb0-A-alaska2-steghide.h5')

# Load and preprocess an image
img_path = input("Enter image path: ")  # Upload an image to Colab
img = image.load_img(img_path, target_size=model.input_shape[1:3])  # Resize to model's expected input
img_array = image.img_to_array(img)
img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
img_array = tf.keras.applications.efficientnet.preprocess_input(img_array)  # Normalize if needed

predictions = model.predict(img_array)
print("Raw predictions:", predictions)

# If classification, get the class with highest probability
predicted_class = np.argmax(predictions, axis=1)
print("Predicted class:", predicted_class)