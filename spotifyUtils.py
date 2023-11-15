import simplejson as json
import requests
import time
import urllib.parse as urllib

delay = 0.25

def getSpotifyAuthorization():
    global delay
    url = 'https://accounts.spotify.com/api/token'
    client_id = '79badebf95ca4cc39b83f932a55ba7e6'
    client_secret = '803753f450e54388ab266522e0ac2b58'

    data = "grant_type=client_credentials&client_id={cid}&client_secret={cs}".format(cid=client_id, cs=client_secret)
    time.sleep(delay)
    r = requests.post(url, data, headers={"Content-Type":"application/x-www-form-urlencoded"})

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
    song_data = json.loads(r.content)
    if (r.status_code != 200):
        return None
    if song_data["preview_url"] != None:
        time.sleep(delay)
        r = requests.get(song_data["preview_url"])
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
    if (r.status_code != 200):
        return None
    search = json.loads(r.content)
    if (len(search["tracks"]["items"]) > 0):
        song_id=search["tracks"]["items"][0]["id"]
        return song_id
    return None