#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json

import xbmcvfs

from . import _xbmc



def ReadJsonFile(path,keys=None):
	'''use _xbmc._joinPath(base_path,folders=None,file_name=None,file_ext=None) to create path
	Key param is a list of keys to get to key end point placed in order through dict or json object'''
	_error = False
	message = None
	if _xbmc.FileExists(path):
		with open(path) as f:
			try:
				data = json.load(f)
				if keys:
					for key in keys:
						data = data.get(key)
					return data
				else:
					return data
			except json.JSONDecodeError as de:
				message = f'Error json.JSONDecodeError {de}'
				_error = True
			except ValueError as ve:
				message = f'Error ValueError {ve}'
				_error = True
			except Exception as e:
				message = f'Error Exception {e}'
				_error = True
			finally:
				if _error:
					_xbmc.Log(message)
					return None
	else:
		_xbmc.Log(f'File not found at {path}')
		return None

def WriteJsonFile(path,data):
	'''use _xbmc._joinPath(base_path,folders=None,file_name=None,file_ext=None) to create path'''
	if _xbmc.FileExists(path):
		with xbmcvfs.File(path,'w') as f:
			json.dump(data,f,indent=4)


def ResetJsonFile(file,base_dict):
	data = ReadJsonFile(file)
	data.update(**base_dict)
	WriteJsonFile(file,data)


