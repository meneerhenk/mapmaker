#!/usr/bin/python
import urllib2
import json
import pickle
import math
postcodes = {}
vals = {}
markers = []
try:
    postcodes = pickle.load( open( "pc.p", "rb" ) )
except IOError:
    pass
f = urllib2.urlopen('https://data.rivm.nl/covid-19/COVID-19_rioolwaterdata.json')
data = json.loads(f.read())
for block in data:
  pc = block['Postal_code']
  if pc not in postcodes:
      f = urllib2.urlopen('https://api.opencagedata.com/geocode/v1/json?q='+pc+'%20Nederland&key=5ef2349fa1a8489fad3a33c34ff4b15a&no_annotations=1&language=nl')
      geo = json.loads(f.read())['results'][0]['geometry']
      postcodes[pc] = geo
      pickle.dump( postcodes, open( "pc.p", "wb" ) )
  vals[pc] = block['RNA_per_ml']
percolor = float(256*2) / math.log(max(vals.values()))
for pc in vals:
  value = (math.log(int(vals[pc])) if int(vals[pc])> 0 else 0) * percolor
  if value >= 256 :
     red = 255
     green = 256 - (value-256)
  else:
     green = 255
     red = value
  markers.append({
     "type": "Feature",
     "properties": {
       "marker-color": "#%02x%02x00" % (red,green), "marker-size": "medium", "marker-symbol": "", "location": pc, "value": vals[pc]
     },
     "geometry": {
       "type": "Point",
       "coordinates": [ postcodes[pc]['lng'], postcodes[pc]['lat'] ]
     } })
tada = { "type": "FeatureCollection", "features":  markers  }
print json.dumps(tada)
