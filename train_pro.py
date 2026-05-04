import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.datasets import mnist
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import os
from PIL import Image

# =========================
# LOAD MNIST
# =========================
(x_train, y_train), (x_test, y_test) = mnist.load_data()

x_train = x_train.astype("float32") / 255.0
x_test = x_test.astype("float32") / 255.0

x_train = x_train.reshape(-1,28,28,1)
x_test = x_test.reshape(-1,28,28,1)

# =========================
# LOAD CUSTOM DATASET
# =========================
custom_images = []
custom_labels = []

dataset_path = "dataset"

for label in range(10):

    folder = os.path.join(dataset_path, str(label))

    if not os.path.exists(folder):
        continue

    for file in os.listdir(folder):

        path = os.path.join(folder, file)

        try:
            img = Image.open(path).convert("L")
            img = img.resize((28,28))

            img = np.array(img)

            img = 255 - img

            img = img.astype("float32") / 255.0

            custom_images.append(img)
            custom_labels.append(label)

        except:
            pass

# =========================
# ADD CUSTOM DATA
# =========================
if len(custom_images) > 0:

    custom_images = np.array(custom_images)
    custom_images = custom_images.reshape(-1,28,28,1)

    custom_labels = np.array(custom_labels)

    x_train = np.concatenate((x_train, custom_images))
    y_train = np.concatenate((y_train, custom_labels))

print("Training Images:", len(x_train))

# =========================
# AUGMENTATION
# =========================
datagen = ImageDataGenerator(
    rotation_range=10,
    zoom_range=0.1,
    width_shift_range=0.1,
    height_shift_range=0.1
)

# =========================
# MODEL
# =========================
# =========================
# MODEL
# =========================
model = models.Sequential([

    layers.Input(shape=(28,28,1)),

    layers.Conv2D(32, (3,3), activation='relu'),    #detects pattern (edges,shapes)
    layers.BatchNormalization(),
    layers.Conv2D(32, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),

    layers.Conv2D(64, (3,3), activation='relu'),
    layers.BatchNormalization(),
    layers.Conv2D(64, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),   #reduces sizes

    layers.Flatten(),

    layers.Dense(256, activation='relu'),

    layers.Dropout(0.4),

    layers.Dense(10, activation='softmax')  #op prob(0-9)
])

# =========================
# COMPILE
# =========================
model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# =========================
# TRAIN
# =========================
model.fit(
    datagen.flow(x_train, y_train, batch_size=64),
    epochs=15,
    validation_data=(x_test, y_test)
)

# =========================
# SAVE MODEL
# =========================
model.save("mnist_cnn_model.h5")

print("PERFECT MODEL READY")