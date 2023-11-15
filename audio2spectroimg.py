from scipy.fft import fft
from scipy.io import wavfile
from scipy.signal.windows import hamming, blackman, blackmanharris
import numpy as np
from PIL import Image
import glob

# fft_size = 512
# img_len = 256
# batch_size = 882

def audio2images(filename, fft_size, img_len, batch_size):

    if not str(filename).endswith(".wav"):
        return

    samprate, samples = wavfile.read(filename)
    # freqs = np.linspace(0,samprate/2, num=fft_size)

    data = np.add(samples[:,0], samples[:,1]) / 2

    length = data.shape[0] / samprate
    time = np.linspace(0., length, len(data))

    samp_buf = np.zeros(fft_size)


    batch_data = np.zeros((fft_size, batch_size))

    img_num = 0

    samp_start = 0
    samp_stop = img_len * batch_size

    w = blackmanharris(fft_size)

    while batch_size * img_len * img_num < len(data):
        img_data = np.zeros((fft_size, img_len))
        batch_num = 0
        for i in range(samp_start,samp_stop):
            samp_buf = np.roll(samp_buf, fft_size - 1)
            samp_buf[-1] = data[i]
            # samp_buf = np.roll(samp_buf, 1)
            # samp_buf[0] = data[i]
            four = (fft(samp_buf * w, fft_size))
            # norm_four = abs(four) / np.linalg.norm(abs(four))
            # batch_data[:,i - (batch_num * batch_size)] = np.uint8(norm_four * 255)
            batch_data[:,i - samp_start - (batch_num * batch_size)] = abs(four)
            if (i + 1) % batch_size == 0:
                # print(batch_num + 1)
                img_data[:,batch_num] = np.mean(batch_data, axis=1)
                batch_data = np.zeros((fft_size, batch_size))
                batch_num += 1

        img_data = img_data[0:256,:]
        img_data = np.uint8((img_data / np.max(img_data)) * 255)
        img = Image.fromarray(img_data, 'L')
        samp_start = samp_stop
        samp_stop += img_len * batch_size
        if (samp_stop > len(data)):
            samp_stop = len(data)

        outname = '{name}_{num}.bmp'.format(name = filename[0:-4], num = img_num+1)

        # if img.mode != 'RGB':
        #     img = img.convert('RGB')

        img.save(outname)
        img_num += 1

# filename = 'mss_preview_dataset\\A\\A\\A\\TRAAABD128F429CF47.wav'

# files = glob.glob('mss_preview_dataset\\A\\A\\A\\*.wav')

# for f in files:
#     print(f)
#     audio2images(f, 512, 256, 882)

# audio2images('mss_preview_dataset\\A\\A\\A\\TRAAABD128F429CF47.wav', 512, 256, 882)

# img.show()


# plt.plot(freqs,abs(four))

# plt.show()
