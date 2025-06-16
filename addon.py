#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import os
import sys
from urllib.parse import parse_qs,urlencode

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

from resources.lib.modules.utils import Log,ReadJsonFile,ValidateJsonFile,CheckCreateFile,WriteJsonFile,TimeStamp
from resources.lib.modules.userjson import UserDataFile,CheckUserAccount,ReadUserDataFile,ClearUserLists,writeUserDataFile,UserReFreshLists
from resources.lib.modules._xbmcaddon import _AddonInfo,_AddonLocalStr,_AddonSettings
from resources.lib.modules._xbmcgui import ListItemBasic,ListitemTMDBitem
from resources.lib.modules._tmdb.tmdb import TMDB_API
from resources.lib.modules._tmdb.tmdb_authentication import Tmdb_Authentication
from resources.lib.modules._tmdb.tmdb_account import Tmdb_Account
from resources.lib.modules._tmdb import tmdb_registeration
from resources.lib.modules._youtube import youtube as YT

__addon__ = 'plugin.video.tmdbtrailers'

addon_url      = sys.argv[0]
addon_handle   = int(sys.argv[1])
addon_args     = parse_qs(sys.argv[2][1:])
addon_settings = _AddonSettings(__addon__)

try:
	submenu  = addon_args.get('submenu')[0]
except:
	submenu  = None
try:
	menutype = addon_args.get('type')[0]
except:
	menutype = None
try:
	callurl  = addon_args.get('callurl')[0]
except:
	callurl  = None
try:
	page = addon_args.get('page')[0]
except:
	page = 1
try:
	mediatype = addon_args.get('mediatype')[0]
except:
	mediatype = None
try:
	mode = addon_args.get('mode')[0]
except:
	mode = 'addon'




Log(f'addon_url={addon_url},\naddon_handle={addon_handle}\naddon_args={addon_args}')

'''Notes of functions
	ListItemBasic(label,icon=None,fanart=None,properties=None)
'''
def GetIconPath(filename):
	return os.path.join(_AddonInfo(__addon__,'path'),'resources','media',filename)

def GetMenuItems(menuname):
	menuitems = ReadJsonFile(_AddonInfo(__addon__,'path'),'menus.json',key="menus")
	if menuitems:
		return menuitems.get(menuname)
	else:
		return None


def AddDir(query,listitem,isFolder):
	u = BuildPluginUrl(query)
	xbmcplugin.addDirectoryItem(handle=int(addon_handle),url=u,listitem=listitem,isFolder=isFolder)

def AddDirs(items,total):
	xbmcplugin.addDirectoryItems(handle=int(addon_handle), items=items, totalItems=total)


def LoadFixedMenu(menu):
	items = GetMenuItems(menu)
	Log(items)
	if items:
		for i in items:
			li = ListItemBasic(_AddonLocalStr(__addon__,i.get("localstr")),icon=GetIconPath(i.get('icon')),properties=i)
			AddDir(i,li,True)
	else:
		return

def GetList(callurl,next_submenu,_type,path,page,prev_submenu):
	if page:
		newpage = int(page)+1
	tmdbapi = TMDB_API(addon_settings.getString('tmdb.api.token'))
	# items,apipage,totalpages = tmdbapi.GetList(callurl,page)
	data = tmdbapi.GetList(callurl,page)
	totalpages = data.get('total_pages')
	results = data.get('results')
	for r in results:
		li = ListitemTMDBitem(r,True)
		media_type = callurl.split('/')[0]
		AddDir({'submenu':next_submenu,'type':_type,'callurl':path.format(tmdbID=r.get('id')),'mediatype':media_type},li,True)
	if page and newpage <= totalpages:
		li = ListItemBasic(f'{_AddonLocalStr(__addon__,32014)} {newpage}/{totalpages}')
		AddDir({'submenu':prev_submenu,'type':'tmdb_api_call','callurl':callurl,'page':newpage},li,True)

def GetPersonCredits(call_url):
	tmdbapi = TMDB_API(addon_settings.getString('tmdb.api.token'))
	items,apipage,totalpages = tmdbapi.GetList(call_url,None)
	for i in items:
		vi = i.getVideoInfoTag()
		tmdbID = vi.getUniqueID('tmdb')
		properties = json.loads(i.getProperty('properties'))
		media_type = properties.get('media_type')
		if media_type == 'movie':
			AddDir({'submenu':'moviegetvideo','type':'tmdb_api_call','callurl':f'movie/{tmdbID}/videos'},i,True)
		elif media_type == 'tv':
			AddDir({'submenu':'tvgetvideo','type':'tmdb_api_call','callurl':f'tv/{tmdbID}/videos'},i,True)


def GetVideo(callurl):
	videos = []
	tmdbapi = TMDB_API(addon_settings.getString('tmdb.api.token'))
	items = tmdbapi.GetVidoes(callurl,listitems=False)
	for i in items:
		if i.get('site') == "YouTube":
			key = i.get('key')
			if key not in videos:
				videos.append(key)
	if len(videos) >= 1:
		youtubevideos = YT.YouTubeGetVideos(videos,__addon__)
		if youtubevideos:
			for i in youtubevideos:
				yt_id = i.getProperty("id")
				AddDir({'submenu':'youtube_video','callurl':yt_id,'type':'play'},i,False)
	else:
		path = callurl.split('/')
		path = '/'.join(path[:2])
		tmdbapi = TMDB_API(addon_settings.getString('tmdb.api.token'))
		item = tmdbapi.GetItem(path,listitems=False)
		ret = xbmcgui.Dialog().ok(_AddonLocalStr(__addon__,32016), _AddonLocalStr(__addon__,32017).format(item.get('title',item.get('name'))))
		if ret:
			xbmc.executebuiltin('Action(Back)')



def MovieSearch(callurl):
	query = Search(_AddonInfo(__addon__,'profile'),'user.json','movie_search')
	tmdbapi = TMDB_API(addon_settings.getString('tmdb.api.token'))
	items = tmdbapi.Search(query,callurl)
	for i in items:
		vi = i.getVideoInfoTag()
		tmdbID = vi.getUniqueID('tmdb')
		AddDir({'submenu':'moviegetvideo','type':'tmdb_api_call','callurl':f'movie/{tmdbID}/videos'},i,True)

def TvSearch(callurl):
	query = Search(_AddonInfo(__addon__,'profile'),'user.json','tv_search')
	tmdbapi = TMDB_API(addon_settings.getString('tmdb.api.token'))
	items = tmdbapi.Search(query,callurl)
	for i in items:
		vi = i.getVideoInfoTag()
		tmdbID = vi.getUniqueID('tmdb')
		AddDir({'submenu':'tvgetvideo','type':'tmdb_api_call','callurl':f'tv/{tmdbID}/videos'},i,True)

def Search(filepath,filename,key):
	data = ReadJsonFile(filepath,filename)
	searches = data.get(key)
	searches  = sorted(searches, key=lambda d: d['timestamp'],reverse=True)
	searches = searches[:15]
	newsearch = _AddonLocalStr(__addon__,32013)
	items = [xbmcgui.ListItem(newsearch)]
	if len(searches)>=1:
		for ms in searches:
			items.append(xbmcgui.ListItem(ms.get('query')))
		ret = xbmcgui.Dialog().select(_AddonLocalStr(__addon__,32012), items)
		q = items[ret]
	elif len(searches)==0:
		q = items[0]
	if q.getLabel() == newsearch:
		d = xbmcgui.Dialog().input(_AddonLocalStr(__addon__,32011),type=xbmcgui.INPUT_ALPHANUM)
		data[key].append({'query':d,'timestamp':TimeStamp()})
		WriteJsonFile(filepath,filename,data)
	else:
		d = q.getLabel()
	return d


def PlayContent(callurl,submenu):
	stream = None
	if submenu == 'youtube_video':
		stream = YT.ResolveVideo(callurl,__addon__)
	if stream:
		# signin = YT.YouTubeSignIn(__addon__)
		# if signin:
		xbmcplugin.setResolvedUrl(addon_handle, True, listitem=stream)

def tmdbMenu():
	items = []
	# data = ReadJsonFile(_AddonInfo(__addon__,'profile'),'user.json',key="access")
	session_id = addon_settings.getString('tmdb.user.sessionid')
	Log(session_id)
	# session_details = data.get(__addon__).get("session_details")
	# signedin = session_details.get('inuse')
	if not session_id:
		li = ListItemBasic(_AddonLocalStr(__addon__,32019),icon=None,fanart=None,properties={'submenu':'usertmdb','type':'signin'})
		items.append((BuildPluginUrl({'submenu':'usertmdb','type':'signin'}),li,False))
	else:
		li = ListItemBasic(_AddonLocalStr(__addon__,32020),icon=None,fanart=None,properties={'submenu':'usertmdb','type':'signout'})
		items.append((BuildPluginUrl({'submenu':'usertmdb','type':'signout'}),li,False))
		_items = GetMenuItems('usertmdb')
		for i in _items:
			li = ListItemBasic(_AddonLocalStr(__addon__,i.get("localstr")),icon=GetIconPath(i.get('icon')),properties=i)
			items.append((BuildPluginUrl(i),li,True))
	AddDirs(items,len(items))

def tmdbSignIn():
	tmdbauth = Tmdb_Authentication()
	session_id = tmdbauth.SignIn()
	# updated = addon_settings.setString('tmdb.user.sessionid', session_id)
	updated = xbmcaddon.Addon(__addon__).setSettingString('tmdb.user.sessionid', session_id)
	Log(updated)
	# UserReFreshLists(favorite=True,rated=True,watchlist=True,lists=True)
	xbmc.executebuiltin('Container.Refresh')
	

def tmdbSignOut():
	tmdbauth = Tmdb_Authentication()
	tmdbauth.SignOut()
	xbmc.executebuiltin('Container.Refresh')

def tmdbGetList(callurl,next_submenu,_type,path,page,prev_submenu,prev_type):
	account_id,session_id = tmdbuserCreditianls()
	callurl = callurl.format(account_id)
	tmdbacc = Tmdb_Account(session_id)
	items,apipage,totalpages = tmdbacc.GetList(callurl,page)
	newpage = page+1
	for i in items:
		vi = i.getVideoInfoTag()
		tmdbID = vi.getUniqueID('tmdb')
		AddDir({'submenu':next_submenu,'type':_type,'callurl':path.format(tmdbID=tmdbID)},i,True)
	if page and newpage <= totalpages:
		li = ListItemBasic(f'{_AddonLocalStr(__addon__,32014)} {newpage}/{totalpages}')
		AddDir({'submenu':prev_submenu,'type':prev_type,'callurl':callurl,'page':newpage},li,True)

def tmdbGetLists(callurl,page,path):
	account_id,session_id = tmdbuserCreditianls()
	callurl = callurl.format(account_id)
	tmdbacc = Tmdb_Account(session_id)
	items,apipage,totalpages = tmdbacc.GetLists(callurl,page)
	newpage = page+1
	li = ListItemBasic(_AddonLocalStr(__addon__,32028))
	AddDir({'submenu':'usertmdb','type':'addlist'},li,False)
	for i in items:
		properties = json.loads(i.getProperty('properties'))
		list_id = properties.get('id')
		AddDir({'submenu':'usertmdb','type':'tmdbgetlistdetails','callurl':path.format(list_id=list_id)},i,True)
	if page and newpage <= totalpages:
		li = ListItemBasic(f'{_AddonLocalStr(__addon__,32014)} {newpage}/{totalpages}')
		AddDir({'submenu':'usertmdb','type':'tmdbGetList','page':newpage,'callurl':callurl},li,True)	

def tmdbGetListDetails(callurl,page):
	account_id,session_id = tmdbuserCreditianls()
	tmdbacc = Tmdb_Account(session_id)
	items,apipage,totalpages = tmdbacc.GetListDetails(callurl,page)
	newpage = page+1
	for i in items:
		vi = i.getVideoInfoTag()
		tmdbID = vi.getUniqueID('tmdb')
		properties = json.loads(i.getProperty('properties'))
		media_type = properties.get('media_type')
		if media_type == 'movie':
			AddDir({'submenu':'moviegetvideo','type':'tmdb_api_call','callurl':f'movie/{tmdbID}/videos'},i,True)
		elif media_type == 'tv':
			AddDir({'submenu':'tvgetvideo','type':'tmdb_api_call','callurl':f'tv/{tmdbID}/videos'},i,True)
	if page and newpage <= totalpages:
		li = ListItemBasic(f'{_AddonLocalStr(__addon__,32014)} {newpage}/{totalpages}')
		AddDir({'submenu':'usertmdb','type':'tmdbgetlistdetails','page':newpage,'callurl':callurl},li,True)

def tmdbAddList():
	payload = {'name':None,'description':None,'language':xbmc.getInfoLabel('System.Language')}
	dialog = xbmcgui.Dialog()
	ret1 = dialog.input(_AddonLocalStr(__addon__,32029))
	ret2 = dialog.input(_AddonLocalStr(__addon__,32030))
	payload.update({'name':ret1,'description':ret2})
	account_id,session_id = tmdbuserCreditianls()
	tmdbacc = Tmdb_Account(session_id)
	tmdbacc.AddList(payload)
	xbmc.executebuiltin('Container.Refresh')


def tmdbuserCreditianls():
	uj = ReadJsonFile(_AddonInfo(__addon__,'profile'),'user.json')
	session_details = uj.get('access').get(__addon__).get('session_details')
	account = uj.get('account')
	account_id = account.get('id')
	session_id = session_details.get('session_id')
	return account_id,session_id


def BuildPluginUrl(query):
	return addon_url + '?' + urlencode(query)


YT.YouTubeRegistration(addon_id=__addon__,api_key=addon_settings.getString("youtube.api.key"),client_id=addon_settings.getString("youtube.api.clientid"),client_secret=addon_settings.getString("youtube.api.clientsecret"))

if mode == 'addon':
	if submenu == None:
		UserDataFile()
		# tmdb_registeration.RegistrateAPIKey(_AddonInfo(__addon__,'profile'),'user.json',__addon__,addon_settings.getString('tmdb.api.key'),addon_settings.getString('tmdb.api.token'))
		# if addon_settings.getBool('tmdb.lists.refresh'):
		# 	UserReFreshLists(favorite=True,rated=True,watchlist=True,lists=True)
		Log('Loading Home page')
		LoadFixedMenu("main")
	elif submenu and menutype == "fixed":
		LoadFixedMenu(submenu)
	elif submenu and menutype == "tmdb_api_call":
		if submenu == "moviegetlist":
			GetList(callurl,'moviegetvideo',menutype,'movie/{tmdbID}/videos',page,submenu)
		elif submenu == "moviegetvideo":
			GetVideo(callurl)
		elif submenu == "tvgetlist":
			GetList(callurl,'tvgetvideo',menutype,'tv/{tmdbID}/videos',page,submenu)
		elif submenu == "tvgetvideo":
			GetVideo(callurl)
		elif submenu == "persongetlist":
			GetList(callurl,'persongetcredits',menutype,'person/{tmdbID}/combined_credits',page,submenu)
		elif submenu == 'persongetcredits':
			GetPersonCredits(callurl)
	elif menutype == "play":
		PlayContent(callurl,submenu)
	elif submenu == "search":
		if menutype == 'movies':
			MovieSearch(callurl)
		elif menutype == 'tv':
			TvSearch(callurl)
	elif submenu == "usertmdb":
		if menutype == 'main':
			tmdbMenu()
		elif menutype == 'signin':
			tmdbSignIn()
		elif menutype == 'signout':
			tmdbSignOut()
		elif menutype == 'tmdbmoviegetlist':
			tmdbGetList(callurl,'moviegetvideo',"tmdb_api_call",'movie/{tmdbID}/videos',page,submenu,menutype)
		elif menutype == 'tmdbtvgetlist':
			tmdbGetList(callurl,'tvgetvideo',"tmdb_api_call",'tv/{tmdbID}/videos',page,submenu,menutype)
		elif menutype == 'tmdbgetlists':
			tmdbGetLists(callurl,page,'list/{list_id}')
		elif menutype == 'tmdbgetlistdetails':
			Log(type(page))
			tmdbGetListDetails(callurl,page)
		elif menutype == 'addlist':
			tmdbAddList(callurl,page)




xbmcplugin.endOfDirectory(addon_handle)
