import h5py

fname = "MillionSongSubset\A\A\A\TRAAAAW128F429D538.h5"

with h5py.File(fname, "r") as f:
    print(f.data)
    print("Keys: %s" % f.keys())
    for key in list(f.keys()):
        print("%s: %s" % (key, f[key].keys()))