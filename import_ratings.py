"""plex-music-import-ratings"""

from datetime import datetime
import sys
import time
from plexapi.server import PlexServer
from plexapi.exceptions import BadRequest
from libpytunes import Library
import config

if __name__ == '__main__':
    # Defines
    PLEX_URL = config.plexUrl
    PLEX_NAME = config.plexName
    PLEX_TOKEN = config.plexToken
    PLEX_IDENTIFIER = 'com.plexapp.plugins.library'
    APPLE_MUSIC_LIBRARY_NAME = config.appleMusicLibraryName
    LOG_FILE = 'details.log'

    # start logic
    choiceyes = {'yes', 'y'}
    choiceno = {'no', 'n'}
    choice = input(
        "Overwrite your existing Plex library ratings? (y/n): ").lower()
    if choice in choiceyes:
        print("[INFO] Overwriting existing ratings")
        choice = 'y'
    elif choice in choiceno:
        print("[INFO] Skipping existing ratings")
        choice = 'n'
    else:
        print("[ERROR] Please respond with 'y' or 'n'. Exiting...")
        quit()

    choiceRatings = input(
        "Do you want to sync 1 star ratings? (y/n): ").lower()
    if choiceRatings in choiceyes:
        print("[INFO] Syncing 1 star ratings")
        choiceRatings = 10
    elif choiceRatings in choiceno:
        print("[INFO] Skipping 1 star ratings")
        choiceRatings = 20
    else:
        print("[ERROR] Please respond with 'y' or 'n'. Exiting...")
        sys.exit(0)

    print("[INFO] Loading Apple Music library...")
    appleMusicLibrary = Library(APPLE_MUSIC_LIBRARY_NAME)
    appleMusicLibraryCount = len(appleMusicLibrary.songs.items())
    print("[INFO] Total number of Apple Music tracks: ", appleMusicLibraryCount)
    file_debug = open("library-parsed-rated-songs.log", "w", encoding="utf-8")
    for id, song in appleMusicLibrary.songs.items():
        if song and song.rating:
            file_debug.write("{a} - {t}, {r}\n".format(
                a=song.artist, t=song.name, r=song.rating))
    time.sleep(2)

    print("[INFO] Optimizing Apple Music library...")
    appleMusicRatingList = {}
    counter = 0
    for x, song in appleMusicLibrary.songs.items():
        counter += 1
        print("\r[", counter, "/", appleMusicLibraryCount,
              "]     ", end='', flush=True)
        if song and song.rating and song.rating > choiceRatings:
            songFullName = str(song.name) + ' - ' + \
                str(song.artist) + ' - ' + str(song.album)
            songRating = song.rating/10
            appleMusicRatingList[songFullName] = songRating
    appleMusicRatingListCount = len(appleMusicRatingList)
    print("\n[INFO] Total number of Apple Music tracks with ratings: ",
          appleMusicRatingListCount)
    time.sleep(2)

    print("[INFO] Connecting to Plex server...")
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    music = plex.library.section(config.plexMusicLibrary)

    print("[INFO] Loading Plex music library in memory. This may take a while...")
    plexLibrary = music.searchTracks()
    plexLibraryCount = len(plexLibrary)
    print("[INFO] Total number of Plex tracks: ", plexLibraryCount)
    time.sleep(2)

    print("[INFO] [", datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          "] Updating ratings... See", LOG_FILE, "for more information")
    with open(LOG_FILE, "w", encoding="utf-8") as file:
        counter = 0
        for plexTrack in plexLibrary:
            counter += 1
            print("\r[", counter, "/", plexLibraryCount,
                "]     ", end='', flush=True)
            trackFullName = str(plexTrack.title) + ' - ' + \
                str(plexTrack.artist().title) + \
                ' - ' + str(plexTrack.album().title)
            if choice == 'yes' or choice == 'y' or int(0 if plexTrack.userRating is None else plexTrack.userRating) < 1:
                ratingValue = appleMusicRatingList.get(trackFullName, 999)
                if ratingValue < 999 and ratingValue != plexTrack.userRating:
                    try:
                        plexTrack.rate(ratingValue)
                        file.write("[MATCHED] Rating changed           : [" + str(plexTrack.userRating)
                                + "] => [" + str(ratingValue) + "] : " + str(trackFullName) + "\n")
                    except BadRequest:
                        file.write("[SKIPPED] Unknown error        : "
                                + str(trackFullName) + "\n")
        file.close()
    print("\n[INFO] [", datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"), "] Complete!")
