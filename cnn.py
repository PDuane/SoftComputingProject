from tensorflow import keras, data
import os
import glob

# TRAINING_RATIO = 0.8
TESTING_RATIO = 0.2
BATCH_SIZE = 50
EPOCHS = 100

master_genres = ['rock', 'metal', 'pop', 'blues', 'country', 'classic', 'alternative', 'hip hop', 'punk', 'reggae', 'folk', 'jazz']
root_dir = "prelim_processed"

model = keras.Sequential([
    keras.layers.Conv2D(64, 3),
    keras.layers.Conv2D(64, 3),
    keras.layers.MaxPool2D(2),

    keras.layers.Conv2D(128, 3),
    keras.layers.Conv2D(128, 3),
    keras.layers.MaxPool2D(2),

    keras.layers.Conv2D(256, 5),
    keras.layers.Conv2D(256, 3),
    keras.layers.MaxPool2D(4),

    keras.layers.Conv2D(512, 3),
    keras.layers.MaxPool2D(4),

    keras.layers.Flatten(),
    keras.layers.GlobalAveragePooling1D(),
    keras.layers.Dense(1024),
    keras.layers.Dense(512),
    keras.layers.Dense(12, activation=keras.activations.softmax)
    # keras.layers.Softmax()
])

model.compile(optimizer=keras.optimizers.Adam(learning_rate=1e-3),
              loss=keras.losses.SparseCategoricalCrossentropy())

# genres_dict = {}

# for i in range(len(master_genres)):
#     genres_dict[master_genres[i]] = i

dataset = keras.utils.image_dataset_from_directory("dataset_labeled")

dataset_len = len(list(dataset))

ds_test = dataset.take(int(TESTING_RATIO * dataset_len))
ds_train = dataset.skip(int(TESTING_RATIO * dataset_len))

model.fit_generator(ds_train, 50, len(list(ds_train)) // BATCH_SIZE, EPOCHS)

model.predict_generator(ds_test)

# dataset = []

# for root, dirs, files in os.walk(root_dir):
#         for f in files:
#             if f.endswith(".h3"):
#                 file_root = os.path.join(root, f[:-3])
#                 label = -1
#                 with open("{}.lab".format(file_root)) as f:
#                     label = master_genres.index(f.readline().strip())
#                     f.close()
                
#                 images = glob.glob("{}*.bmp".format(file_root))
#                 for img in images:
#                     dataset.append
    