# Plex Music Library - Import Apple Music Ratings

## Source

My customizations are based on the [original source script](https://forums.plex.tv/t/importing-itunes-ratings-to-plex/446411) from Plex forums user freshprince.

## Install

1. Install prerequisites (plexapi) using pip:

    pip install plexapi

2. Manually download libpytunes from [https://github.com/liamks/libpytunes](https://github.com/liamks/libpytunes)

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

1. Upgrade plexapi using pip:

    pip install --upgrade plexapi

2. Manually download libpytunes from [https://github.com/liamks/libpytunes](https://github.com/liamks/libpytunes)
