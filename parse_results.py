import json
import os


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
            offsets = [instance['offset'] for instance in blob['instances']]
            # yield [i for i in process_place(place, offsets, max_offset)]

            for offset in offsets:
                register[offset + max_offset] = process_place(place)
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
        parsed_json = parse_result('output/' + result)
        places.update(extract_places(parsed_json, max_offset))
        max_offset = extract_offset(parsed_json)

    for place in sorted(places):
        print(place, places[place])
