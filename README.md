# JSON and IIIF export templates for Embark Web Kiosk
This repo contains SHTML templates to export bulk JSON data and IIIF image data for the Embark WebKiosk. The big blob of JSON they produce is in [Colby's repo](https://github.com/ColbyMuseum/MuseumLOD).

## Use:
- Put `ccma_objects.shtml`, `ccma_artists.shtml`, `ccma_exhibs.shtml`, `iiif_imgs.shtml` in the Web Kiosk's `WebFolder` directory.
- **For JSON**:
	- Requests to `http://foo.bar/results.html?layout=ccma_objects&format=shtml&maximumrecords=20&recordType=objects_1&query=_ID>1` will return the first 20 objects
	- Requests to `http://foo.bar/results.html?layout=ccma_artists&format=shtml&maximumrecords=20&recordType=artist_maker&query=_ID>1` will return the first 20 artists        
	- Requests to `http://foo.bar/results.html?layout=ccma_exhibs&format=shtml&maximumrecords=20&recordType=objects_1&query=_ID>1` will return a mess of data about exhibitions 
	- We clean the results, legalize the JSON (the return is not *quite* valid due to trailing commas on some array items), and mash them together with `json_export.py`
- **For IIIF Manifests**:
	- Requests to `http://foo.bar/results.html?layout=ccma_objects&format=shtml&maximumrecords=20&recordType=objects_1&query=_ID=4204` returns a valid IIIF Presentation manifest for the object's views.

## Known Bugs:
- These are just shims--the bits that process image data use Colby's image filename convention (web-ready JPEGs end with `_cd.jpg`) to do important stuff so YMMV.
- The contents of the "exhibitions" key are pretty useless--it lists every instance of an object in an exhibition. 
- The IIIF manifests have bad Canvas height/width terms. The spurious `'height': 999` and `'width': 999`  doesn't seem to upset [UniversalViewer](http://universalviewer.io).
