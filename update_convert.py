"""
Update original OSM data in line to audit outcomes and convert to CSVs
v1.1: Docstrings included for functions
v1.0
"""

import clean_city_street
import clean_postcode
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
import schema

# Input OSM file

#OSMFILE = "sample.osm"
OSMFILE = "map.osm"

# Name the CSV files
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

# Compiling a regular expression pattern into a regular expression object
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Proposed cleaning for City and Street names
mapping = {"bangalore": "Bengaluru",
           "Bangalore": "Bengaluru",
           "bengaluru": "Bengaluru",
           "cross": "Cross",
           "road": "Road",
           "Ft.": "Feet",
           "ft": "Feet",
           "Rd": "Road",
           "Rd,": "Road,",
           "Rd.": "Road",
           "Apt": "Appartment",
           "Road,": "Road"
            }

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """
         Clean and shape node or way XML element to dictionary
         Key Argument:
                   element (string):xml element  
         Returns:
                   elem (string): updated xml element string extracted
    """
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []
    if element.tag == 'node':
        for i in node_attr_fields:
            node_attribs[i] = element.get(i)
        for j in element.iter('tag'):  
            tags_dict = {}
            if re.match(problem_chars,j.get('k')):
                continue
            m = re.match(LOWER_COLON,j.get('k'))
            if m:
                split_key = re.split(':',j.get('k'),maxsplit=1)
                tags_dict['id'] = node_attribs['id']
                tags_dict['key'] = split_key[1]
                if split_key[1] == 'city':
                    tags_dict['value'] = clean_city_street.update_city_name(j.get('v'))
                elif split_key[1] == 'street':
                    tags_dict['value'] = clean_city_street.update_name_st(j.get('v'), mapping)
                elif split_key[1] == 'postcode':
                    tags_dict['value'] = clean_postcode.update_pc(j.get('v'))
                else: 
                    tags_dict['value'] = j.get('v')
                tags_dict['type'] = split_key[0]
            else:
                tags_dict['id'] = node_attribs['id']
                tags_dict['key'] = j.get('k')
                tags_dict['value'] = j.get('v')
                tags_dict['type'] = 'regular'
            tags.append(tags_dict)
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        for i in way_attr_fields:
            way_attribs[i] = element.get(i)
        count = 0
        for x in element.iter('nd'):
            wn_dict = {}
            wn_dict['id'] = way_attribs['id']
            wn_dict['node_id'] = x.get('ref')
            wn_dict['position'] = count
            count += 1
            way_nodes.append(wn_dict)
        for j in element.iter('tag'):
            way_tags_dict = {}
            if re.match(problem_chars,j.get('k')):
                continue
            m = re.match(LOWER_COLON,j.get('k'))
            if m:
                split_key = re.split(':',j.get('k'),maxsplit=1)
                way_tags_dict['id'] = way_attribs['id']
                way_tags_dict['key'] = j.get('k')
                if split_key[1] == 'city':
                    way_tags_dict['value'] = clean_city_street.update_city_name(j.get('v'))
                elif split_key[1] == 'street':
                    way_tags_dict['value'] = clean_city_street.update_name_st(j.get('v'), mapping)
                elif split_key[1] == 'postcode':
                    way_tags_dict['value'] = clean_postcode.update_pc(j.get('v'))
                else: 
                    way_tags_dict['value'] = j.get('v')
                way_tags_dict['type'] = split_key[0]
            else:
                way_tags_dict['id'] = way_attribs['id']
                way_tags_dict['key'] = j.get('k')
                way_tags_dict['value'] = j.get('v')
                way_tags_dict['type'] = 'regular'
            tags.append(way_tags_dict)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


def get_element(osm_file, tags=('node', 'way', 'relation')):
    """
         extract element from xml file
         Arguments:
                   osm_file (xml): input osm file
                   tags (array): tags we are looking for
         Returns:
                   elem (string): xml element string extracted
    """
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """
         validates if element is as per eference schema or not
         Arguments:
                   element (string): element to be validated
                   validator (): validator function from cerberus
                   schema (): reference schema
    """
    if validator.validate(element, schema) is not True:
        field, errors = next(iter(validator.errors.items())) 
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow(row)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def process_map(file_in, validate):
    """
         Iteratively process each XML element and write to csv files
         Arguments:
                   file_in (xml): input xml file
                   validate (boolean): TRUE to validate or else FALSE
    """
    with codecs.open(NODES_PATH, 'w',encoding='utf8') as nodes_file, codecs.open(NODE_TAGS_PATH, 'w',encoding='utf8') as nodes_tags_file, codecs.open(WAYS_PATH, 'w',encoding='utf8') as ways_file, codecs.open(WAY_NODES_PATH, 'w',encoding='utf8') as way_nodes_file, codecs.open(WAY_TAGS_PATH, 'w',encoding='utf8') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])

process_map(OSMFILE, validate=True)