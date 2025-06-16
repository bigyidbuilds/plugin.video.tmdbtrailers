#!/usr/bin/python3
# -*- coding: utf-8 -*-



from resources.lib.modules._tmdb.tmdb_account import Tmdb_Account

"""
Sample of path
paths = RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=user_detatils

sys.argv

mode 
	mode = account

action
	available actions:
		user_details: Pulls account details from TMDB and sets relative settings
		sigin: sign in and create session id
		signout: sign out and delete session id

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
				raise exceptions.RUNPLUGIN_sysargv_keys_Exception(message='ERROR',req_keys=self.req_keys,keys=keys)
			ret,missing = self.ValidateSysArgvValues()
			if not ret:
				raise exceptions.RUNPLUGIN_sysargv_var_Exception(message='ERROR',missing) 
		except exceptions.RUNPLUGIN_sysargv_keys_Exception as ke:
			utils.Log(ke.logmessage)
			return
		except exceptions.RUNPLUGIN_sysargv_var_Exception ve:
			utils.Log(ve.message)
		except Exception as exc:
			utils.Log(exc)
			return


	def RunPluginMethod(self):
		mode = self.sysargv.get('mode')[0]
		action = self.sysargv.get('action')[0]
		if action == 'user_details':
			self.UserDetails()
		elif action == 'signin':
			self.SignIn()
		elif action == 'signout':
			self.SignOut()
		else:
			return

	def UserDetails(self):
		pass
		self.AddonSettings.setInt('tmdb.user.id', ret.get('id'))
		self.AddonSettings.setString('tmdb.user.name',ret.get('name'))
		self.AddonSettings.setString('tmdb.user.defaultlanguage',ret.get('iso_639_1'))
		self.AddonSettings.setBool('tmdb.user.adultsearch',ret.get('include_adult'))
		self.AddonSettings.setString('tmdb.user.avatar',self.ImageUrl(ret.get('tmdb').get('avatar_path')))

	def SignIn(self):
		pass

	def SignOut(self):
		pass


	def ValidateSysArgvKeys(self,keys):
		return all(key in self.req_keys for key in keys)

	def ValidateSysArgvValues(self):
		missing = []
		for k,v in self.sysargv:
			if k in self.req_keys:
				v = v[0]
				if v == None:
					missing.append(k)
		if len(missing) == 0:
			return True,missing
		else:
			return False,missing
		
