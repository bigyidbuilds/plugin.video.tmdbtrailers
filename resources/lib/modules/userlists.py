#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

import xbmcvfs

from resources.lib._tmdb.tmdb_account import TMDB_Account 
from resources.lib.modules._xbmc import Log
from resources.lib.modules import _jsonfiles




		
def BuildUserListsCache(file,session_id,account_id,bearer):
	tmdbacc = TMDB_Account(bearer,session_id)
	cache_data = _jsonfiles.ReadJsonFile(file)
	items = [{'path':f'account/{account_id}/favorite/movies','params':cache_data.get('account_favorite').get('movie')},
			{'path':f'account/{account_id}/favorite/tv','params':cache_data.get('account_favorite').get('tv')},
			{'path':f'account/{account_id}/rated/movies','params':cache_data.get('account_rated').get('movie')},
			{'path':f'account/{account_id}/rated/tv','params':cache_data.get('account_rated').get('tv')},
			{'path':f'account/{account_id}/watchlist/movies','params':cache_data.get('account_watchlist').get('movie')},
			{'path':f'account/{account_id}/watchlist/tv','params':cache_data.get('account_watchlist').get('tv')},
			{'path':f'account/{account_id}/lists','params':cache_data.get('account_lists')}
			]
	for i in items:
		r = tmdbacc.GetListsAllItems(i.get('path'))
		i.get('params').update(**r)
	lists = cache_data.get('account_lists')
	_jsonfiles.WriteJsonFile(file,cache_data)


def ListCacheUpdate(file,session_id,account_id,bearer):
	path = f'account/{account_id}/lists'
	cache_data = _jsonfiles.ReadJsonFile(file)
	lists = cache_data.get('account_lists')
	lists.clear()
	tmdbacc = TMDB_Account(bearer,session_id)
	r = tmdbacc.GetListsAllItems(path)
	lists.update(**r)
	_jsonfiles.WriteJsonFile(file,cache_data)


def FavoriteCacheUpdate(file,session_id,account_id,bearer,media_type):
	path = None
	tmdbacc = TMDB_Account(bearer,session_id)
	cache_data = _jsonfiles.ReadJsonFile(file)
	data = cache_data.get('account_favorite').get(media_type)
	data.clear()
	if media_type == 'movie':
		path = f'account/{account_id}/favorite/movies'
	elif media_type == 'tv':
		path = f'account/{account_id}/favorite/tv'
	if path:
		r = tmdbacc.GetListsAllItems(path)
		data.update(**r)
		_jsonfiles.WriteJsonFile(file,cache_data)

def WatchlistCacheUpdate(file,session_id,account_id,bearer,media_type):
	path = None
	tmdbacc = TMDB_Account(bearer,session_id)
	cache_data = _jsonfiles.ReadJsonFile(file)
	data = cache_data.get('account_watchlist').get(media_type)
	data.clear()
	if media_type == 'movie':
		path = f'account/{account_id}/watchlist/movies'
	elif media_type == 'tv':
		path = f'account/{account_id}/watchlist/tv'
	if path:
		r = tmdbacc.GetListsAllItems(path)
		data.update(**r)
		_jsonfiles.WriteJsonFile(file,cache_data)

def RatedCacheUpdate(file,session_id,account_id,bearer,media_type):
	path = None
	tmdbacc = TMDB_Account(bearer,session_id)
	cache_data = _jsonfiles.ReadJsonFile(file)
	data = cache_data.get('account_rated').get(media_type)
	data.clear()
	if media_type == 'movie':
		path = f'account/{account_id}/rated/movies'
	elif media_type == 'tv':
		path = f'account/{account_id}/rated/tv'
	if path:
		r = tmdbacc.GetListsAllItems(path)
		data.update(**r)
		_jsonfiles.WriteJsonFile(file,cache_data)


def IsIn(file,menu,media_type,tmdb_id):
	data = _jsonfiles.ReadJsonFile(file,keys=[menu,media_type])
	if data:
		for k,v in data.items():
			results = v.get('results')
			if not results:
				continue
			else:
				for r in results:
					if r.get('id') == tmdb_id:
						return True
		else:
			return False

	else:
		return False


