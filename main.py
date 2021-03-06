import requests
import matplotlib.pyplot as plt
import numpy
import random
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import base64
import sys

# prerequisite links and ids
V1_URL = 'https://api.spotify.com/v1/playlists/'
AUTH_URL = 'https://accounts.spotify.com/api/token'
global check
check = False

CLIENT_ID = 'fa9c7ce9f46e45a5ad8661bbf11d89a3'
CLIENT_SECRET = '7899184f3fda481383b6e4a4442b0ab3'

AUTHO = 'ZmE5YzdjZTlmNDZlNDVhNWFkODY2MWJiZjExZDg5YTM6Nzg5OTE4NGYzZmRhNDgxMzgzYjZlNGE0NDQyYjBhYjM='

# PLAYLISTID = '1QrMDK9IL8JK7YTIsclb8T'  # gangster
# PLAYLISTID = '3vjr3IER5PmWNv9AzZj12s'  # jack rando playlist (low amt of songs)

hostName = 'localhost'
serverPort = 8888
getTracks = ''
factor = 0

SpotPlaylist = []
Popularity = []
SongLength = []
SongID = []

Danceability = []
Energy = []
Loudness = []
Liveness = []
Acousticness = []
Speechiness = []
Artists = []
ArtistID = []
Tracks = []

RecommendedIDS = []
RecommendedTotal = []
RecommendedPrint = []

DecodeErrorsSkipped = 0

resp = ""


def getSpotifyAccessToken():
    header = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic {}'.format(AUTHO),

    }
    body = {
        'grant_type': 'client_credentials',
        'scope': 'playlist-modify-public playlist-modify-private'
    }

    # get access token using id and secret
    auth_response = requests.post(AUTH_URL, data=body, headers=header)

    return auth_response.json()['access_token']


def getSongFeatures(id):
    getString = "https://api.spotify.com/v1/audio-features?ids="
    jsonID = requests.get(getString + str(id), headers=authoHeader)
    return jsonID.json()


def allThreeVals(std, ave):
    lis = []
    lis.append(str(ave))
    lis.append(str(ave - std))
    lis.append(str(ave + std))
    return lis


def getGenres(id):
    genres = []
    getString = "https://api.spotify.com/v1/artists/"
    jsonID = requests.get(getString + str(id), headers=authoHeader)
    counter = 0
    while counter != 2:
        try:
            gen = jsonID.json()['genres'][counter]
            genres.append(gen)
            counter = counter + 1
        except IndexError:
            genres.append(gen)

    return genres


def standDev(val):
    return numpy.std(val)


def ave(val):
    return numpy.average(val)


def storeValsForRecommended():
    limit = input("\nHow Many Recommended Songs Do You Want Added?   ")

    counter = 0
    while counter != len(SongID):
        try:
            feature = getSongFeatures(SongID[counter])
            print(str(counter / len(SongID)*100) + "%")

            dance = feature['audio_features'][0]['danceability']
            energy = feature['audio_features'][0]['energy']
            loud = feature['audio_features'][0]['loudness']
            live = feature['audio_features'][0]['liveness']
            acoustic = feature['audio_features'][0]['acousticness']

            Danceability.append(dance)
            Energy.append(energy)
            Loudness.append(loud)
            Liveness.append(live)
            Acousticness.append(acoustic)


            counter = counter + 1
        except requests.exceptions.JSONDecodeError:
            pass
        except TypeError:
            counter = counter + 1
    getRecommended(Danceability, Energy, Loudness, Liveness, Acousticness, limit, 0)


def getRecommended(Danceability, Energy, Loudness, Liveness, Acousticness, limit, factor):

    aveD = ave(Danceability)
    aveE = ave(Energy)
    aveLo = ave(Loudness)
    aveLi = ave(Liveness)
    aveA = ave(Acousticness)

    stdD = standDev(Danceability)
    stdE = standDev(Energy)
    stdLo = standDev(Loudness)
    stdLi = standDev(Liveness)
    stdA = standDev(Acousticness)


    RA1 = random.randint(0, len(ArtistID)-1)
    RA2 = random.randint(0, len(ArtistID)-1)
    RA3 = random.randint(0, len(ArtistID)-1)

    counter = 0
    while counter != len(ArtistID):
        if ArtistID[counter] == None:
            ArtistID.pop(counter)
        counter = counter+1
    counter=0
    while counter != len(SongID):
        if SongID[counter] == None:
            SongID.pop(counter)
        counter = counter+1

    getString1 = "https://api.spotify.com/v1/recommendations?limit=" + str(limit) + "&seed_artists=" + ArtistID[
        RA1] + "%2C" + ArtistID[RA2] + "%2C" + ArtistID[RA3]
    getString2 = "&seed_genres=" + getGenres(ArtistID[RA1])[0] + "%2C" + getGenres(ArtistID[RA1])[1]
    try:
        getString3 = "&seed_tracks" + "%2C".join(SongID[len(SongID)-70:]) + "%2C".join(SongID[:30]) + "&min_danceability=" + str(
                aveD - stdD - factor) + "&max_danceability=" + str(aveD + stdD + factor) + "&target_danceability=" + str(aveD + factor)
    except IndexError:
        getString3 = "&seed_tracks" + "%2C".join(SongID) + "&min_danceability=" + str(
                aveD - stdD - factor) + "&max_danceability=" + str(aveD + stdD + .13) + "&target_danceability=" + str(aveD + .13)
    getString4 = "&min_energy=" + str((aveE - stdE) - factor) + "&max_energy=" + str((aveE + stdE) + factor) + "&target_energy=" + str(
        aveE)
    getString5 = "&min_loudness=" + str((aveLo - stdLo - factor)) + "&max_loudness=" + str(
        (aveLo + stdLo + factor)) + "&target_loudness=" + str(aveLo)
    getString6 = "&min_acousticness=" + str(aveA-stdA - factor) + "&max_acousticness=" + str(
        aveA+stdA + factor) + "&target_acousticness=" + str(aveA)
    getString7 = "&min_liveness=" + str(aveLi-stdLi - factor) + "&max_liveness=" + str(
        aveLi+stdLi + factor) + "&target_liveness=" + str(aveLi)

    getString = getString1 + getString2 + getString4 + getString5 + getString6 + getString7 + getString3
    getString = getString.replace(" ", "%20")

    getTracks = (requests.get(getString, headers=authoHeader)).json()


    counter = 0
    while counter != int(limit):
        counter2 = 0

        id = getTracks['tracks'][counter]['id']
        name = getTracks['tracks'][counter]['name']
        artist = getTracks['tracks'][counter]['album']['artists'][0]['name']


        while counter2 != len(SongID):
            if id == SongID[counter2]:
                factor = factor + .05
                getRecommended(Danceability, Energy, Loudness, Liveness, Acousticness, limit, factor)
                print(factor)

            counter2 = counter2+1

        RecommendedPrint.append(('{} - {}'.format(name, artist)))
        RecommendedIDS.append(id)
        RecommendedTotal.append("{} - {} (RECOMMENDED)".format(name, artist))
        counter = counter + 1


    for i in RecommendedPrint:
        print(i)
    addToPlaylist(RecommendedIDS, limit)


def addToPlaylist(ids, limit):
    print("\nADDING TO PLAYLIST")
    baseString = "https://api.spotify.com/v1/playlists/{}/tracks?uris=".format(PLAYLISTID)

    base2 = "spotify%3Atrack%3A"
    base3 = "%2Cspotify%3Atrack%3A".join(ids)
    url = baseString + base2 + base3
    global check
    if check == False:
        tokn = input("Spotify Access Code (https://developer.spotify.com/console/post-playlist-tracks/):  ")
    else:
        quit()
    authoHeader = {
        'Authorization': 'Bearer {}'.format(tokn),
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    pos = requests.post(url, headers=authoHeader)
    print(pos.json())
    check = True
    storeToTxt(0)


def getSongInfo(offset):
    # get call
    playlistJson = requests.get(V1_URL + PLAYLISTID + '/tracks?limit=100&offset=' + str(offset), headers=authoHeader)

    return playlistJson.json()


def getPlaylistName():
    # create header for GET call
    autoHeader = {
        'Authorization': 'Bearer {}'.format(getSpotifyAccessToken())
    }

    # get call
    req = requests.get(V1_URL + PLAYLISTID, headers=autoHeader)

    return req.json()


def getMostFrequentValue(list):
    counter = 0
    num = list[0]

    for i in list:
        freq = list.count(i)
        if freq > counter:
            counter = freq
            num = i

    return num


def plot():
    model = numpy.poly1d(numpy.polyfit(SongLength, Popularity, 3))

    line = numpy.linspace(0, max(SongLength), max(Popularity))

    plt.scatter(SongLength, Popularity)
    plt.plot(line, model(line))

    print("\nVALUES PLOTTED")
    plt.show()


def storeToTxt(ero):
    # user and playlist link
    user = "\nPLAYLIST CREATOR: {}".format(getSongInfo(0)['items'][0]['added_by']['external_urls']['spotify'])
    playlistLink = "\nPLAYLIST LINK: https://open.spotify.com/playlist/" + PLAYLISTID + '\n'

    try:
        # username playlist name
        userName = getPlaylistName()['owner']['display_name']
        playlistName = getPlaylistName()['name']

    except requests.exceptions.JSONDecodeError:
        return

    userString = '\n\n{} created by {}'.format(playlistName, userName)

    # average song popularity (tenths)
    pop = (round(10 * (sum(Popularity) / len(Popularity))))
    pop = pop / 10
    popLn = "\n\nAverage Song Popularity: ", str(pop)

    # average song length (m) (tenths)
    length = 10 * (sum(SongLength) / len(SongLength))
    length = length / 600000
    lengthLn = "\nAverage Song Length: ", str(length)

    # print list to text file
    with open('playlist.txt', 'w') as text:
        text.write('\n'.join(SpotPlaylist))

    # print average length, average popularity, user and link
    with open('playlist.txt', 'a') as t:
        t.writelines(userString)
        t.writelines(popLn)
        t.writelines(lengthLn)
        t.writelines(user)
        t.writelines(playlistLink)
        t.writelines('\n'.join(RecommendedTotal))

    print("\nADDED TO TXT FILE")
    sys.exit()



def storeAllPlaylistTracks():
    try:
        # username playlist name
        userName = getPlaylistName()['owner']['display_name']
        playlistName = getPlaylistName()['name']
    except requests.exceptions.JSONDecodeError:
        return

    userString = '\n\n{} created by {}'.format(playlistName, userName)
    print(userString)

    DecodeErrorsSkipped = 0
    counter = 0
    counter2 = 0
    info = getSongInfo(0)
    while True:
        try:
            if counter == 100:
                counter2 = counter2 + 100
                counter = 0
                info = getSongInfo(counter2)
            # get song artist, name, popularity, song length
            track = info['items'][counter]['track']['name']
            artist = info['items'][counter]['track']['artists'][0]['name']
            artistId = info['items'][counter]['track']['artists'][0]['id']
            pop = info['items'][counter]['track']['popularity']
            length = (info['items'][counter]['track']['duration_ms']) / 60000
            id = info['items'][counter]['track']['id']

            Artists.append(artist)
            Popularity.append(pop)
            SongLength.append(length)
            SongID.append(id)
            ArtistID.append(artistId)
            Tracks.append(track)

            # creates string from track + artist + counter
            ListAdd = '{} - {}  {}   Popularity: {}'.format(track, artist, str(counter + 1), pop)

            # add song name + artist to playlist
            SpotPlaylist.append(ListAdd)
            print(ListAdd)

            counter = counter + 1


        except IndexError:
            storeValsForRecommended()
            break

        except requests.exceptions.JSONDecodeError:
            DecodeErrorsSkipped = DecodeErrorsSkipped + 1


# create header for GET call
authoHeader = {
    'Authorization': 'Bearer {}'.format(getSpotifyAccessToken()),
    'Content-Type': 'application/x-www-form-urlencoded',
}
# input playlist link for playlist id
PLAYLISTID = input("Playlist Link: ")
PLAYLISTID = PLAYLISTID[slice(34, 56)]

storeAllPlaylistTracks()
