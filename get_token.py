"""plex-music-import-ratings > get_token.py helper script to register a new Plex API token"""
#!/usr/bin/env python3

# for more information, refer to PlexAPI documentation:
# https://github.com/pkkid/python-plexapi#getting-a-plexserver-instance

from base64 import b64encode
from contextlib import closing
from hashlib import sha512
from http.client import HTTPSConnection
from json import loads
import sys
import os

try:
    username = input('Username: ')
    password = input('Password: ')
    client_name = input('Client Name: ')
    client_version = input('Client Version: ')
    print()
except KeyboardInterrupt:
    sys.exit(os.EX_NOINPUT)

CLIENT_ID = sha512('{} {}'.format(client_name, client_version).encode()).hexdigest()
base64string = b64encode('{}:{}'.format(username, password).encode())
headers = {'Authorization': 'Basic {}'.format(base64string.decode('ascii')),
           'X-Plex-Client-Identifier': CLIENT_ID,
           'X-Plex-Product': client_name,
           'X-Plex-Version': client_version}

with closing(HTTPSConnection('plex.tv')) as conn:
    conn.request('POST', '/users/sign_in.json', '', headers)
    response = conn.getresponse()

    if response.status == 201:
        data = loads(response.read().decode())
        print('Auth-Token: {}'.format(data['user']['authentication_token']))
        sys.exit(os.EX_OK)
    else:
        print(response.status, response.reason)
        sys.exit(os.EX_DATAERR)
