#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import requests
from urllib.parse import urlunparse

import xbmc
import xbmcgui

from resources.lib.modules import _xbmcaddon
from resources.lib.modules.utils import Log,TimeStamp
from resources.lib.modules import exceptions
# from resources.lib.modules.userjson import ReadUserDataFile,WriteJsonFile



class Tmdb_Account():
	"""docstring for Tmdb_Account"""
	def __init__(self,session_id,clientaddon=None,tmdb_api_key=None,tmdb_api_bearer=None):
		super(Tmdb_Account, self).__init__()
		self.__addon__     = 'plugin.video.tmdbtrailers'
		self.session_id    = session_id
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
		# self.userjson      = ReadUserDataFile()
		self.scheme        = 'https'
		self.netloc        = 'api.themoviedb.org'
		self.apiversion    = '3'
		self.headers       = {"accept": "application/json","Authorization":f"Bearer {self.bearer}"}
		self.session       = requests.Session()
		self.session.headers.update(self.headers)
		self.error_keys = ['success', 'status_code', 'status_message']
		self.Validate_keys = ['success']
		self.req_keys_list = ['results','cast','crew']
		self.Language      = xbmc.getInfoLabel('System.Language')
		self.session.params.update({'language':self.Language})


	def _Session(self,method,path,_headers=None,_params=None,_json=None):
		try:
			URL = urlunparse((self.scheme,self.netloc,f'{self.apiversion}/{path}',None,None,None))
			if method == 'GET':
				u = self.session.get(URL,headers=_headers,params=_params)
			elif method == 'POST':
				u = self.session.post(URL,headers=_headers,params=_params,json=_json)
			elif method == 'DEL':
				u = self.session.delete(URL,headers=_headers,params=_params,json=_json)
			ret = u.json()
			keys = list(ret.keys())
			if all(keys in ret for keys in self.error_keys):
				raise exceptions.TMDBAPI_Response_Exception(message='Response Error',errors_dict=ret,url=u.url)
			return ret,keys
		except exceptions.TMDBAPI_Response_Exception as e:
			Log(e.logmessage)
			return None,None
		except Exception as exc:
			Log(exc)
			return None,None


	def AccountDetails(self):
		'''https://developer.themoviedb.org/reference/account-details'''
		ret = self._Session('GET','account',_params={'session_id':self.session_id})
		return ret


	def AddList(self,payload):
		'''https://developer.themoviedb.org/reference/list-create'''
		ret,keys = self._Session(
			'POST',
			'list',
			_params={
				'session_id':self.session_id},
			_json=payload,
			_headers={
				"content-type": "application/json"})


	def GetLists(self,path,page,listitems=True):
		'''https://developer.themoviedb.org/reference/account-lists'''
		data,keys = self._Session('GET',path,_params={'page':page,'session_id':self.session_id})
		if data:
			try:
				if not 'results' in keys:
					raise exceptions.TMDBAPI_KeyError_Exception('Key Error','results',','.join(keys))
				page = data.get('page')
				pages = data.get('total_pages')
				results = data.get('results')
				if listitems:
					lilist = []
					for r in results:
						li = xbmcgui.ListItem(r.get('name',_xbmcaddon._AddonLocalStr(self.__addon__,32015)))
						li.setArt({'poster':r.get('poster_path')})
						li.setIsFolder(True)
						li.setProperty('Properties',json.dumps(r))
						lilist.append(li)
					return lilist,page,pages
				else:
					return results,page,pages
			except exceptions.TMDBAPI_KeyError_Exception as e:
				Log(e.logmessage)
				return data,0,0
		else:
			return None,0,0

	def GetListDetails(self,path,page,listitems=True):
		'''https://developer.themoviedb.org/reference/list-details'''
		data,keys = self._Session('GET',path,_params={'page':page})
		if data:
			try:
				if not 'items' in keys:
					raise exceptions.TMDBAPI_KeyError_Exception('Key Error','results',','.join(keys))
				page = data.get('page')
				pages = data.get('total_pages')
				items = data.get('items')
				if listitems:
					return self.ListItems(items,True),page,pages
				else:
					return items,page,pages
			except exceptions.TMDBAPI_KeyError_Exception as e:
				Log(e.logmessage)
				return None,0,0
			except Exception as exc:
				Log(exc)
				return None,0,0
		else:
			return None,0,0



	def GetList(self,path,page,listitems=True):
		'''If listitems is True returns items as a list of xbmcgui.listitems false returns raw json data'''
		data,keys = self._Session('GET',path,_params={'page':page,'session_id':self.session_id})
		if data:
			try:
				if not any(key in self.req_keys_list for key in keys):
					raise exceptions.TMDBAPI_KeyError_Exception('Key Error',','.join(self.req_keys_list),','.join(keys))
				page = data.get('page',1)
				pages = data.get('total_pages',1)
				if 'results' in keys:
					data = data.get('results')
					if listitems:
						return self.ListItems(data,True),page,pages
					else:
						return data,page,pages
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
				return None,0,0
		else:
			return None,0,0


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

		
