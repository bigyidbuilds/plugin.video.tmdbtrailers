#!/usr/bin/python3
# -*- coding: utf-8 -*-

import xbmc
import xbmcgui

from resources.lib._tmdb.tmdb import TMDB_API
from resources.lib._tmdb.tmdb_account import TMDB_Account
from resources.lib._tmdb.tmdb_token import TOKEN
from resources.lib._tmdb.tmdb_utils import TMDB_ImageUrl
from resources.lib._youtube.youtube_api import YouTubeAPI
from resources.lib.modules import _xbmc
from resources.lib.modules import userfiles

__addon__ = 'plugin.video.tmdbtrailers'

class VideoWindow(xbmcgui.WindowXML):
	"""docstring for VideoWindow"""

	ACTION_SELECT_ITEM   = 7
	ACTION_PREVIOUS_MENU = 10
	ACTION_NAV_BACK = 92

	BACKDROP = 1001
	POSTER = 1002
	LABEL = 1003
	CLOSE = 1004
	DESCRIPTION_BACKGROUND = 1005
	DESCRIPTION = 1006
	VIDEO_LIST = 2000
	VIDEO_LIST_DESCRIPTION = 2003
	CONTEXT_GROUP = 3000
	SIGN_IN = 3001
	SIGN_OUT = 3002
	LISTS = 3003
	ADD_FAV = 3004
	REM_FAV = 3005
	ADD_WATCH = 3006
	REM_WATCH = 3007

	def __new__(cls,tmdbid,mediatype):
		return super(VideoWindow, cls).__new__(cls,'video_window.xml',_xbmc._AddonInfo(__addon__,'path'),'Default', '1080i')

	def __init__(self, tmdbid,mediatype):
		super().__init__()
		self.addon_settings = _xbmc._AddonSettings(__addon__)
		self.yt_api = self.addon_settings.getString('youtube.api.key')
		self.use_yt_api = True if self.addon_settings.getBool('youtube.general.useapi') and self.yt_api  else False
		self.configpath = _xbmc._joinPath(_xbmc._AddonInfo(__addon__,'path'),file_name='config',file_ext='json')
		self.tmdbid = tmdbid
		self.mediatype = mediatype
		self.TMDB_API = TMDB_API(TOKEN)
		self.TMDB_ACC = None
		if self.use_yt_api:
			self.YT_API = YouTubeAPI(self.yt_api)
		else:
			self.YT_API = None
		self.media = self.TMDB_API.GetDetailsandVidoes(self.tmdbid,self.mediatype)
		self.backdrop = TMDB_ImageUrl(self.media.get('backdrop_path'))
		self.poster = TMDB_ImageUrl(self.media.get('poster_path'))
		if self.mediatype == 'movie':
			self.label = self.media.get('title',self.media.get('original_title'))
			self.release_date = self.media.get('release_date')
		elif self.mediatype == 'tv':
			self.label = self.media.get('name')
			self.first_air_date = self.media.get('first_air_date')
			self.last_air_date = self.media.get('last_air_date')
		else:
			self.label = 'Label missing or not found'
		self.genres = self.media.get('genres')
		self.rating = self.media.get('vote_average')
		self.plot = self.media.get('overview')
		self.overview = self.OverView()
		try:
			self.trailers = self.media.get('videos').get('results')
		except Exception as e:
			_xbmc.Log(e)
			self.trailers = None
		if self.trailers:
			self.videolistitems = self.VideoListItems()
			self.videolistitems_count = len(self.videolistitems)
			_xbmc.Log(self.videolistitems_count)
		else:
			self.videolistitems = None
			self.videolistitems_count = 0
		userfiles.RequiredFiles(self.configpath)
		userfiles.RequiredDirs(self.configpath)





	def onInit(self):
		self.setProperty('label',self.label)
		self.setProperty('overview',self.overview)
		self.setImage(self.BACKDROP,self.backdrop)
		self.setImage(self.POSTER,self.poster)
		if self.videolistitems:
			if self.videolistitems_count < 18:
				height = self.videolistitems_count*50
				list_posy = 100+(900-height)
				list_posx = 1290
				if list_posy < 500:
					desc_posy = list_posy+5
				else:
					desc_posy = list_posy-385
					_xbmc.Log(desc_posy)
				desc_posx = 565

			else:
				list_posx = 1290
				list_posy = 100
				height = 900
				desc_posy = 105
				desc_posx = 565
			self.setHeight(self.VIDEO_LIST,height)
			self.setPosition(self.VIDEO_LIST,list_posx,list_posy)
			self.addItems(self.VIDEO_LIST,self.videolistitems)
			self.setPosition(self.VIDEO_LIST_DESCRIPTION,desc_posx,desc_posy)
		self.UserMenu()

	def onAction(self,actionID):
		actionid = actionID.getId()
		focusid = self.getFocusId()
		_xbmc.Log(f'onAction {actionid} Focus ID {focusid}')
		if actionid in [self.ACTION_PREVIOUS_MENU,self.ACTION_NAV_BACK]:
			self.Close()
		elif actionid in [self.ACTION_SELECT_ITEM]:
			if focusid == self.VIDEO_LIST:
				item = self.getSelectedItem(self.VIDEO_LIST)
				path = item.getPath()
				xbmc.Player().play(path)

	def onClick(self,controlID):
		_xbmc.Log(f'onClick{controlID}')
		if controlID == self.CLOSE:
			self.Close()
		elif controlID == self.SIGN_IN:
			self.SignIn()
		elif controlID == self.SIGN_OUT:
			self.SignOut()
		elif controlID == self.ADD_FAV:
			self.Fav(True)
		elif controlID == self.ADD_WATCH:
			self.Watch(True):
		elif controlID == self.REM_FAV:
			self.Fav(False)
		elif controlID == self.REM_WATCH:
			self.Watch(False)


	def Close(self):
		super().close()


	def UserMenu(self):
		for i in [self.SIGN_IN,self.SIGN_OUT,self.LISTS,self.REM_FAV,self.REM_WATCH,self.ADD_FAV,self.ADD_WATCH]:
			self.setVisible(i,False)
		sessionid = self.SessionId()
		if sessionid:
			self.setVisible(self.SIGN_OUT,True)
			self.setVisible(self.LISTS,True)
			self.TMDB_ACC = TMDB_Account(TOKEN,sessionid)
			if self.TMDB_ACC.IsInFavourites(self.mediatype,self.UserId(),self.tmdbid):
				self.setVisible(self.REM_FAV,True)
			else:
				self.setVisible(self.ADD_FAV,True)	
			if self.TMDB_ACC.IsInWatchlist(self.mediatype,self.UserId(),self.tmdbid):
				self.setVisible(self.REM_WATCH,True)
			else:
				self.setVisible(self.ADD_WATCH,True)
		else:
			self.setVisible(self.SIGN_IN,True)



	def SignIn(self):
		pass
		
	def SignOut(self):
		pass

	def Fav(self,add):
		sessionid = self.SessionId()
		account_id = self.UserId()
		if not self.TMDB_ACC:
			self.TMDB_ACC = TMDB_Account(TOKEN,sessionid)
		ret = self.TMDB_ACC.Favorites(account_id,self.tmdbid,add,self.media_type)
		success = ret.get('status_message')

	def Watch(self,add):
		pass


	def VideoListItems(self):
		listitems = []
		for item in self.trailers:
			site = item.get('site')
			key = item.get('key')
			name = item.get('name')
			if site == 'YouTube':
				if self.addon_settings.getBool('youtube.general.useaddon'):		
					if self.use_yt_api :
						d = self.YT_API.VideoDetails(key,'snippet')
						if d:
							pageinfo = d.get('pageInfo')
							if pageinfo:
								totalresults = pageinfo.get('totalResults')
								if totalresults >= 1:
									items = d.get('items')
									item = items[0]
									snippet = item.get('snippet')
									li = _xbmc.ListitemYouTubeVideoItem(snippet,False)
								else:
									li = _xbmc.ListItemBasic(name,properties=item)
							else:
								li = _xbmc.ListItemBasic(name,properties=item)
						else:
							li = _xbmc.ListItemBasic(name,properties=item)
					else:
						li = _xbmc.ListItemBasic(name,properties=item)
					li.setPath(f'plugin://plugin.video.youtube/play/?video_id={key}')
			elif site == 'Vimeo':
				li = _xbmc.ListItemBasic(name,properties=item)
				li.setPath(f'plugin://plugin.video.vimeo/play/?video_id={key}')
			listitems.append(li)
		return listitems




	def OverView(self):
		genre_list = ','.join([g.get('name') for g in self.genres])
		des = [self.plot,f'[I]{_xbmc._AddonLocalStr(__addon__,32052)}[/I]: {genre_list}',f'[I]{_xbmc._AddonLocalStr(__addon__,32077)}[/I]: {self.rating}']
		if self.mediatype == 'movie':
			des.extend([f'[I]{_xbmc._AddonLocalStr(__addon__,32078)}[/I]: {self.release_date}'])
			return '\n\n'.join(des)
		elif self.mediatype == 'tv':
			des.extend([f'[I]{_xbmc._AddonLocalStr(__addon__,32079)}[/I]: {self.first_air_date}',f'[I]{_xbmc._AddonLocalStr(__addon__,32080)}[/I]: {self.last_air_date}'])
			return '\n\n'.join(des)
		else:
			return

	def SessionId(self):
		self.addon_settings = _xbmc._AddonSettings(__addon__)
		return self.addon_settings.getString('tmdb.user.sessionid')

	def UserId(self):
		self.addon_settings = _xbmc._AddonSettings(__addon__)
		return self.addon_settings.getInt('tmdb.user.id')

	def setImage(self,controlid,path):
		control = self.getControl(controlid)
		control.setImage(path)

	def setLabel(self,controlid,label):
		control = self.getControl(controlid)
		control.setLabel(label)

	def getHeight(self,controlid):
		control = self.getControl(controlid)
		return control.getHeight()

	def setHeight(self,controlid,height):
		control = self.getControl(controlid)
		control.setHeight(height)

	def addItems(self,controlid,items):
		control = self.getControl(controlid)
		control.addItems(items)

	def setPosition(self,controlid,x, y):
		control = self.getControl(controlid)
		control.setPosition(x, y)

	def getSelectedItem(self,controlid):
		control = self.getControl(controlid)
		return control.getSelectedItem()

	def setVisible(self,controlid,visible):
		control = self.getControl(controlid)
		control.setVisible(visible)