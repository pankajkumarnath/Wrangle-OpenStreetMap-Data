"""
Auditing City name and Postal Code from Sample data
v1.1: Docstrings included for functions
v1.0
"""

import xml.etree.cElementTree as ET
import pprint
from collections import defaultdict

# Input OSM file

OSMFILE = "sample.osm"
#OSMFILE = "map.osm"


# Auditing city names and postal codes by creating dictionary of City names and associated postal codes from input data

def audit_citypc(city_pcs, city, pc):
    """
         Includes city name and post code into city_pcs dictionary if not present
         Arguments:
                   city_pcs (dict): array of city names and corresponding post codes
                   city (string): city name to include
                   pc (string): post code to include
         Returns:
                   city_pcs (dict): updated dictionary
    """
    if city in city_pcs:
        if pc in city_pcs[city]:
            city_pcs[city][pc] += 1
        else:
            city_pcs[city][pc] = 1
    else:
        city_pcs[city][pc] = 1


def audit_pc(filename):
    """
         Parse through input file and extract city names and corresponding post codes
         Arguments:
                   filename (xml): input OSM (xml) file
         Returns:
                   city_pcs (dict): array of city names and corresponding post codes
    """
    city_pcs = defaultdict(dict)
    for event, elem in ET.iterparse(filename, events=('start',)):
        if elem.tag == 'node' or elem.tag == 'way':
            city = ''
            pc = ''
            for tag in elem.iter('tag'):
                if tag.attrib['k'] == 'addr:city':
                    city = tag.attrib['v']
                if tag.attrib['k'] == 'addr:postcode':
                    pc = tag.attrib['v']
            if city != '' or pc != '':
                audit_citypc(city_pcs, city, pc)
    return city_pcs

city_pcs = audit_pc(OSMFILE)

# Printing the dictionary to visualize the data for auditing
pprint.pprint(dict(city_pcs))