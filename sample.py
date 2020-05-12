"""
Extract a smaller sample data from original OSM data
v1.1: Docstrings included for functions
v1.0
"""

import xml.etree.cElementTree as ET

# Name of Original (larger) OSM data
OSMFILE = "map.osm"

# Name of smaller sample extract to be created
SAMPLEFILE = "sample.osm"

# Extraction of every kth top level element from original OSM data (OSMFILE)
k = 50 

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """
         extract element from xml file
         Arguments:
                   osm_file (xml): input osm file
                   tags (array): tags we are looking for
         Returns:
                   elem (string): element string extracted
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

# Writing the extract into new sample OSM data file (SAMPLEFILE)
with open(SAMPLEFILE, 'w') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every kth top level element
    for i, element in enumerate(get_element(OSMFILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='unicode'))

    output.write('</osm>')