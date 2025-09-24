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

