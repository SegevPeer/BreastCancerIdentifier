import matplotlib
matplotlib.use("Agg")

from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping
import numpy as np
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from CNN_Model import CNN_Model
import config
from imutils import paths
import matplotlib.pyplot as plt
import numpy as np
import os

# Specify the number of classes and other parameters
classes = 2
NUM_EPOCHS = 10
INIT_LR = 1e-2
BS = 32

trainPaths = list(paths.list_images(config.TRAIN_PATH))
lenTrain = len(trainPaths)
lenVal = len(list(paths.list_images(config.VAL_PATH)))
lenTest = len(list(paths.list_images(config.TEST_PATH)))

trainLabels = [int(p.split(os.path.sep)[-2]) for p in trainPaths]
trainLabels = np.eye(classes)[trainLabels]
classTotals = trainLabels.sum(axis=0)
classWeight = classTotals.max() / classTotals

# Use GPU acceleration if available
import tensorflow as tf
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
    print("GPU acceleration enabled")

trainAug = ImageDataGenerator(
    rescale=1/255.0,
    rotation_range=20,
    zoom_range=0.05,
    width_shift_range=0.1,
    height_shift_range=0.1,
    shear_range=0.05,
    horizontal_flip=True,
    vertical_flip=True,
    fill_mode="nearest"
)

valAug = ImageDataGenerator(rescale=1 / 255.0)

trainGen = trainAug.flow_from_directory(
    config.TRAIN_PATH,
    class_mode="categorical",
    target_size=(48, 48),
    color_mode="rgb",
    shuffle=True,
    batch_size=BS
)

valGen = valAug.flow_from_directory(
    config.VAL_PATH,
    class_mode="categorical",
    target_size=(48, 48),
    color_mode="rgb",
    shuffle=False,
    batch_size=BS
)

testGen = valAug.flow_from_directory(
    config.TEST_PATH,
    class_mode="categorical",
    target_size=(48, 48),
    color_mode="rgb",
    shuffle=False,
    batch_size=BS
)

model = CNN_Model.build(width=48, height=48, depth=3, classes=2)
opt = Adam(learning_rate=INIT_LR)
model.compile(loss="binary_crossentropy", optimizer=opt, metrics=["accuracy"])

# Early stopping callback
early_stopping = EarlyStopping(monitor='val_loss', patience=5, verbose=1, restore_best_weights=True)

class_weight = {0: classWeight[0], 1: classWeight[1]}

M = model.fit(
    trainGen,
    steps_per_epoch=lenTrain // BS,
    validation_data=valGen,
    validation_steps=lenVal // BS,
    class_weight=class_weight,  # Specify class weights as a dictionary
    epochs=NUM_EPOCHS,
    callbacks=[early_stopping]  # Include the early stopping callback
)

print("Now evaluating the model")
testGen.reset()
pred_indices = model.predict(testGen, steps=(lenTest // BS) + 1)

pred_indices = np.argmax(pred_indices, axis=1)

print(classification_report(testGen.classes, pred_indices, target_names=testGen.class_indices.keys()))

cm = confusion_matrix(testGen.classes, pred_indices)
total = sum(sum(cm))
accuracy = (cm[0, 0] + cm[1, 1]) / total
specificity = cm[1, 1] / (cm[1, 0] + cm[1, 1])
sensitivity = cm[0, 0] / (cm[0, 0] + cm[0, 1])
print(cm)
print(f'Accuracy: {accuracy}')
print(f'Specificity: {specificity}')
print(f'Sensitivity: {sensitivity}')

N = NUM_EPOCHS
plt.style.use("ggplot")
plt.figure()
plt.plot(np.arange(0, N), M.history["loss"], label="train_loss")
plt.plot(np.arange(0, N), M.history["val_loss"], label="val_loss")
plt.plot(np.arange(0, N), M.history["accuracy"], label="train_accuracy")
plt.plot(np.arange(0, N), M.history["val_accuracy"], label="val_accuracy")
plt.title("Training Loss and Accuracy on the IDC Dataset")
plt.xlabel("Epoch No.")
plt.ylabel("Loss/Accuracy")
plt.legend(loc="lower left")
plt.savefig('plot.png')

model.save('my_model.keras')

