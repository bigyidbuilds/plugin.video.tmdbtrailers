#!/usr/bin/python3
# -*- coding: utf-8 -*-

import xbmc
import xbmcgui

import json
from urllib.parse import parse_qs

from resources.lib._tmdb.tmdb_account import TMDB_Account
from resources.lib._tmdb.tmdb import TMDB_API
from resources.lib.modules import _xbmc
from resources.lib.modules import userlists
from resources.lib.modules._paths import File_Paths
from resources.lib.modules import exceptions
from resources.lib.modules import _jsonfiles

		
__addon__ = 'plugin.video.tmdbtrailers'

class Account():
	"""
	Sample of paths
	1.  RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=user_detatils
	2.  RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=favorite_add&media_type=movie&tmdbid=10000
	3.  RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=favorite_remove&media_type=tv&tmbid=2000
	4.  RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=watchlist_add&media_type=movie&tmdbid=10000
	5.  RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=watchlist_remove&media_type=tv&tmbid=2000
	6.  RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=rate&media_type=movie&tmdbid=123456&rating=8.7)
	7.  RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=unrate&media_type=tv&tmdbid=654321)
	8.  RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=clear_list&list_id=1234)
	9.  RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=delete_list&list_id=1234)
	10. RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&&action=delete_listitem&list_id=1234&tmdbid=123456)


	sys.argv

	mode 
		mode = account

	action
		available actions:
			user_details: Pulls account details from TMDB and sets relative settings
			sigin: sign in and create session id
			signout: sign out and delete session id
			favorite_add: required params media_type(movie or tv),tmdbid(id of tmdb media)
			favorite_remove: required params media_type(movie or tv),tmdbid(id of tmdb media)
			watchlist_add: required params media_type(movie or tv),tmdbid(id of tmdb media)
			watchlist_remove: required params media_type(movie or tv),tmdbid(id of tmdb media)
			rate: required params media_type(movie or tv),tmdbid(id of tmdb media),rating(0-10 value as float 1 decimal place value must be dividable by 0.5 or '###' will call xbmc ui to enter a valve )
			unrate: required params media_type(movie or tv),tmdbid(id of tmdb media)
			clear_list: required params list_id (id of list)
			delete_list: required params list_id (id of list)
			delete_listitem: required params list_id(id of list), tmdbid(id of tmdb media)

	"""
	def __init__(self,sysargv):
		super(Account, self).__init__()
		self.sysargv = sysargv
		_xbmc.Log(self.sysargv)
		self.keyvalues = parse_qs(self.sysargv[2][1:])
		self.req_keys = ['mode','action']
		self.keys = list(self.keyvalues.keys())
		self.tmdbacc = None
		self.bearer = None
		self.session_id = None
		self.user_id = None
		self.addon = None
		self.CONFIGPATH = _xbmc._joinPath(_xbmc._AddonInfo(__addon__,'path'),file_name='config',file_ext='json')
		self.FILEPATHS = File_Paths(self.CONFIGPATH)
		self.dialog = xbmcgui.Dialog()
		self.AddonSettings = _xbmc._AddonSettings(__addon__)
		lang = self.AddonSettings.getString('tmdb.language')
		if lang == 'xbmc':
			self.Language = xbmc.getInfoLabel('System.Language')
		elif lang == 'tmdb':
			l = self.AddonSettings.getString('tmdb.user.defaultlanguage')
			if l != '':
				self.Language == l
			else:
				self.Language = 'en-US'
		else:
			self.Language = 'en-US'
		try:
			if not self.ValidateSysArgvKeys(self.keys,self.req_keys):
				raise exceptions.RUNPLUGIN_sysargv_keys_Exception(message='ERROR',req_keys=self.req_keys,keys=self.keys)
			ret,missing = self.ValidateSysArgvValues(self.req_keys)
			if not ret:
				raise exceptions.RUNPLUGIN_sysargv_var_Exception(message='ERROR',missing=missing) 
		except exceptions.RUNPLUGIN_sysargv_keys_Exception as ke:
			_xbmc.Log(ke.logmessage)
			return None
		except exceptions.RUNPLUGIN_sysargv_var_Exception as ve:
			_xbmc.Log(ve.message)
			return None
		except Exception as exc:
			_xbmc.Log(exc)
			return None


	def RunPluginMethod(self):
		mode = self.keyvalues.get('mode')[0]
		action = self.keyvalues.get('action')[0]
		try:
			self.addon = self.keyvalues.get('addon_id')[0]
		except:
			self.addon = __addon__
		if self.addon == __addon__:
			self.bearer = self.AddonSettings.getString('tmdb.api.token')
			self.session_id = self.AddonSettings.getString('tmdb.user.sessionid')
			self.user_id = self.AddonSettings.getInt('tmdb.user.id')
		if self.bearer and self.session_id and self.user_id:
			self.tmdbacc = TMDB_Account(self.bearer,self.session_id)
			self.tmdbapi = TMDB_API(self.bearer)
		if not self.tmdbacc:
			return
		if action == 'user_details':
			self.UserDetails()
		elif action == 'signin':
			self.SignIn()
		elif action == 'signout':
			self.SignOut()
		elif action == 'favorite_add':
			if self.CorrectFormat(['media_type','tmdbid']):
				self.Favorite(int(self.keyvalues.get('tmdbid')[0]),True,self.keyvalues.get('media_type')[0])
			else:
				return
		elif action == 'favorite_remove':
			if self.CorrectFormat(['media_type','tmdbid']):
				self.Favorite(int(self.keyvalues.get('tmdbid')[0]),False,self.keyvalues.get('media_type')[0])
			else:
				return
		elif action == 'watchlist_add':
			if self.CorrectFormat(['media_type','tmdbid']):
				self.Watchlist(int(self.keyvalues.get('tmdbid')[0]),True,self.keyvalues.get('media_type')[0])
			else:
				return
		elif action == 'watchlist_remove':
			if self.CorrectFormat(['media_type','tmdbid']):
				self.Watchlist(int(self.keyvalues.get('tmdbid')[0]),False,self.keyvalues.get('media_type')[0])
			else:
				return
		elif action == 'rate':
			if self.CorrectFormat(['media_type','tmdbid','rating']):
				self.Rate(self.keyvalues.get('media_type')[0],int(self.keyvalues.get('tmdbid')[0]),self.keyvalues.get('rating')[0])
			else:
				return
		elif action == 'unrate':
			if self.CorrectFormat(['media_type','tmdbid']):
				self.unRate(self.keyvalues.get('media_type')[0],int(self.keyvalues.get('tmdbid')[0]))
			else:
				return
		elif action == 'clear_list':
			if self.CorrectFormat(['list_id']):
				self.ClearList(int(self.keyvalues.get('list_id')[0]))
		elif action == 'delete_list':
			if self.CorrectFormat(['list_id']):
				self.DeleteList(int(self.keyvalues.get('list_id')[0]))
		elif action == 'edit_lists':
			if self.CorrectFormat(['media_type','tmdbid']):
				self.EditLists(self.keyvalues.get('media_type')[0],int(self.keyvalues.get('tmdbid')[0]))
		elif action == 'delete_listitem':
			if self.CorrectFormat(['list_id','tmdbid']):
				self.DeleteListItem(int(self.keyvalues.get('list_id')[0]),int(self.keyvalues.get('tmdbid')[0]))
		else:
			return

	def CorrectFormat(self,reqkeys):
		try:
			if not self.ValidateSysArgvKeys(self.keys,reqkeys):
				raise exceptions.RUNPLUGIN_sysargv_keys_Exception(message='ERROR',req_keys=reqkeys,keys=self.keys)
			ret,missing = self.ValidateSysArgvValues(reqkeys)
			if not ret:
				raise exceptions.RUNPLUGIN_sysargv_var_Exception(message='ERROR',missing=missing)
			return True
		except exceptions.RUNPLUGIN_sysargv_keys_Exception as ke:
			_xbmc.Log(ke.logmessage)
			return False
		except exceptions.RUNPLUGIN_sysargv_var_Exception as ve:
			_xbmc.Log(ve.message)
			return False
		except Exception as exc:
			_xbmc.Log(exc)
			return False


	def DeleteListItem(self,list_id,tmdbid):
		data = self.tmdbacc.RemoveListItem(list_id,tmdbid)
		self.Notification(data)
		xbmc.executebuiltin('Container.Refresh')


	def EditLists(self,media_type,tmdbid):
		selection = [_xbmc.ListItemBasic(_xbmc._AddonLocalStr(__addon__,32046),isfolder=False)]
		account_lists = _jsonfiles.ReadJsonFile(self.FILEPATHS.account,keys=['account_lists'])
		for k,v in account_lists.items():
			results = v.get('results')
			for r in results:
				list_id = r.get('id')
				name = r.get('name')
				item_present = self.tmdbapi.CheckListSatus(list_id,tmdbid)
				d={'list_id':list_id,'name':name,'item_present':item_present}
				if item_present:
					selection.append(_xbmc.ListItemBasic(_xbmc._AddonLocalStr(__addon__,32048).format(name=name),properties=d,isfolder=False))
				else:
					selection.append(_xbmc.ListItemBasic(_xbmc._AddonLocalStr(__addon__,32049).format(name=name),properties=d,isfolder=False))
		ret = self.dialog.select(_xbmc._AddonLocalStr(__addon__,32047),selection)
		_xbmc.Log(ret)
		if ret >= 0:
			if ret == 0:
				payload = {'name':None,'description':None,'language':self.Language}
				ret1 = self.dialog.input(_xbmc._AddonLocalStr(__addon__,32029))
				ret2 = self.dialog.input(_xbmc._AddonLocalStr(__addon__,32030))
				payload.update({'name':ret1,'description':ret2})
				data = self.tmdbacc.AddList(payload)
				success = data.get('success')
				list_id = data.get('list_id')
				if success:
					userlists.ListCacheUpdate(self.FILEPATHS.account,self.session_id,self.user_id,self.bearer)
					data = self.tmdbacc.AddListItem(list_id,tmdbid)
					self.Notification( data)
			else:
				sel = selection[ret]
				properties = json.loads(sel.getProperty('Properties'))
				item_present = properties.get('item_present')
				list_id = properties.get('list_id')
				if item_present:	
					data = self.tmdbacc.RemoveListItem(list_id,tmdbid)
					self.Notification( data)
				else:
					data = self.tmdbacc.AddListItem(list_id,tmdbid)
					self.Notification( data)
	
				


	def DeleteList(self,list_id):
		data = self.tmdbacc.DeleteList(list_id)
		self.Notification( data)
		userlists.ListCacheUpdate(self.FILEPATHS.account,self.session_id,self.user_id,self.bearer)
		xbmc.executebuiltin('Container.Refresh')


	def ClearList(self,list_id):
		data = self.tmdbacc.ClearList(list_id)
		self.Notification( data)
		xbmc.executebuiltin('Container.Refresh')


	def Favorite(self,tmdbid,action,media_type):
		data = self.tmdbacc.Favorites(self.user_id,tmdbid,action,media_type)
		self.Notification( data)
		userlists.FavoriteCacheUpdate(self.FILEPATHS.account,self.session_id,self.user_id,self.bearer,media_type)
		xbmc.executebuiltin('Container.Refresh')


	def Watchlist(self,tmdbid,action,media_type):
		data = self.tmdbacc.Watchlist(self.user_id,tmdbid,action,media_type)
		self.Notification(data)
		userlists.WatchlistCacheUpdate(self.FILEPATHS.account,self.session_id,self.user_id,self.bearer,media_type)
		xbmc.executebuiltin('Container.Refresh')

	
	def Rate(self,media_type,tmdbid,rating):
		data = None
		media_title = None
		if rating == '###':
			if media_type == 'movie':
				path = f'movie/{tmdbid}'
				kw = 'title'
				_data = self.tmdbapi.GetItem(path)
				media_title = _data.get(kw)
			elif media_type == 'tv':
				path = f'tv/{tmdbid}'
				kw = 'name'
				_data = self.tmdbapi.GetItem(path)
				media_title = _data.get(kw)
			else:
				rating = None
			from resources.lib.windows.rate_slider import RateSlider
			rating = RateSlider(media_title)
		if rating:
			rating = float(rating)
			if media_type == 'movie':
				data = self.tmdbacc.RateMovie(tmdbid,rating)
				userlists.RatedCacheUpdate(self.FILEPATHS.account,self.session_id,self.user_id,self.bearer,media_type)
			elif media_type == 'tv':
				data = self.tmdbacc.RateTv(tmdbid,rating)
				userlists.RatedCacheUpdate(self.FILEPATHS.account,self.session_id,self.user_id,self.bearer,media_type)
			if data:
				self.Notification(data)	
			xbmc.executebuiltin('Container.Refresh')

	def unRate(self,media_type,tmdbid):
		data = None
		if media_type == 'movie':
			data = self.tmdbacc.unRateMovie(tmdbid)
			userlists.RatedCacheUpdate(self.FILEPATHS.account,self.session_id,self.user_id,self.bearer,media_type)
		elif media_type == 'tv':
			data = self.tmdbacc.unRateTv(tmdbid)
			userlists.RatedCacheUpdate(self.FILEPATHS.account,self.session_id,self.user_id,self.bearer,media_type)
		if data:
			self.Notification( data)
		xbmc.executebuiltin('Container.Refresh')

	def Notification(self,data):
		_xbmc.Log(data)
		self.dialog.notification(_xbmc._AddonInfo(self.addon,'name'), data.get('status_message'),_xbmc._AddonInfo(self.addon,'icon'))

	def UserDetails(self):
		pass
		self.AddonSettings.setInt('tmdb.user.id', ret.get('id'))
		self.AddonSettings.setString('tmdb.user.name',ret.get('name'))
		self.AddonSettings.setString('tmdb.user.defaultlanguage',ret.get('iso_639_1'))
		self.AddonSettings.setBool('tmdb.user.adultsearch',ret.get('include_adult'))
		self.AddonSettings.setString('tmdb.user.avatar',self.ImageUrl(ret.get('tmdb').get('avatar_path')))

	def SignIn(self):
		pass

	def SignOut(self):
		pass


	def ValidateSysArgvKeys(self,keys,req_keys):
		return all(key in keys for key in req_keys)

	def ValidateSysArgvValues(self,req_keys):
		missing = []
		for k,v in self.keyvalues.items():
			if k in self.req_keys:
				v = v[0]
				if v == None:
					missing.append(k)
		if len(missing) == 0:
			return True,missing
		else:
			return False,missing
		
