import hdf5_getters as h5
import os

dir = "MillionSongSubset\A\A\A"
lst = os.listdir(dir)
files = [os.path.join(dir, f) for f in lst if os.path.isfile(os.path.join(dir, f))]
for f in files:
    file = h5.open_h5_file_read(f)
    art_name = h5.get_artist_name(file).decode('UTF-8')
    song_name = h5.get_title(file).decode('UTF-8')
    # print(type(art_name))

    file.close()
    print("{sname} by {aname}".format(sname = str(song_name), aname = str(art_name)))
