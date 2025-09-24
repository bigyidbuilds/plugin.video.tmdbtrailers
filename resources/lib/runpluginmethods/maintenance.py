#!/usr/bin/python3
# -*- coding: utf-8 -*-


from urllib.parse import parse_qs

from resources.lib.modules import _jsonfiles
from resources.lib.modules import _xbmc
from resources.lib.modules._paths import File_Paths
from resources.lib.modules import exceptions

__addon__ = 'plugin.video.tmdbtrailers'

class Maintenance():
	"""docstring for Maintenance"""
	def __init__(self,sysargv):
		super(Maintenance, self).__init__()
		self.sysargv = sysargv
		_xbmc.Log(self.sysargv)
		self.keyvalues = parse_qs(self.sysargv[2][1:])
		self.req_keys = ['mode','action']
		self.keys = list(self.keyvalues.keys())
		self.CONFIGPATH = _xbmc._joinPath(_xbmc._AddonInfo(__addon__,'path'),file_name='config',file_ext='json')
		self.FILEPATHS = File_Paths(self.CONFIGPATH)
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


	def CorrectFormat(self,reqkeys):
		try:
			if not self.ValidateSysArgvKeys(self.keys,reqkeys):
				raise exceptions.RUNPLUGIN_sysargv_keys_Exception(message='ERROR',req_keys=reqkeys,keys=self.keys)
			ret,missing = self.ValidateSysArgvValues(reqkeys)
			if not ret:
				raise exceptions.RUNPLUGIN_sysargv_var_Exception(message='ERROR',missing=missing)
			return True
		except exceptions.RUNPLUGIN_sysargv_keys_Exception as ke:
			_xbmc.Log(ke.logmessage)
			return False
		except exceptions.RUNPLUGIN_sysargv_var_Exception as ve:
			_xbmc.Log(ve.message)
			return False
		except Exception as exc:
			_xbmc.Log(exc)
			return False

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
		

	def RunPluginMethod(self):
		mode = self.keyvalues.get('mode')[0]
		action = self.keyvalues.get('action')[0]
		if action == 'delete_search_history':
			self.DeleteSearchHistory()


	def DeleteSearchHistory(self):
		file = FILEPATHS.search
		if _xbmc.FileExists(file):
			_jsonfiles.ResetJsonFile(file,self.GetBaseDict('search'))


	def GetBaseDict(self,file_name):
		data = _jsonfiles.ReadJsonFile(CONFIGPATH)
		paths = data.get('paths')
		files = data.get('files')
		file_data = next(filter(lambda x: x['filename'] == file_name, files), None)
		return file_data.get('base_dict')