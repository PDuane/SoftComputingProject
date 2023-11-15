# This program converts .mp3 audio preview to .wav files (to be
#     compatible with the Python library), then generates the
#     spectral image using the FFT

import simplejson as json
import requests
import time
import os
import urllib.parse as urllib
import shutil
import hdf5_getters as h5
import subprocess
import audio2spectroimg
from multiprocessing import Process, Lock, Array, Value
import random
import ctypes

# FFT size should be a power of two (256, 512, 1024, etc)
# The frequency resolution (pixels in the y-dimension) will be
#     half of fft_size (half of the values are redundant for
#     real-valued samples
fft_size = 512

# The number of pixels in the x direction
img_len = 256

# The number of samples to average for a single pixel in time
#     The audio has a sample rate of 44,100 Hz, which is much
#     higher than we need or want to deal with
# Averaging 882 samples into a single time step gives us
#     44,100 / 882 = 50 Hz,
#     or 1 sample for every .02 seconds. This is consistent with
#     the pictures generated in the Music-CRN paper
batch_size = 882
delay = 0.25

# We are using multiple threads to generate the spectral images
#     in order to speed up processing (this process takes a few
#     minutes per song)
# Change this number based on how many threads you want to use
num_parallel_procs = 8

# Keep track of what files still need to be processed
to_process = []
# Mutex lock to prevent parallel memory access issues
mutex = Lock()

# The process that acually generates the spectral images.
#     Each thread is running an instance of this function
def imageProcess(queue, counter, fft_size, img_len, batch_size):
    while (True):
        # Exit the loop (and terminate the thread) if there are no
        #     new files to be processed
        with counter.get_lock():
            if len(queue) <= counter.value:
                break
            wav_name = queue[counter.value]
            counter.value += 1
        print("Generating images for {fname}".format(fname=wav_name))
        audio2spectroimg.audio2images(wav_name, fft_size, img_len, batch_size)

# Make sure spawned threads/processes don't try to run the main function
if __name__ == '__main__':
    root_dir = "full_dataset_labeled"
    count = 0

    for root, dirs, files in os.walk(root_dir):
        for f in files:
            if f.endswith(".wav") or f.endswith(".mp3"):
                new_path = "{root_dir}\\{tree}".format(root_dir=root_dir, tree=root[len(root_dir) + 1:])
                
                # If the file ends with .mp3, convert it to a .wav first
                if (f.endswith(".mp3")):
                    mp3_name = os.path.join(new_path, f)
                    wav_name = os.path.join(new_path, "{}.wav".format(f[:-4]))
                    print("Processing {}".format(f))
                    subprocess.call(['ffmpeg', '-hide_banner', '-y', '-v', '0', '-i', mp3_name, wav_name])
                    os.remove(mp3_name)
                else:
                    wav_name = os.path.join(new_path, f)
                
                # Add the wave file to the processing queue
                mutex.acquire()
                print("Adding {} to processing queue".format(wav_name))
                to_process.append(wav_name)
                mutex.release()

    print("Files found: {}".format(count))
    print("Waiting for image processes to finish")

    # idx keeps track of where we are in the processing queue. Easier
    #     than trying to remove files from the queue
    idx = Value(ctypes.c_int, 0)

    # Spawn subprocesses
    procs = []
    for i in range(0,num_parallel_procs):
        print("Spawning process {num}".format(num=i + 1))
        p = Process(target=imageProcess, args=(to_process, idx, fft_size, img_len, batch_size))
        procs.append(p)
        p.start()

    # After all the subprocesses have been spawned, wait for them to finish
    for p in procs:
        p.join()
    
    print("done")
