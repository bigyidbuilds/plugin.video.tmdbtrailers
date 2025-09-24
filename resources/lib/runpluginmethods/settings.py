#!/usr/bin/python3
# -*- coding: utf-8 -*-

import xbmc
import xbmcgui

from urllib.parse import parse_qs

from resources.lib.modules import exceptions
from resources.lib.modules import _xbmc

__addon__ = 'plugin.video.tmdbtrailers'

class Settings():
	"""docstring for Settings"""
	def __init__(self,sysargv):
		super().__init__()
		self.sysargv = sysargv
		self.keyvalues = parse_qs(self.sysargv[2][1:])
		self.req_keys = ['mode','action']
		self.keys = list(self.keyvalues.keys())
		self.addonsettings = _xbmc._AddonSettings(__addon__)
		self.dialog = xbmcgui.Dialog()
		try:
			if not self.ValidateSysArgvKeys(self.keys,self.req_keys):
				raise exceptions.RUNPLUGIN_sysargv_keys_Exception(message='ERROR',req_keys=self.req_keys,keys=self.keys)
			ret,missing = self.ValidateSysArgvValues(self.req_keys)
			if not ret:
				raise exceptions.RUNPLUGIN_sysargv_var_Exception(message='ERROR',missing=missing) 
		except exceptions.RUNPLUGIN_sysargv_keys_Exception as ke:
			_xbmc.Log(ke.logmessage)
			return None
		except exceptions.RUNPLUGIN_sysargv_var_Exception as ve:
			_xbmc.Log(ve.message)
			return None
		except Exception as exc:
			_xbmc.Log(exc)
			return None


	def RunPluginMethod(self):
		mode = self.keyvalues.get('mode')[0]
		action = self.keyvalues.get('action')[0]
		if action == 'set_tmdb_api_token':
			self.SetAPIToken()
		elif action == 'reload_tmdb_api_token':
			self.ReloadAPIToken()

	def ReloadAPIToken(self):
		addon_name = _xbmc._AddonInfo(__addon__,'name')
		addon_icon = _xbmc._AddonInfo(__addon__,'icon')
		check_overwrite = self.dialog.yesno(addon_name, _xbmc._AddonLocalStr(__addon__,30047))
		if check_overwrite:
			from resources.lib._tmdb.tmdb_token import TOKEN
			_xbmc._AddonSetSetting(__addon__,'tmdb.api.token',TOKEN)
			message = _xbmc._AddonLocalStr(__addon__,30048)
			xbmc.sleep(1000)
			self.addonsettings = _xbmc._AddonSettings(__addon__)
			if self.addonsettings.getString('tmdb.api.token') == TOKEN:
				message = _xbmc._AddonLocalStr(__addon__,30044)
			else:
				message = _xbmc._AddonLocalStr(__addon__,30045)
			self.dialog.notification(addon_name, message,icon=addon_icon)


	def SetAPIToken(self):
		addon_name = _xbmc._AddonInfo(__addon__,'name')
		addon_icon = _xbmc._AddonInfo(__addon__,'icon')
		check_overwrite = self.dialog.yesno(addon_name, _xbmc._AddonLocalStr(__addon__,30007))
		if check_overwrite:
			token = self.dialog.input(_xbmc._AddonLocalStr(__addon__,30014))
			_xbmc._AddonSetSetting(__addon__,'tmdb.api.token',token)
			message = _xbmc._AddonLocalStr(__addon__,30048)
			xbmc.sleep(1000)
			self.addonsettings = _xbmc._AddonSettings(__addon__)
			if self.addonsettings.getString('tmdb.api.token') == token:
				message = _xbmc._AddonLocalStr(__addon__,30044)
			else:
				message = _xbmc._AddonLocalStr(__addon__,30045)
			self.dialog.notification(addon_name, message)



	def ValidateSysArgvKeys(self,keys,req_keys):
		return all(key in keys for key in req_keys)

	def ValidateSysArgvValues(self,req_keys):
		missing = []
		for k,v in self.keyvalues.items():
			if k in self.req_keys:
				v = v[0]
				if v == None:
					missing.append(k)
		if len(missing) == 0:
			return True,missing
		else:
			return False,missing