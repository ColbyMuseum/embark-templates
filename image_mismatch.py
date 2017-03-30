#!/usr/local/bin/python
import json

with open('ccma.json','r') as f:
	json_data = json.load(f)

def webPMs(json_obj):
	pms = ['List of image surrogate records with "_pm" in the filename and web access enabled\n']
	for obj in json_obj['objects']:
		for img in obj['Images']:
			filename = img['ImagePath'].split('/')[-1]
			obj_accnum = obj['Disp_Access_No']
			obj_id = obj['embark_ID']
			if 'pm' in filename:
				pms.append("Object ID %s (AccNum %s) with image %s \n" % (obj_id, obj_accnum, filename))
	return pms

def mismatches(json_obj):
        mismatched = ['List of image surrogates whose filenames are different than their current accession numbers:\n']
	for obj in json_obj['objects']:
		for img in obj['Images']:
			filename = img['ImagePath'].split('/')[-1]
			file_accnum = filename.split('_')[0].strip('.jpg').strip('.JPG')
			obj_accnum = obj['Disp_Access_No']
			if file_accnum != obj_accnum:
				mismatched.append("Accession Number: %s  || Image File: %s \n" % (obj['Disp_Access_No'], filename))
	return mismatched

def FMs(json_obj):
	# FIXME: This should give me a list of FM images, and then another should give me a list of FMs that don't match the accession number
	fms = ['List of linked surrogates still located in "Lo Res and FMs":\n']
	for obj in json_obj['objects']:
		for img in obj['Images']:
			filename = img['ImagePath'].split('/')[-1]
			url = img['ImagePath']
			accession = obj['Disp_Access_No']
			if 'fm' in filename:
				fms.append("Accession: %s || FM Image File: %s\n" % (accession,filename))
	return fms

mismatched = mismatches(json_data)
pms = webPMs(json_data)
fms = FMs(json_data)

with open('mismatched.txt','w') as f:
	for item in mismatched:
		f.write(item)

with open('web_pms.txt', 'w') as f:
	for item in pms:
		f.write(item)
	
with open('misplaced_fms.txt', 'w') as f:
	for item in fms:
		f.write(item)
