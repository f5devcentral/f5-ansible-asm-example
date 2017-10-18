#!/usr/bin/env python3
"""JSON minify program. """

import json 
import sys 

def minify(file_name):
    "Minify JSON"
    file_data = open(file_name, "r", 1).read() # store file info in variable
    json_data = json.loads(file_data) # store in json structure
    #json_string = json.dumps(json_data, separators=(',', ":")) # Compact JSON structure
    json_string = json.dumps(json_data, sort_keys=True, indent=1 ) # Compact JSON structure
    file_name = str(file_name).replace(".template", "") # remove .json from end of file_name string
    new_file_name = "{0}_smaller.template".format(file_name)
    open(new_file_name, "w+", 1).write(json_string) # open and write json_string to file


ARGS = sys.argv[1:] # get arguments passed to command line excluding first arg
for arg in ARGS: # loop through arguments
    minify(arg)