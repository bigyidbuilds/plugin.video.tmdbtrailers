#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import sys
from urllib.parse import parse_qs,urlencode

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

from resources.lib.modules import _xbmc
from resources.lib.modules.utils import ValidateJsonFile,TimeStamp
from resources.lib.modules.userlists import BuildUserListsCache,IsIn
from resources.lib.modules._jsonfiles import WriteJsonFile,ReadJsonFile,ResetJsonFile
from resources.lib.modules._paths import File_Paths
from resources.lib._tmdb.tmdb import TMDB_API
from resources.lib._tmdb.tmdb_authentication import Tmdb_Authentication
from resources.lib._tmdb.tmdb_account import TMDB_Account
from resources.lib._tmdb.tmdb_utils import TMDB_ArtWorkDownloader
from resources.lib._tmdb import tmdb_registeration
from resources.lib._youtube import youtube as YT

__addon__ = 'plugin.video.tmdbtrailers'

addon_url      = sys.argv[0]
addon_handle   = int(sys.argv[1])
addon_args     = parse_qs(sys.argv[2][1:])
addon_settings = _xbmc._AddonSettings(__addon__)
CONFIGPATH = _xbmc._joinPath(_xbmc._AddonInfo(__addon__,'path'),file_name='config',file_ext='json')
FILEPATHS = File_Paths(CONFIGPATH)


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
	page = int(addon_args.get('page')[0])
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
try:
	query = addon_args.get('query')[0]
except:
	query = None
try:
	tmdbid = addon_args.get('tmdbid')[0]
except:
	tmdbid = None
try:
	listid = addon_args.get('list_id')[0]
except:
	listid = None
try:
	results = json.loads(addon_args.get('results')[0])
except:
	results = None


_xbmc.Log(f'addon_url={addon_url},\naddon_handle={addon_handle}\naddon_args={addon_args}')

'''Notes of functions
	_xbmc.ListItemBasic(label,icon=None,fanart=None,properties=None)
'''

def AddDir(query,listitem,isFolder):
	u = BuildPluginUrl(query)
	xbmcplugin.addDirectoryItem(handle=int(addon_handle),url=u,listitem=listitem,isFolder=isFolder)

def AddDirs(items,total):
	xbmcplugin.addDirectoryItems(handle=int(addon_handle), items=items, totalItems=total)

def BuildPluginUrl(query):
	return addon_url + '?' + urlencode(query)

def ContextMenu(items,mediatype,list_id,tmdb_id):
	''' 
		items supplied in list of strings

		Available context menu items:

		'favorite'
		'watchlist'
		'rate'
		'clear_list'
		'delete_list'
		'edit_list'
		'delete_listitem'
	'''
	if list_id:
		list_id = int(list_id)
	if tmdb_id:
		tmdb_id = int(tmdb_id)
	menu = []
	if 'favorite' in items:
		if IsIn(FILEPATHS.account,'account_favorite',mediatype,tmdb_id):
			pluginpath = BuildPluginUrl({'mode':'account','action':'favorite_remove','media_type':mediatype,'tmdbid':tmdb_id})
			menu.append((_xbmc._AddonLocalStr(__addon__,32037),f'RunPlugin({pluginpath})',))
		else:
			pluginpath = BuildPluginUrl({'mode':'account','action':'favorite_add','media_type':mediatype,'tmdbid':tmdb_id})
			menu.append((_xbmc._AddonLocalStr(__addon__,32036),f'RunPlugin({pluginpath})',))
	if 'watchlist' in items:
		if IsIn(FILEPATHS.account,'account_watchlist',mediatype,tmdb_id):
			pluginpath = BuildPluginUrl({'mode':'account','action':'watchlist_remove','media_type':mediatype,'tmdbid':tmdb_id})
			menu.append((_xbmc._AddonLocalStr(__addon__,32039),f'RunPlugin({pluginpath})',))
		else:
			pluginpath = BuildPluginUrl({'mode':'account','action':'watchlist_add','media_type':mediatype,'tmdbid':tmdb_id})
			menu.append((_xbmc._AddonLocalStr(__addon__,32038),f'RunPlugin({pluginpath})',))
	if 'rate' in items:
		if IsIn(FILEPATHS.account,'account_rated',mediatype,tmdb_id):
			pluginpath = BuildPluginUrl({'mode':'account','action':'unrate','media_type':mediatype,'tmdbid':tmdb_id,})
			menu.append((_xbmc._AddonLocalStr(__addon__,32041),f'RunPlugin({pluginpath})',))
		else:
			pluginpath = BuildPluginUrl({'mode':'account','action':'rate','media_type':mediatype,'tmdbid':tmdb_id,'rating':'###'})
			menu.append((_xbmc._AddonLocalStr(__addon__,32040),f'RunPlugin({pluginpath})',))
	if 'clear_list'in items:
		pluginpath = BuildPluginUrl({'mode':'account','action':'clear_list','list_id':list_id})
		menu.append((_xbmc._AddonLocalStr(__addon__,32043),f'RunPlugin({pluginpath})',))
	if 'delete_list' in items:
		pluginpath = BuildPluginUrl({'mode':'account','action':'delete_list','list_id':list_id})
		menu.append((_xbmc._AddonLocalStr(__addon__,32044),f'RunPlugin({pluginpath})',))
	if 'edit_lists' in items:
		pluginpath = BuildPluginUrl({'mode':'account','action':'edit_lists','media_type':mediatype,'tmdbid':tmdb_id})
		menu.append((_xbmc._AddonLocalStr(__addon__,32045),f'RunPlugin({pluginpath})',))
	if 'delete_listitem' in items:
		pluginpath = BuildPluginUrl({'mode':'account','action':'delete_listitem','media_type':mediatype,'tmdbid':tmdb_id,'list_id':list_id})
		menu.append((_xbmc._AddonLocalStr(__addon__,32050),f'RunPlugin({pluginpath})',))
	return menu



def GetIconPath(item):
	path,full_filename = item.split('/')
	filename,fileext = full_filename.split('.')
	return _xbmc._joinPath(_xbmc._AddonInfo(__addon__,path),folders=['resources','media'],file_name=filename,file_ext=fileext)


def GetList(callurl,next_submenu,_type,path,page,prev_submenu,media_type):
	_xbmc.Log(path)
	if page:
		newpage = int(page)+1
	tmdbapi = TMDB_API(addon_settings.getString('tmdb.api.token'))
	data = tmdbapi.GetList(callurl,page)
	if data:
		totalpages = data.get('total_pages')
		results = data.get('results')
		for r in results:
			tmdbid = r.get('id')
			_xbmc.Log(tmdbid)
			li = _xbmc.ListitemTMDBitem(r,True)
			if media_type in ['movie','tv']:
				contextitems = ContextMenu(['favorite','watchlist','rate','edit_lists'],media_type,None,tmdbid)
				li.addContextMenuItems(contextitems)
			_xbmc.Log(path)
			if path:
				fullpath = path.format(tmdbID=tmdbid)
			else:
				fullpath = path
			_xbmc.Log(path)
			AddDir({
				'submenu':next_submenu,
				'type':_type,
				'callurl':fullpath,
				'mediatype':media_type,
				'tmdbid':tmdbid
				},li,True)
		if page and newpage <= totalpages:
			li = _xbmc.ListItemBasic(f'{_xbmc._AddonLocalStr(__addon__,32014)} {newpage}/{totalpages}',fanart=_xbmc._AddonInfo(__addon__,'fanart'))
			AddDir({
				'submenu':prev_submenu,
				'type':'tmdb_api_call',
				'callurl':callurl,
				'page':newpage,
				'mediatype':media_type
				},li,True)
		xbmcplugin.endOfDirectory(addon_handle)
	else:
		return

def GetMenuItems(menuname):
	menuitems = ReadJsonFile(CONFIGPATH,keys=['menus'])
	if menuitems:
		return menuitems.get(menuname)
	else:
		return None

def GetPersonCredits(call_url):
	tmdbapi = TMDB_API(addon_settings.getString('tmdb.api.token'))
	data = tmdbapi.GetList(call_url,None)
	cast_movie = []
	cast_tv = []
	crew_movie = []
	crew_tv = []
	cast = data.get('cast')
	for c in cast:
		media_type = c.get('media_type')
		if media_type == 'movie':
			cast_movie.append(c)
		elif media_type == 'tv':
			cast_tv.append(c)
		else:
			pass
	crew = data.get('crew')
	for c in crew:
		media_type = c.get('media_type')
		if media_type == 'movie':
			crew_movie.append(c)
		elif media_type == 'tv':
			crew_tv.append(c)
	selection = []
	if len(cast_movie) > 0:
		li = (_xbmc.ListItemBasic(f'{_xbmc._AddonLocalStr(__addon__,32031)} {len(cast_movie)}',properties={'items':cast_movie}))
		selection.append((BuildPluginUrl({'results':json.dumps(cast_movie),'submenu':'personviewcredits','type':'tmdb_api_call','mediatype':'movie'}),li,True))
	if len(crew_movie) > 0:
		li = (_xbmc.ListItemBasic(f'{_xbmc._AddonLocalStr(__addon__,32032)} {len(crew_movie)}',properties={'items':crew_movie}))
		selection.append((BuildPluginUrl({'results':json.dumps(crew_movie),'submenu':'personviewcredits','type':'tmdb_api_call','mediatype':'movie'}),li,True))
	if len(cast_tv) > 0:
		li = (_xbmc.ListItemBasic(f'{_xbmc._AddonLocalStr(__addon__,32033)} {len(cast_tv)}',properties={'items':cast_tv}))
		selection.append((BuildPluginUrl({'results':json.dumps(cast_tv),'submenu':'personviewcredits','type':'tmdb_api_call','mediatype':'tv'}),li,True))
	if len(crew_tv) > 0:
		li = (_xbmc.ListItemBasic(f'{_xbmc._AddonLocalStr(__addon__,32034)} {len(crew_tv)}',properties={'items':crew_tv}))
		selection.append((BuildPluginUrl({'results':json.dumps(crew_tv),'submenu':'personviewcredits','type':'tmdb_api_call','mediatype':'tv'}),li,True))
	AddDirs(selection,len(selection))
	xbmcplugin.endOfDirectory(addon_handle)


def GetVideo(tmdbid,mediatype):
	tmdbapi = TMDB_API(addon_settings.getString('tmdb.api.token'))
	data = tmdbapi.GetVidoes(tmdbid,mediatype)
	results = data.get('results')
	content = []
	if len(results) > 0:
		for r in results:
			site = r.get('site')
			key = r.get('key')
			name = r.get('name')
			if site == 'YouTube':
				if addon_settings.getBool('youtube.general.useaddon'):
					_xbmc.Log(key)
					li = _xbmc.ListItemBasic(name,properties=r)
					content.append((BuildPluginUrl({'type':'play','submenu':'youtube_direct','callurl':f'plugin://plugin.video.youtube/play/?video_id={key}'}),li,False))
			elif site == 'Vimeo':
				pass
			else:
				_xbmc.Log(f'{site} not recognize in filter {r}')
		AddDirs(content,len(content))
		xbmcplugin.endOfDirectory(addon_handle)
	# for i in items:
	# 	if i.get('site') == "YouTube":
	# 		key = i.get('key')
	# 		if key not in videos:
	# 			videos.append(key)
	# if len(videos) >= 1:
	# 	youtubevideos = YT.YouTubeGetVideos(videos,__addon__)
	# 	if youtubevideos:
	# 		for i in youtubevideos:
	# 			yt_id = i.getProperty("id")
	# 			AddDir({'submenu':'youtube_video','callurl':yt_id,'type':'play'},i,False)
	else:
		tmdbapi = TMDB_API(addon_settings.getString('tmdb.api.token'))
		path = f'{mediatype}/{tmdbid}'
		item = tmdbapi.GetItem(path)
		ret = xbmcgui.Dialog().ok(_xbmc._AddonLocalStr(__addon__,32016), _xbmc._AddonLocalStr(__addon__,32017).format(item.get('title',item.get('name'))))
		if ret:
			xbmc.executebuiltin('Action(Back)')

def LoadFixedMenu(menu):
	items = GetMenuItems(menu)
	if items:
		for i in items:
			icon_name = i.get('icon')
			fanart_name = i.get('fanart')
			if icon_name:
				icon = GetIconPath(icon_name)
			else:
				icon = _xbmc._AddonInfo(__addon__,'icon')
			if fanart_name:
				fanart = GetIconPath(fanart_name)
			else:
				fanart = _xbmc._AddonInfo(__addon__,'fanart')
			li = _xbmc.ListItemBasic(_xbmc._AddonLocalStr(__addon__,i.get("localstr")),icon=icon,fanart=fanart,properties=i)
			AddDir(i,li,True)
		xbmcplugin.endOfDirectory(addon_handle)
	else:
		return


def MovieSearch(callurl,page,query):
	tmdbapi = TMDB_API(addon_settings.getString('tmdb.api.token'))
	data = tmdbapi.Search(query,callurl,page)
	totalpages = data.get('total_pages')
	results = data.get('results')
	newpage = page+1
	for r in results:
		li = _xbmc.ListitemTMDBitem(r,True)
		tmdbID = r.get('id')
		contextitems = ContextMenu(['favorite','watchlist','rate','edit_lists'],'movie',None,tmdbID)
		li.addContextMenuItems(contextitems)
		AddDir({
			'submenu':'getvideo',
			'type':'tmdb_api_call',
			'tmdbid':tmdbID,
			'mediatype':'movie'
			},li,True)
	if newpage <= totalpages:
		li = _xbmc.ListItemBasic(f'{_xbmc._AddonLocalStr(__addon__,32014)} {newpage}/{totalpages}')
		AddDir({
			'submenu':'search',
			'page':newpage,
			'callurl':'search/movie',
			'icon':'path/search.png',
			'mediatype':'movie',
			'query':query,
			'type':'movies'
			},li,True)
	xbmcplugin.endOfDirectory(addon_handle)


def PersonSearch(callurl,page,query):
	tmdbapi = TMDB_API(addon_settings.getString('tmdb.api.token'))
	data = tmdbapi.Search(query,callurl,page)
	totalpages = data.get('total_pages')
	results = data.get('results')
	newpage = page+1
	for r in results:
		li = _xbmc.ListitemTMDBitem(r,True)
		tmdbID = r.get('id')
		AddDir({
			"callurl":f"person/{tmdbID}/combined_credits",
			"type":"tmdb_api_call",
			"submenu":"persongetcredits"
			},li,True)
	if newpage <= totalpages:
		li = _xbmc.ListItemBasic(f'{_xbmc._AddonLocalStr(__addon__,32014)} {newpage}/{totalpages}')
		AddDir({
			'submenu':'search',
			'page':newpage,
			'callurl':'search/movie',
			'icon':'path/search.png',
			'mediatype':'person',
			'query':query,
			'type':'person'
			},li,True)
	xbmcplugin.endOfDirectory(addon_handle)

def PlayContent(callurl,submenu):
	stream = None
	if submenu == 'youtube_video':
		stream = YT.ResolveVideo(callurl,__addon__)
	if stream:
		# signin = YT.YouTubeSignIn(__addon__)
		# if signin:
		xbmcplugin.setResolvedUrl(addon_handle, True, listitem=stream)

def RequiredFiles():
	data = ReadJsonFile(CONFIGPATH)
	paths = data.get('paths')
	files = data.get('files') 
	for f in files:
		filepath  = f.get('filepath')
		filepath  = paths.get(filepath)
		filepath  = _xbmc._joinPath(filepath.get('path_base'),folders=filepath.get('path_dirs'))
		filename  = f.get('filename')
		fileext   = f.get('ext')
		base_dict = f.get('base_dict')
		exists,created = _xbmc.CheckCreateFile(filepath,filename,fileext)
		if exists and  created:
			WriteJsonFile(_xbmc._joinPath(filepath,file_name=filename,file_ext=fileext),base_dict)

		
def RequiredDirs():
	dirs = ReadJsonFile(CONFIGPATH,keys=['paths'])
	for k,v in dirs.items():
		_xbmc.CheckCreatePath(v.get('path_base'),folders=v.get('path_dirs'))

def Search(callurl,mediatype):
	if mediatype == 'movie':
		key = 'movie_search'
	elif mediatype == 'tv':
		key = 'tv_search'
	elif mediatype == 'person':
		key = 'people_search'
	data = ReadJsonFile(FILEPATHS.search)
	searches = data.get(key)
	searches  = sorted(searches, key=lambda d: d['timestamp'],reverse=True)
	searches = searches[:15]
	newsearch = _xbmc._AddonLocalStr(__addon__,32013)
	items = [_xbmc.ListItemBasic(newsearch,isfolder=False)]
	if len(searches)>=1:
		for ms in searches:
			items.append(_xbmc.ListItemBasic(ms.get('query'),isfolder=False))
		ret = xbmcgui.Dialog().select(_xbmc._AddonLocalStr(__addon__,32012), items)
		q = items[ret]
	elif len(searches)==0:
		q = items[0]
	if q.getLabel() == newsearch:
		d = xbmcgui.Dialog().input(_xbmc._AddonLocalStr(__addon__,32011),type=xbmcgui.INPUT_ALPHANUM)
		data[key].append({'query':d,'timestamp':TimeStamp()})
		WriteJsonFile(FILEPATHS.search,data)
	else:
		d = q.getLabel()
	li = _xbmc.ListItemBasic(_xbmc._AddonLocalStr(__addon__,32051).format(name=d))
	AddDir({'query':d,'mediatype':mediatype,'callurl':callurl,'page':1,'submenu':'search'},li,True)
	xbmcplugin.endOfDirectory(addon_handle)
	xbmc.executebuiltin(f'Container.Update({BuildPluginUrl({"query":d,"mediatype":mediatype,"callurl":callurl,"page":1,"submenu":"search"})})')

	

def SetAccountDetails(addonID):
	tmdbacc = TMDB_Account(addon_settings.getString('tmdb.api.token'),addon_settings.getString('tmdb.user.sessionid'))
	data = tmdbacc.AccountDetails()
	a=b=c=d=e = False
	if data:
		try:
			U_avatar = data.get('avatar').get('tmdb').get('avatar_path')
		except:
			U_avatar = ''
		a = _xbmc._AddonSetSetting(addonID,'tmdb.user.avatar',U_avatar)
		u_id = data.get('id')
		b = _xbmc._AddonSetSetting(addonID,'tmdb.user.id',u_id)
		u_lang = data.get('iso_639_1')
		c = _xbmc._AddonSetSetting(addonID,'tmdb.user.defaultlanguage',u_lang)
		u_adult = data.get('include_adult')
		d = _xbmc._AddonSetSetting(addonID,'tmdb.user.adultsearch',u_adult)
		u_name = data.get('name')
		e = _xbmc._AddonSetSetting(addonID,'tmdb.user.name',u_name)
		if a==b==c==d==e==True:
			return True
		else:
			return False
	else:
		return False


def tmdbAddList():
	lang = addon_settings.getString('tmdb.language')
	if lang == 'xbmc':
		Language = xbmc.getInfoLabel('System.Language')
	elif lang == 'tmdb':
		l = self.AddonSettings.getString('tmdb.user.defaultlanguage')
		if l != '':
			Language == l
		else:
			Language = 'en-US'
	else:
		Language = 'en-US'
	payload = {'name':None,'description':None,'language':Language}
	dialog = xbmcgui.Dialog()
	ret1 = dialog.input(_xbmc._AddonLocalStr(__addon__,32029))
	ret2 = dialog.input(_xbmc._AddonLocalStr(__addon__,32030))
	payload.update({'name':ret1,'description':ret2})
	tmdbacc = TMDB_Account(addon_settings.getString('tmdb.api.token'),addon_settings.getString('tmdb.user.sessionid'))
	tmdbacc.AddList(payload)
	xbmc.executebuiltin('Container.Refresh')


def tmdbGetList(callurl,next_submenu,_type,page,prev_submenu,prev_type,mediatype):
	account_id = addon_settings.getInt('tmdb.user.id')
	tmdbacc = TMDB_Account(addon_settings.getString('tmdb.api.token'),addon_settings.getString('tmdb.user.sessionid'))
	data = tmdbacc.GetList(callurl.format(account_id),page)
	results = data.get('results')
	totalpages = data.get('total_pages')
	newpage = page+1
	for r in results:
		tmdbID = r.get('id')
		li = _xbmc.ListitemTMDBitem(r,True)
		contextitems = ContextMenu(['favorite','watchlist','edit_lists'],mediatype,None,tmdbID)
		li.addContextMenuItems(contextitems)
		AddDir({
			'submenu':next_submenu,
			'type':_type,
			'tmdbid':tmdbID,
			'mediatype':mediatype},
			li,True)
	if page and newpage <= totalpages:
		li = _xbmc.ListItemBasic(f'{_xbmc._AddonLocalStr(__addon__,32014)} {newpage}/{totalpages}')
		AddDir({
			'submenu':prev_submenu,
			'type':prev_type,
			'callurl':callurl,
			'page':newpage,
			'mediatype':mediatype},
			li,True)
	xbmcplugin.endOfDirectory(addon_handle)


def tmdbGetListDetails(callurl,page):
	tmdbapi = TMDB_API(addon_settings.getString('tmdb.api.token'))
	data = tmdbapi.GetList(callurl,page)
	items = data.get('items')
	list_id = data.get('id')
	totalpages = data.get('total_pages')
	newpage = page+1
	for i in items:
		li = _xbmc.ListitemTMDBitem(i,True)
		tmdbID = i.get('id')
		media_type = i.get('media_type')
		contextitems = ContextMenu(['delete_listitem'],media_type,list_id,None)
		li.addContextMenuItems(contextitems)
		AddDir({'submenu':'getvideo','type':'tmdb_api_call','tmdbid':tmdbID,'mediatype':media_type},li,True)
	if page and newpage <= totalpages:
		li = _xbmc.ListItemBasic(f'{_xbmc._AddonLocalStr(__addon__,32014)} {newpage}/{totalpages}')
		AddDir({'submenu':'usertmdb','type':'tmdbgetlistdetails','page':newpage,'callurl':callurl},li,True)
	xbmcplugin.endOfDirectory(addon_handle)


def tmdbGetLists(callurl,page,path):
	account_id = addon_settings.getInt('tmdb.user.id')
	session_id = addon_settings.getString('tmdb.user.sessionid')
	bearer = addon_settings.getString('tmdb.api.token')
	callurl = callurl.format(account_id)
	tmdbacc = TMDB_Account(bearer,session_id)
	data = tmdbacc.GetList(callurl,page)
	results = data.get('results')
	totalpages = data.get('total_pages')
	newpage = page+1
	li = _xbmc.ListItemBasic(_xbmc._AddonLocalStr(__addon__,32028))
	AddDir({'submenu':'usertmdb','type':'addlist'},li,False)
	for r in results:
		li = _xbmc.ListItemTMDBList(r,True)
		list_id = r.get('id')
		contextitems = ContextMenu(['clear_list','delete_list'],None,list_id,None)
		li.addContextMenuItems(contextitems)
		AddDir({'submenu':'usertmdb','type':'tmdbgetlistdetails','callurl':path.format(list_id=list_id),'listid':list_id},li,True)
	if page and newpage <= totalpages:
		li = _xbmc.ListItemBasic(f'{_xbmc._AddonLocalStr(__addon__,32014)} {newpage}/{totalpages}')
		AddDir({'submenu':'usertmdb','type':'tmdbGetList','page':newpage,'callurl':callurl},li,True)
	xbmcplugin.endOfDirectory(addon_handle)


def tmdbMenu():
	items = []
	session_id = addon_settings.getString('tmdb.user.sessionid')
	_xbmc.Log(session_id)
	if not session_id:
		li = _xbmc.ListItemBasic(_xbmc._AddonLocalStr(__addon__,32019),icon=None,fanart=None,properties={'submenu':'usertmdb','type':'signin'})
		items.append((BuildPluginUrl({'submenu':'usertmdb','type':'signin'}),li,False))
	else:
		li = _xbmc.ListItemBasic(_xbmc._AddonLocalStr(__addon__,32020),icon=None,fanart=None,properties={'submenu':'usertmdb','type':'signout'})
		items.append((BuildPluginUrl({'submenu':'usertmdb','type':'signout'}),li,False))
		_items = GetMenuItems('usertmdb')
		for i in _items:
			icon_name = i.get('icon')
			fanart_name = i.get('fanart')
			if icon_name:
				icon = GetIconPath(icon_name)
			else:
				icon = _xbmc._AddonInfo(__addon__,'icon')
			if fanart_name:
				fanart = GetIconPath(fanart_name)
			else:
				fanart = _xbmc._AddonInfo(__addon__,'fanart')
			li = _xbmc.ListItemBasic(_xbmc._AddonLocalStr(__addon__,i.get("localstr")),icon=icon,fanart=fanart,properties=i)
			items.append((BuildPluginUrl(i),li,True))
	AddDirs(items,len(items))
	xbmcplugin.endOfDirectory(addon_handle)






def tmdbSignIn():
	tmdbauth = Tmdb_Authentication(addon_settings.getString('tmdb.api.token'))
	session_id = tmdbauth.SignIn(addon_settings.getString('tmdb.api.username'),addon_settings.getString('tmdb.api.password'))
	updated = _xbmc._AddonSetSetting(__addon__,'tmdb.user.sessionid',session_id)
	if updated:
		_updated = SetAccountDetails(__addon__)
		if _updated:
			_xbmc.Log('Sign in complete and all settings set')
			xbmc.executebuiltin('Container.Refresh')
		else:
			return
	else:
		return
	

def tmdbSignOut():
	tmdbauth = Tmdb_Authentication(addon_settings.getString('tmdb.api.token'))
	tmdbauth.SignOut(addon_settings.getString('tmdb.user.sessionid'))
	_xbmc._AddonSetSetting(__addon__,'tmdb.user.sessionid','')
	xbmc.executebuiltin('Container.Refresh')



def tmdbuserCreditianls():
	uj = ReadJsonFile(_xbmc._AddonInfo(__addon__,'profile'),'user.json')
	session_details = uj.get('access').get(__addon__).get('session_details')
	account = uj.get('account')
	account_id = account.get('id')
	session_id = session_details.get('session_id')
	return account_id,session_id

def tmdbUserRefresh():
	SetAccountDetails(__addon__)
	TMDB_ArtWorkDownloader(addon_settings.getString('tmdb.user.avatar'),_xbmc._joinPath(_xbmc._AddonInfo(__addon__,'profile'),folders=['resources','media'],file_name='mytmdb',file_ext='png'))
	files = ReadJsonFile(CONFIGPATH,keys=['files'])
	file = list(filter(lambda d: d['filename'] == 'account', files))[0]
	ResetJsonFile(FILEPATHS.account,file.get('base_dict'))
	BuildUserListsCache(FILEPATHS.account,addon_settings.getString('tmdb.user.sessionid'),addon_settings.getInt('tmdb.user.id'),addon_settings.getString('tmdb.api.token'))
	xbmc.executebuiltin('Container.Refresh')


def TvSearch(callurl,page,query):
	tmdbapi = TMDB_API(addon_settings.getString('tmdb.api.token'))
	data = tmdbapi.Search(query,callurl,page)
	totalpages = data.get('total_pages')
	results = data.get('results')
	newpage = page+1
	for r in results:
		tmdbID = r.get('id')
		li = _xbmc.ListitemTMDBitem(r,True)
		contextitems = ContextMenu(['favorite','watchlist','rate','edit_lists'],'tv',None,tmdbID)
		li.addContextMenuItems(contextitems)
		AddDir({
			'submenu':'getvideo',
			'type':'tmdb_api_call',
			'tmdbid':tmdbID,
			'mediatype':'tv'
			},li,True)
	if newpage <= totalpages:
		li = _xbmc.ListItemBasic(f'{_xbmc._AddonLocalStr(__addon__,32014)} {newpage}/{totalpages}')
		AddDir({
			'submenu':'search',
			'page':newpage,
			'query':query,
			'callurl':'search/tv',
			'type':'tv',
			'mediatype':'tv'
			},li,True)
	xbmcplugin.endOfDirectory(addon_handle)


def ViewPersonCredits(results):
	if results:
		for r in results:
			media_type = r.get('media_type')
			tmdbID = r.get('id')
			li = _xbmc.ListitemTMDBitem(r,True)
			contextitems = ContextMenu(['favorite','watchlist','rate','edit_lists'],media_type,None,tmdbID)
			li.addContextMenuItems(contextitems)
			AddDir({'submenu':'getvideo','type':'tmdb_api_call','tmdbid':tmdbID,'mediatype':media_type},li,True)
		xbmcplugin.endOfDirectory(addon_handle)
	else:
		xbmc.executebuiltin('Action(Back)')



YT.YouTubeRegistration(addon_id=__addon__,api_key=addon_settings.getString("youtube.api.key"),client_id=addon_settings.getString("youtube.api.clientid"),client_secret=addon_settings.getString("youtube.api.clientsecret"))

if mode == 'addon':
	if submenu == None:
		RequiredDirs()
		RequiredFiles()
		if addon_settings.getBool('tmdb.account.refresh') and addon_settings.getString('tmdb.user.sessionid') != None:
			tmdbUserRefresh()
		_xbmc.Log('Loading Home page')
		LoadFixedMenu("main")
	elif submenu and menutype == "fixed":
		LoadFixedMenu(submenu)
	elif submenu and menutype == "tmdb_api_call":
		if submenu == "moviegetlist":
			GetList(callurl,'getvideo',menutype,None,page,submenu,mediatype)
		elif submenu == "getvideo":
			GetVideo(tmdbid,mediatype)
		elif submenu == "tvgetlist":
			GetList(callurl,'getvideo',menutype,None,page,submenu,mediatype)
		elif submenu == "persongetlist":
			GetList(callurl,'persongetcredits',menutype,'person/{tmdbID}/combined_credits',page,submenu,mediatype)
		elif submenu == 'persongetcredits':
			GetPersonCredits(callurl)
		elif submenu == 'personviewcredits':
			ViewPersonCredits(results)
	elif menutype == "play":
		if submenu == 'youtube_direct':
			xbmc.executebuiltin(f'RunPlugin({callurl})')
	elif submenu == "search":
		if query:
			if mediatype == 'movie':
				MovieSearch(callurl,page,query)
			elif mediatype == 'tv':
				TvSearch(callurl,page,query)
			elif mediatype == 'person':
				PersonSearch(callurl,page,query)
		else:
			Search(callurl,mediatype)
	elif submenu == "usertmdb":
		if menutype == 'main':
			tmdbMenu()
		elif menutype == 'signin':
			tmdbSignIn()
		elif menutype == 'signout':
			tmdbSignOut()
		elif menutype == 'tmdbmoviegetlist':
			tmdbGetList(callurl,'getvideo',"tmdb_api_call",page,submenu,menutype,mediatype)
		elif menutype == 'tmdbtvgetlist':
			tmdbGetList(callurl,'getvideo',"tmdb_api_call",page,submenu,menutype,mediatype)
		elif menutype == 'tmdbgetlists':
			tmdbGetLists(callurl,page,'list/{list_id}')
		elif menutype == 'tmdbgetlistdetails':
			tmdbGetListDetails(callurl,page)
		elif menutype == 'addlist':
			tmdbAddList()
elif mode == 'account':
	from resources.lib.runpluginmethods.account import Account
	acc = Account(sys.argv)
	if acc:
		acc.RunPluginMethod()





