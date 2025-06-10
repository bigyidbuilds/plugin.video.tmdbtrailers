#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

import xbmcvfs

from .utils import CheckCreateFile,ValidateJsonFile,WriteJsonFile,ReadJsonFile,Log,TimeStamp
from ._xbmcaddon import _AddonInfo

__addon__ = 'plugin.video.tmdbtrailers'

FILEEXT      = 'user.json'
ADDONPATH    = _AddonInfo(__addon__,'path')
ADDONPROFILE = _AddonInfo(__addon__,'profile')
USERJSONFILE = os.path.join(ADDONPROFILE,FILEEXT)
USERJSONBASE = os.path.join(ADDONPATH,FILEEXT)


# def UserDataFile(filepath,filename):
# 	'''creates user.json file with required keys'''
# 	s = {'movie_search':[],'tv_search':[],'people_search':[],'access':{},'account':{}}
# 	f = CheckCreateFile(filepath,filename)
# 	if f:
# 		v = ValidateJsonFile(filepath,filename,s)
# 		if not v:
# 			WriteJsonFile(filepath,filename,s)
# 			v = ValidateJsonFile(filepath,filename,s)
# 	return f,v

def UserDataFile(force_replace=False):
	if not xbmcvfs.exists(ADDONPROFILE):
		xbmcvfs.mkdirs(ADDONPROFILE)
	if xbmcvfs.exists(USERJSONBASE):
		if not force_replace:
			if xbmcvfs.exists(USERJSONFILE):
				data_file = ReadJsonFile(USERJSONFILE,key='version')
				base_file = ReadJsonFile(USERJSONBASE,key='version')
				if data_file == None or base_file > data_file:
					fname = f'user_{TimeStamp()}.json'
					xbmcvfs.rename(USERJSONFILE,os.path.join(ADDONPROFILE,fname))
					xbmcvfs.copy(USERJSONBASE,USERJSONFILE)
			else:
				xbmcvfs.copy(USERJSONBASE,USERJSONFILE)
		else:
			xbmcvfs.copy(USERJSONBASE,USERJSONFILE)



def ClearUserLists():
	data = ReadUserDataFile()
	acc = data.get('account')
	acc.update({
		"account_favorite": {
			"movies": [],
			"tv": []
		},
		"account_watchlist": {
			"movies": [],
			"tv": []
		},
		"account_rated": {
			"movies": [],
			"tv": []
		},
		"account_lists": {}})
	writeUserDataFile(data)

def AddonUserValidate(filepath,filename,addon_id):
	'''Adds client addon id and required keys to user.json file ''' 
	d = ReadJsonFile(filepath,filename)
	access_data = d.get('access')
	addons = list(access_data.keys())
	if addon_id not in addons:
		access_data.update({addon_id:{'key_details':{},'token_details':{},'session_details':{}}})
		WriteJsonFile(filepath,filename,d)
		dd = ReadJsonFile(filepath,filename,'access')
		addons = list(dd.keys())
		if addon_id in addons:
			return True
		else:
			return False
	else:
		return True

def ReadUserDataFile():
	return ReadJsonFile(USERJSONFILE)

def writeUserDataFile(data):
	WriteJsonFile(USERJSONFILE,data=data)


def CheckUserAccount():
	d = ReadJsonFile(USERJSONFILE,key='account')
	if d:
		if d.get('account_details').get('id'):
			return True
		else:
			return False
	else:
		return False
		