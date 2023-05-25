# Plex Music Library - Import Apple Music Ratings

## Source

My customizations are based on the original source script here:

https://forums.plex.tv/t/importing-itunes-ratings-to-plex/446411

## Install

Install prerequisites (plexapi, libpytunes) using pip:

    pip install plexapi
    pip install libpytunes

## Config

Create a config.py containing:

    plexUrl = 'http://< PLEX IP ADDRESS OR URL >/:/rate'
    plexName = '< PLEX SERVER NAME >'
    plexToken = '< PLEX SERVER TOKEN >'
    plexMusicLibrary = '< PLEX MUSIC LIBRARY NAME >'
    appleMusicLibraryName = '< LIBRARY XML FILE TO IMPORT>.xml'

### Plex Authentication

Use the helper script get_token.py to generate a Plex authentication token.

## Upgrade

Upgrade plexapi and libpytunes using pip:

    pip install --upgrade plexapi
    pip install --upgrade libpytunes
