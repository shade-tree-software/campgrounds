import pandas as pd
import json
import sys
from xml.sax.saxutils import escape

input_filename = sys.argv[1]
output_filename = sys.argv[2]

with open(input_filename, "rt") as f:
    input_data = json.loads(f.read())

with open(output_filename, "wt") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    f.write('<Document>\n')
    for elem in input_data:
        loc = elem.get("location", None)
        if loc is not None:
            f.write('<Placemark>\n')
            f.write(f'  <name>{escape(elem["name"])}</name>\n')
            alt = elem.get("elevation")
            if alt is None:
                alt = 0
                elevation = "unknown"
            elif alt < 2000:
                elevation = "low"
            elif alt >= 2000 and alt < 2500:
                elevation = "2000+"
            elif alt >= 2500 and alt < 3000:
                elevation = "2500+"
            elif alt >= 3000 and alt < 3500:
                elevation = "3000+"
            elif alt >= 3500 and alt < 4000:
                elevation = "3500+"
            else:
                elevation = "4000+"
            f.write(f"  <elevation>{escape(elevation)}</elevation>\n")
            lat, lon = loc.split(",")
            f.write("  <Point>\n")
            f.write(f"    <coordinates>{lon},{lat},{alt}</coordinates>\n")
            f.write("  </Point>\n")
            note = elem.get("note", None)
            if note is not None:
                f.write(f"  <note>{escape(note)}</note>\n")
            f.write('</Placemark>\n')
    f.write('</Document>\n</kml>')
