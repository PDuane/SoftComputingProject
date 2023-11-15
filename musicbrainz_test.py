import musicbrainzngs as mbz
import hdf5_getters as h5

mbz.set_useragent('patrick.duane@student.nmt.edu', '0.1')

file = h5.open_h5_file_read('mss_preview_dataset\A\A\A\TRAAAEF128F4273421.h5')
h5.gettrack