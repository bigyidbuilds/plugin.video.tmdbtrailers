#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import requests
from urllib.parse import urlunparse

from resources.lib.modules import _xbmcaddon
from resources.lib.modules.utils import Log,TimeStamp
from resources.lib.modules import exceptions
from resources.lib.modules.userjson import ReadUserDataFile,WriteJsonFile



class Tmdb_Authentication():
	"""docstring for Tmdb_Authentication"""
	def __init__(self,clientaddon=None,tmdb_api_key=None,tmdb_api_bearer=None):
		super(Tmdb_Authentication, self).__init__()
		self.__addon__     = 'plugin.video.tmdbtrailers'
		if clientaddon == None:
			self.clientaddon = self.__addon__
		else:
			self.clientaddon = clientaddon
		self.AddonSettings = _xbmcaddon._AddonSettings(self.__addon__)
		self.username      = self.AddonSettings.getString('tmdb.api.username')
		self.password      = self.AddonSettings.getString('tmdb.api.password')
		if tmdb_api_bearer == None:
			self.bearer      = self.AddonSettings.getString("tmdb.api.token")
		else:
			self.bearer 		 = tmdb_api_bearer
		self.userjson      = ReadUserDataFile()
		self.scheme        = 'https'
		self.netloc        = 'api.themoviedb.org'
		self.apiversion    = '3'
		self.headers       = {"accept": "application/json","Authorization":f"Bearer {self.bearer}"}
		self.session       = requests.Session()
		self.session.headers.update(self.headers)
		self.error_keys = ['success', 'status_code', 'status_message']
		self.Validate_keys = ['success']

	def _Session(self,method,path,_headers=None,_params=None,_json=None):
		try:
			URL = urlunparse((self.scheme,self.netloc,f'{self.apiversion}/{path}',None,None,None))
			if method == 'GET':
				u = self.session.get(URL,headers=_headers,params=_params)
			elif method == 'POST':
				u = self.session.post(URL,headers=_headers,params=_params,json=_json)
			elif method == 'DEL':
				u = self.session.delete(URL,headers=_headers,params=_params,json=_json)
			auth = u.json()
			keys = list(auth.keys())
			if all(keys in auth for keys in self.error_keys):
				raise exceptions.TMDBAPI_Response_Exception(message='Response Error',errors_dict=auth,url=u.url)
			Log(auth)
			Log(keys)
			return auth,keys
		except exceptions.TMDBAPI_Response_Exception as e:
			Log(e.logmessage)
			return None,None
		except Exception as exc:
			Log(exc)
			return None,None

	def CreateRequestToken(self):
		''' API reference https://developer.themoviedb.org/reference/authentication-create-request-token '''
		ret,keys = self._Session('GET','/authentication/token/new')
		Log(ret)
		if ret.get('success') == True and 'request_token' in keys:
			return ret.get('request_token')
		

	def CreateSession_Withlogin(self,token):
		''' API reference https://developer.themoviedb.org/reference/authentication-create-request-token '''
		ret,keys = self._Session(
			'POST',
			'authentication/token/validate_with_login',
			_headers={"content-type": "application/json"},
			_json={ 
				"username": self.username,
				"password": self.password,
				"request_token": token})
		if ret.get('success') == True and 'request_token' in keys:
			return ret.get('request_token')


	def CreateSession(self,token):
		'''API reference https://developer.themoviedb.org/reference/authentication-create-session '''
		ret,keys = self._Session(
			'POST',
			'authentication/session/new',
			_headers={"content-type": "application/json"},
			_json={'request_token':token})
		if ret.get('success') == True and "session_id" in keys:
			return ret.get('session_id')

	def DeleteSession(self,sessionID):
		''' API reference https://developer.themoviedb.org/reference/authentication-delete-session'''
		ret,keys = self._Session(
			'DEL',
			'authentication/session',
			_headers={"content-type": "application/json"},
			_json={"session_id":sessionID})
		if ret.get('success') == True:
			return ret,keys


	def SignIn(self):
		ret = self.CreateRequestToken()
		tok = self.CreateSession_Withlogin(ret)
		sid = self.CreateSession(tok)
		session_details = self.userjson.get('access').get(self.clientaddon).get('session_details')
		session_details.update({'session_id':sid,'created':TimeStamp(),'inuse':True})
		WriteJsonFile(_xbmcaddon._AddonInfo(self.__addon__,'profile'),'user.json',self.userjson)

	def SignOut(self):
		session_details = self.userjson.get('access').get(self.clientaddon).get('session_details')
		session_id = session_details.get('session_id')
		ret,key = self.DeleteSession(session_id)
		if ret.get('success') == True:
			session_details.update({'inuse':False})
			WriteJsonFile(_xbmcaddon._AddonInfo(self.__addon__,'profile'),'user.json',self.userjson)


		
	def ValidateKey(self):
		Log('validating key')
		try:
			ret,keys = _Session('GET','authentication')
			Log(ret)
			Log(keys)
			if not all(keys in data for keys in self.Validate_keys):
				raise exceptions.TMDBAPI_KeyError_Exception('key error',','.join(keys),','.join(self.Validate_keys))
		except exceptions.TMDBAPI_KeyError_Exception as e:
			Log(e.logmessage)
		except Exception as exc:
			Log(exc)
		return True


'''
ValidateKey return
{
  "success": true
}
'''