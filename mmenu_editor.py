#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
path = r'C:\Users\Andy\AppData\Roaming\Kodi\addons\plugin.video.tmdbtrailers\menus.json'
# path = r"C:\Users\Andy\AppData\Roaming\Kodi\addons\plugin.video.tmdbtrailers\menus - Copy.json"

def read():
	with open(path) as f:
		data = json.load(f)
		return data

def write(data):
	with open(path,'w') as f:
		json.dump(data,f,indent=4)

def addkeyvalue(key,value):
	data = read()
	menus = data.get('menus')
	keys = list(menus.keys())
	for k in keys:
		submenu = menus.get(k)
		for s in submenu:
			s.update({key:value}) 
	write(data)		


if __name__ == '__main__':
	addkeyvalue('mediatype',None)

