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

fft_size = 512
img_len = 256
batch_size = 882
delay = 0.25

num_parallel_procs = 8

to_process = []
mutex = Lock()

def imageProcess(queue, counter, fft_size, img_len, batch_size):
    while (True):
        with counter.get_lock():
            if len(queue) <= counter.value:
                break
            wav_name = queue[counter.value]
            counter.value += 1
        print("Generating images for {fname}".format(fname=wav_name))
        audio2spectroimg.audio2images(wav_name, fft_size, img_len, batch_size)

if __name__ == '__main__':
    root_dir = "dataset_labeled"
    count = 0

    for root, dirs, files in os.walk(root_dir):
        for f in files:
            if f.endswith(".wav") or f.endswith(".mp3"):
                new_path = "{root_dir}\\{tree}".format(root_dir=root_dir, tree=root[len(root_dir) + 1:])
                if (f.endswith(".mp3")):
                    mp3_name = os.path.join(new_path, f)
                    wav_name = os.path.join(new_path, "{}.wav".format(f[:-4]))
                    print("Processing {}".format(f))
                    subprocess.call(['ffmpeg', '-hide_banner', '-y', '-v', '0', '-i', mp3_name, wav_name])
                    os.remove(mp3_name)
                else:
                    wav_name = os.path.join(new_path, f)
                
                mutex.acquire()
                print("Adding {} to processing queue".format(wav_name))
                to_process.append(wav_name)
                mutex.release()

                # count = count + 1

    print("Files found: {}".format(count))
    print("Waiting for image processes to finish")

    idx = Value(ctypes.c_int, 0)
    # for i in range(0,len(to_process)):
    #     arr[i] = to_process[i].encode('utf-8')

    procs = []
    for i in range(0,num_parallel_procs):
        print("Spawning process {num}".format(num=i + 1))
        p = Process(target=imageProcess, args=(to_process, idx, fft_size, img_len, batch_size))
        procs.append(p)
        p.start()

    for p in procs:
        p.join()
    
    print("done")
