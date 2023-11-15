from spotifyUtils import *
import time

access = getSpotifyAuthorization()

sid = getSongIdFromTitleAndArtist("I Can Only Imagine", "MercyMe", access)

if time.time() > access["timeout"]:
    exit()
time.sleep(delay)
r = requests.get("https://api.spotify.com/v1/tracks/{id}".format(id = sid), headers={"Authorization":"{type} {tok}".format(type=access["token"]["token_type"], tok=access["token"]["access_token"])})
song_data = json.loads(r.content)

artist_id = song_data['artists'][0]['id']
r = requests.get("https://api.spotify.com/v1/artists/{id}".format(id = artist_id), headers={"Authorization":"{type} {tok}".format(type=access["token"]["token_type"], tok=access["token"]["access_token"])})
artist_data = json.loads(r.content)

exit()