#!/usr/bin/python3
# -*- coding: utf-8 -*-


from resources.lib.modules import userlists
from resources.lib.modules import utils

def RegistrateAPIKey(filepath,filename,addon_id,key,bearer,overwrite=False):
	if userjson.AddonUserValidate(filepath,filename,addon_id):
		data = utils.ReadJsonFile(filepath,filename)
		access_data = data.get('access')
		addon_data = access_data.get(addon_id)
		addon_api = addon_data.get('key_details')
		if not bool(addon_api) or overwrite:
			addon_api.update({'key':key,'bearer':bearer})
			utils.WriteJsonFile(filepath,filename,data)



