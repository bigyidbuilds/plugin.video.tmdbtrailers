#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import requests
from urllib.parse import urlunparse

from resources.lib.modules._xbmc import Log
from resources.lib.modules import exceptions

from . import tmdb_var


class Tmdb_Authentication():
	"""docstring for Tmdb_Authentication"""

	def __new__(cls,tmdb_api_bearer,tmdb_api_key=None):
			return super().__new__(cls)

	def __init__(self,tmdb_api_bearer,tmdb_api_key=None):
		super(Tmdb_Authentication, self).__init__()
		self.headers       = {"accept": "application/json","Authorization":f"Bearer {tmdb_api_bearer}"}
		self.session       = requests.Session()
		self.session.headers.update(self.headers)
		self.error_keys = ['success', 'status_code', 'status_message']
		self.Validate_keys = ['success']

	def _Session(self,method,path,_headers=None,_params=None,_json=None):
		try:
			URL = urlunparse((tmdb_var.SCHEME,tmdb_var.NETLOC,f'{tmdb_var.APIVERISON}/{path}',None,None,None))
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
		if ret.get('success') == True and 'request_token' in keys:
			return ret.get('request_token')
		else:
			return None
		

	def CreateSession_Withlogin(self,token,username,password):
		''' API reference https://developer.themoviedb.org/reference/authentication-create-request-token '''
		ret,keys = self._Session(
			'POST',
			'authentication/token/validate_with_login',
			_headers={"content-type": "application/json"},
			_json={ 
				"username": username,
				"password": password,
				"request_token": token})
		if ret.get('success') == True and 'request_token' in keys:
			return ret.get('request_token')
		else:
			return None


	def CreateSession(self,token):
		'''API reference https://developer.themoviedb.org/reference/authentication-create-session '''
		ret,keys = self._Session(
			'POST',
			'authentication/session/new',
			_headers={"content-type": "application/json"},
			_json={'request_token':token})
		return ret
		# if ret.get('success') == True and "session_id" in keys:
		# 	return ret.get('session_id')
		# else:
		# 	return None

	def DeleteSession(self,sessionID):
		''' API reference https://developer.themoviedb.org/reference/authentication-delete-session'''
		ret,keys = self._Session(
			'DEL',
			'authentication/session',
			_headers={"content-type": "application/json"},
			_json={"session_id":sessionID})
		return ret,keys


	def SignIn(self,username,password):
		sid = None
		ret = self.CreateRequestToken()
		if ret:
			tok = self.CreateSession_Withlogin(ret,username,password)
			if tok:
					sid = self.CreateSession(tok)
		return sid


	def SignOut(self,session_id):
		ret,key = self.DeleteSession(session_id)
		return ret,key

		
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


