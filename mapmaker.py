#!/usr/bin/python
import json
import math
import pickle
import urllib.request
from datetime import datetime, timedelta

postcodes = {}
vals = {}
dates = {}
markers = []
allvals = []
try:
    postcodes = pickle.load(open("pc.p", "rb"))
except IOError:
    pass
f = urllib.request.urlopen('https://data.rivm.nl/covid-19/COVID-19_rioolwaterdata.json')
data = json.loads(f.read())

last = datetime.strptime('1970-01-01', "%Y-%m-%d")
for block in data:
    datum = datetime.strptime(block['Date_measurement'],
                              "%Y-%m-%d" if block['Date_measurement'].startswith("2020") else "%d-%m-%Y")
    if datum > last:
        last = datum

twoweek = last - timedelta(days=14)
for block in data:
    pc = block['Postal_code']
    if pc != '' and datetime.strptime(block['Date_measurement'], "%Y-%m-%d" if block['Date_measurement'].startswith(
            "2020") else "%d-%m-%Y") >= twoweek:
        if pc not in postcodes:
            # print(pc)
            # print(block)
            f = urllib.request.urlopen('https://api.opencagedata.com/geocode/v1/json?q=' + pc + '%20' + '%20' + (
                block['RWZI_AWZI_name'].replace(' ',
                                                '%20')) + '%20Netherlands&key=5ef2349fa1a8489fad3a33c34ff4b15a&no_annotations=1&language=nl')
            data = f.read()
            js = json.loads(data)
            for res in js['results']:
                if (res['components']['_type'] == 'neighbourhood' and res['components']['country_code'] == 'nl') or \
                        res['components']['_type'] == 'postcode' or 'postcode' in res['components'] and \
                        res['components']['postcode'] == str(pc):
                    geo = res['geometry']
                    postcodes[pc] = geo
                    pickle.dump(postcodes, open("pc.p", "wb"))
                    break
            if pc not in postcodes:
                print((js['results']))
                postcodes[pc] = js['results'][0]['geometry']
        vals[pc] = block['RNA_per_ml']
        dates[pc] = block['Date_measurement']

# print "Aantal locaties",len(vals)

percolor = float(256 * 2) / math.log(1041 if max(vals.values()) < 1041 else max(vals.values()))
for pc in vals:
    value = int((math.log(int(vals[pc])) if int(vals[pc]) > 0 else 0) * percolor)
    if value >= 256:
        red = 255
        green = 256 - (value - 256)
    else:
        green = 255
        red = value
    markers.append({
        "type": "Feature",
        "properties": {
            "marker-size": "medium",
            "marker-color": "#%02x%02x00" % (red, green),
            "marker-symbol": "",
            "location": pc,
            "value": vals[pc], "date": dates[pc]
        },
        "geometry": {
            "type": "Point",
            "coordinates": [postcodes[pc]['lng'], postcodes[pc]['lat']]
        }})
tada = {"type": "FeatureCollection", "features": markers}
print((json.dumps(tada)))
