"""A script to convert any XML file into a JSON file.

Requirements:

    $ pip install xmltodict

Usage:

    $ python xml_to_json.py wordpress.xml

"""
import json
import os
import sys
import time

import xmltodict


def main():
    input_filepath = sys.argv[1]
    with open(input_filepath) as f:
        data = xmltodict.parse(f.read())

    basename = os.path.basename(input_filepath)
    base, ext = os.path.splitext(basename)
    output_filepath = os.path.join(base + "." + str(time.time()) + ".json")

    with open(output_filepath, "w") as f:
        f.write(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
