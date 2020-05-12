"""
Update City and Street names from input OSM data
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

# Expected names in the data
expected = ["Bengaluru", "Road", "Main", "Cross"]

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

# Create list of mapping keys
mapping_keys = []
for k,v in mapping.items():
    mapping_keys.append(k)

# Compare city name with mapping and update
def update_city_name(name):
    """
         Update of city name as per mapping
         Arguments:
                   name (string): city name as input
         Returns:
                   name (string): updated city name as per mapping
    """
    if name in mapping_keys:
        good = mapping[name]
        return good
    else:
        return name

# Auditing city names and postal codes by creating dictionary of City names and associated postal codes from input data
def audit_city_st(city_st, city, st):
    """
         Includes city name and street name into city_st dictionary if not present
         Arguments:
                   city_st (dict): array of city names and street names
                   city (string): city name to include
                   st (string): street name to include
         Returns:
                   city_st (dict): updated dictionary
    """
    if city in city_st:
        if st in city_st[city]:
            city_st[city][st] += 1
        else:
            city_st[city][st] = 1
    else:
        city_st[city][st] = 1


def audit(filename):
    """
         Parse through input file and extract city names and street names
         Arguments:
                   filename (xml): input OSM (xml) file
         Returns:
                   city_st (dict): array of city names and street names
    """
    city_st = defaultdict(dict)
    for event, elem in ET.iterparse(filename, events=('start',)):
        if elem.tag == 'node' or elem.tag == 'way':
            city = ''
            st = ''
            for tag in elem.iter('tag'):
                if tag.attrib['k'] == 'addr:city':
                    city = tag.attrib['v']
                if tag.attrib['k'] == 'addr:street':
                    st = tag.attrib['v']
            if city != '' or st != '':
                audit_city_st(city_st, city, st)
    return city_st

update = audit(OSMFILE)

# Print the updated city names
for city_name in update.items():
    for name in city_name:
        better_name = update_city_name(name)
        print (name, "=>", better_name)

# Change first letter from lowercase to uppercase
def string_case(s):
    """
         Checks and then updates a string's first letter from lowercase to uppercase
         Arguments:
                   s (string): input string
         Returns:
                   s (string): updated string
    """
    if s.isupper():
        return s
    else:
        return s.title()

# Compare street name with mapping and update
def update_name_st(name, mapping):
    """
         Checks and then updates a string's first letter from lowercase to uppercase
         Arguments:
                   name (string): street name to be checked against proposed corrections in mapping
                   mapping (array): proposed corrections
         Returns:
                   name (string): updated street name
    """
    name = re.sub('[^a-zA-Z.,;\d\s]', '', name)
    name = name.split(' ')
    for i in range(len(name)):
        if name[i] in mapping:
            name[i] = mapping[name[i]]
            name[i] = string_case(name[i])
        else:
            name[i] = string_case(name[i])
    
    name = ' '.join(name)
   
    return name

# Print the updated street names
for city_name, street in update.items():
    for name in street:
        better_name = update_name_st(name, mapping)
        print (name, "=>", better_name)