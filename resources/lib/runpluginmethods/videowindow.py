#!/usr/bin/python3
# -*- coding: utf-8 -*-

from urllib.parse import parse_qs

from resources.lib.modules import exceptions
from resources.lib.modules import _xbmc

class VideoWindow():
	"""docstring for VideoWindow"""
	def __init__(self,sysargv):
		super().__init__()
		self.sysargv = sysargv
		self.keyvalues = parse_qs(self.sysargv[2][1:])
		self.req_keys = ['mode','mediatype','tmdbid']
		self.keys = list(self.keyvalues.keys())
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
		mediatype = self.keyvalues.get('mediatype')[0]
		tmdbid = self.keyvalues.get('tmdbid')[0]
		from resources.lib.windows.video_window import VideoWindow
		d = VideoWindow(tmdbid,mediatype)
		d.doModal()
		del d


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