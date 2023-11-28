import tensorflow as tf
import random

def normalize(image,label):
    print(tf.norm(image))
    image = tf.cast(image/tf.norm(image) ,tf.float32)
    return image,label

TESTING_RATIO = 0.2

s = random.randint(0, 2^32 - 1)
ds_train, ds_test = tf.keras.utils.image_dataset_from_directory("../dataset_labeled", validation_split=TESTING_RATIO, subset='both', seed=s)

ds_train = ds_train.map(normalize)
ds_test = ds_test.map(normalize)

# ds_train and ds_test should both be normalized such that the euclidean
#     distance from origin for each image is 1

# Add clustering code below


