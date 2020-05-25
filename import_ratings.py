# https://forums.plex.tv/t/importing-itunes-ratings-to-plex/446411
# to upgrade:
# pip3 install --upgrade plexapi
# pip3 install --upgrade libpytunes

from plexapi.myplex import MyPlexAccount
from libpytunes import Library
from datetime import datetime
import requests
import time
import config

if __name__ == '__main__':
	# Defines
	plexUrl = config.plexUrl
	plexName = config.plexName
	plexToken = config.plexToken
	plexAccount = config.plexAccount
	plexPassword = config.plexPassword
	plexIdentifier = 'com.plexapp.plugins.library'
	itunesLibraryName = 'library.xml'
	logFile = 'details.log'

	# start logic
	choiceyes = {'yes','y'}
	choiceno = {'no','n'}
	choice = input("Do you want to overwrite existing ratings? (yes/no): ").lower()
	if choice in choiceyes:
		print("[INFO] Overwriting existing ratings")
		choice = 'yes'
	elif choice in choiceno:
		print("[INFO] Skipping existing ratings")
		choice = 'no'
	else:
		print("[ERROR] Please respond with 'yes' or 'no'. Exiting...")
		quit()

	choiceRatings = input("Do you want to sync 1 star ratings? (yes/no): ").lower()
	if choiceRatings in choiceyes:
		print("[INFO] Syncing 1 star ratings")
		choiceRatings = 10
	elif choiceRatings in choiceno:
		print("[INFO] Skipping 1 star ratings")
		choiceRatings = 20
	else:
		print("[ERROR] Please respond with 'yes' or 'no'. Exiting...")
		quit()

	print("[INFO] Loading iTunes library...")
	itunesLibrary = Library(itunesLibraryName)
	itunesLibraryCount = len(itunesLibrary.songs.items())
	print("[INFO] Total number of iTunes tracks: ", itunesLibraryCount)
	time.sleep(2)

	print("[INFO] Optimizing iTunes library...")
	itunesRatingList = { }
	counter = 0
	for x, song in itunesLibrary.songs.items():
		counter += 1
		print("\r[",counter,"/",itunesLibraryCount,"]     ", end='', flush=True)
		if song and song.rating and song.rating > choiceRatings :
			songFullName = str(song.name) + ' - ' + str(song.album_artist) + ' - ' + str(song.album)
			songRating = song.rating/10
			itunesRatingList[songFullName] = songRating
	itunesRatingListCount = len(itunesRatingList)
	print("\n[INFO] Total number of iTunes tracks with ratings: ", itunesRatingListCount)
	time.sleep(2)

	print("[INFO] Connecting to Plex server...")
	account = MyPlexAccount(plexAccount, plexPassword)
	plex = account.resource(plexName).connect()
	music = plex.library.section('Music Collection')

	print("[INFO] Loading Plex music library in memory. This may take a while...")
	plexLibrary = music.searchTracks()
	plexLibraryCount = len(plexLibrary)
	print("[INFO] Total number of Plex tracks: ", plexLibraryCount)
	time.sleep(2)

	print("[INFO] [", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "] Updating ratings... See", logFile, "for more information")
	file = open(logFile,"w", encoding="utf-8")
	counter = 0
	for plexTrack in plexLibrary:
		counter += 1
		print("\r[",counter,"/",plexLibraryCount,"]     ", end='', flush=True)
		trackFullName = str(plexTrack.title) + ' - ' + str(plexTrack.artist().title) + ' - ' + str(plexTrack.album().title)
		if choice == 'yes' or plexTrack.userRating == 0:
			ratingValue = itunesRatingList.get(trackFullName, 999)
			if ratingValue == 999:
				file.write("[SKIPPED] No iTunes rating found   : " + str(trackFullName) + "\n")
			elif ratingValue == plexTrack.userRating:
				file.write("[SKIPPED] Rating already up-to-date: " + str(trackFullName) + "\n")
			else:
				payload = {
					'X-Plex-Token': plexToken,
					'identifier': plexIdentifier,
					'key': plexTrack.ratingKey,
					'rating': ratingValue,
				}
				response = requests.get(plexUrl, params=payload)
				responseCode = str(response.status_code)
				if response.ok:
					file.write("[MATCHED] Rating changed           : [" + str(plexTrack.userRating) + "] => [" + str(ratingValue) + "] : " + str(trackFullName) + "\n")
				else:
					file.write("[SKIPPED] Unknown error " + str(responseCode) + "        : " + str(trackFullName) + "\n")
		else:
			file.write("[SKIPPED] Rating already exists    : " + str(trackFullName) + "\n")

	file.close()
	print("\n[INFO] [", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "] All done!")
