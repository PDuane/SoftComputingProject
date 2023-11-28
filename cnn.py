import tensorflow as tf
import random

# TRAINING_RATIO = 0.8
TESTING_RATIO = 0.2
# BATCH_SIZE = 200
EPOCHS = 100 

master_genres = ['rock', 'metal', 'pop', 'blues', 'country', 'classic', 'alternative', 'hip hop', 'punk', 'reggae', 'folk', 'jazz']
root_dir = "../dataset_labeled"

def norm(image,label):
    image = tf.cast(image/255. ,tf.float32)
    return image,label

def scheduler(epoch, lr):
      if epoch < 10  :
          return lr
      else:
          return lr * tf.math.exp(-0.1)

# ds = tf.keras.preprocessing.image_dataset_from_directory(IMAGE_DIR)
# ds = ds.map(process)

reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.2,
                              patience=3, min_lr=1e-10)

model = tf.keras.Sequential([
#     keras.layers.Input(shape=(None,256,256,3)),        
    tf.keras.layers.Conv2D(64, 3),
    tf.keras.layers.Conv2D(64, 3),
    tf.keras.layers.MaxPool2D(2),

    tf.keras.layers.Conv2D(128, 3),
    tf.keras.layers.Conv2D(128, 3),
    tf.keras.layers.MaxPool2D(2),

    tf.keras.layers.Conv2D(256, 5),
    tf.keras.layers.Conv2D(256, 3),
    tf.keras.layers.MaxPool2D(4),

    tf.keras.layers.Conv2D(512, 3),
    tf.keras.layers.MaxPool2D(4),

    # keras.layers.Flatten(),
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(1024),
    tf.keras.layers.Dense(512),
    tf.keras.layers.Dense(12, activation=tf.keras.activations.softmax)
    # keras.layers.Softmax()
])

model.compile(optimizer=tf.keras.optimizers.Adam(),
              loss=tf.keras.losses.SparseCategoricalCrossentropy(),
              metrics=tf.keras.metrics.SparseCategoricalAccuracy())

# genres_dict = {}

# for i in range(len(master_genres)):
#     genres_dict[master_genres[i]] = i


s = random.randint(0, 2^32 - 1)
ds_train, ds_test = tf.keras.utils.image_dataset_from_directory("../dataset_labeled", validation_split=TESTING_RATIO, subset='both', seed=s)

ds_train = ds_train.map(norm)
ds_test = ds_test.map(norm)

lr_callbk = tf.keras.callbacks.LearningRateScheduler(scheduler)

history = model.fit(ds_train, epochs=EPOCHS, callbacks=[lr_callbk])

model.evaluate(ds_test)
    