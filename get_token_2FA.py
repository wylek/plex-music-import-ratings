"""plex-music-import-ratings > get_token_2FA.py helper script to:
* connect your Plex account and retrieve the account token
* register as a new Device and get a Plex API Application token"""

#!/usr/bin/env python3
# for more information, refer to Python PlexAPI documentation:
# https://python-plexapi.readthedocs.io/en/latest/modules/utils.html#plexapi.utils.createMyPlexDevice

import uuid
from plexapi.utils import createMyPlexDevice
from plexapi.myplex import MyPlexAccount

USER = input("Plex username: ")
PASSWD = input("Plex password: ")
CODE2FA = input("Plex 2FA Code: ")

print("[INFO] Connecting to Plex server...")
account = MyPlexAccount(username=USER, password=PASSWD, code=CODE2FA)
print("[INFO] Connected !")

# This is the account Auth-Token
print("Plex account Auth-Token:", account.authenticationToken)
