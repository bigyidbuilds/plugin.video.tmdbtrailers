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
from resources.lib.modules.utils import TimeStamp
from resources.lib.modules.userlists import BuildUserListsCache,IsIn
from resources.lib.modules._jsonfiles import WriteJsonFile,ReadJsonFile,ResetJsonFile
from resources.lib.modules._paths import File_Paths
from resources.lib._tmdb.tmdb import TMDB_API
from resources.lib._tmdb.tmdb_authentication import Tmdb_Authentication
from resources.lib._tmdb.tmdb_account import TMDB_Account
from resources.lib._tmdb.tmdb_utils import TMDB_ArtWorkDownloader
from resources.lib._tmdb.tmdb_token import TOKEN
from resources.lib._tmdb import tmdb_registeration
from resources.lib._youtube.youtube_api import YouTubeAPI 

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

def AddCollection():
	menu_data = ReadJsonFile(FILEPATHS.usermenus)
	menus = menu_data.get('menus')
	collections = menus.get('collections')
	query =  xbmcgui.Dialog().input(_xbmc._AddonLocalStr(__addon__,32011),type=xbmcgui.INPUT_ALPHANUM)
	tmdbapi = TMDB_API(addon_settings.getString('tmdb.api.token'))
	data = tmdbapi.SearchCollectionsAll(query)
	results = data.get('results')
	items = []
	for r in results:
		items.append(_xbmc.ListitemTMDBCollection(r,False))
	dialog = xbmcgui.Dialog()
	ret = dialog.multiselect(_xbmc._AddonLocalStr(__addon__,32060),items,useDetails=True)
	if ret:
		for r in ret:
			li = items[r]
			collection_data = json.loads(li.getProperty('properties'))
			collections.append(collection_data)
		WriteJsonFile(FILEPATHS.usermenus,menu_data)
		xbmc.executebuiltin('Container.Refresh')


def AddCompany():
	tmdbapi = TMDB_API(addon_settings.getString('tmdb.api.token'))
	country_data = tmdbapi.ConfigCountry()
	menu_data = ReadJsonFile(FILEPATHS.usermenus)
	menus = menu_data.get('menus')
	company = menus.get('company')
	dialog = xbmcgui.Dialog()
	query =  dialog.input(_xbmc._AddonLocalStr(__addon__,32011),type=xbmcgui.INPUT_ALPHANUM)
	data = tmdbapi.SearchCompanyAll(query)
	results = data.get('results')
	items = []
	if len(results)>0:
		for r in results:
			name = r.get('name')
			origin_country = r.get('origin_country')
			matched_dict=list(filter(lambda country_data:country_data['iso_3166_1']==origin_country,country_data))
			_xbmc.Log(matched_dict)
			if len(matched_dict)>0:
				native_name = matched_dict[0].get('native_name')
				r.update({'name':f'{name}({native_name})'})
			items.append(_xbmc.ListItemTMDBCompany(r,False))
		ret = dialog.multiselect(_xbmc._AddonLocalStr(__addon__,32065),items,useDetails=True)
		if ret:
			for _r in ret:
				li = items[_r]
				company_data = json.loads(li.getProperty('properties'))
				company.append(company_data)
			WriteJsonFile(FILEPATHS.usermenus,menu_data)
			xbmc.executebuiltin('Container.Refresh')
	else:
		dialog.notification(_xbmc._AddonInfo(__addon__,'name'),_xbmc._AddonLocalStr(__addon__,32067),_xbmc._AddonInfo(__addon__,'icon'))


def AddGenres(mediatype):
	items = []
	menu_data = ReadJsonFile(FILEPATHS.usermenus)
	menus = menu_data.get('menus')
	genres = menus.get('genres').get(mediatype)
	tmdbapi = TMDB_API(addon_settings.getString('tmdb.api.token'))
	data = tmdbapi.GetGenres(mediatype)
	tmdb_genres = data.get('genres')
	if mediatype == 'movie':
		icon = 'path/movie.png'
	elif mediatype == 'tv':
		icon = 'path/tvshow.png'
	else:
		icon = 'path/icon.png'
	for g in tmdb_genres:
		if g not in genres:
			items.append(_xbmc.ListItemBasic(g.get('name'),properties=g))
	dialog = xbmcgui.Dialog()
	ret = dialog.multiselect(_xbmc._AddonLocalStr(__addon__,32055),items)
	for r in ret:
		li = items[r]
		genre_data = json.loads(li.getProperty('properties'))
		genre_data.update({'icon':icon,'mediatype':mediatype,'type':'genres'})
		genres.append(genre_data)
	WriteJsonFile(FILEPATHS.usermenus,menu_data)
	xbmc.executebuiltin('Container.Refresh')


def BuildPluginUrl(query):
	return addon_url + '?' + urlencode(query)

def CollectionsContent(tmdbid):
	tmdbapi = TMDB_API(addon_settings.getString('tmdb.api.token'))
	data = tmdbapi.CollectionItems(tmdbid)
	parts = data.get('parts')
	for p in parts:
		media_type = p.get('media_type')
		tmdbid = p.get('id')
		li = _xbmc.ListitemTMDBitem(p,True)
		contextitems = ContextMenu(['favorite','watchlist','rate','edit_lists'],media_type,None,tmdbid)
		li.addContextMenuItems(contextitems)
		AddDir({
			'submenu':'getvideo',
			'type':'tmdb_api_call',
			'tmdbid':tmdbid,
			'mediatype':media_type},
			li,True)
	xbmcplugin.endOfDirectory(addon_handle)

def CollectionsLists():
	content = [(BuildPluginUrl({'type':'collections','submenu':'addcolletion'}),_xbmc.ListItemBasic(_xbmc._AddonLocalStr(__addon__,32058),icon=GetIconPath('path/add.png'),fanart=_xbmc._AddonInfo(__addon__,'fanart')))]
	menu_data = ReadJsonFile(FILEPATHS.usermenus)
	menus = menu_data.get('menus')
	collections = menus.get('collections')
	if len(collections)>0:
		content.append((BuildPluginUrl({'type':'collections','submenu':'removecollection'}),_xbmc.ListItemBasic(_xbmc._AddonLocalStr(__addon__,32059),icon=GetIconPath('path/remove.png'),fanart=_xbmc._AddonInfo(__addon__,'fanart'))))
		for c in collections:
			li = _xbmc.ListitemTMDBCollection(c,True)
			content.append((BuildPluginUrl({
				'type':'collections',
				'submenu':'collectioncontent',
				'tmdbid':c.get('id')}),
				li,True))
	AddDirs(content,len(content))
	xbmcplugin.endOfDirectory(addon_handle)

def CompanyContent(company_id,page,mediatype):
	if page == 1 and mediatype == None:
		items = [_xbmc.ListItemBasic(_xbmc._AddonLocalStr(__addon__,32000),icon=GetIconPath('path/movie.png'),properties={'mediatype':'movie'},isfolder=False),_xbmc.ListItemBasic(_xbmc._AddonLocalStr(__addon__,32001),icon=GetIconPath('path/tvshow.png'),properties={'mediatype':'tv'},isfolder=False)]
		dialog = xbmcgui.Dialog()
		ret = dialog.select(_xbmc._AddonLocalStr(__addon__,32068),items,useDetails=True)
		_xbmc.Log(ret)
		if ret >= 0:
			mediatype = json.loads(items[ret].getProperty('properties')).get('mediatype')
		else:
			return
	_xbmc.Log(mediatype)
	tmdbapi = TMDB_API(addon_settings.getString('tmdb.api.token'))
	if mediatype == 'movie':
		data = tmdbapi.DiscoverMovies(page,params={'with_companies':company_id})
	elif mediatype == 'tv':
		data = tmdbapi.DiscoverTv(page,params={'with_companies':company_id})
	else:
		return
	newpage = int(page) + 1
	if data:
		totalpages = data.get('total_pages')
		results = data.get('results')
		for r in results:
			tmdbid = r.get('id')
			li = _xbmc.ListitemTMDBitem(r,True)
			contextitems = ContextMenu(['favorite','watchlist','rate','edit_lists'],mediatype,None,tmdbid)
			li.addContextMenuItems(contextitems)
			AddDir({
				'submenu':'getvideo',
				'type':'tmdb_api_call',
				'tmdbid':tmdbid,
				'mediatype':mediatype},
				li,True)
		if newpage <= totalpages:
			li = _xbmc.ListItemBasic(f'{_xbmc._AddonLocalStr(__addon__,32014)} {newpage}/{totalpages}',icon=GetIconPath('path/nextpage.png'),fanart=_xbmc._AddonInfo(__addon__,'fanart'))
			AddDir({
				'type':'company',
				'submenu':'companycontent',
				'mediatype':mediatype,
				'tmdbid':company_id,
				'page':newpage
				},li,True)
		xbmcplugin.endOfDirectory(addon_handle)
	else:
		return

def CompanyLists():
	content = [(BuildPluginUrl({'type':'company','submenu':'addcompany'}),_xbmc.ListItemBasic(_xbmc._AddonLocalStr(__addon__,32065),icon=GetIconPath('path/add.png'),fanart=_xbmc._AddonInfo(__addon__,'fanart')))]
	menu_data = ReadJsonFile(FILEPATHS.usermenus)
	menus = menu_data.get('menus')
	company = menus.get('company')
	if len(company)>0:
		content.append((BuildPluginUrl({'type':'company','submenu':'removecompany'}),_xbmc.ListItemBasic(_xbmc._AddonLocalStr(__addon__,32066),icon=GetIconPath('path/remove.png'),fanart=_xbmc._AddonInfo(__addon__,'fanart'))))
		for c in company:
			li = _xbmc.ListItemTMDBCompany(c,True)
			content.append((BuildPluginUrl({
				'type':'company',
				'submenu':'companycontent',
				'tmdbid':c.get('id')}),
				li,True))
	AddDirs(content,len(content))
	xbmcplugin.endOfDirectory(addon_handle)



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
	signin_status = True if addon_settings.getString('tmdb.user.sessionid') != None else False
	if list_id:
		list_id = int(list_id)
	if tmdb_id:
		tmdb_id = int(tmdb_id)
	menu = []
	if 'favorite' in items and signin_status:
		if IsIn(FILEPATHS.account,'account_favorite',mediatype,tmdb_id):
			pluginpath = BuildPluginUrl({'mode':'account','action':'favorite_remove','media_type':mediatype,'tmdbid':tmdb_id})
			menu.append((_xbmc._AddonLocalStr(__addon__,32037),f'RunPlugin({pluginpath})',))
		else:
			pluginpath = BuildPluginUrl({'mode':'account','action':'favorite_add','media_type':mediatype,'tmdbid':tmdb_id})
			menu.append((_xbmc._AddonLocalStr(__addon__,32036),f'RunPlugin({pluginpath})',))
	if 'watchlist' in items and signin_status:
		if IsIn(FILEPATHS.account,'account_watchlist',mediatype,tmdb_id):
			pluginpath = BuildPluginUrl({'mode':'account','action':'watchlist_remove','media_type':mediatype,'tmdbid':tmdb_id})
			menu.append((_xbmc._AddonLocalStr(__addon__,32039),f'RunPlugin({pluginpath})',))
		else:
			pluginpath = BuildPluginUrl({'mode':'account','action':'watchlist_add','media_type':mediatype,'tmdbid':tmdb_id})
			menu.append((_xbmc._AddonLocalStr(__addon__,32038),f'RunPlugin({pluginpath})',))
	if 'rate' in items and signin_status:
		if IsIn(FILEPATHS.account,'account_rated',mediatype,tmdb_id):
			pluginpath = BuildPluginUrl({'mode':'account','action':'unrate','media_type':mediatype,'tmdbid':tmdb_id,})
			menu.append((_xbmc._AddonLocalStr(__addon__,32041),f'RunPlugin({pluginpath})',))
		else:
			pluginpath = BuildPluginUrl({'mode':'account','action':'rate','media_type':mediatype,'tmdbid':tmdb_id,'rating':'###'})
			menu.append((_xbmc._AddonLocalStr(__addon__,32040),f'RunPlugin({pluginpath})',))
	if 'clear_list'in items and signin_status:
		pluginpath = BuildPluginUrl({'mode':'account','action':'clear_list','list_id':list_id})
		menu.append((_xbmc._AddonLocalStr(__addon__,32043),f'RunPlugin({pluginpath})',))
	if 'delete_list' in items and signin_status:
		pluginpath = BuildPluginUrl({'mode':'account','action':'delete_list','list_id':list_id})
		menu.append((_xbmc._AddonLocalStr(__addon__,32044),f'RunPlugin({pluginpath})',))
	if 'edit_lists' in items and signin_status:
		pluginpath = BuildPluginUrl({'mode':'account','action':'edit_lists','media_type':mediatype,'tmdbid':tmdb_id})
		menu.append((_xbmc._AddonLocalStr(__addon__,32045),f'RunPlugin({pluginpath})',))
	if 'delete_listitem' in items and signin_status:
		pluginpath = BuildPluginUrl({'mode':'account','action':'delete_listitem','media_type':mediatype,'tmdbid':tmdb_id,'list_id':list_id})
		menu.append((_xbmc._AddonLocalStr(__addon__,32050),f'RunPlugin({pluginpath})',))
	return menu


def GenresContent(genresid,mediatype,page):
	tmdbapi = TMDB_API(addon_settings.getString('tmdb.api.token'))
	if mediatype == 'movie':
		data = tmdbapi.DiscoverMovies(page,params={'with_genres':genresid})
	elif mediatype == 'tv':
		data = tmdbapi.DiscoverTv(page,params={'with_genres':genresid})
	else:
		return
	newpage = int(page) + 1
	if data:
		totalpages = data.get('total_pages')
		results = data.get('results')
		for r in results:
			tmdbid = r.get('id')
			li = _xbmc.ListitemTMDBitem(r,True)
			contextitems = ContextMenu(['favorite','watchlist','rate','edit_lists'],mediatype,None,tmdbid)
			li.addContextMenuItems(contextitems)
			AddDir({
				'submenu':'getvideo',
				'type':'tmdb_api_call',
				'tmdbid':tmdbid,
				'mediatype':mediatype},
				li,True)
		if newpage <= totalpages:
			li = _xbmc.ListItemBasic(f'{_xbmc._AddonLocalStr(__addon__,32014)} {newpage}/{totalpages}',icon=GetIconPath('path/nextpage.png'),fanart=_xbmc._AddonInfo(__addon__,'fanart'))
			AddDir({
				'type':'genres',
				'submenu':'genrescontent',
				'mediatype':mediatype,
				'tmdbid':genresid,
				'page':newpage
				},li,True)
		xbmcplugin.endOfDirectory(addon_handle)
	else:
		return

def GenresList(mediatype):
	content = [(BuildPluginUrl({'type':'genres','submenu':'addgenres','mediatype':mediatype}),_xbmc.ListItemBasic(_xbmc._AddonLocalStr(__addon__,32053),fanart=_xbmc._AddonInfo(__addon__,'fanart'),icon=GetIconPath('path/add.png')),False)]
	menu_data = ReadJsonFile(FILEPATHS.usermenus)
	menus = menu_data.get('menus')
	genres = menus.get('genres').get(mediatype)
	if len(genres) > 0:
		content.append((BuildPluginUrl({'type':'genres','submenu':'removegenres','mediatype':mediatype}),_xbmc.ListItemBasic(_xbmc._AddonLocalStr(__addon__,32054),fanart=_xbmc._AddonInfo(__addon__,'fanart'),icon=GetIconPath('path/remove.png')),False))
		for g in genres:
			content.append((BuildPluginUrl({'type':'genres','submenu':'genrescontent','mediatype':mediatype,'tmdbid':g.get('id')}),_xbmc.ListItemBasic(g.get('name'),fanart=_xbmc._AddonInfo(__addon__,'fanart'),icon=GetIconPath(g.get('icon'))),True))
	AddDirs(content,len(content))
	xbmcplugin.endOfDirectory(addon_handle)





def GetIconPath(item):
	path,full_filename = item.split('/')
	filename,fileext = full_filename.split('.')
	if path == 'path':
		folders = ['resources','media',addon_settings.getString('general.icon.color')]
	else:
		folders = ['resources','media']
	return _xbmc._joinPath(_xbmc._AddonInfo(__addon__,path),folders=folders,file_name=filename,file_ext=fileext)


def GetList(callurl,next_submenu,_type,path,page,prev_submenu,media_type):
	if page:
		newpage = int(page)+1
	tmdbapi = TMDB_API(addon_settings.getString('tmdb.api.token'))
	data = tmdbapi.GetList(callurl,page)
	if data:
		totalpages = data.get('total_pages')
		results = data.get('results')
		for r in results:
			tmdbid = r.get('id')
			li = _xbmc.ListitemTMDBitem(r,True)
			if media_type in ['movie','tv']:
				contextitems = ContextMenu(['favorite','watchlist','rate','edit_lists'],media_type,None,tmdbid)
				li.addContextMenuItems(contextitems)
			if path:
				fullpath = path.format(tmdbID=tmdbid)
			else:
				fullpath = path
			AddDir({
				'submenu':next_submenu,
				'type':_type,
				'callurl':fullpath,
				'mediatype':media_type,
				'tmdbid':tmdbid
				},li,True)
		if page and newpage <= totalpages:
			li = _xbmc.ListItemBasic(f'{_xbmc._AddonLocalStr(__addon__,32014)} {newpage}/{totalpages}',icon=GetIconPath('path/nextpage.png'),fanart=_xbmc._AddonInfo(__addon__,'fanart'))
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
					yt_api = addon_settings.getString('youtube.api.key')
					if addon_settings.getBool('youtube.general.useapi') and yt_api != None :
						d = YouTubeAPI(yt_api).VideoDetails(key,'snippet')
						if d:
							pageinfo = d.get('pageInfo')
							if pageinfo:
								totalresults = pageinfo.get('totalResults')
								if totalresults >= 1:
									items = d.get('items')
									item = items[0]
									snippet = item.get('snippet')
									li = _xbmc.ListitemYouTubeVideoItem(snippet,True)
								else:
									li = _xbmc.ListItemBasic(name,properties=r)
							else:
								li = _xbmc.ListItemBasic(name,properties=r)
						else:
							li = _xbmc.ListItemBasic(name,properties=r)
					else:
						li = _xbmc.ListItemBasic(name,properties=r)
					content.append((BuildPluginUrl({
						'type':'play',
						'submenu':'runplugin',
						'callurl':f'plugin://plugin.video.youtube/play/?video_id={key}'}),
					li,False))
			elif site == 'Vimeo':
				li = _xbmc.ListItemBasic(name,properties=r)
				content.append((BuildPluginUrl({
					'type':'play',
					'submenu':'runplugin',
					'callurl':f'plugin://plugin.video.vimeo/play/?video_id={key}'}),
				li,False))
			else:
				_xbmc.Log(f'{site} not recognize in filter {r}')
		AddDirs(content,len(content))
		xbmcplugin.endOfDirectory(addon_handle)
	else:
		tmdbapi = TMDB_API(addon_settings.getString('tmdb.api.token'))
		path = f'{mediatype}/{tmdbid}'
		item = tmdbapi.GetItem(path)
		ret = xbmcgui.Dialog().ok(_xbmc._AddonLocalStr(__addon__,32016), _xbmc._AddonLocalStr(__addon__,32017).format(item.get('title',item.get('name'))))
		if ret:
			xbmc.executebuiltin('Action(Back)')

def LoadFixedMenu(menu):
	items = GetMenuItems(menu)
	session_id = addon_settings.getString('tmdb.user.sessionid')
	if items:
		for i in items:
			if i.get('account_required') == True and not session_id:
				continue 
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


def Search(callurl,page,query,mediatype):
	if page == 1 and query == None:
		query = SearchQuery(mediatype)
	_xbmc.Log(query)
	if query:
		tmdbapi = TMDB_API(addon_settings.getString('tmdb.api.token'))
		data = tmdbapi.Search(query,callurl,page)
		totalpages = data.get('total_pages')
		results = data.get('results')
		newpage = page+1
		for r in results:
			li = _xbmc.ListitemTMDBitem(r,True)
			tmdbID = r.get('id')
			contextitems = ContextMenu(['favorite','watchlist','rate','edit_lists'],mediatype,None,tmdbID)
			li.addContextMenuItems(contextitems)
			AddDir({
				'submenu':'getvideo',
				'type':'tmdb_api_call',
				'tmdbid':tmdbID,
				'mediatype':mediatype
				},li,True)
		if newpage <= totalpages:
			li = _xbmc.ListItemBasic(f'{_xbmc._AddonLocalStr(__addon__,32014)} {newpage}/{totalpages}',icon=GetIconPath('path/nextpage.png'),fanart=_xbmc._AddonInfo(__addon__,'fanart'))
			AddDir({
				'submenu':'search',
				'page':newpage,
				'callurl':callurl,
				'icon':'path/search.png',
				'mediatype':mediatype,
				'query':query,
				'type':'search'
				},li,True)
		xbmcplugin.endOfDirectory(addon_handle)


def PersonSearch(callurl,page,query,mediatype):
	if page == 1 and query == None:
		query = SearchQuery(mediatype)
	if query:
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
			li = _xbmc.ListItemBasic(f'{_xbmc._AddonLocalStr(__addon__,32014)} {newpage}/{totalpages}',icon=GetIconPath('path/nextpage.png'),fanart=_xbmc._AddonInfo(__addon__,'fanart'))
			AddDir({
				'submenu':'search',
				'page':newpage,
				'callurl':'search/person',
				'icon':'path/nextpage.png',
				'mediatype':'person',
				'query':query,
				'type':'search'
				},li,True)
		xbmcplugin.endOfDirectory(addon_handle)


def RecomendGetList(callurl,next_submenu,_type,page,prev_submenu,prev_type,mediatype):
	account_id = addon_settings.getInt('tmdb.user.id')
	tmdbacc = TMDB_Account(addon_settings.getString('tmdb.api.token'),addon_settings.getString('tmdb.user.sessionid'))
	data = tmdbacc.GetList(callurl.format(account_id),page)
	results = data.get('results')
	totalpages = data.get('total_pages')
	newpage = page+1
	for r in results:
		tmdbID = r.get('id')
		li = _xbmc.ListitemTMDBitem(r,True)
		title = li.getLabel()
		li.setLabel(f'{_xbmc._AddonLocalStr(__addon__,32073)}')
		contextitems = ContextMenu(['favorite','watchlist','edit_lists'],mediatype,None,tmdbID)
		li.addContextMenuItems(contextitems)
		AddDir({
			'callurl':f'movie/{tmdbID}/recommendations',
			'submenu':next_submenu,
			'type':_type,
			'tmdbid':tmdbID,
			'mediatype':mediatype},
			li,True)
	if page and newpage <= totalpages:
		li = _xbmc.ListItemBasic(f'{_xbmc._AddonLocalStr(__addon__,32014)} {newpage}/{totalpages}',icon=GetIconPath('path/nextpage.png'),fanart=_xbmc._AddonInfo(__addon__,'fanart'))
		AddDir({
			'submenu':prev_submenu,
			'type':prev_type,
			'callurl':callurl,
			'page':newpage,
			'mediatype':mediatype},
			li,True)
	xbmcplugin.endOfDirectory(addon_handle)

def RemoveCollection():
	items = []
	menu_data = ReadJsonFile(FILEPATHS.usermenus)
	menus = menu_data.get('menus')
	collections = menus.get('collections')
	for c in collections:
		items.append(_xbmc.ListitemTMDBCollection(c,False))
	dialog = xbmcgui.Dialog()
	ret = dialog.multiselect(_xbmc._AddonLocalStr(__addon__,32061),items,useDetails=True)
	if ret:
		ret.reverse()
		for r in ret:
			collections.pop(r)
		WriteJsonFile(FILEPATHS.usermenus,menu_data)
		xbmc.executebuiltin('Container.Refresh')

def RemoveGenres(mediatype):
	items = []
	menu_data = ReadJsonFile(FILEPATHS.usermenus)
	menus = menu_data.get('menus')
	genres = menus.get('genres').get(mediatype)
	for g in genres:
		items.append(_xbmc.ListItemBasic(g.get('name'),properties=g))
	dialog = xbmcgui.Dialog()
	ret = dialog.multiselect(_xbmc._AddonLocalStr(__addon__,32056),items)
	if ret:
		ret.reverse()
		for r in ret:
			genres.pop(r)
		WriteJsonFile(FILEPATHS.usermenus,menu_data)
		xbmc.executebuiltin('Container.Refresh')



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

def SearchQuery(mediatype):
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
		if ret >= 0:
			q = items[ret]
		else:
			return None
	elif len(searches)==0:
		q = items[0]
	if q.getLabel() == newsearch:
		d = xbmcgui.Dialog().input(_xbmc._AddonLocalStr(__addon__,32011),type=xbmcgui.INPUT_ALPHANUM)
		data[key].append({'query':d,'timestamp':TimeStamp()})
		WriteJsonFile(FILEPATHS.search,data)
	else:
		d = q.getLabel()
	return d

	

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

def StartUp():
	RequiredDirs()
	RequiredFiles()
	if not addon_settings.getBool('tmdb.api.token.user') and addon_settings.getString('tmdb.api.token') != TOKEN:
		_xbmc._AddonSetSetting(__addon__,'tmdb.api.token',TOKEN)
	if addon_settings.getBool('tmdb.account.refresh') and addon_settings.getString('tmdb.user.sessionid') != None:
		tmdbUserRefresh()


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
		li = _xbmc.ListItemBasic(f'{_xbmc._AddonLocalStr(__addon__,32014)} {newpage}/{totalpages}',icon=GetIconPath('path/nextpage.png'),fanart=_xbmc._AddonInfo(__addon__,'fanart'))
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
		li = _xbmc.ListItemBasic(f'{_xbmc._AddonLocalStr(__addon__,32014)} {newpage}/{totalpages}',icon=GetIconPath('path/nextpage.png'),fanart=_xbmc._AddonInfo(__addon__,'fanart'))
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
	li = _xbmc.ListItemBasic(_xbmc._AddonLocalStr(__addon__,32028),icon=GetIconPath('path/add.png'),fanart=_xbmc._AddonInfo(__addon__,'fanart'))
	AddDir({'submenu':'usertmdb','type':'addlist'},li,False)
	for r in results:
		li = _xbmc.ListItemTMDBList(r,True)
		list_id = r.get('id')
		contextitems = ContextMenu(['clear_list','delete_list'],None,list_id,None)
		li.addContextMenuItems(contextitems)
		AddDir({'submenu':'usertmdb','type':'tmdbgetlistdetails','callurl':path.format(list_id=list_id),'listid':list_id},li,True)
	if page and newpage <= totalpages:
		li = _xbmc.ListItemBasic(f'{_xbmc._AddonLocalStr(__addon__,32014)} {newpage}/{totalpages}',icon=GetIconPath('path/nextpage.png'),fanart=_xbmc._AddonInfo(__addon__,'fanart'))
		AddDir({'submenu':'usertmdb','type':'tmdbGetList','page':newpage,'callurl':callurl},li,True)
	xbmcplugin.endOfDirectory(addon_handle)


def tmdbMenu():
	items = []
	session_id = addon_settings.getString('tmdb.user.sessionid')
	if not session_id:
		li = _xbmc.ListItemBasic(_xbmc._AddonLocalStr(__addon__,32019),icon=None,fanart=None,properties={'submenu':'signin','type':'usertmdb'})
		items.append((BuildPluginUrl({'submenu':'usertmdb','type':'signin'}),li,False))
	else:
		li = _xbmc.ListItemBasic(_xbmc._AddonLocalStr(__addon__,32020),icon=None,fanart=None,properties={'submenu':'signout','type':'usertmdb'})
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


def tmdbUserRefresh():
	SetAccountDetails(__addon__)
	TMDB_ArtWorkDownloader(addon_settings.getString('tmdb.user.avatar'),_xbmc._joinPath(_xbmc._AddonInfo(__addon__,'profile'),folders=['resources','media'],file_name='mytmdb',file_ext='png'))
	files = ReadJsonFile(CONFIGPATH,keys=['files'])
	file = list(filter(lambda d: d['filename'] == 'account', files))[0]
	ResetJsonFile(FILEPATHS.account,file.get('base_dict'))
	BuildUserListsCache(FILEPATHS.account,addon_settings.getString('tmdb.user.sessionid'),addon_settings.getInt('tmdb.user.id'),addon_settings.getString('tmdb.api.token'))
	xbmc.executebuiltin('Container.Refresh')


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


if mode == 'addon':
	if submenu == None:
		StartUp()
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
	elif submenu and menutype == 'genres':
		if submenu == 'genreslist':
			GenresList(mediatype)
		elif submenu == 'genrescontent':
			GenresContent(tmdbid,mediatype,page)
		elif submenu == 'addgenres':
			AddGenres(mediatype)
		elif submenu == 'removegenres':
			RemoveGenres(mediatype)
	elif menutype == "play":
		if submenu == 'runplugin':
			xbmc.executebuiltin(f'RunPlugin({callurl})')
	elif menutype == 'collections' and submenu:
		if submenu == 'collectionslists':
			CollectionsLists()
		elif submenu == 'addcolletion':
			AddCollection()
		elif submenu == 'removecollection':
			RemoveCollection()
		elif submenu == 'collectioncontent':
			CollectionsContent(tmdbid)
	elif menutype == 'company' and submenu:
		if submenu == 'companylists':
			CompanyLists()
		elif submenu == 'addcompany':
			AddCompany()
		elif submenu == 'removecompany':
			RemoveCompany()
		elif submenu == 'companycontent':
			CompanyContent(tmdbid,page,mediatype)
	elif menutype == "search":
		if mediatype == 'movie':
			Search(callurl,page,query,mediatype)
		elif mediatype == 'tv':
			Search(callurl,page,query,mediatype)
		elif mediatype == 'person':
			PersonSearch(callurl,page,query,mediatype)
	elif menutype == "usertmdb":
		if submenu == 'main':
			tmdbMenu()
		elif submenu == 'signin':
			tmdbSignIn()
		elif submenu == 'signout':
			tmdbSignOut()
		elif submenu == 'tmdbmoviegetlist':
			tmdbGetList(callurl,'getvideo',"tmdb_api_call",page,submenu,menutype,mediatype)
		elif submenu == 'tmdbtvgetlist':
			tmdbGetList(callurl,'getvideo',"tmdb_api_call",page,submenu,menutype,mediatype)
		elif submenu == 'tmdbgetlists':
			tmdbGetLists(callurl,page,'list/{list_id}')
		elif submenu == 'tmdbgetlistdetails':
			tmdbGetListDetails(callurl,page)
		elif submenu == 'addlist':
			tmdbAddList()
	elif menutype == 'movierecommened':
		if submenu == 'recommenedgetlist':
			RecomendGetList(callurl,'moviegetlist','tmdb_api_call',page,submenu,menutype,mediatype)
	elif menutype == 'tvrecommened':
		if submenu == 'recommenedgetlist':
			RecomendGetList(callurl,'tvgetlist','tmdb_api_call',page,submenu,menutype,mediatype)
elif mode == 'account':
	from resources.lib.runpluginmethods.account import Account
	acc = Account(sys.argv)
	if acc:
		acc.RunPluginMethod()
elif mode == 'maintenance':
	from resources.lib.runpluginmethods.maintenance import Maintenance
	maint = Maintenance(sys.argv)
	if maint:
		maint.RunPluginMethod()
elif mode == 'settings':
	from resources.lib.runpluginmethods.settings import Settings
	settings = Settings(sys.argv)
	if settings:
		settings.RunPluginMethod()





