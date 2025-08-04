#!/usr/bin/python3
# -*- coding: utf-8 -*-

from resources.lib.modules import _xbmcaddon
from resources.lib.modules import exceptions
from resources.lib.modules import utils

from resources.lib.modules._tmdb.tmdb_account import TMDB_Account

"""
Sample of path
paths = RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=contextmenu&action=add_to_favorite&media_type=movie&media_id=123456&addon_id=plugin.video.tmdbtrailers)

sys.argv

mode
	Available modes 'contextmenu'

action
	available actions 'add_to_favorites',
					  'add_to_watchlist'
media_type
	avaiable media_types 'movies'
						 'tv'
media_id
	tmdb ID of media

addon_id
	optional use this if session id is created for this addon, it will default to plugin.video.tmdbtrailers


"""

class ContextMenu():
	"""docstring for ContextMenu"""
	def __init__(self,sysargv):
		super(ContextMenu, self).__init__()
		self.__addon__ = 'plugin.video.tmdbtrailers'
		self.__addonprofile__ = _xbmcaddon._AddonInfo(self.__addon__,'profile')
		self.userjson = utils.ReadJsonFile(self.__addonprofile__,'user.json')
		self.sysargv = sysargv
		self.req_keys = ['mode','action','media_type','media_id']
		keys = list(self.sysargv.keys())
		try:
			if not self.ValidateSysArgvKeys(keys):
				raise exceptions.RUNPLUGIN_sysargv_keys_Exception(req_keys=self.req_keys,keys=keys)
			else:
				self.RunPluginMethod(self.sysargv)
		except exceptions.RUNPLUGIN_sysargv_Exception as e:
			utils.Log(e.logmessage)
			return
		except Exception as exc:
			utils.Log(exc)
			return


	def RunPluginMethod(self,sysargv):
		try:
			mode = sysargv.get('mode')
			action = sysargv.get('action')
			media_type = sysargv.get('media_type')
			media_id = sysargv.get('media_id')
			try:
				addon_id = sysargv.get('addon_id')
			except:
				addon_id = self.__addon__
			list_var = [[mode,'mode'],[action,'action'],[media_type,'media_type'],[media_id,'media_id'],[addon_id,'addon_id']]
			b,missing = ValidateSysArgvVariable(list_var):
			if not b:
				raise exceptions.RUNPLUGIN_sysargv_var_Exception(f'ERROR values missing from sys.argv of run plugin method\n\tMissing values are {missing}')
			self.tmdbacc = TMDB_Account()
			if mode == 'contextmenu' and action == 'add_to_favorites':
				self.AddFavorites()
		except Exception exceptions.RUNPLUGIN_sysargv_Exception as e:
			utils.Log(e)
			return
		except Exception as exc:
			utils.Log(exc)
			return


	def ValidateSysArgvKeys(self,keys):
		return all(key in self.req_keys for key in keys)

	def ValidateSysArgv(self):
		missing = []
		for k,v in self.sysargv:
			v = v[0]
			if v == None:
				missing.append(k)
		if len(missing) == 0:
			return True,missing
		else:
			return False,missing

