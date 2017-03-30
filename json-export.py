#!/usr/local/bin/python
'''
Colby College Museum of Art JSON export script, V1.0
Simple script to download JSON from the webKiosk, do some basic cleanup of embark webkiosk quirks (HTML tag removal and making valid JSON)
'''
import requests, re, json, argparse
from pprint import pprint
import HTMLParser

#-1: Parse command line args
'''
parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url", required = True, help = "URL of the embark server (eg, http://embark.colby.edu)")
parser.add_argument("-l","--layout", required = True, help = "Template layout name (eg, ccma_objects)")
parser.add_argument("-a","--all", required = False, help = "Get all objects")
parser.add_argument("-t","--type", required = True, help="Embark record type (ie, objects_1, artist_maker, etc)")
args = vars(parser.parse_args())
'''

# 0: Get objects, artists, and exhibitions from the embark webkiosk
objects_response = requests.get('http://embark.colby.edu/results.html?layout=ccma_objects&format=shtml&maximumrecords=-1&recordType=objects_1&query=_ID>1')
artists_response = requests.get('http://embark.colby.edu/results.html?layout=ccma_artists&format=shtml&maximumrecords=-1&recordType=artist_maker&query=_ID>1')
exhibs_response =  requests.get('http://embark.colby.edu/results.html?layout=ccma_exhibs&format=shtml&maximumrecords=-1&recordType=objects_1&query=_ID>1')

if objects_response.status_code == 200:
	print "Got objects and exhibitions successfully."
	objects = objects_response.content

if artists_response.status_code == 200:
	print "Got artists successfully"
	artists = artists_response.content

if exhibs_response.status_code == 200:
	print "Got exhibitions successfully"
	exhibs = exhibs_response.content

# Data-munging hacks to get around limits in Embark template language... 

# 1: Strip <pre> HTML tags
objects = objects.replace('<pre>','')
objects = objects.replace('</pre>','')

artists = artists.replace('<pre>','')
artists = artists.replace('</pre>','')

exhibs = exhibs.replace('<pre>','')
exhibs = exhibs.replace('</pre>','')

# 2: Strip trailing commas out of each table
objects = ''.join( objects.rsplit(',',1) )
artists = ''.join( artists.rsplit(',',1) )
exhibs = ''.join( exhibs.rsplit(',',1) )

# 2a: Strip trailing commas out of object images array
# Matches a magic pattern--"},]"
regex = re.compile("}[ \t]+,[ \t]+\]", re.MULTILINE)
objects = regex.sub('} ]',objects)

# 3: Strip ^M chars out (necessary? may have just been curl being prickish)
objects = objects.replace('\r', '')
artists = artists.replace('\r','')
exhibs = exhibs.replace('\r','')

# =======
# 3a: Go through each line and make sure it ends with '{' , '}' , '[' , ']' , '"', or ','.
# If it doesn't, append the next line (catches weird error where EOL is in embark fields)
# FIXME: A gross hack, need to find all entries of this kind and fix them.

lines = objects.splitlines()
for i,line in enumerate(lines):
	if line.endswith( ('Y', 'i') ):
		print line
		lines[i+1] = lines[i] + lines[i+1]
		lines.pop(i)
objects = ''.join(lines)

# 4: Make dicts from the JSON strings
objects_dict = json.loads(objects)
artists_dict = json.loads(artists)
exhibs_dict = json.loads(exhibs)
				
# 5(-a): Unescape fields in all objects and fix image links in objects
# FIXME: This should be done in template w/ 4DHTML/4DVAR tags
parser = HTMLParser.HTMLParser()
for obj in objects_dict['objects']:
	
	for key,value in obj.iteritems():
		if isinstance(value, basestring):
			obj[key] = parser.unescape(value)

	for image in obj['Images']:
		path = image.get('ImagePath')
		iiif = image.get('IIIF_URL')
		
		if path and iiif:
			print "Fixing image %s" % path
			image['ImagePath'] = path.replace("_cd.jpg","").replace("http://iiif.museum.colby.edu/","https://iiif.museum.colby.edu/image/")
			image['IIIF_URL'] = iiif.replace("_cd.jpg","").replace("http://","https://")

for artist in artists_dict['artists']:
	for key,value in artist.iteritems():
		if isinstance(value, basestring):
			artist[key] = parser.unescape(value)

for exhib in exhibs_dict['exhibitions']:
	for key,value in exhib.iteritems():
		if isinstance(value, basestring):
			exhib[key] = parser.unescape(value)

# 6: Make objects, artists, and exhibitions into one JSON dict
objects_dict.update(exhibs_dict)
objects_dict.update(artists_dict)

# 7: Write out 
with open('ccma.json', 'w') as f:
	json.dump(objects_dict,f, sort_keys=True, indent=4, separators=(',', ': '))

