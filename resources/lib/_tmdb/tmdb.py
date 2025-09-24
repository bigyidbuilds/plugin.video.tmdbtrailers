#!/usr/bin/python3
# -*- coding: utf-8 -*-


import json
import requests
from urllib.parse import urlunparse,urljoin,quote

import xbmc
import xbmcgui

from resources.lib.modules._xbmc import Log,_AddonSettings,_AddonLocalStr
from resources.lib.modules.utils import TodaysDate
from resources.lib.modules import exceptions

from . import tmdb_utils
from . import tmdb_var

class TMDB_API():
	"""docstring for TMDB_API"""

	def __new__(cls,token):
		return super().__new__(cls)

	def __init__(self,token):
		super(TMDB_API, self).__init__()
		self.token         = token
		self.headers       = {"accept": "application/json","Authorization":f"Bearer {self.token}"}
		self.session       = requests.Session()
		self.session.headers.update(self.headers)
		self.error_keys = ['success', 'status_code', 'status_message']

	def _Session(self,url,headers=None,params=None):
		try:
			if headers:
				self.session.headers.update(headers)
			if params:
				self.session.params.update({k: v for k, v in params.items() if v is not None})
			u = self.session.get(url)
			data = u.json()
			if isinstance(data,dict):
				keys = list(data.keys())
				if all(keys in data for keys in self.error_keys):
					raise exceptions.TMDBAPI_Response_Exception(message='Response Error',errors_dict=data,url=u.url)
			return data
		except exceptions.TMDBAPI_Response_Exception as e:
			Log(e.logmessage)
			return None
		except Exception as e:
			Log(e)
			return None

	def _BuildUrl(self,path):
		return urlunparse((tmdb_var.SCHEME,tmdb_var.NETLOC,f'/{tmdb_var.APIVERISON}/{path}',None,None,None))

	def CheckListSatus(self,list_id,tmdb_id):
		"""Required params: language, movie_id"""
		path = f'list/{list_id}/item_status'
		data = self._Session(self._BuildUrl(path),params={'movie_id':tmdb_id,'language':tmdb_var.LANGUAGE})
		if data.get('item_present'):
			return True
		else:
			return False

	def CollectionItems(self,collection_id):
		"""Required params: language"""
		path = f'/collection/{collection_id}'
		data = self._Session(self._BuildUrl(path),params={'language':tmdb_var.LANGUAGE})
		if data:
			return data
		else:
			return None

	def ConfigCountry(self):
		"""Required params: language"""
		path = 'configuration/countries'
		data = self._Session(self._BuildUrl(path),params={'language':tmdb_var.LANGUAGE})
		if data:
			return data
		else:
			return None

	def DiscoverMovies(self,page,params=None,**kwargs):
		"""Required params: language,include_adult"""
		path = 'discover/movie'
		_params = {'page':page,'language':tmdb_var.LANGUAGE,'sort_by':'popularity.desc','include_adult':tmdb_var.ADULTSEARCH}
		if params:
			_params.update({**params})
		elif not params:
			certification = kwargs.get('certification')
			if certification:
				_params.update({'certification':certification})

		data = self._Session(self._BuildUrl(path),params=_params)
		if data:
			return data
		else:
			return None

	def DiscoverTv(self,page,params=None,**kwargs):
		"""Required params: language include_adult"""
		path = 'discover/tv'
		_params = {'page':page,'language':tmdb_var.LANGUAGE,'sort_by':'popularity.desc','include_adult':tmdb_var.ADULTSEARCH}
		if params:
			_params.update({**params})
		elif not params:
			certification = kwargs.get('certification')
			if certification:
				_params.update({'certification':certification})

		data = self._Session(self._BuildUrl(path),params=_params)
		if data:
			return data
		else:
			return None

	def GetList(self,path,page):
		''' Required params: language

		returns json object  consiting of "results" 'page' "total_pages" main keys  

		page is int of page number wanted in return 

		https://api.themoviedb.org/3/movie/now_playing
		path = movie/now_playing

		https://api.themoviedb.org/3/movie/popular 
		path = movie/popular

		https://api.themoviedb.org/3/movie/top_rated 
		path = movie/top_rated

		https://api.themoviedb.org/3/movie/upcoming 
		path = movie/upcoming 

		https://api.themoviedb.org/3/tv/airing_today
		path = tv/airing_today

		https://api.themoviedb.org/3/tv/on_the_air
		path = tv/on_the_air

		https://api.themoviedb.org/3/tv/popular
		path = tv/popular

		https://api.themoviedb.org/3/tv/top_rated
		path = tv/top_rated

		https://api.themoviedb.org/3/person/popular
		path = person/popular
		'''
		 
		data = self._Session(self._BuildUrl(path),params={'page':page,'language':tmdb_var.LANGUAGE})
		if data:
			return data
		else:
			return None



	def GetItem(self,path):
		"""Required params: language"""
		return  self._Session(self._BuildUrl(path),params={'language':tmdb_var.LANGUAGE})

	def GetGenres(self,media_type):
		"""Required params: language"""
		path = f'genre/{media_type}/list'
		return  self._Session(self._BuildUrl(path),params={'language':tmdb_var.LANGUAGE})

	def GetVidoes(self,tmdb_id,media_type):
		"""Required params: language"""
		if media_type == 'movie':
			path = f'movie/{tmdb_id}/videos'
		elif media_type == 'tv':
			path = f'tv/{tmdb_id}/videos'
		else:
			return None
		return  self._Session(self._BuildUrl(path),params={'language':tmdb_var.LANGUAGE})


	def Search(self,query,path,page):
		"""Required params: language include_adult"""
		return  self._Session(self._BuildUrl(path),params={
															'query':quote(query),
															'page':page,
															'language':tmdb_var.LANGUAGE,
															'include_adult':tmdb_var.ADULTSEARCH})

	def SearchCollectionsAll(self,query):
		"""Required params: language include_adult"""
		path = 'search/collection'
		page = 1
		params = {'query':quote(query),'language':tmdb_var.LANGUAGE,'page':page,'include_adult':tmdb_var.ADULTSEARCH}
		data = self._Session(self._BuildUrl(path),params=params)
		if data:
			page+=1
			total_pages = data.get('total_pages')
			results = data.get('results')
			while page <= total_pages:
				_params = {'query':quote(query),'language':tmdb_var.LANGUAGE,'page':page,'include_adult':tmdb_var.ADULTSEARCH}
				_data = self._Session(self._BuildUrl(path),params=_params)
				results.extend(_data.get('results'))
				page+=1
			return data
		else:
			return None

	def SearchCompanyAll(self,query):
		path = 'search/company'
		page = 1
		params = {'query':quote(query),'page':page}
		data = self._Session(self._BuildUrl(path),params=params)
		if data:
			page+=1
			total_pages = data.get('total_pages')
			results = data.get('results')
			while page <= total_pages:
				_params = {'query':quote(query),'page':page}
				_data = self._Session(self._BuildUrl(path),params=_params)
				results.extend(_data.get('results'))
				page+=1
			return data
		else:
			return None

