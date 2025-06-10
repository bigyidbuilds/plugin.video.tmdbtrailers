#!/usr/bin/python3
# -*- coding: utf-8 -*-

import xbmcaddon


def _Addon(addonID):
	return xbmcaddon.Addon(addonID)

def _AddonInfo(addonID,info):
	'''options for info :- path,name,version,profile'''
	return _Addon(addonID).getAddonInfo(info)

def _AddonLocalStr(addonID,msgctxt):
	'''msgctxt = id from strings.po'''
	return _Addon(addonID).getLocalizedString(msgctxt)

def _AddonSettings(addonID):
	return _Addon(addonID).getSettings()