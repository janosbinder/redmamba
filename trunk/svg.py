import re
import string
import random

from html import *

import visualization
import mamba.setup
import mamba.task
import mamba.http
import pg

""" Subcell (should be renamed later) mamba plugin creates a webpage using visualization database.
    It is assumed that in the database figures and also color entries identified by id, type are stored
	The color entries contain label->color pairs for the figures
"""
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
		self.database = pg.connect(host=self.conn_info[0], port=int(self.conn_info[1]), user=self.conn_info[2], passwd='', dbname=self.conn_info[3])		
		XSVG(content, str(visualization.SVG(self.database, 'cell_%', qtype, qid)))
		self.database.close()
		reply = mamba.http.HTMLResponse(self, page.tohtml())
		reply.send()


"""XSVG class can handle svg files, and provide on-the-fly manupulation of the embedded svg"""
class XSVG(XNode):
	__svg = ''
	
	def __init__(self, parent, svg):
		XNode.__init__(self, parent)
		# get rid of XML comments and XML header, and whitespace on the beginning of the document
		svg = re.sub("<\?xml.*?\?>\n?", '', svg)		
		svg = re.sub("<!--.*?-->\n?", '', svg)
		svg = re.sub("$\s*", '', svg)
		if not re.match("<svg", svg):
			raise Exception, "You tried to embed wrong type of SVG to the XSVG node"
		self.__svg = svg
		
	def begin_html(self):
		return self.__svg