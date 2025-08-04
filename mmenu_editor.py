#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
MENUS = r'C:\Users\Andy\AppData\Roaming\Kodi\addons\plugin.video.tmdbtrailers\menus.json'
MENUSCOPY = r"C:\Users\Andy\AppData\Roaming\Kodi\addons\plugin.video.tmdbtrailers\menus - Copy.json"
PATHS = r'C:\Users\Andy\AppData\Roaming\Kodi\addons\plugin.video.tmdbtrailers\paths.json'
FILES = r'C:\Users\Andy\AppData\Roaming\Kodi\addons\plugin.video.tmdbtrailers\files.json'

def read(file):
	with open(file) as f:
		data = json.load(f)
		return data

def write(file,data):
	with open(file,'w') as f:
		json.dump(data,f,indent=4)

def keys(data):
	return list(data.keys())

def addkeyvalue(key,value):
	data = read()
	menus = data.get('menus')
	keys = list(menus.keys())
	for k in keys:
		submenu = menus.get(k)
		for s in submenu:
			s.update({key:value}) 
	write(data)

def BulkupdateKeyValue(file,query,key,isvalue,replacement):
	data = read(file)
	menus = data.get(query)
	_keys = keys(menus)
	for k in _keys:
		submenu = menus.get(k)
		for s in submenu:
			for k,v in list(s.items()):
				if k == key and v == isvalue:
					s.update({k:replacement})
	write(data)	

def DeleteKey(key):
	data = read()
	menus = data.get('menus')
	_keys = keys(menus)
	for k in _keys:
		submenu = menus.get(k)
		for s in submenu:
			for k,v in list(s.items()):
				if k == key:
					s.pop(key)
	write(data)

def EditValues(key,appendfront=None):
	data = read()
	menus = data.get('menus')
	_keys = keys(menus)
	for k in _keys:
		submenu = menus.get(k)
		for s in submenu:
			for k,v in list(s.items()):
				if k == key:
					if appendfront:
						s.update({key:f'{appendfront}{v}'})
	write(data)

def KeyValueUpdate(key,value):
	data = read()
	for d in data:
		d.update({})

def Print(data):
	print(json.dumps(data,indent=4))


if __name__ == '__main__':
	data = read(MENUS)
	files = data.get('files')
	for f in files:
		f.update({'filepath':'addon_profile'})
	# print(json.dumps(data,indent=4))
	write(MENUS,data)




