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
    CHOICE_YES = {'yes', 'y'}
    CHOICE_NO = {'no', 'n'}
    CHOICE = input(
        "Overwrite your existing Plex library ratings? (y/n): ").lower()
    if CHOICE in CHOICE_YES:
        print("[INFO] Overwriting existing ratings")
        CHOICE = 'y'
    elif CHOICE in CHOICE_NO:
        print("[INFO] Skipping existing ratings")
        CHOICE = 'n'
    else:
        print("[ERROR] Please respond with 'y' or 'n'. Exiting...")
        sys.exit(0)

    CHOICE_RATINGS = input(
        "Do you want to sync 1 star ratings? (y/n): ").lower()
    if CHOICE_RATINGS in CHOICE_YES:
        print("[INFO] Syncing 1 star ratings")
        CHOICE_RATINGS = 10
    elif CHOICE_RATINGS in CHOICE_NO:
        print("[INFO] Skipping 1 star ratings")
        CHOICE_RATINGS = 20
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
    APPLE_MUSIC_RATING_LIST = {}
    COUNTER = 0
    for x, song in appleMusicLibrary.songs.items():
        COUNTER += 1
        print("\r[", COUNTER, "/", appleMusicLibraryCount,
              "]     ", end='', flush=True)
        if song and song.rating and song.rating > CHOICE_RATINGS:
            SONG_FULL_NAME = str(song.name) + ' - ' + \
                str(song.artist) + ' - ' + str(song.album)
            SONG_RATING = song.rating/10
            APPLE_MUSIC_RATING_LIST[SONG_FULL_NAME] = SONG_RATING
    print("\n[INFO] Total number of Apple Music tracks with ratings: ",
          len(APPLE_MUSIC_RATING_LIST))
    time.sleep(1)

    print("[INFO] Connecting to Plex server...")
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    music = plex.library.section(config.plexMusicLibrary)

    print("[INFO] Loading Plex music library in memory. This may take a while...")
    plexLibrary = music.searchTracks()
    plexLibraryCount = len(plexLibrary)
    print("[INFO] Total number of Plex tracks: ", plexLibraryCount)
    time.sleep(1)
    
    # TODO: add support for removing Plex-only ratings when the Apple Music rating is blank?

    print("[INFO] [", datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          "] Updating ratings... See", LOG_FILE, "for more information")
    with open(LOG_FILE, "w", encoding="utf-8") as file:
        COUNTER = 0
        for plexTrack in plexLibrary:
            COUNTER += 1
            print("\r[", COUNTER, "/", plexLibraryCount,
                "]     ", end='', flush=True)
            TRACK_FULL_NAME = str(plexTrack.title) + ' - ' + \
                str(plexTrack.artist().title) + \
                ' - ' + str(plexTrack.album().title)
            if CHOICE == 'y' or int(0 if plexTrack.userRating is None else plexTrack.userRating) < 1:
                ratingValue = APPLE_MUSIC_RATING_LIST.get(TRACK_FULL_NAME, 999)
                if ratingValue < 999 and ratingValue != plexTrack.userRating:
                    try:
                        plexTrack.rate(ratingValue)
                        file.write("[MATCHED] Rating changed           : [" + str(plexTrack.userRating)
                                + "] => [" + str(ratingValue) + "] : " + str(TRACK_FULL_NAME) + "\n")
                    except BadRequest:
                        file.write("[SKIPPED] Unknown error        : "
                                + str(TRACK_FULL_NAME) + "\n")
        file.close()
    print("\n[INFO] [", datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"), "] Complete!")
