# Music Classification
## Data Preprocessing
This repository has the code to download and process songs into spectral images. Below is a discussion of the various files and when/how to use them

### GenreLabeling.py
This file has two parts. The first half is used to identiy the most common genre superlabels. It is advised that you use a debugger and put a breakpoint where noted in the file, then manually enter the master list of genres based on the results it prints in the first half. The second half used the manually entered master genre list (at the beginning of `Stage 2`) to label the files in the preview dataset by moving them into a folder of the corresponding label

### process_mp3.py
This file goes through the provided directory and processes any .mp3 or .wav into a spectral image based on the parameters specified in the file. This process takes a _long_ time for a dataset of any reasonable size. It uses parallel processing to speed this up, so make sure you set the number of subprocesses to use (`num_parallel_procs` parameter). It is set to 8 by default.


## Neural Network Training
This repository also has the code to train a CNN based on the one in MusicCRN. This is in `cnn.py`.

### cnn.py
This program will read an image dataset from a specified directory. The directory should have the format:
```
directory_name
  |
  --- class 1
  |   |
  |   --- file 1
  |   --- file 2
  |     ...
  |   --- file n
  --- class 2
  |   |
  |   --- file 1
  |     ...
  |   --- file n
  | ...
  --- class n
```

The program will then use the images to train and evaluate the neural network