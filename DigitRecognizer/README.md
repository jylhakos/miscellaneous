# Digit Recognizer

MNIST ("Modified National Institute of Standards and Technology") is the de facto dataset of handwritten images.

The goal is to identify digits from a dataset of handwritten images. 

Each training example consists of the image of a digit and a label, which tells us which digit the image represents.

The image is processed by the neural network, which produces an answer.

The answer is compared to the label and if the the answer is different from the label then feedback is given to the neural network so that it can improve the answer. 

The connections between the neurons are modified and and the neural network learns in an iterative process.

The Convolutional Neural Networks (CNNs) are useful for finding patterns in images to recognize objects, classes, and categories. 

The convolutional layers perform operations that alter the data with the intent of learning features specific to the data. Three of the most common layers are convolution, activation or ReLU, and pooling.

Filters are applied to each training image at different resolutions, and the output of each convolved image is used as the input to the next layer.

The standard way to construct a convolutional neural network is to have several convolutional layers, sometimes with max pooling and then have one or several dense layers just before the output layer.

As the input features flow through more and more hidden convolutional layers, more and more refined image features are detected.

You can classify new images using the VGG-19 network. 

```

from tensorflow.keras.applications.vgg19 import VGG19
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg19 import preprocess_input
from tensorflow.keras.models import Model
import numpy as np

base_model = VGG19(weights='imagenet')
model = Model(inputs=base_model.input, outputs=base_model.get_layer('block4_pool').output)

img_path = 'bicycle.png'
img = image.load_img(img_path, target_size=(224, 224))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)
x = preprocess_input(x)

block4_pool_features = model.predict(x)

```

![alt text](https://github.com/jylhakos/miscellaneous/blob/main/DigitRecognizer/convolutional.jpg?raw=true)

Figure: A convolutional neural network

***References***

Convolutional Neural Networks https://deeplearningmath.org/convolutional-neural-networks.html

Feature Learning, Layers, and Classification https://uk.mathworks.com/discovery/convolutional-neural-network-matlab.html

Classify images https://www.tensorflow.org/tutorials/keras/classification
