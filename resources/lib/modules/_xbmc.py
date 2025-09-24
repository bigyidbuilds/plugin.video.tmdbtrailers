#!/usr/bin/python3
# -*- coding: utf-8 -*-

import xbmc
import xbmcaddon
import xbmcvfs
import xbmcgui

import os
import json
from urllib.parse import urlunparse





__addon__ = 'plugin.video.tmdbtrailers' 



''' XBMC based functions '''

def Log(msg):
	settings = _AddonSettings(__addon__)
	if settings.getBool('general.debug'):
		from inspect import getframeinfo, stack
		fileinfo = getframeinfo(stack()[1][0])
		xbmc.log(f"*__{_AddonInfo(__addon__,'name')}__{_AddonInfo(__addon__,'version')}*{msg} Python file name = {fileinfo.filename} Line Number = {fileinfo.lineno}", level=xbmc.LOGINFO)


def _joinPath(base_path,folders=None,file_name=None,file_ext=None):
	''' folders is a list and must be layed out in sqence of path os.path.join used as no XBMC module to join a path'''
	full_path = ''
	base_path = _translatePath(base_path)
	if not folders:
		folders = []
	if file_name and file_ext:
		full_file_name = '.'.join([file_name,file_ext])
		folders.append(full_file_name)
	else:
		folders.append('')
	full_path = os.path.join(base_path,*folders)
	Log(full_path)
	return full_path

def FileExists(path):
	return xbmcvfs.exists(path)


def _translatePath(filepath):
	if filepath.startswith('special://'):
		filepath = xbmcvfs.translatePath(filepath)
	else:
		filepath = filepath
	return filepath


def ReadFile(filepath):
	with xbmcvfs.File(file) as f:
		return f.read()

def WriteFile(filepath,content,seek_point=None):
	'''seek_point params = 0 beginning, 1 current , 2 end position'''
	with xbmcvfs.File(file, 'w') as f:
		if seek_point:
			f.seek(0,seek_point)
		return f.write(content)


def CheckCreateFile(path,filename,fileext):
	path = _translatePath(path)
	file = _joinPath(path,file_name=filename,file_ext=fileext)
	if not xbmcvfs.exists(file):
		if not xbmcvfs.exists(path):
			Log(f'Creating path {path}')
			success = xbmcvfs.mkdirs(path)
		else:
			success = True
		if success:
			f = xbmcvfs.File(file, 'w')
			f.close()
			if xbmcvfs.exists(file):
				fileexists = True
				created = True
			else:
				fileexists = False
				created = False
		else:
			Log(f'File path missing or not created at {filepath}')
			fileexists = False
			created = False
	else:
		fileexists = True
		created = False
	if fileexists:
		Log(f'File exists {filename} at path {path}')
	else:
		Log('Unable to create file ')
	return fileexists,created


def CheckCreatePath(base_path,folders=None):
	''' folders list must be layed out in sqence'''
	base_path = _translatePath(base_path)
	path = _joinPath(base_path,folders=folders)
	Log(path)
	if  xbmcvfs.exists(path):
		Log(f'Dirs Path alredy exists:{path}')
		return True
	else:
		success = xbmcvfs.mkdirs(path)
		if success:
			Log(f'Dirs Path created {path}')
		return success


def ListitemYouTubeVideoItem(item,IsFolder):
	if isinstance(item,dict):
		localized = item.get('localized')
		li = xbmcgui.ListItem(localized.get('title',item.get('title')))
		vi = li.getVideoInfoTag()
		vi.setPlot(localized.get(localized.get('description'),item.get('description')))
		vi.setFirstAired(item.get('publishedAt'))
		thumbnails = item.get('thumbnails')
		artwork = {}
		medium = thumbnails.get('medium',thumbnails.get('default'))
		default  = thumbnails.get('default')
		maxres = thumbnails.get('maxres',thumbnails.get('high',thumbnails.get('default')))
		if medium:
			artwork.update({'poster':medium.get('url')})
		if default:
			artwork.update({'thumb':default.get('url')})
		if maxres:
			artwork.update({'fanart':maxres.get('url')})
		li.setArt(artwork)
		li.setProperty('Properties',json.dumps(item))
		li.setIsFolder(IsFolder)
		return li
	else:
		return None



def ListItemBasic(label,label2=None,icon=None,fanart=None,properties=None,isfolder=True,thumb=None):
	li = xbmcgui.ListItem(label)
	if label2:
		li.setLabel2(label2)
	artwork = {'icon':icon,'fanart':fanart,'thumb':thumb}
	artwork = {k:v for k,v in artwork.items() if v is not None}
	li.setArt(artwork)
	if properties:
		li.setProperty('Properties',json.dumps(properties))
	li.setIsFolder(isfolder)
	return li 



def ListItemTMDBList(item,IsFolder):
	def ImageUrl(path):
		return urlunparse(('https','image.tmdb.org',f't/p/original/{path}',None,None,None))
	if isinstance(item,dict):
		li = xbmcgui.ListItem(item.get('name'))
		li.setProperty('Properties',json.dumps(item))
		li.setArt({'poster':ImageUrl(item.get('poster_path'))})
		return li
	else:
		return None

def ListItemTMDBCompany(item,IsFolder):
	def ImageUrl(path):
		return urlunparse(('https','image.tmdb.org',f't/p/original/{path}',None,None,None))
	if isinstance(item,dict):
		li = xbmcgui.ListItem(item.get('name'))
		li.setProperty('Properties',json.dumps(item))
		logo_path = item.get('logo_path')
		if logo_path:
			logo_pathURL = ImageUrl(logo_path)
			li.setArt({'poster':logo_pathURL,'thumb':logo_pathURL})
		li.setIsFolder(IsFolder)
		vi = li.getVideoInfoTag()
		desc = item.get('description')
		if desc:
			vi.setPlot(desc)
		return li
	else:
		return None



def ListitemTMDBCollection(item,IsFolder):
	def ImageUrl(path):
		return urlunparse(('https','image.tmdb.org',f't/p/original/{path}',None,None,None))
	if isinstance(item,dict):
		li = xbmcgui.ListItem(item.get('name'))
		li.setProperty('Properties',json.dumps(item))
		artwork = {}
		backdrop_path = item.get('backdrop_path')
		poster_path = item.get('poster_path')
		if backdrop_path:
			artwork.update({'fanart':ImageUrl(backdrop_path)})
		if poster_path:
			poster_pathURL = ImageUrl(poster_path)
			artwork.update({'poster':poster_pathURL,'thumb':poster_pathURL})
		if backdrop_path or poster_path:
			li.setArt(artwork)
		li.setIsFolder(IsFolder)
		vi = li.getVideoInfoTag()
		vi.setPlot(item.get('overview'))
		return li
	else:
		return None




def ListitemTMDBitem(item,IsFolder):
	'''Converts json object return from TMDB in to a list item'''
	def ImageUrl(path):
		return urlunparse(('https','image.tmdb.org',f't/p/original/{path}',None,None,None))
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
			poster = ImageUrl(item.get('profile_path'))
		elif 'poster_path' in kw:
			poster = ImageUrl(item.get('poster_path'))
		else:
			poster = None
		if 'backdrop_path' in kw:
			fanart = ImageUrl(item.get('backdrop_path'))
		else:
			fanart = None
		li = xbmcgui.ListItem(label)
		artwork = {'poster':poster,'fanart':fanart,'thumb':poster}
		artwork = {k:v for k,v in artwork.items() if v is not None}
		li.setArt(artwork)
		li.setProperty('Properties',json.dumps(item))
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





def _Addon(addonID):
	return xbmcaddon.Addon(addonID)

def _AddonInfo(addonID,info):
	'''options for info :- path,name,version,profile,icon,fanart'''
	return _Addon(addonID).getAddonInfo(info)

def _AddonLocalStr(addonID,msgctxt):
	'''msgctxt = id from strings.po'''
	return _Addon(addonID).getLocalizedString(msgctxt)

def _AddonSettings(addonID):
	return _Addon(addonID).getSettings()

def _AddonSetSetting(addonID,setting_id,setting_value):
	addon = _Addon(addonID)
	setting_type = type(setting_value)
	a =False
	if setting_type == bool:
		a = addon.setSettingBool(setting_id,setting_value)
	elif setting_type == int:
		a = addon.setSettingInt(setting_id,setting_value)
	elif setting_type == float:
		a = addon.setSettingNumber(setting_id,setting_value)
	elif setting_type == str:
		a = addon.setSettingString(setting_id,setting_value)
	else:
		a = addon.setSetting(setting_id,setting_value)
	if a:
		Log(f'Setting {setting_id}\nupdated or set to {setting_value}\nfor addon:{addonID}')
	else:
		Log(f'Setting {setting_id}\nnot updated or not set to {setting_value}\nfor addon:{addonID}')
	return a