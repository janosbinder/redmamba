import re
import string
import random

from html import *

import mamba.setup
import mamba.task
import mamba.http
import pg

class MockSubcell(mamba.task.Request):
	conn_info = ['localhost','5432','ljj','visualization']
	table = "figures"
	
	def main(self):
		rest = mamba.task.RestDecoder(self)

		page = XPage("Localization, Localization, Localization")

		evidence = XGroup(page.frame.content, "Overview - Evidence channels")
		XSection(evidence.body, "Results from different subcellular localization methods", "Press refresh if you are not satisfied with the results. Then the monkeys will be shocked in the box and they will paint the squares with different green")
		xsvg(evidence.body, svg_colorer.get_figure_from_file("www/figures/overview_figure.svg"), self.get_mock_different_methods(9606, 'fake'))
		
		kingdoms = XGroup(page.frame.content, "Cell types - Kingdoms of life")

		XSection(kingdoms.body, "Results from text mining - plant", "Press refresh if you are not satisfied with the results. Then the boxes will be colored here using some random noise")
		xsvg(kingdoms.body, svg_colorer.get_figure(self.conn_info,self.table,'cell_plants'), self.get_mock_subcell_loc(9606, 'fake'))

		XSection(kingdoms.body, "Results from text mining - animal", "Press refresh if you are not satisfied with the results. Then the boxes will be colored here using some random noise")
		xsvg(kingdoms.body, svg_colorer.get_figure(self.conn_info,self.table,'cell_animals'), self.get_mock_subcell_loc(9606, 'fake'))
		
		XSection(kingdoms.body, "Results from text mining - fungus", "Press refresh if you are not satisfied with the results. Then the boxes will be colored here using some random noise")
		xsvg(kingdoms.body, svg_colorer.get_figure(self.conn_info,self.table,'cell_fungi'), self.get_mock_subcell_loc(9606, 'fake'))

		reply = mamba.http.HTMLResponse(self, page.tohtml())
		reply.send()
		
	def get_mock_subcell_loc(self, type, id):
		compartments = ['nu','cy','cs','pe','ly','er','go','pm','en','va','ex','mi']
		compartment_score_map = {}
		random.seed()
		for compartment in compartments:
			compartment_score_map[compartment] = MockSubcell.define_color(random.random())
		return compartment_score_map
	
	def get_mock_different_methods(self, type, id):
		compartments = ['nu','cy','cs','pe','ly','er','go','pm','en','va','ex','mi']
		methods = ['YLocH','YLocL','TargetP','PSORT','LocTree','KnowPred','BaCellLo']
		compartment_score_map = {}
		random.seed()
		for method in methods:
			for compartment in compartments:
				entry = method + "-" + compartment
				compartment_score_map[entry] = MockSubcell.define_color(random.random())
		return compartment_score_map
	
	@staticmethod
	def define_color(w):
		return "#%02x%02x%02x" % (255*(1-w), 255*(1-0.5*w), 255*(1-w))

class Subcell(mamba.task.Request):
	#TODO, make database connection work, make sure that it can accept passed parameters
	#create some normal HTML page
	#p53 ensembl ENSP00000269305
	
	conn_string = ['localhost','5432','ljj','knowledge']	
	go_location_dict = {'GO:0005576':'ex', 'GO:0005634':'nu', 'GO:0005739':'mi', 'GO:0005764':'ly', 'GO:0005768':'en', 'GO:0005773':'va', 'GO:0005777':'pe', 'GO:0005783':'er', 'GO:0005794':'go', 'GO:0005829':'cy', 'GO:0005856':'cs', 'GO:0005886':'pm', 'GO:0009507':'ch'}
	
	def main(self):
		# these variables should be passed as parameters		
		type = 9606
		id = 'ENSP00000269305'
		
		rest = mamba.task.RestDecoder(self)
		page = XPage("Localization, Localization, Localization")
		content = page.frame.content
		XSection(content, "Results from text mining", "Here is some fact about p53")
		xsvg(content, "www/figures/subcell.svg", self.get_localizations(type, id))
		reply = mamba.http.HTMLResponse(self, page.tohtml())
		reply.send()
		
	def get_localizations(self, type, id):
		compartment_score_map = {}
		for go in Subcell.go_location_dict:
			compartment_score_map[Subcell.go_location_dict[go]] = 0.0
		conn = pg.connect(host = self.conn_string[0], port = int(self.conn_string[1]), user = self.conn_string[2], passwd = '', dbname = self.conn_string[3])
		query = conn.query("SELECT * FROM knowledge WHERE type1 = %s AND id1 = '%s'" % (pg.escape_string(str(type)), pg.escape_string(id)))
		for result in query.dictresult():
			if (result['id2'] in self.go_location_dict):
				weight = float(result['score'])/5
				compartment_score_map[self.go_location_dict[result['id2']]] = weight
		compartment_score_map = {'va': 0.0, 'ch': 0.0, 'mi': 0.0, 'cs': 0.0, 'cy': 0.4, 'en': 0.1, 'ex': 0.0, 'pe': 0.0, 'go': 0.3, 'ly': 0.0, 'er': 0.2, 'nu': 0.5, 'pm': 0.0}
		conn.close()
		return compartment_score_map
		
		

class xsvg(XNode):
	
	def __init__(self, parent, input_string, compartment_color_map):
		XNode.__init__(self, parent)
		self.input_string = input_string
		self.compartment_color_map = compartment_color_map
		
	def begin_html(self):
		return svg_colorer.create_colored_html(self.input_string, self.compartment_color_map)

class svg_colorer:
	
	@staticmethod
	def get_figure(conn_info, table, figure):
		conn_info = ['localhost','5432','ljj','visualization']
		table = "figures"
		#figure = "cell_animals"
		database = pg.connect(host=conn_info[0], port=int(conn_info[1]), user=conn_info[2], passwd='', dbname=conn_info[3])
		q  = database.query("SELECT svg FROM %s WHERE figure = '%s';" % (pg.escape_string(str(table)),pg.escape_string(str(figure)))).getresult()
		if len(q) != 1:
			raise Exception, "Error: No figure called %s from table %s has been returned" % figure, table
		return q[0][0]
		
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
	def create_colored_html(input_svg, compartment_color_map):	
		buf = [];
		exp = svg_colorer.concatenate_list(compartment_color_map.keys(),'<.* title="','".*>','|')
		for line in input_svg.split("\n"):
			if re.search("^ *<[?!]", line): #ignore XML header
				continue
			match = re.search(exp, line)
			if match:
				for key, value in compartment_color_map.iteritems():
					match2 = re.search('title="'+key+'"',line)
					if match2:
						buf.append(re.sub('(?<=fill:|ill=")#.{6}', '%s' % value, line))
			else:
				buf.append(line)
		return string.join(buf,"\n")
		
	@staticmethod
	def get_figure_from_file(filename):
		f = open(filename, 'r')
		buf = []
		for line in f:
			line = line[:-1]
			buf.append(line)
		f.close()
		return string.join(buf,"\n")

