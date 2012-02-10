import os
import sys
import re
import string
import random
import tempfile

import html

import mamba.setup
import mamba.task
import mamba.http

class Subcell(mamba.task.Request):
	
	def main(self):
		rest = mamba.task.RestDecoder(self)
		page = html.xpage("Localization, Localization, Localization")
		page.get_content().add(xsvg("www/figures/overview_figure.svg", get_mock_different_methods(9606, 'fake')))
		#page.get_content().add(html.xfree('<img src="figures/figure.png">'))
		reply = mamba.http.HTMLResponse(self, page.tohtml())
		reply.send()
	

class xmock_subcell(html.xnode):
	def __init__(self, type, id):
		html.xnode.__init__(self)
		self.type = type
		self.id = id
		
class xxmock_overviewtable(html.xnode):
	def __init__(self, type, id):
		html.xnode.__init__(self)
		self.type = type
		self.id = id

class xsvg(html.xnode):
	def __init__(self, filename, compartment_color_map):
		html.xnode.__init__(self)
		self.filename = filename
		self.compartment_color_map = compartment_color_map
		
	def begin_html(self):
		return svg_colorer.create_colored_html(self.filename, self.compartment_color_map)
	
def get_mock_subcell_loc(type,id):
	compartments = ['nu','cy','cs','pe','ly','er','go','pm','en','va','ex','mi']
	compartment_score_map = {}
	random.seed()
	for compartment in compartments:
		compartment_score_map[compartment] = random.random()
	return compartment_score_map

def get_mock_different_methods(type, id):
	compartments = ['nu','cy','cs','pe','ly','er','go','pm','en','va','ex','mi']
	methods = ['YLocH','YLocL','TargetP','PSORT','LocTree','KnowPred','BaCellLo']
	compartment_score_map = {}
	random.seed()
	for method in methods:
		for compartment in compartments:
			entry = method + "-" + compartment
			compartment_score_map[entry] = random.random()
	return compartment_score_map

class svg_colorer:
	
	@staticmethod
	def define_color(weight):
		r=0
		dr=0
		g=0
		dg=255
		b=0
		db=0
		color = "#%2.2x%2.2x%2.2x" % (r+dr*float(weight), g+dg*float(weight), b+db*float(weight))
		return color
	
	@staticmethod
	def concatenate_list(mylist, prefix, suffix, separator):
		str_list = [];
		for s in mylist:
			str_list.append(prefix)
			str_list.append(s)
			str_list.append(suffix)
			str_list.append(separator)
		str_list.pop();
		return string.join(str_list,'')

	@staticmethod
	def create_colored_html(filename, compartment_color_map):
		buffer = [];
		f = open(filename, 'r')
		tmp1 = tempfile.mktemp()
		tmp2 = tempfile.mktemp()
		os.system("convert -size 400x300 %s %s" % (tmp1, tmp2))
		exp = svg_colorer.concatenate_list(compartment_color_map.keys(),'<\w* title="','".*>','|')
		for line in f:
			if re.search("^ *<[?!]", line): #ignore XML header
				continue
			line = line[:-1]
			match = re.search(exp, line)
			if match:
				for key, value in compartment_color_map.iteritems():
					match2 = re.search('title="'+key+'"',line)
					if match2:				   
						buffer.append(re.sub('fill="#.{6}"', 'fill="%s"' % svg_colorer.define_color(value), line))
			else:
				buffer.append(line)
		f.close()
		return string.join(buffer,"\n")

