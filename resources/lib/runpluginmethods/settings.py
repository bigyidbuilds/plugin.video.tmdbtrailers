#!/usr/bin/python3
# -*- coding: utf-8 -*-



from resources.lib.modules._tmdb.tmdb_account import Tmdb_Account

"""
Sample of path
paths = RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=settings&action=user_detatils

sys.argv

mode 
	mode = account

action
	available actions:
		user_details: Pulls account details from TMDB and sets relative settings

"""


class Account():
	"""docstring for Settings"""
	def __init__(self,sysargv):
		super(Settings, self).__init__()
		self.sysargv = sysargv
		self.req_keys = ['mode','action']
		keys = list(self.sysargv.keys())
		try:
			if not self.ValidateSysArgvKeys(keys):
				raise exceptions.RUNPLUGIN_sysargv_keys_Exception(req_keys=self.req_keys,keys=keys)
		except exceptions.RUNPLUGIN_sysargv_keys_Exception as e:
			utils.Log(e.logmessage)
			return
		except Exception as exc:
			utils.Log(exc)
			return





	def ValidateSysArgvKeys(self,keys):
		return all(key in self.req_keys for key in keys)

	def ValidateSysArgvVariable(self,list_var):
		missing = []
		for v,k in list_var:
			if v == None:
				missing.append(k)
		if len(missing) == 0:
			return True,missing
		else:
			return False,missing

		
