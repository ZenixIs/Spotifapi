#!/usr/bin/python2.7
# coding: utf-8

import sys
import os
import base64
import requests
import webbrowser
import json

'''
Makes requests on spotify api to
get the final acces token used for the Bearer
auth.
'''
class Auth:
	def __init__(self):
		'''
		Spoticopy application API ids
		'''
		self.CLIENT_ID = os.environ.get("SPOTICOPY_CLIENT")
		self.CLIENT_SECRET_ID = os.environ.get("SPOTICOPY_SECRET")
		self.REDIRECT_URI = "https://spotify.com" #os.environ.get("SPOTICOPY_REDIRECT")
		self.header = {'Authorization' : 'Basic ' + 
						base64.b64encode(
							self.CLIENT_ID + 
							':' +
							self.CLIENT_SECRET_ID)}
		self.SCOPES = "user-read-private playlist-read-private playlist-read-collaborative" \
					  " playlist-modify-public" + " playlist-modify-private"
		self.data_params = {'grant_type': 'authorization_code', 'redirect_uri': self.REDIRECT_URI}
		self.endpoint = "authorize?client_id={0}&response_type=code&redirect_uri={1}&scope={2}" \
										.format(self.CLIENT_ID , self.REDIRECT_URI, self.SCOPES)
		self.auth_url = "https://accounts.spotify.com/" + self.endpoint
		self.token_url = "https://accounts.spotify.com/api/token"

	def get_token(self):
		webbrowser.open_new(self.auth_url)
		code = raw_input("enter code: ")
		self.data_params.update({'code': code})
		r = requests.post(self.token_url, headers=self.header, data=self.data_params)
		return r.json()["access_token"]

	def req_auth(self):
		return {'Authorization': 'Bearer ' + self.get_token()}

'''
Some functions that can interract to
spotify API with python ;)
'''
class Spoticopy(Auth):
	def __init__(self):
		self.auth = Auth().req_auth()
		self.url = "https://api.spotify.com/v1/"

	def get(self, point, json=False):
		if (json):
			self.auth.update({'Accept': 'application/json', 'Content-Type': 'application/json'})
		return requests.get(self.url + point, headers=self.auth)

	def post(self, point, data):
		self.auth.update({'Content-Type': 'application/json'})
		return requests.post(self.url + point, headers=self.auth, data=data)

	def add_playlist(self, name, desc='', public=True):
		data = json.dumps({'name': name, 'description': desc, 'public': public});
		return self.post('users/shakeouz/playlists', data)

	def list_playlists(self, user="shakeouz"):
		return self.get('users/' + user + '/playlists')

	def search_tracks_uri(self, track_name, point="search?q="):
		extend = '&type=track&limit=1'

		if (' ' in track_name):
			track_name.replace(' ', '%20')
		j = self.get(point + track_name + extend, True).json()
		return j["tracks"]['items'][0]["uri"]

	def add_tracks_to_playlist(self, track_uri, playlist_name):
		playlist_id = self.add_playlist(playlist_name, "description").json()["id"]
		point = "playlists/{0}/tracks".format(playlist_id)
		data = json.dumps({"uris": [track_uri]})
		self.post(point, data)


sp = Spoticopy()
sp.add_tracks_to_playlist(sp.search_tracks_uri("the doors - the end"), 'API-test')
