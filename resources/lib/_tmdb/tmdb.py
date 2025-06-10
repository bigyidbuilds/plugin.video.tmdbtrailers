#!/usr/bin/python3
# -*- coding: utf-8 -*-


import json
import requests
from urllib.parse import urlunparse,urljoin,quote

import xbmc
import xbmcgui

from resources.lib.modules import _xbmcaddon
from resources.lib.modules.utils import Log,TodaysDate
from resources.lib.modules import exceptions

class Tmdb_API():
	"""docstring for Tmdb_API"""
	def __init__(self):
		super(Tmdb_API, self).__init__()
		self.AddonSettings = _xbmcaddon._AddonSettings('plugin.video.tmdbtrailers')
		self.Language      = xbmc.getInfoLabel('System.Language')
		self.token         = self.AddonSettings.getString("tmdb.api.token")
		self.scheme        = 'https'
		self.netloc        = 'api.themoviedb.org'
		self.apiversion    = '3'
		self.headers       = {"accept": "application/json","Authorization":f"Bearer {self.token}"}
		self.session       = requests.Session()
		self.session.headers.update(self.headers)
		self.session.params.update({'language':self.Language})
		self.req_keys_list = ['results','cast','crew']
		self.error_keys = ['success', 'status_code', 'status_message']

	def _Session(self,url,headers=None,params=None):
		try:
			if headers:
				self.session.headers.update(headers)
			if params:
				self.session.params.update({k: v for k, v in params.items() if v is not None})
			u = self.session.get(url)
			data = u.json()
			keys = list(data.keys())
			if all(keys in data for keys in self.error_keys):
				raise exceptions.TMDBAPI_Response_Exception(message='Response Error',errors_dict=data,url=u.url)
			return data
		except exceptions.TMDBAPI_Response_Exception as e:
			Log(e.logmessage)
			return None


	def GetList(self,path,page,listitems=True):
		'''If listitems is True returns items as a list of xbmcgui.listitems false returns raw json data'''
		data = self._Session(urlunparse((self.scheme,self.netloc,f'/{self.apiversion}/{path}',None,None,None)),params={'page':page})
		if data:
			try:
				keys = list(data.keys())
				page = data.get('page',1)
				pages = data.get('total_pages',1)
				if not any(key in self.req_keys_list for key in keys):
					raise exceptions.TMDBAPI_KeyError_Exception('Key Error',','.join(req_keys_list),','.join(keys))
				if 'results' in keys:
					data = data.get('results')
					if listitems:
						return self.ListItems(data,True),page,pages
				elif all(keys in data for keys in ['cast','crew']):
					cast = data.get('cast')
					crew = data.get('crew')
					_all = cast+crew
					if listitems:
						items = []
						for a in _all:
							for k,v in a.items():
								if k == 'release_date' and v == '':
									a.update({'release_date':'9999-12-31'})
								elif  k == 'first_air_date' and v == '':
									a.update({'first_air_date':'9999-12-31'})
						_all = sorted(_all, key=lambda d: d.get('release_date',d.get('first_air_date')),reverse=True)
						m = []
						t = []
						clean_all = []
						for a in _all:
							if a.get('release_date') == '9999-12-31':
								a.pop('release_date',None)
							elif a.get('first_air_date') == '9999-12-31':
								a.pop('first_air_date',None)
							media_type = a.get('media_type')
							tmdbid = a.get('id')
							if media_type == 'movie':
								if not tmdbid in m:
									m.append(tmdbid)
									clean_all.append(a)
							elif media_type == 'tv':
								if not tmdbid in t:
									t.append(tmdbid)
									clean_all.append(a)
						return self.ListItems(clean_all,True),page,pages
				else:
					return data,page,pages
			except exceptions.TMDBAPI_KeyError_Exception as e:
				Log(e.logmessage)
				return None,page,pages
		else:
			return None,page,pages

	def GetItem(self,path,listitems=True):
		data = self._Session(urlunparse((self.scheme,self.netloc,f'/{self.apiversion}/{path}',None,None,None)))
		if data:
			if listitems:
				pass
			else:
				return data
		else:
			return


	def GetVidoes(self,path,listitems=True):
		ret = self._Session(urlunparse((self.scheme,self.netloc,f'/{self.apiversion}/{path}',None,None,None)))
		if ret:
			data = ret.get('results')
			if listitems:
				pass
			else:
				return data
		else:
			return

	def Search(self,query,path,listitems=True):
		ret = self._Session(urlunparse((self.scheme,self.netloc,f'{self.apiversion}/{path}',None,None,None)),params={'query':quote(query)})
		if ret:
			data = ret.get('results')
			if listitems:
				return self.ListItems(data,True)
			else:
				return data
		else:
			return

	def ListItems(self,data,IsFolder):
		items = []
		if isinstance(data,list):
			for item in data:
				listitem = self.CreateListitem(item,IsFolder)
				if listitem:
					items.append(listitem)
			return items
		else:
			return self.CreateListitem(data,IsFolder)

	def CreateListitem(self,item,IsFolder):
		if isinstance(item,dict):
			kw = list(item.keys())
			if 'title' in kw:
				label = item.get('title')
			elif not 'title' in kw and 'original_title' in kw:
				label = item.get('original_title')
			elif 'name' in kw:
				label = item.get('name')
			elif not 'name' in kw and 'original_name' in kw:
				label = item.get('original_name')
			else:
				label = _xbmcaddon._AddonLocalStr('plugin.video.tmdbtrailers',32015)
			if 'profile_path' in kw:
				poster = self.ImageUrl(item.get('profile_path'))
			elif 'poster_path' in kw:
				poster = self.ImageUrl(item.get('poster_path'))
			else:
				poster = None
			if 'backdrop_path' in kw:
				fanart = self.ImageUrl(item.get('backdrop_path'))
			else:
				fanart = None
			li = xbmcgui.ListItem(label)
			li.setArt({'poster':poster,'fanart':fanart,'thumb':poster})
			# for k,v in item.items():
			li.setProperty('Properties',json.dumps(item))
			Log(li.getProperty('media_type'))
			li.setIsFolder(IsFolder)
			vi = li.getVideoInfoTag()
			if 'overview' in kw:
				overview = item.get('overview')
			else:
				overview = None
			if 'release_date' in kw:
				premiered = item.get('release_date')
			else:
				premiered = None
			if 'first_air_date' in kw:
				airdate = item.get('first_air_date')
			else:
				airdate = None
			if 'vote_average' in kw and 'vote_count' in kw:
				voteaverage = item.get('vote_average')
				votecount = item.get('vote_count')
			else:
				voteaverage = None
				votecount = None
			if overview:
				vi.setPlot(overview)
			if premiered:
				vi.setPremiered(premiered)
			if airdate:
				vi.setFirstAired(airdate)
			if voteaverage and votecount:
				vi.setRating(voteaverage,votecount,'tmdb',True)
			vi.setUniqueID(json.dumps(item.get('id')),'tmdb',True)
			return li
		else:
			return None


	def ImageUrl(self,path):
		return urlunparse((self.scheme,'image.tmdb.org',f't/p/original/{path}',None,None,None))

