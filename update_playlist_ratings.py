"""plex-playlist-update-ratings

This script allows batch updating of ratings for all tracks in a Plex playlist.
Users can select a playlist and set a new rating for all tracks, with the option
to preserve existing ratings.
"""

import sys
import time
from datetime import datetime
from typing import List, Set, Union

from plexapi.audio import Track
from plexapi.exceptions import BadRequest
from plexapi.playlist import Playlist
from plexapi.server import PlexServer

import config


def get_valid_rating() -> float:
    """Prompt the user for a valid rating between 1 and 5 stars.

    Returns:
        float: The rating converted to Plex's 0-10 scale (input * 2)
    """
    while True:
        try:
            rating = float(input("Enter rating (1-5 stars): "))
            if 1 <= rating <= 5:
                # Convert to Plex's 0-10 scale (1 star = 2, 2 stars = 4, etc.)
                return rating * 2
            print("Rating must be between 1 and 5 stars")
        except ValueError:
            print("Please enter a valid number")


def get_valid_playlist_choice(playlists: List[Playlist]) -> Playlist:
    """Prompt the user to select a playlist from the list.

    Args:
        playlists: List of available Plex playlists

    Returns:
        Playlist: The selected playlist object
    """
    while True:
        try:
            choice = int(input("Enter playlist number: "))
            if 1 <= choice <= len(playlists):
                return playlists[choice - 1]
            print(f"Please enter a number between 1 and {len(playlists)}")
        except ValueError:
            print("Please enter a valid number")


def update_track_rating(track: Track, rating: float, overwrite: bool, file) -> None:
    """Update the rating for a single track if conditions are met.

    Args:
        track: The Plex track to update
        rating: The new rating to set (in Plex's 0-10 scale)
        overwrite: Whether to overwrite existing ratings
        file: Open file handle for logging
    """
    # Skip if track already has a rating and we're not overwriting
    if not overwrite and track.userRating is not None:
        file.write(
            f"[SKIPPED] Existing rating kept: [{track.userRating}] : {track.title} - {track.artist().title}\n"
        )
        return

    try:
        track.rate(rating)
        file.write(
            f"[UPDATED] Rating set to: [{rating/2} stars] : {track.title} - {track.artist().title}\n"
        )
    except BadRequest as e:
        file.write(
            f"[ERROR] Failed to update: {track.title} - {track.artist().title} - Error: {str(e)}\n"
        )
    except Exception as e:
        file.write(
            f"[ERROR] Unexpected error: {track.title} - {track.artist().title} - Error: {str(e)}\n"
        )


if __name__ == "__main__":
    # Constants
    PLEX_URL: str = config.plexUrl
    PLEX_TOKEN: str = config.plexToken
    LOG_FILE: str = "playlist_ratings_update.log"
    CHOICE_YES: Set[str] = {"yes", "y"}
    CHOICE_NO: Set[str] = {"no", "n"}

    # Connect to Plex server
    print("[INFO] Connecting to Plex server...")
    plex: PlexServer = PlexServer(PLEX_URL, PLEX_TOKEN, timeout=4 * 60 * 60)
    music = plex.library.section(config.plexMusicLibrary)

    # Get all playlists
    print("[INFO] Fetching playlists...")
    playlists: List[Playlist] = music.playlists()

    if not playlists:
        print("[ERROR] No playlists found in your music library")
        sys.exit(1)

    # Display playlists
    print("\nAvailable playlists:")
    for i, playlist in enumerate(playlists, 1):
        print(f"{i}. {playlist.title} ({len(playlist.items())} tracks)")

    # Get playlist choice
    selected_playlist: Playlist = get_valid_playlist_choice(playlists)
    print(f"\nSelected playlist: {selected_playlist.title}")

    # Get rating choice
    CHOICE: str = input("Overwrite existing ratings? (y/n): ").lower()
    if CHOICE in CHOICE_YES:
        print("[INFO] Will overwrite existing ratings")
        overwrite: bool = True
    elif CHOICE in CHOICE_NO:
        print("[INFO] Will keep existing ratings")
        overwrite = False
    else:
        print("[ERROR] Please respond with 'y' or 'n'. Exiting...")
        sys.exit(0)

    # Get new rating
    new_rating: float = get_valid_rating()
    print(f"[INFO] Will set rating to {new_rating/2} stars")

    # Confirm action
    confirm: str = input(
        f"\nAre you sure you want to update {len(selected_playlist.items())} tracks in '{selected_playlist.title}' to {new_rating/2} stars? (y/n): "
    ).lower()
    if confirm not in CHOICE_YES:
        print("[INFO] Operation cancelled")
        sys.exit(0)

    # Update ratings
    print(
        f"\n[INFO] [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Updating ratings... See {LOG_FILE} for details"
    )
    with open(LOG_FILE, "w", encoding="utf-8") as file:
        counter: int = 0
        total_tracks: int = len(selected_playlist.items())

        for track in selected_playlist.items():
            counter += 1
            print(f"\r[{counter}/{total_tracks}]     ", end="", flush=True)
            update_track_rating(track, new_rating, overwrite, file)

    print(f"\n[INFO] [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Complete!")
