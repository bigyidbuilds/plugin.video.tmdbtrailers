#!/usr/bin/python3
# -*- coding: utf-8 -*-

import xbmc

from resources.lib.modules import _xbmc

__addon__         = 'plugin.video.tmdbtrailers'
__addonsettings__ = _xbmc._AddonSettings(__addon__)

def Language():
	language = 'en-US'
	lang = __addonsettings__.getString('tmdb.language')
	if lang == 'xbmc':
		language = xbmc.getInfoLabel('System.Language')
	elif lang == 'tmdb':
		l = __addonsettings__.getString('tmdb.user.defaultlanguage')
		if l != '':
			language == l
		else:
			language = 'en-US'
	else:
		language = 'en-US'
	return language

SCHEME      = 'https'
NETLOC      = 'api.themoviedb.org'
APIVERISON  = '3'
LANGUAGE    = Language()
ADULTSEARCH = __addonsettings__.getBool('tmdb.user.adultsearch')


