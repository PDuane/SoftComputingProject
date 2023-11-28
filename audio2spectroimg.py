# This file does the heavy lifting for converting a .wav file
#     to a spectral image

from scipy.fft import fft
from scipy.io import wavfile
from scipy.signal.windows import hamming, blackman, blackmanharris
import numpy as np
from PIL import Image

def audio2images(filename, fft_size, img_len, batch_size):
    # We need a .wav file to work with this library. If the
    #     provide file is not a .wav, don't attempt anything
    if not str(filename).endswith(".wav"):
        return

    # Read data from the file
    samprate, samples = wavfile.read(filename)

    # Merge the stereo channels into a mono channel
    data = np.add(samples[:,0], samples[:,1]) / 2

    # Determine the length in seconds of the sound file
    length = data.shape[0] / samprate
    time = np.linspace(0., length, len(data))

    # Initialize values

    samp_buf = np.zeros(fft_size)
    batch_data = np.zeros((fft_size, batch_size))

    # One audio file will result in multiple images
    # These keep track of where each image should start and stop
    img_num = 0
    samp_start = 0
    samp_stop = img_len * batch_size

    # Applying a window mitigates the effect of a finite sample set on
    #     the frequency response
    w = blackmanharris(fft_size)

    # While there are still samples to be processed
    while batch_size * img_len * img_num < len(data):
        # Create an empty array to convert to an image
        img_data = np.zeros((fft_size, img_len))
        batch_num = 0
        # Run the FFT on all the samples for the current image
        for i in range(samp_start,samp_stop):
            # Move all the samples back 1 spot
            samp_buf = np.roll(samp_buf, fft_size - 1)
            # Insert the new sample
            samp_buf[-1] = data[i]

            # Apply the window and run the FFT
            four = (fft(samp_buf * w, fft_size))
            # Store the result in the batch buffer
            batch_data[:,i - samp_start - (batch_num * batch_size)] = abs(four)
            # If the batch has been completed, take the average of the batch for
            #     each frequency point and store it in the image
            if (i + 1) % batch_size == 0:
                img_data[:,batch_num] = np.mean(batch_data, axis=1)
                batch_data = np.zeros((fft_size, batch_size))
                batch_num += 1

        # Look at the lower half of the frequency curve (upper half is redundant)
        img_data = img_data[0:256,:]
        # Map the values in the image between 0 and 255
        img_data = np.uint8((img_data / np.max(img_data)) * 255)
        # Convert the array to an Image object
        img = Image.fromarray(img_data, 'L')
        # Set the start and stop points for the next image
        samp_start = samp_stop
        samp_stop += img_len * batch_size
        if (samp_stop > len(data)):
            samp_stop = len(data)

        # Save the image
        outname = '{name}_{num}.bmp'.format(name = filename[0:-4], num = img_num+1)
        img.save(outname)
        img_num += 1