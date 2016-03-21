import json
import os
import pprint
import time
import geocoder


def parse_result(result_file):
    with open(result_file) as f:
        raw = f.read()
        return json.loads(raw)


def extract_offset(json_input):
    max_o = 0
    for key in sorted(json_input):
        blob = json_input[key]
        if 'instances' in blob:
            for instance in blob['instances']:
                o = instance['offset']
                if o > max_o:
                    max_o = o
    return max_o


def extract_places(json_input, max_offset):
    register = dict()
    for key in sorted(json_input):
        blob = json_input[key]
        if '_type' in blob and blob['_type'] in ["City", "Country", "Region", "ProvinceOrState"]:
            if 'resolutions' in blob:
                place = blob['resolutions'][0]
            else:
                place = blob
            instances = blob['instances']

            for instance in instances:
                adjusted_offset = instance['offset'] + max_offset
                instance['offset'] = adjusted_offset
                instance.update(place)
                if 'shortname' not in instance:
                    instance['shortname'] = instance['name']
                register[adjusted_offset] = instance
    return register


def process_place(place):
    name = place['name']
    lat, lng = '', ''
    if 'latitude' in place and 'longitude' in place:
        lat = str(place['latitude'])
        lng = str(place['longitude'])
    return name + '(' + lat + ',' + lng + ')'


if __name__ == '__main__':
    results = os.listdir('output')
    places = dict()
    max_offset = 0
    for result in results:
        print('NOW PARSING:', result)
        parsed_json = parse_result('output/' + result)
        places.update(extract_places(parsed_json, max_offset))
        max_offset += extract_offset(parsed_json)

    for instance in sorted(places):
        place = places[instance]
        # print(place['offset'], place['exact'])
        if 'longitude' not in place:
            print('Geocoding:', place['name'])
            print('Context:', place['detection'])
            g = geocoder.google(place['name'])
            pprint.pprint(g.json)
            time.sleep(1)
