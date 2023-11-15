import os
from glob import glob
from shutil import copyfile

def dictCount(dict, k):
    if k in dict.keys():
        dict[k] += 1
    else:
        dict[k] = 1

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

root_dir = "prelim_processed"
ds_dir = "dataset_labeled"

genres = {}
words = {}

for root, dirs, files in os.walk(root_dir):
    for f in files:
        if f.endswith(".lab"):
            # fname_root = f[:-3]
            # label_path = os.path.join(root, "{}.lab".format(fname_root))
            label_path = os.path.join(root, f)
            print(label_path)
            lab = open(label_path, 'r')
            genre = lab.readline()
            while genre != '':
                dictCount(genres, genre.strip())
                ws = genre.strip().split(' ')
                for w in ws:
                    w = w.strip()
                    dictCount(words, w)
                # if genre.strip() in genres.keys():
                #     genres[genre.strip()] += 1
                # else:
                #     genres[genre.strip()] = 1
                genre = lab.readline()
            lab.close()

print("")

cmn = nMostCommon(15, words)
for l in cmn:
    print("{} --> {}".format(l[0], l[1]))

master_genres = ['rock', 'metal', 'pop', 'blues', 'country', 'classic', 'alternative', 'hip hop', 'punk', 'reggae', 'folk', 'jazz']

for g in master_genres:
    pathname = "{}\\{}".format(ds_dir, g)
    if (not os.path.exists(pathname)):
        os.makedirs(pathname)

genre_count = {}
valid_files = 0

for root, dirs, files in os.walk(root_dir):
    for f in files:
        if f.endswith(".lab"):
            label_path = os.path.join(root, f)
            lab = open(label_path, 'r')

            for g in master_genres:
                genre_count[g] = 0
            genre = lab.readline()
            while genre != '':
                dictCount(genres, genre.strip())
                for g in master_genres:
                    if g in genre:
                        genre_count[g] += 1

                genre = lab.readline()
            
            lab.close()

            genre = [master_genres[0], genre_count[master_genres[0]]]
            for i in range(1, len(master_genres)):
                if genre_count[master_genres[i]] > genre[1]:
                    genre = [master_genres[i], genre_count[master_genres[i]]]
            
            fname_root = f[0:-4]
            path_root = os.path.join(root, fname_root)
            fs = glob("{}*".format(path_root))
            if (genre[1] > 0):
                nfn = "{}\\{}\\{}".format(ds_dir, genre[0], "{}.mp3".format(fname_root))
                copyfile("{}.mp3".format(path_root), nfn)
                # print("{} --> {}".format(fname_root, genre[0]))
                # for fil in fs:
                #     nfn = "{}\\{}\\{}".format(ds_dir, genre[0], os.path.basename(fil))
                #     copyfile(fil, nfn)
                # with open(label_path, "w") as out:
                #     out.write(genre[0])
                #     out.close()
                print("{} --> {}".format(label_path, genre[0]))
                valid_files += 1
            # else:
            #     # fname_root = f[0:-4]
            #     # path_root = os.path.join(root, fname_root)
            #     # fs = glob("{}*".format(path_root))
            #     for fil in fs:
            #         os.remove(fil)


print("{} valid files".format(valid_files))