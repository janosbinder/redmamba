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
import pg

class MockSubcell(mamba.task.Request):
	
	def main(self):
		rest = mamba.task.RestDecoder(self)
		page = html.xpage("Localization, Localization, Localization")
		page.get_content().add(html.xsection("Results from different subcellular localization methods", "Press refresh if you are not satisfied with the results. Then the monkeys will be shocked in the box and they will paint the squares with different green"))
		page.get_content().add(xsvg("www/figures/overview_figure.svg", self.get_mock_different_methods(9606, 'fake')))
		page.get_content().add(html.xsection("Results from text mining", "Press refresh if you are not satisfied with the results. Then the boxes will be colored here using some random noise"))
		page.get_content().add(xsvg("www/figures/subcell.svg", self.get_mock_subcell_loc(9606, 'fake')))
		#page.get_content().add(html.xfree('<img src="figures/figure.png">'))
		reply = mamba.http.HTMLResponse(self, page.tohtml())
		reply.send()
		
	def get_mock_subcell_loc(self, type, id):
		compartments = ['nu','cy','cs','pe','ly','er','go','pm','en','va','ex','mi']
		compartment_score_map = {}
		random.seed()
		for compartment in compartments:
			compartment_score_map[compartment] = random.random()
		return compartment_score_map
	
	def get_mock_different_methods(self, type, id):
		compartments = ['nu','cy','cs','pe','ly','er','go','pm','en','va','ex','mi']
		methods = ['YLocH','YLocL','TargetP','PSORT','LocTree','KnowPred','BaCellLo']
		compartment_score_map = {}
		random.seed()
		for method in methods:
			for compartment in compartments:
				entry = method + "-" + compartment
				compartment_score_map[entry] = random.random()
		return compartment_score_map

class Subcell(mamba.task.Request):
	#TODO, make database connection work, make sure that it can accept passed parameters
	#create some normal HTML page
	#p53 ensembl ENSP00000269305
	
	conn_string = ['localhost','5432','ljj','knowledge']	
	go_location_dict = {'GO:0005576':'ex', 'GO:0005634':'nu', 'GO:0005739':'mi', 'GO:0005764':'ly', 'GO:0005768':'en', 'GO:0005773':'va', 'GO:0005777':'pe', 'GO:0005783':'er', 'GO:0005794':'go', 'GO:0005829':'cy', 'GO:0005856':'cs', 'GO:0005886':'pm', 'GO:0009507':'ch'}
	
	def main(self):
		rest = mamba.task.RestDecoder(self)
		page = html.xpage("Localization, Localization, Localization")
		page.get_content().add(html.xsection("Results from text mining", "Here is some fact about p53"))
		page.get_content().add(xsvg("www/figures/subcell.svg", self.get_localizations(9606, 'ENSP00000269305')))
		reply = mamba.http.HTMLResponse(self, page.tohtml())
		reply.send()
		
	def get_localizations(self, type, id):
		compartment_score_map = {}
		conn = pg.connect(host = self.conn_string[0], port = int(self.conn_string[1]), user = self.conn_string[2], passwd = '', dbname = self.conn_string[3])
		query = conn.query("SELECT * FROM knowledge WHERE type1 = %s AND id1 = '%s'" % (type, id))
		for result in query.dictresult():
			#print result['id1']+result['id2']+"\n"
			
			if (result['id2'] in self.go_location_dict):
				compartment_score_map[self.go_location_dict[result['id2']]] = float(result['score'])/5
				
		conn.close()
		return compartment_score_map
		
		

class xsvg(html.xnode):
	def __init__(self, filename, compartment_color_map):
		html.xnode.__init__(self)
		self.filename = filename
		self.compartment_color_map = compartment_color_map
		
	def begin_html(self):
		return svg_colorer.create_colored_html(self.filename, self.compartment_color_map)

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

