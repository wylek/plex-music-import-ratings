"""plex-playlist-update-ratings"""

from datetime import datetime
import sys
import time
from plexapi.server import PlexServer
from plexapi.exceptions import BadRequest
import config

def get_valid_rating():
    while True:
        try:
            rating = float(input("Enter rating (1-5 stars): "))
            if 1 <= rating <= 5:
                # Convert to Plex's 0-10 scale (1 star = 2, 2 stars = 4, etc.)
                return rating * 2
            print("Rating must be between 1 and 5 stars")
        except ValueError:
            print("Please enter a valid number")

def get_valid_playlist_choice(playlists):
    while True:
        try:
            choice = int(input("Enter playlist number: "))
            if 1 <= choice <= len(playlists):
                return playlists[choice - 1]
            print(f"Please enter a number between 1 and {len(playlists)}")
        except ValueError:
            print("Please enter a valid number")

if __name__ == '__main__':
    # Defines
    PLEX_URL = config.plexUrl
    PLEX_TOKEN = config.plexToken
    LOG_FILE = 'playlist_ratings_update.log'

    # Connect to Plex server
    print("[INFO] Connecting to Plex server...")
    plex = PlexServer(PLEX_URL, PLEX_TOKEN, timeout=4*60*60)
    music = plex.library.section(config.plexMusicLibrary)

    # Get all playlists
    print("[INFO] Fetching playlists...")
    playlists = music.playlists()
    
    if not playlists:
        print("[ERROR] No playlists found in your music library")
        sys.exit(1)

    # Display playlists
    print("\nAvailable playlists:")
    for i, playlist in enumerate(playlists, 1):
        print(f"{i}. {playlist.title} ({len(playlist.items())} tracks)")

    # Get playlist choice
    selected_playlist = get_valid_playlist_choice(playlists)
    print(f"\nSelected playlist: {selected_playlist.title}")

    # Get rating choice
    CHOICE_YES = {'yes', 'y'}
    CHOICE_NO = {'no', 'n'}
    CHOICE = input("Overwrite existing ratings? (y/n): ").lower()
    if CHOICE in CHOICE_YES:
        print("[INFO] Will overwrite existing ratings")
        overwrite = True
    elif CHOICE in CHOICE_NO:
        print("[INFO] Will keep existing ratings")
        overwrite = False
    else:
        print("[ERROR] Please respond with 'y' or 'n'. Exiting...")
        sys.exit(0)

    # Get new rating
    new_rating = get_valid_rating()
    print(f"[INFO] Will set rating to {new_rating/2} stars")

    # Confirm action
    confirm = input(f"\nAre you sure you want to update {len(selected_playlist.items())} tracks in '{selected_playlist.title}' to {new_rating/2} stars? (y/n): ").lower()
    if confirm not in CHOICE_YES:
        print("[INFO] Operation cancelled")
        sys.exit(0)

    # Update ratings
    print(f"\n[INFO] [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Updating ratings... See {LOG_FILE} for details")
    with open(LOG_FILE, "w", encoding="utf-8") as file:
        counter = 0
        total_tracks = len(selected_playlist.items())
        
        for track in selected_playlist.items():
            counter += 1
            print(f"\r[{counter}/{total_tracks}]     ", end='', flush=True)
            
            # Skip if track already has a rating and we're not overwriting
            if not overwrite and track.userRating is not None:
                file.write(f"[SKIPPED] Existing rating kept: [{track.userRating}] : {track.title} - {track.artist().title}\n")
                continue
            
            try:
                # Set the rating directly as the star value (1-5)
                track.rate(new_rating)
                file.write(f"[UPDATED] Rating set to: [{new_rating/2} stars] : {track.title} - {track.artist().title}\n")
            except BadRequest as e:
                file.write(f"[ERROR] Failed to update: {track.title} - {track.artist().title} - Error: {str(e)}\n")
            except Exception as e:
                file.write(f"[ERROR] Unexpected error: {track.title} - {track.artist().title} - Error: {str(e)}\n")

    print(f"\n[INFO] [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Complete!") 