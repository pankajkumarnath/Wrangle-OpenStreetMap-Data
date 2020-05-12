"""
Auditing Street Names from sample data
v1.1: Docstrings included for functions
v1.0
"""

import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict

# Input OSM file

OSMFILE = "sample.osm"
#OSMFILE = "map.osm"

# Compiling a regular expression pattern into a regular expression object
st_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


# List of expected street types
expected_st_types = ['Main', 'Road', 'Cross']


# Auditing street name by creating a dictionary of street types and names
def audit_st_type(st_types, st_name):
    """
         Parse through input file and extract city names and corresponding post codes
         Arguments:
                   st_types (dict): array fo street type and street name to be updated
                   st_name (string): complete street name to include
         Returns:
                   st_types (dict): updated dictionary
    """
    m = st_type_re.search(st_name)
    if m:
        st_type = m.group()
        if st_type not in expected_st_types:
            st_types[st_type].add(st_name)


def audit_st(filename):
    """
         Parse through input file and extract street names
         Arguments:
                   filename (xml): input OSM (xml) file
         Returns:
                   st_types (dict): array of street types and street names
    """
    st_types = defaultdict(set)
    for event, elem in ET.iterparse(filename, events=('start',)):
        if elem.tag == "way" or elem.tag == 'node':
            for tag in elem.iter('tag'):
                if tag.attrib['k'] == 'addr:street':
                    audit_st_type(st_types, tag.attrib['v'])
    return st_types

st_types = audit_st(OSMFILE)

# Printing the dictionary to visualize the data for auditing
pprint.pprint(dict(st_types))