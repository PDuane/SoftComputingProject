import os
from glob import glob
from shutil import copyfile

# Use a dictionary to keep track of the count of an entry
# (e.g. tracking the occurances of a word)
def dictCount(dict, k):
    if k in dict.keys():
        dict[k] += 1
    else:
        dict[k] = 1

# Returns an array of the n keys with the highest count values
# The dictionary should be of the format
#        {key:count}
def nMostCommon(n, dict):
    common = [['', 0]] * n
    for k in dict.keys():
        for i in range (0,n):
            if dict[k] > common[i][1]:
                for j in range (0, n-i-1):
                    common[n - j - 1] = common [n - j - 2]
                common[i] = [k, dict[k]]
                break
    return common

# The directory to read from
root_dir = "mss_preview_dataset"
# The directory to write the labeled dataset to
ds_dir = "full_dataset_labeled"

genres = {}
words = {}

# Stage 1: Identify the most common genre superclasses by the number of
#     occurrances of each word in the dataset genres
for root, dirs, files in os.walk(root_dir):
    for f in files:
        # Open the label file (has the list of genres)
        if f.endswith(".lab"):
            label_path = os.path.join(root, f)
            print(label_path)
            lab = open(label_path, 'r')
            # Each line has 1 genre specific to that artist
            genre = lab.readline()
            while genre != '':
                # dictCount(genres, genre.strip())
                ws = genre.strip().split(' ')
                # Subgenres usually have the supergenre in the name, so
                #     the most common word will probably be the most common
                #     supergenre
                for w in ws:
                    w = w.strip()
                    dictCount(words, w)
                genre = lab.readline()
            lab.close()

print("")

# Print out the 15 most common words
cmn = nMostCommon(15, words)
for l in cmn:
    print("{} --> {}".format(l[0], l[1]))

# !!! IMPORTANT !!!
# Place a debug breakpoint below to see the most common words/genres.
# NOTE: If you do not stop/pause execution here, the label file WILL get overwritten, and you
#     will have to start over.
#     YOU MAY WANT TO RUN THIS ON A COPY OF THE DATASET RATHER THAN THE ORIGINAL
# -------------------------------------------------------------------------------------------

# Stage 2: Labeling by supergenre in a new dataset structure
master_genres = ['rock', 'metal', 'pop', 'blues', 'country', 'classic', 'hip hop', 'alternative', 'punk', 'reggae', 'folk', 'jazz']

# Create a folder for each genre
for g in master_genres:
    pathname = "{}\\{}".format(ds_dir, g)
    if (not os.path.exists(pathname)):
        os.makedirs(pathname)

genre_count = {}
valid_files = 0

# For each track, count up the occurrances of each supergenre name in
#     the label file. The supergenre that has the most occurrances in
#     the file (or the first one found in case of a tie) is taken to
#     be the label for that track

# Walk through the entire dataset
for root, dirs, files in os.walk(root_dir):
    for f in files:
        # Read the label file with the specific genres
        if f.endswith(".lab"):
            label_path = os.path.join(root, f)
            lab = open(label_path, 'r')

            # Initialize the count for each genre to be 0
            for g in master_genres:
                genre_count[g] = 0
            
            # Each line contains one genre the artist belongs to.
            # If a line contains the name of a supergenre, add one to
            # the count for that genre
            genre = lab.readline()
            while genre != '':
                dictCount(genres, genre.strip())
                for g in master_genres:
                    if g in genre:
                        genre_count[g] += 1

                genre = lab.readline()
            
            lab.close()

            # Find the genre with the highest number of occurances in the
            #     label file
            genre = [master_genres[0], genre_count[master_genres[0]]]
            for i in range(1, len(master_genres)):
                if genre_count[master_genres[i]] > genre[1]:
                    genre = [master_genres[i], genre_count[master_genres[i]]]
            
            # Copy the audio preview file to the new dataset folder
            fname_root = f[0:-4]
            path_root = os.path.join(root, fname_root)
            fs = glob("{}*".format(path_root))
            if (genre[1] > 0):
                nfn = "{}\\{}\\{}".format(ds_dir, genre[0], "{}.mp3".format(fname_root))
                copyfile("{}.mp3".format(path_root), nfn)
                print("{} --> {}".format(label_path, genre[0]))
                valid_files += 1


print("{} valid files".format(valid_files))