#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime
import json
import os

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

from ._xbmc import _translatePath,_AddonSettings,_AddonInfo


__addon__ = 'plugin.video.tmdbtrailers'


def _joinPath(filepath,filename):
	return os.path.join(filepath,filename)

def WriteJsonFile(filepath,filename=None,data=None):
	filepath = _translatePath(filepath)
	if filename:
		path = _joinPath(filepath,filename)
	else:
		path = filepath
	if xbmcvfs.exists(path):
		with open(path,'w') as f:
			json.dump(data,f,indent=4)


def ReadJsonFile(filepath,filename=None,key=None):
	filepath = _translatePath(filepath)
	if filename:
		path = _joinPath(filepath,filename)
	else:
		path = filepath
	if xbmcvfs.exists(path):
		with open(path) as f:
			try:
				data = json.load(f)
				if key:
					return data.get(key)
				else:
					return data
			except ValueError as ve:
				Log(f'file at {path} error {ve}')
				return None
			except Exception as exc:
				Log(exc)
				return None
	else:
		Log(f'file not found at {path}')
		return None

def ValidateJsonFile(filepath,filename,basedict):
	'''needs amethod for if the user.json dicts have chabged that it saves the old verison'''
	filepath = _translatePath(filepath)
	file = _joinPath(filepath,filename)
	if xbmcvfs.exists(file):
		with open(file) as f:
			try:
				data = json.load(f)
			except ValueError as e:
				Log(f'file at {file} error {e}')
				data = None
				validation = False
		if data:
			basedict_keys = list(basedict.keys())
			file_keys = list(data.keys())
			Log(basedict_keys)
			Log(file_keys)
			if set(basedict) == set(file_keys):
				Log(f'file: {filename} at path: {filepath} validated for keys {file_keys}')
				validation = True
			else:
				Log(f'file: {filename} at path: {filepath} not validated for keys {file_keys}')
				validation = False
		else:
			validation = False
	else:
		validation = False
	return validation


def TimeStamp(date_time=None,now=True):
	'''params:
				date_time is a datetime object
				now if True will return timestamp from now
	'''
	if now:
		dt = datetime.now()
	else:
		dt = date_time
	return datetime.timestamp(dt)

def TodaysDate():
	return datetime.today().strftime('%Y-%m-%d')



def GetListLoop(call,path,page):
	items = []
	def func(call,path,page):
		_data,_page,_pages = call(path,page,listitems=False)
		for _d in _data:
			items.append(_d)
		_page += 1
		if _page <= _pages:
			func(call,path,_page)
	func(call,path,page)
	return items