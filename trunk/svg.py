import re
import string
import random

from html import *

import mamba.setup
import mamba.task
import mamba.http
import pg

class Subcell(mamba.task.Request):
	conn_info = ['localhost','5432','ljj','visualization']
	table = "figures"
	database = None
	
	def main(self):
		# these variables should be passed as parameters		
		qtype = 9606
		qid = 'ENSP00000269305'
		
		rest = mamba.task.RestDecoder(self)
		page = XPage("Localization, Localization, Localization")
		content = page.frame.content
		XSection(content, "Results from text mining", "Here is some fact about p53")
		#xsvg(content, self.get_localizations(qtype, qid))
		self.create_colored_xsvg(content, qtype, qid)
		reply = mamba.http.HTMLResponse(self, page.tohtml())
		reply.send()
		
	def db_connect(self):
		self.database = pg.connect(host=self.conn_info[0], port=int(self.conn_info[1]), user=self.conn_info[2], passwd='', dbname=self.conn_info[3])		
		
	def db_close(self):
		self.database.close()
	
	def create_colored_xsvg(self, parent, qtype, qid):
		compartment_color_map = {}
		self.db_connect()
		figure = ""
		q  = self.database.query("SELECT * FROM colors WHERE id = '%s' AND type = %i;" % (pg.escape_string(str(qid)), qtype)).getresult()
		#record[0] = type ,record[1] = id ,record[2] = figure , record[3] = label , record[4] = color
		if len(q) == 0:
			raise Exception, "Error: No record exists for %s,%s" % (str(qtype), str(qid))		
		for record in q:
			compartment_color_map[record[3]] = record[4]
			figure = record[2]
		
		svg = xsvg(parent, self.get_figure(figure))
		svg.recolor(compartment_color_map)
		self.db_close()
		return svg
		
	def get_figure(self, figure):
		q  = self.database.query("SELECT svg FROM figures WHERE figure = '%s';" % (pg.escape_string(str(figure)))).getresult()
		if len(q) != 1:
			raise Exception, "Error: No figure called %s from table %s has been returned" % figure, table
		svg = q[0][0];
		return svg

class MockSubcell(Subcell):
	conn_info = ['localhost','5432','ljj','visualization']
	table = "figures"
	
	def main(self):
		rest = mamba.task.RestDecoder(self)

		page = XPage("Localization, Localization, Localization")

		evidence = XGroup(page.frame.content, "Overview - Evidence channels")
		XSection(evidence.body, "Results from different subcellular localization methods", "Press refresh if you are not satisfied with the results. Then the monkeys will be shocked in the box and they will paint the squares with different green")
		evidence_svg = xsvg.get_svg_from_file(evidence.body, "www/figures/overview_figure.svg")
		evidence_svg.recolor(self.get_mock_different_methods(9606, 'fake'))		
		
		kingdoms = XGroup(page.frame.content, "Cell types - Kingdoms of life")

		self.db_connect()
		XSection(kingdoms.body, "Results from text mining - plant", "Press refresh if you are not satisfied with the results. Then the boxes will be colored here using some random noise")
		xsvg(kingdoms.body, self.get_figure('cell_plants')).recolor(self.get_mock_subcell_loc(9606, 'fake'))

		XSection(kingdoms.body, "Results from text mining - animal", "Press refresh if you are not satisfied with the results. Then the boxes will be colored here using some random noise")
		xsvg2 = xsvg(kingdoms.body, self.get_figure('cell_animals')).recolor(self.get_mock_subcell_loc(9606, 'fake'))
		
		XSection(kingdoms.body, "Results from text mining - fungus", "Press refresh if you are not satisfied with the results. Then the boxes will be colored here using some random noise")
		xsvg(kingdoms.body, self.get_figure('cell_fungi')).recolor(self.get_mock_subcell_loc(9606, 'fake'))

		self.db_close()
		
		reply = mamba.http.HTMLResponse(self, page.tohtml())
		reply.send()
		
	def get_mock_subcell_loc(self, type, id):
		compartments = ['nu','cy','cs','pe','ly','er','go','pm','en','va','ex','mi']
		compartment_color_map = {}
		random.seed()
		for compartment in compartments:
			compartment_color_map[compartment] = MockSubcell.define_color(random.random())		
		return compartment_color_map
	
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


class xsvg(XNode):
	__svg = ''	
	
	def __init__(self, parent, svg_as_string):
		XNode.__init__(self, parent)
		self.__svg = svg_as_string
		
	def begin_html(self):
		return self.__svg
		
	def replace_content(self, new_content):
		self.svg = new_content
	
	def get_content(self):
		return self.__svg
	
	def recolor(self, label_color_map):
		buf = []
		l = []
		
		for key in label_color_map.keys():
			l.append('<.* title="')
			l.append(key)
			l.append('".*>')
			l.append('|')
		l.pop()
		exp = string.join(l,'')
		
		for line in self.__svg.split("\n"):
			if re.search("^ *<[?!]", line): #ignore XML header
				continue
			if re.search(exp, line):
				for key, value in label_color_map.iteritems():
					if re.search('title="'+key+'"',line):
						buf.append(re.sub('(?<=fill:|ill=")#.{6}', '%s' % value, line))
			else:
				buf.append(line)
		self.__svg = string.join(buf,"\n")
		return
		
	@staticmethod
	def get_svg_from_file(parent, svg_as_file):
		f = open(svg_as_file, 'r')
		buf = []
		for line in f:
			if re.search("^ *<[?!]", line): #ignore XML header
				continue
			line = line[:-1]
			buf.append(line)
		f.close()
		return xsvg(parent, string.join(buf,"\n"))		
