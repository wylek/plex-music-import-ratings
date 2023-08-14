# Plex Music Library - Import Apple Music Ratings

## Source

My customizations are based on the [original source script](https://forums.plex.tv/t/importing-itunes-ratings-to-plex/446411) from Plex forums user freshprince.

## Install

To install dependencies (PlexAPI, libpytunes), use the provided pyproject.toml file and [https://python-poetry.org/docs/](Poetry).

    poetry install

Alternatively, manually download libpytunes from [https://github.com/liamks/libpytunes](https://github.com/liamks/libpytunes) and install any other prerequisites using your preferred method.

## Config

Create a config.py containing:

    plexUrl = 'http://< PLEX IP ADDRESS OR URL >'
    plexName = '< PLEX SERVER NAME >'
    plexToken = '< PLEX SERVER TOKEN >'
    plexMusicLibrary = '< PLEX MUSIC LIBRARY NAME >'
    appleMusicLibraryName = '< LIBRARY XML FILE TO IMPORT>.xml'

### Plex Authentication

Use the helper script get_token.py to generate a Plex authentication token.

## Execute

Run the import_ratings.py script using the following command:

    poetry run python import_ratings.py

## Upgrade

Upgrade dependencies using Poetry:

    poetry update

Alternatively, manually download libpytunes from [https://github.com/liamks/libpytunes](https://github.com/liamks/libpytunes) and update any other prerequisites using your preferred method.
