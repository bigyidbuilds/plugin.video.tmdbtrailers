#!/usr/bin/python3
# -*- coding: utf-8 -*-


import json
import requests
from urllib.parse import urlunparse


from resources.lib.modules import exceptions
from resources.lib.modules import _xbmc

class YouTubeAPI():
	"""docstring for YouTubeAPI"""
	def __init__(self,api_key):
		super(YouTubeAPI, self).__init__()
		self.scheme   = 'https'
		self.netloc   = 'youtube.googleapis.com'
		self.path     = 'youtube/v3/{}'
		self.api_key  = api_key
		self.headers  = {"accept": "application/json"}
		self.params   = {"key":self.api_key}
		self.session  = requests.Session()
		self.session.headers.update(self.headers)
		self.session.params.update(self.params)



	def _Session(self,path_extension,params):
		URL = urlunparse((self.scheme,self.netloc,self.path.format(path_extension),None,None,None))
		try:
			r = self.session.get(URL,params=params)
			j = r.json()
			if r.status_code >= 400:
				error = j.get('error')
				raise exceptions.YOUTUBEAPI_Response_Exception(code=error.get('code'),message=error.get('message'),status=error.get('status'))
			else:
				return j 
		except exceptions.YOUTUBEAPI_Response_Exception as e:
			_xbmc.Log(e.logmessage)
			return None
		except Exception as e:
			_xbmc.Log(e)
			return None

	def VideoDetails(self,ID,parts):
		return self._Session('videos',params={'id':ID,'part':parts})


		