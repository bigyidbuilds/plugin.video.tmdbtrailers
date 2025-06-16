#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
from urllib.parse import urlunparse

import xbmcgui


def ListItemBasic(label,label2=None,icon=None,fanart=None,properties=None,isfolder=True):
	li = xbmcgui.ListItem(label)
	if label2:
		li.setLabel2(label2)
	artwork = {'icon':icon,'fanart':fanart,'thumb':icon}
	artwork = {k:v for k,v in artwork.items() if v is not None}
	li.setArt(artwork)
	if properties:
		li.setProperty('Properties',json.dumps(properties))
	li.setIsFolder(isfolder)
	return li 


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