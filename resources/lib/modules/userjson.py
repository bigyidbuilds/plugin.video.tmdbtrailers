#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

import xbmcvfs

from resources.lib.modules._tmdb.tmdb_account import Tmdb_Account 
from resources.lib.modules.utils import CheckCreateFile,ValidateJsonFile,WriteJsonFile,ReadJsonFile,Log,TimeStamp,GetListLoop
from resources.lib.modules._xbmcaddon import _AddonInfo

__addon__ = 'plugin.video.tmdbtrailers'

FILEEXT      = 'user.json'
ADDONPATH    = _AddonInfo(__addon__,'path')
ADDONPROFILE = _AddonInfo(__addon__,'profile')
USERJSONFILE = os.path.join(ADDONPROFILE,FILEEXT)
USERJSONBASE = os.path.join(ADDONPATH,FILEEXT)


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



def ClearUserLists(favorite=False,rated=False,watchlist=False,lists=False):
	data = ReadUserDataFile()
	acc = data.get('account')
	if favorite:
		fav = acc.get('account_favorite')
		fav.update({'movies':[],'tv':[]})
	if rated:
		rat = acc.get('account_rated')
		rat.update({'movies':[],'tv':[]})
	if watchlist:
		wat = acc.get('account_watchlist')
		wat.update({'movies':[],'tv':[]})
	if lists:
		lis = acc.get('account_lists')
		lis.update({})
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
		

def UserReFreshLists(favorite=False,rated=False,watchlist=False,lists=False):
	ClearUserLists(favorite=favorite,rated=rated,watchlist=watchlist,lists=lists)
	data = ReadUserDataFile()
	session_details = data.get('access').get(__addon__).get("session_details")
	tmdbacc = Tmdb_Account(session_details.get('session_id'))
	accdet = tmdbacc.AccountDetails(writetofile=False)
	account = data.get('account')
	account_details = account.get('account_details')
	account_id = account_details.get('id')
	account_details.update(accdet)
	items = []
	if favorite:
		items.append(
			{'path':f'account/{account_id}/favorite/movies','params':account.get('account_favorite').get('movies')},
			{'path':f'account/{account_id}/favorite/tv','params':account.get('account_favorite').get('tv')})
	if rated:
		items.append(
			{'path':f'account/{account_id}/rated/movies','params':account.get('account_rated').get('movies')},
			{'path':f'account/{account_id}/rated/tv','params':account.get('account_rated').get('tv')})
	if watchlist:
		items.append(
			{'path':f'account/{account_id}/watchlist/movies','params':account.get('account_watchlist').get('movies')},
			{'path':f'account/{account_id}/watchlist/tv','params':account.get('account_watchlist').get('tv')})
	if len(items) < 0:
		for i in items: 
			_data = GetListLoop(tmdbacc.GetList,i.get('path'),1)
			for _d in _data:
				i.get('params').append(_d.get('id'))
	if lists:
		account_lists = account.get('account_lists')
		for _i in GetListLoop(tmdbacc.GetLists,f'account/{account_id}/lists',1):
			list_id = _i.get('id')
			list_data = GetListLoop(tmdbacc.GetListDetails,f'list/{list_id}',1)
			list_detail = []
			for list_item in list_data:
				item_id = list_item.get('id')
				media_type = list_item.get('media_type')
				list_detail.append({'media_type':media_type,'id':item_id})
			account_lists.update({list_id:list_detail})
	writeUserDataFile(data)	