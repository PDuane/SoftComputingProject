import simplejson as json
import requests
import time
import os
import urllib.parse as urllib
import shutil
import hdf5_getters as h5
import subprocess
import audio2spectroimg
from multiprocessing import Process, Lock
import random
import csv

fft_size = 512
img_len = 256
batch_size = 882
delay = 0.25

genres = []

to_process = []
mutex = Lock()

def getSpotifyAuthorization():
    global delay
    url = 'https://accounts.spotify.com/api/token'
    client_id = '79badebf95ca4cc39b83f932a55ba7e6'
    client_secret = '803753f450e54388ab266522e0ac2b58'

    data = "grant_type=client_credentials&client_id={cid}&client_secret={cs}".format(cid=client_id, cs=client_secret)
    time.sleep(delay)
    r = requests.post(url, data, headers={"Content-Type":"application/x-www-form-urlencoded"})
    if (r.status_code == 429):
        print("Access limit surpassed. Exiting.")
        exit()
    if (r.status_code != 200):
        print("Error renewing access: Response {}".format(r.status_code))
        return None

    data = json.loads(r.content)

    access = {"token":None, "timeout":None}

    access["token"] = data
    access["timeout"] = time.time() + int(data["expires_in"])

    return access

def getPreviewFromId(song_id, access):
    global delay
    if time.time() > access["timeout"]:
        return None
    time.sleep(delay)
    r = requests.get("https://api.spotify.com/v1/tracks/{id}".format(id = song_id), headers={"Authorization":"{type} {tok}".format(type=access["token"]["token_type"], tok=access["token"]["access_token"])})
    # if r.status_code == 429:
    #     delay *= 2
    #     return getPreviewFromId(song_id, access)
    if (r.status_code == 429):
        print("Access limit surpassed. Exiting.")
        exit()
    song_data = json.loads(r.content)
    if (r.status_code != 200):
        return None
    if song_data["preview_url"] != None:
        time.sleep(delay)
        try:
            r = requests.get(song_data["preview_url"])
        except:
            return None
        return r.content
    return None

def getSongIdFromTitleAndArtist(title, artist, access):
    global delay, mutex, live_threads
    if time.time() > access["timeout"]:
        return None
    title = urllib.quote(title)
    artist = urllib.quote(artist)
    search_url = 'https://api.spotify.com/v1/search?q=track:{track_title}%20artist:{track_artist}&type=track'.format(track_title = title, track_artist = artist)
    time.sleep(delay)
    r = requests.get(search_url, headers={"Authorization":"{type} {tok}".format(type=access["token"]["token_type"], tok=access["token"]["access_token"])})
    if (r.status_code == 429):
        print("Access limit surpassed. Exiting.")
        exit()
    if (r.status_code != 200):
        return None
    search = json.loads(r.content)
    if (len(search["tracks"]["items"]) > 0):
        song_id=search["tracks"]["items"][0]["id"]
        return song_id
    return None

def getArtistGenresFromSongId(song_id, access):
    global delay
    if time.time() > access["timeout"]:
        return None
    time.sleep(delay)
    r = requests.get("https://api.spotify.com/v1/tracks/{id}".format(id = song_id), headers={"Authorization":"{type} {tok}".format(type=access["token"]["token_type"], tok=access["token"]["access_token"])})
    if (r.status_code == 429):
        print("Access limit surpassed. Exiting.")
        exit()
    if (r.status_code != 200):
        return None
    song_data = json.loads(r.content)
    if song_data['artists'] != None and len(song_data['artists']) > 0:
        artist_id = song_data['artists'][0]['id']
        time.sleep(delay)
        r = requests.get("https://api.spotify.com/v1/artists/{id}".format(id = artist_id), headers={"Authorization":"{type} {tok}".format(type=access["token"]["token_type"], tok=access["token"]["access_token"])})
        if (r.status_code == 429):
            print("Access limit surpassed. Exiting.")
            exit()
        if (r.status_code != 200):
            return None
        artist_data = json.loads(r.content)
        if len(artist_data['genres']) < 1:
            return None
        return artist_data['genres']

def imageProcess(lock, queue, fft_size, img_len, batch_size):
    wait = 10 + 5 * random.random()
    time.sleep(wait)
    while (True):
        lock.acquire()
        if len(queue) == 0:
            lock.release()
            return
        wav_name = queue.pop(0)
        lock.release()
        audio2spectroimg.audio2images(wav_name, fft_size, img_len, batch_size)

if __name__ == '__main__':

    progress = ['\0', '\0', '\0']
    start = ['\0', '\0', '\0']
    progress_filename = "progress.txt"
    if os.path.exists(progress_filename):
        with open (progress_filename) as csvfile:
            csvdata = csv.reader(csvfile)
            for row in csvdata:
                start[0] = row[0]
                start[1] = row[1]
                start[2] = row[2]

    genres = {}
    genre_filename = 'genres.txt'
    if os.path.exists(genre_filename):
        gf = open(genre_filename, "r")
        line = gf.readline()
        while (len(line) > 0):
            if (len(line.strip()) > 0 and ',' in line):
                info = line.split(",")
                genres[info[0].strip()] = int(info[1].strip())
                # genres.append(line.strip())
            line = gf.readline()
        gf.close()

    access = getSpotifyAuthorization()
    if access == None:
        exit()

    root_dir = "MillionSongSubset"
    copy_dir = "mss_preview_dataset"
    count = 0
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            cd = [None, None, None]
            pth = root
            cd[2] = pth[-1]
            pth = pth[:-2]
            cd[1] = pth[-1]
            pth = pth[:-2]
            cd[0] = pth[-1]

            f1_cond = cd[0] < start[0]
            f2_cond = cd[0] == start[0] and cd[1] < start[1]
            f3_cond = cd[0] == start[0] and cd[1] == start[1] and cd[2] < start[2]

            if f1_cond or f2_cond or f3_cond:
                continue
            
            if cd[0] > progress[0] or cd[1] > progress[1] or cd[2] > progress[2]:
                progress[0] = cd[0]
                progress[1] = cd[1]
                progress[2] = cd[2]
                progress_file = open (progress_filename, "w")
                progress_file.write("{f1},{f2},{f3}\n".format(f1=cd[0], f2=cd[1], f3=cd[2]))
                progress_file.close()
            
            file = h5.open_h5_file_read(os.path.join(root, f))
            # song_data = json.load(file)
            title = h5.get_title(file).decode('UTF-8')
            artist = h5.get_artist_name(file).decode('UTF-8')
            file.close()

            print("\"{name}\" by {art}".format(name=title, art=artist), end='')

            if time.time() < access['timeout'] - 10:
                access = getSpotifyAuthorization()
                if access == None:
                    exit()
            song_id = getSongIdFromTitleAndArtist(title, artist, access)

            if song_id != None:
                if time.time() < access['timeout'] - 10:
                    access = getSpotifyAuthorization()
                    if access == None:
                        exit()
                mp3 = getPreviewFromId(song_id, access)
            else:
                mp3 = None
                print(" - Failed: No search result")
                continue
            
            if time.time() < access['timeout'] - 10:
                access = getSpotifyAuthorization()
                if access == None:
                    exit()
            art_genres = getArtistGenresFromSongId(song_id, access)

            if mp3 != None and art_genres != None:
                new_path = "{root_dir}\\{tree}".format(root_dir=copy_dir, tree=root[len(root_dir) + 1:])
                if not os.path.exists(new_path):
                    os.makedirs(new_path)
                shutil.copyfile(os.path.join(root, f), os.path.join(new_path, f))
                mp3_name = "{fname}.mp3".format(fname=f[:-3])
                mp3_name = os.path.join(new_path, mp3_name)
                lab_name = "{fname}.lab".format(fname=f[:-3])
                lab_name = os.path.join(new_path, lab_name)

                out = open(mp3_name, "wb")
                out.write(mp3)
                out.close()

                lf = open(lab_name, "w")
                for g in art_genres:
                    lf.write("{}\n".format(g))
                    if g in genres.keys():
                        genres[g] += 1
                    else:
                        genres[g] = 1
                lf.close()

                gf = open(genre_filename, "w")
                for g in genres.keys():
                    gf.write("{genre},{num}\n".format(genre=g, num=genres[g]))
                
                gf.close()

                # if genre not in genres:
                #     genres.append(genre)
                #     gf = open(genre_filename, "a")
                #     gf.write("{}\n".format(genre))
                #     gf.close()

                count = count + 1
                print()
            elif mp3 == None:
                print(" - Failed: No audio preview")
            elif art_genres == None:
                print(" - Failed: No genres")

    print("Files found: {}".format(count))
    print("Genres found: {}".format(len(genres)))
    # print("Saving Genre List")

    # with open(genre_filename, "w") as genrefile:
    #     for genre in genres:
    #         genrefile.write("{}\n".format(genre))
    #     genrefile.close()
    
    print("done")
