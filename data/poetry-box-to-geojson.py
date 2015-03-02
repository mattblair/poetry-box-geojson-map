"""
This script converts the original data fetched from CouchDB and reformatted for import into the iOS app back in 2012 into GeoJSON.

It also adds properties specific to display using mapbox.js and variants.

"""

import os
import json
import uuid
from datetime import datetime
from urlparse import urlparse

data_import_dir = "/Users/matt/Documents/codeProjects/poetry-box-map/data/"

# Set manually, for revision control. Do not derive from actual date.
datestamp_string = "150301"

iso8601_format = '%Y-%m-%dT%H:%M:%SZ' # hard-coded timezone?

original_json_path = os.path.join(data_import_dir, "poetry-boxes121025.json")
output_geojson_path = os.path.join(data_import_dir, "poetry-boxes%s.geojson" % datestamp_string)


with open(original_json_path, 'r') as infile:
    box_collection = json.load(infile)

box_list = []

for flat_box_dict in box_collection:
    box_properties_dict = {}
    box_geojson_dict = {}
    geometry_dict = {}
        
    # keep only the filename
    if 'photoURL' in flat_box_dict:
        parsed_url = urlparse(flat_box_dict['photoURL'])
        box_properties_dict['photoName'] = os.path.basename(parsed_url.path)
        
        # only set the photo credit if we actually have a photo
        if 'photoCredit' in flat_box_dict:
            box_properties_dict['photoCredit'] = flat_box_dict['photoCredit']
        else:
            box_properties_dict['photoCredit'] = "Unknown"
    
    box_properties_dict['builder'] = flat_box_dict['builtBy']
    
    box_properties_dict['addr1'] = flat_box_dict['addr1']
    box_properties_dict['addr2'] = flat_box_dict['addr2']
    box_properties_dict['city'] = flat_box_dict['city']
    box_properties_dict['state'] = flat_box_dict['state']
    box_properties_dict['country'] = flat_box_dict['country']
    box_properties_dict['postalCode'] = flat_box_dict['postalCode']
    
    box_properties_dict['owner'] = flat_box_dict['owner']
    box_properties_dict['submittedByName'] = flat_box_dict['submittedByName']
    
    # replace blank space with T
    box_properties_dict['submittedDate'] = flat_box_dict['submittedDate'].replace(" ", "T")
    box_properties_dict['modifiedDate'] = flat_box_dict['modifiedDate'].replace(" ", "T")
    
    # For generating identifiers post-Couch:
    # box_id = uuid.uuid4().hex
    box_properties_dict['uuid'] = flat_box_dict['couchID']
    
    # Mapbox presentation keys
    box_properties_dict['title'] = flat_box_dict['addr1']
    if len(box_properties_dict['builder']) > 0 and box_properties_dict['builder'] != "Unknown":
        box_properties_dict['description'] = "Built by %s" % box_properties_dict['builder']
    else:
        box_properties_dict['description'] = "Last updated: %s" % box_properties_dict['modifiedDate']
    
    # structure it as GeoJSON
    geometry_dict['type'] = "Point"
    geometry_dict['coordinates'] = [flat_box_dict['longitude'], 
                                    flat_box_dict['latitude']]
    
    box_geojson_dict['geometry'] = geometry_dict
    box_geojson_dict['type'] = "Feature"
    box_geojson_dict['properties'] = box_properties_dict
    
    # make the id key a peer of the properties key, in accordance with 
    # 2.2 of GeoJSON spec: http://geojson.org/geojson-spec.html#feature-objects
    box_geojson_dict['id'] = box_properties_dict['uuid']
    
    box_list.append(box_geojson_dict)


boxes_geojson = {}
boxes_geojson['type'] = "FeatureCollection"
boxes_geojson['features'] = box_list

with open(output_geojson_path, 'w') as outfile:
    json.dump(boxes_geojson, outfile, indent=4)