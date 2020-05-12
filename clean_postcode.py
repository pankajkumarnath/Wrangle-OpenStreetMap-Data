"""
Update Postal Code from input OSM data as per audit outcomes
v1.1: Docstrings included for functions
v1.0
"""

import re
import xml.etree.cElementTree as ET
from collections import defaultdict

# Input OSM file

OSMFILE = "sample.osm"
#OSMFILE = "map.osm"

expected = [ '',
 '560001',
 '560002',
 '560003',
 '560004',
 '560005',
 '560006',
 '560007',
 '560008',
 '560009',
 '560010',
 '560011',
 '560012',
 '560013',
 '560014',
 '560015',
 '560016',
 '560017',
 '560018',
 '560019',
 '560020',
 '560021',
 '560022',
 '560023',
 '560024',
 '560025',
 '560026',
 '560027',
 '560028',
 '560029',
 '560030',
 '560031',
 '560032',
 '560033',
 '560034',
 '560035',
 '560036',
 '560037',
 '560038',
 '560039',
 '560040',
 '560041',
 '560042',
 '560043',
 '560044',
 '560045',
 '560046',
 '560047',
 '560048',
 '560049',
 '560050',
 '560051',
 '560052',
 '560053',
 '560054',
 '560055',
 '560056',
 '560057',
 '560058',
 '560059',
 '560060',
 '560061',
 '560062',
 '560063',
 '560064',
 '560065',
 '560066',
 '560067',
 '560068',
 '560069',
 '560070',
 '560071',
 '560072',
 '560073',
 '560074',
 '560075',
 '560076',
 '560077',
 '560078',
 '560079',
 '560080',
 '560081',
 '560082',
 '560083',
 '560084',
 '560085',
 '560086',
 '560087',
 '560088',
 '560089',
 '560090',
 '560091',
 '560092',
 '560093',
 '560094',
 '560095',
 '560096',
 '560097',
 '560098',
 '560099',
 '560100']

# Some of the proposed postal code cleaning
mapping = {"5600109": "560109",
           "5600037": "560037",
          "5560034": "560034",
          "5601003": "560103",
          "628008": ""}


# Create list of mapping keys
mapping_keys = []
for k,v in mapping.items():
    mapping_keys.append(k)

# Harmonizing the Postal code as per audit outcomes
def update_pc(name):
    """
         Update of post codes as per mapping
         Arguments:
                   name (string): post code as input
         Returns:
                   name (string): updated post code as per mapping
    """
    name = name.replace(' ', '')
    name = re.sub('[^0-9]', '', name)
    if name in mapping_keys:
        good = mapping[name]
        return good
    elif len(name) != 6:
        return ''
    elif name[0:2] == '560':
        if len(name) == 6:
            return name
        else:
            return ''
    else:
        return name

# Create list of postal codes
def audit_pc(filename):
    """
         Parse through input file and extract post codes
         Arguments:
                   filename (xml): input OSM (xml) file
         Returns:
                   city_pcs (dict): array of post codes
    """
    for event, elem in ET.iterparse(filename, events=('start',)):
        if elem.tag == 'node' or elem.tag == 'way':
            pc = ''
            for tag in elem.iter('tag'):
                if tag.attrib['k'] == 'addr:postcode':
                    pc = tag.attrib['v']
            if pc != '':
                if pc not in city_pcs:
                    city_pcs.append(pc)
    return city_pcs

city_pcs = []
city_pcs = audit_pc(OSMFILE)
    
# Print the updated postal codes
for pc in city_pcs:
    better_pc = update_pc(pc)
    print (pc, "=>", better_pc)