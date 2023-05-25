# plex-music-import-ratings
# based on: https://forums.plex.tv/t/importing-itunes-ratings-to-plex/446411

from plexapi.myplex import MyPlexAccount
from libpytunes import Library
from datetime import datetime
import time
import config

if __name__ == '__main__':
    # Defines
    plexUrl = config.plexUrl
    plexName = config.plexName
    plexToken = config.plexToken
    # plexAccount = config.plexAccount
    # plexPassword = config.plexPassword
    plexIdentifier = 'com.plexapp.plugins.library'
    appleMusicLibraryName = config.appleMusicLibraryName
    logFile = 'details.log'

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
        quit()

    print("[INFO] Loading Apple Music library...")
    appleMusicLibrary = Library(appleMusicLibraryName)
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
    account = MyPlexAccount(plexToken)
    plex = account.resource(plexName).connect()
    music = plex.library.section(config.plexMusicLibrary)

    print("[INFO] Loading Plex music library in memory. This may take a while...")
    plexLibrary = music.searchTracks()
    plexLibraryCount = len(plexLibrary)
    print("[INFO] Total number of Plex tracks: ", plexLibraryCount)
    time.sleep(2)

    print("[INFO] [", datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          "] Updating ratings... See", logFile, "for more information")
    file = open(logFile, "w", encoding="utf-8")
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
                except:
                    file.write("[SKIPPED] Unknown error        : "
                               + str(trackFullName) + "\n")
    file.close()
    print("\n[INFO] [", datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"), "] Complete!")
