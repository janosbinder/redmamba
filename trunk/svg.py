import re
import pg

from html import *
import datapage
import visualization

import mamba.setup
import mamba.task
import mamba.http

""" Subcell (should be renamed later) mamba plugin creates a webpage using visualization database.
    It is assumed that in the database figures and also color entries identified by id, type are stored
	The color entries contain label->color pairs for the figures
"""
class Subcell(mamba.task.Request):
		
	def main(self):
		rest = mamba.task.RestDecoder(self)
		
		qtype = 9606
		qid = "ENSP00000269305"
		
		if "entity_type" in rest:
			qtype = int(rest["entity_type"])
		if "entity_identifier" in rest:
			qid = rest["entity_identifier"]

		page = XPage("Sub-cellular Protein Localization (ProLoc)")
		XSection(page.frame.content, "Results from text mining", "Here is some fact about p53")
		
		conn = pg.connect(host='localhost', port=5432, user='ljj', passwd='', dbname='visualization')
		XSVG(page.frame.content, str(visualization.SVG(conn, 'cell_%', qtype, qid)))
		conn.close()
		
		conn = pg.connect(host='localhost', port=5432, user='ljj', passwd='', dbname='textmining')
		textmining = datapage.XTextMiningResult(page.frame.content, conn, qtype, qid)
		conn.close()

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