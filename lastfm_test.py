import simplejson as json
import requests
import hdf5_getters as h5
import os

r = requests.get("https://api.7digital.com/1.2/tag?country=US")

exit()
with open('lastfm_subset/A/A/A/TRAAAAW128F429D538.json') as f:
    file_data = json.load(f)

# root_dir = 'lastfm_subset'

api_key = '8e1ec118cef0db8b073073fa2ab54b52'

# token_url = 'http://ws.audioscrobbler.com/2.0/?method=auth.gettoken&api_key={api_key}&format=json'

track_url = 'http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={api_key}&artist={artist}&track={track}&format=json'

r = requests.get(track_url.format(artist=file_data['artist'], track=file_data['title'], api_key = api_key))

if (r.status_code != 200):
    exit()

data = json.loads(r.content)

r = requests.get(data['track']['url'])
if (r.status_code != 200):
    exit()

print(data)

f = open("lastfm_subset/A/C/A/TRACABS128E0786B0B.json")
with json.load(f) as json_data:
    print(json_data)
