import json

file = r'C:\Users\Andy\AppData\Roaming\Kodi\userdata\addon_data\plugin.video.tmdbtrailers\account.json'

tmdb_id = 284053
def read(file):
	with open(file) as f:
		data = json.load(f)
		return data


def f(file,_id=297802):
	ret = []
	data = read(file)
	account_lists = data.get('account_lists')
	for k,v in account_lists.items():
		results = v.get('results')
		for r in results:
			d = {}
			list_id = r.get('id')
			name = r.get('name')
			d.update({'list_id':list_id,'name':name})
			ret.append(d)
	print(json.dumps(ret,indent=4))
		# results = v.get('results')
		# for r in results:
		# 	items = r.get('items')
		# 	for k,v in items.items():
				# name = v.get('name')
				# list_id = v.get('id')
				# _items = v.get('items')
				# d = {'name':name,'list_id':list_id}
				# if len(_items)>0:
				# 	for _i in _items:
				# 		if _i.get('id') == _id:
				# 			d.update({'item_present':True})
				# 		else:
				# 			d.update({'item_present':False})
				# else:
				# 	d.update({'item_present':False})
				# ret.append(d)
				
	# print(json.dumps(ret,indent=4))


items = ['delete_listitem']
print([i in items if i == 'delete_listitem'])