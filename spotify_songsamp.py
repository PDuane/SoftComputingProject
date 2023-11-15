import simplejson as json
import requests
import time
import os
import urllib.parse as urllib
import shutil

def getSpotifyAuthorization():
    url = 'https://accounts.spotify.com/api/token'
    client_id = '79badebf95ca4cc39b83f932a55ba7e6'
    client_secret = '803753f450e54388ab266522e0ac2b58'

    data = "grant_type=client_credentials&client_id={cid}&client_secret={cs}".format(cid=client_id, cs=client_secret)

    r = requests.post(url, data, headers={"Content-Type":"application/x-www-form-urlencoded"})

    data = json.loads(r.content)

    access = {"token":None, "timeout":None}

    access["token"] = data
    access["timeout"] = time.time() + int(data["expires_in"])

    return access

def getPreviewFromId(song_id, access):
    if time.time() > access["timeout"]:
        return None
    r = requests.get("https://api.spotify.com/v1/tracks/{id}".format(id = song_id), headers={"Authorization":"{type} {tok}".format(type=access["token"]["token_type"], tok=access["token"]["access_token"])})
    song_data = json.loads(r.content)
    if (r.status_code != 200):
        return None
    if song_data["preview_url"] != None:
        r = requests.get(song_data["preview_url"])
        return r.content
    return None

def getSongIdFromTitleAndArtist(title, artist, access):
    if time.time() > access["timeout"]:
        return None
    title = urllib.quote(title)
    artist = urllib.quote(artist)
    search_url = 'https://api.spotify.com/v1/search?q=track:{track_title}%20artist:{track_artist}&type=track'.format(track_title = title, track_artist = artist)
    r = requests.get(search_url, headers={"Authorization":"{type} {tok}".format(type=access["token"]["token_type"], tok=access["token"]["access_token"])})
    if (r.status_code != 200):
        return None
    search = json.loads(r.content)
    if (len(search["tracks"]["items"]) > 0):
        song_id=search["tracks"]["items"][0]["id"]
        return song_id
    return None


# root_dir = "lastfm_subset"
# for root, dirs, files in os.walk(root_dir):
#     for name in files:
#         fp = os.path.join(root, name)
#         pp = fp[len(root_dir) + 1:]
#         print(pp)


# path = "lastfm_subset/A/A/A"
# new_path = "preview_dataset/A/A/A"
# if not os.path.exists(new_path):
#     os.makedirs(new_path)
# files = os.listdir(path)

# for f in files:

access = getSpotifyAuthorization()

root_dir = "lastfm_subset"
copy_dir = "preview_dataset"
count = 0
for root, dirs, files in os.walk(root_dir):
    for f in files:
        file = open(os.path.join(root, f), "r")
        song_data = json.load(file)

        title = song_data["title"]
        artist = song_data["artist"]

        print("\"{name}\" by {art}".format(name=title, art=artist))

        song_id = getSongIdFromTitleAndArtist(title, artist, access)
        if song_id != None:
            mp3 = getPreviewFromId(song_id, access)
        else:
            mp3 = None

        if mp3 != None:
            new_path = "{root_dir}/{tree}".format(root_dir=copy_dir, tree=root[len(root_dir) + 1:])
            if not os.path.exists(new_path):
                os.makedirs(new_path)
            shutil.copyfile(os.path.join(root, f), os.path.join(new_path, f))
            mp3_name = "{fname}.mp3".format(fname=f[:-5])

            out = open(os.path.join(new_path, mp3_name), "wb")
            out.write(mp3)
            out.close()

            count = count + 1

print("Files found: {}".format(count))
