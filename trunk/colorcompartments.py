#!/usr/bin/env python
# file: colorcompartments.py

import sys
import re
import string
import random


header = '<html><body><h1>This is some cell SVG</h1>'
footer = '</body></html>'

#compartment = sys.argv[2]
#weight = float(sys.argv[3])
#input = sys.argv[2]
#filename = sys.argv[1]

def show_subcell_loc(type,id):
	#some database lookup stuff
	filename = 'subcell.svg'
	print header
	#print create_colored_html(filename,create_compartment_score(input))
	print create_colored_html(filename,get_mock_subcell_loc(0,0))
	print footer
	return

def show_different_methods(type,id):
	#some database lookup stuff
	filename = 'figure.svg'
	print header
	#print create_colored_html(filename,create_compartment_score(input))
	print create_colored_html(filename,get_mock_different_methods(0,0))
	print footer
	return

def get_mock_subcell_loc(type,id):
	compartments = ['nu','cy','cs','pe','ly','er','go','pm','en','va','ex','mi']
	compartment_score_map = {}
	random.seed()
	for compartment in compartments:
		compartment_score_map[compartment] = random.random()
	return compartment_score_map

def get_mock_different_methods(type,id):
	compartments = ['nu','cy','cs','pe','ly','er','go','pm','en','va','ex','mi']
	methods = ['YLocH','YLocL','TargetP','PSORT','LocTree','KnowPred','BaCellLo']
	compartment_score_map = {}
	random.seed()
	for method in methods:
		for compartment in compartments:
			entry = method + "-" + compartment
			compartment_score_map[entry] = random.random()
	return compartment_score_map

def create_compartment_score(input):
	compartment_score_pairs = input.split(';')
	compartment_score = {}
	for pair in compartment_score_pairs:
		[compartment, weight] = pair.split(',',2)
		compartment_score[compartment] = weight
	return compartment_score;

def define_color(weight):
	r=0
	dr=0
	g=0
	dg=255
	b=0
	db=0
	color = "#%2.2x%2.2x%2.2x" % (r+dr*float(weight), g+dg*float(weight), b+db*float(weight))
	return color

#print color

def concatenate_list(mylist, prefix, suffix, separator):
	str_list = [];
	for s in mylist:
		str_list.append(prefix)
		str_list.append(s)
		str_list.append(suffix)
		str_list.append(separator)
	str_list.pop();
	return string.join(str_list,'')

def create_colored_html(filename, compartment_color_map):
	buffer = [];
	f = open(filename, 'r')
	#change this line to more generic
	
	exp = concatenate_list(compartment_color_map.keys(),'<\w* title="','".*>','|')

	for line in f:
		line = line[:-1]
		if re.search("^ *<\?", line): #ignore XML header
			continue
		match = re.search(exp, line)
		if match:
			for key, value in compartment_color_map.iteritems():
				match2 = re.search('title="'+key+'"',line)
				if match2:				   
					buffer.append(re.sub('fill="#.{6}"', 'fill="%s"' % define_color(value), line))
		else:
			buffer.append(line)
	f.close()
	return string.join(buffer,"\n")

show_subcell_loc(0,0)