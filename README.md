# plugin.video.tmdbtrailers

## RunPlugin methods
 
### Sample of paths
1.  ```RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=user_detatils```
2.  ```RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=favorite_add&media_type=movie&tmdbid=10000```
3.  ```RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=favorite_remove&media_type=tv&tmbid=2000```
4.  ```RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=watchlist_add&media_type=movie&tmdbid=10000```
5.  ```RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=watchlist_remove&media_type=tv&tmbid=2000```
6.  ```RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=rate&media_type=movie&tmdbid=123456&rating=8.7)```
7.  ```RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=unrate&media_type=tv&tmdbid=654321)```
8.  ```RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=clear_list&list_id=1234)```
9.  ```RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=delete_list&list_id=1234)```
10. ```RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&&action=delete_listitem&list_id=1234&tmdbid=123456)```
11. ```RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&&action=edit_lists&media_type=movie&tmdbid=123456)```


### sys.argv

### mode 
	mode = account

### action
available actions:

| Action | Details | Required params |
|--------|---------|-----------------|
| user_details: | Pulls account details from TMDB and sets relative settings | None |
| sigin: | sign in and create session id | None |
| signout: | sign out and delete session id | None |
| favorite_add: | Add to tmdb favorites |media_type(movie or tv),tmdbid(id of tmdb media) |
| favorite_remove: | Remove from favorites | media_type(movie or tv),tmdbid(id of tmdb media) |
| watchlist_add: | Add to watch list | media_type(movie or tv),tmdbid(id of tmdb media) |
| watchlist_remove: | Remove from watch list | media_type(movie or tv),tmdbid(id of tmdb media) |
| rate: | Rate media | media_type(movie or tv),tmdbid(id of tmdb media),rating(0-10 value as float 1 decimal place value must be dividable by 0.5 or '###' will call xbmc ui to enter a valve ) |
| unrate: | Unrate media | media_type(movie or tv),tmdbid(id of tmdb media) | 
| clear_list: | Clear List | list_id (id of list) |
| delete_list: | delete list | list_id (id of list) |
| delete_listitem: | Delete item from list | list_id(id of list), tmdbid(id of tmdb media) |
| edit_list: | Add or remove item from a list | media_type(movie or tv),tmdbid(id of tmdb media) |