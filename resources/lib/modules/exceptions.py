#!/usr/bin/python3
# -*- coding: utf-8 -*-





class TMDBAPI_Response_Exception(Exception):
	"""docstring for ClassName"""
	def __init__(self,message='',errors_dict=None,url=None):
		super(TMDBAPI_Response_Exception, self).__init__(message)
		self.message = message
		self.errors_dict = errors_dict
		self.url = url
		self.logmessage = f"{self.message}\nstatus code = {self.errors_dict.get('status_code')}\nstatus message = {self.errors_dict.get('status_message')} from URL {self.url}"

class TMDBAPI_KeyError_Exception(Exception):
	"""docstring for TMDBAPI_KeyError_Exception"""
	def __init__(self,message,key,allkeys):
		super(TMDBAPI_KeyError_Exception, self).__init__(message)
		self.message = message
		self.key = key
		self.allkeys = allkeys
		self.logmessage = f'{self.message}\nkey:{self.key} not found dict\nAvaiable keys {self.allkeys}'




# class RUNPLUGIN_sysargv_Exception(Exception):
	
class RUNPLUGIN_sysargv_keys_Exception(Exception):
	"""docstring for RUNPLUGIN_sysargv_Exception"""
	def __init__(self,message='',req_keys=None,keys=None):
		super(RUNPLUGIN_sysargv_Exception, self).__init__()
		self.message = message
		self.req_keys = req_keys
		self.keys = keys
		missing = set(self.req_keys)-set(self.keys)
		self.logmessage = f'{self.message} Incorrect keys in passed sys.argv of run plugin method\n\tmissings keys are\n{missing}'
		

class RUNPLUGIN_sysargv_var_Exception(Exception):
	"""docstring for RUNPLUGIN_sysargv_var_Exception"""
	def __init__(self,message='',missing=None):
		super(RUNPLUGIN_sysargv_var_Exception, self).__init__()
		self.message
		self.missing
		self.logmessage = f'{self.message} values missing from sys.argv of run plugin method\n\tMissing values are {missing}'
						
