'''
Colby College Museum of Art JSON export script, V1.0
Simple script to download JSON from the webKiosk, do some basic cleanup of embark webkiosk quirks (HTML tag removal and making valid JSON)
'''
import requests, re, json
from lxml import etree, objectify
from pprint import pprint

# 0: Get objects, artists, and exhibitions from the embark webkiosk
objects_response = requests.get('http://127.0.0.1:8080/results.html?layout=ccma_objects&format=shtml&maximumrecords=9000&recordType=objects_1&query=_ID>1')
artists_response = requests.get('http://127.0.0.1:8080/results.html?layout=ccma_artists&format=shtml&maximumrecords=9000&recordType=artist_maker&query=_ID>1')
exhibs_response =  requests.get('http://127.0.0.1:8080/results.html?layout=ccma_exhibs&format=shtml&maximumrecords=9000&recordType=objects_1&query=_ID>1')

if objects_response.status_code == 200:
	print "Got objects and exhibitions successfully."
	objects = objects_response.content

if artists_response.status_code == 200:
	print "Got artists successfully"
	artists = artists_response.content

if exhibs_response.status_code == 200:
	print "Got exhibitions successfully"
	exhibs = exhibs_response.content

# 1: Strip <pre> HTML tags
objects = objects.replace('<pre>','')
objects = objects.replace('</pre>','')

artists = artists.replace('<pre>','')
artists = artists.replace('</pre>','')

exhibs = exhibs.replace('<pre>','')
exhibs = exhibs.replace('</pre>','')

# 2: Strip trailing commas out of each
objects = ''.join( objects.rsplit(',',1) )
artists = ''.join( artists.rsplit(',',1) )
exhibs = ''.join( exhibs.rsplit(',',1) )

# 3: Strip ^M chars out (necessary? may have just been curl being prickish)
objects = objects.replace('\r', '')
artists = artists.replace('\r','')
exhibs = exhibs.replace('\r','')

# 3a: Go through each line and make sure it ends with '{' , '}' , '[' , ']' , '"', or ','.
# If it doesn't, append the next line (catches weird error where EOL is in embark fields)
# FIXME: A gross hack, need to find all entries of this kind and fix them.

lines = objects.splitlines()
for i,line in enumerate(lines):
	if line.endswith( ('Y', 'i') ):
		lines[i+1] = lines[i] + lines[i+1]
		lines.pop(i)
objects = ''.join(lines)

# 4: Make dicts from the JSON strings
objects_dict = json.loads(objects)
artists_dict = json.loads(artists)
exhibs_dict = json.loads(exhibs)

# 5: Fix image links in objects, in 'ThumbnailPath' and 'PreviewPath' (reserving ImagePath for full-res)
for obj in objects_dict['objects']:
	if 'PreviewPath' in obj:
		obj['PreviewPath'] = obj['PreviewPath'].replace('/Media','http://embark.colby.edu:8080')
	if 'ThumbnailPath' in obj:
		obj['ThumbnailPath'] = obj['ThumbnailPath'].replace('/Media','http://embark.colby.edu:8080')
	if 'ImagePath' in obj:
		obj['ImagePath'] = obj['ImagePath'].replace('/Media','http://embark.colby.edu:8080')
		
# 6: Make objects, artists, and exhibitions into one JSON dict
objects_dict.update(exhibs_dict)
objects_dict.update(artists_dict)

# 7: Write out 
f = open('ccma.json', 'w')
json.dump(objects_dict,f)
f.close()

