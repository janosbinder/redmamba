import os
import sys
import datetime
import mamba.task
import mamba.http


class xnode:
	
	def __init__(self, attr={}):
		self.attr  = attr
		self.nodes = []
		
	def add(self, node):
		if node == self:
			raise Exception, "HTML node %s is a child of itself" % str(node)
		self.nodes.append(node)
		
	def get_attributes(self):
		attr = []
		for name in self.attr:
			value = self.attr[name].replace('"', '\\"')
			attr.append("%s=\"%s\"" % (name, value))
		attr = " ".join(attr)
		if len(attr):
			attr = " " + attr
		return attr
	
	def begin_html(self):
		return ""
		
	def end_html(self):
		return ""
	
	def __setitem__(self, attribute, value):
		self.attr[attribute] = value
		
	def __getitem__(self, attribute):
		return self.attr[attribute]
		
	def __str__(self):
		html = []
		html.append(self.begin_html())
		for node in self.nodes:
			#try:
			s = str(node)
			s = "\r\n".join(map(lambda a: "  " + a, s.split("\r\n")))
			html.append(s)
			#except Exception, e:
			#	html.append('<span style="color: red">%s</span>' % str(e))
		html.append(self.end_html())
		return "\r\n".join(html).rstrip()
		
class xtag(xnode):
	
	def __init__(self, tag, attr={}):
		xnode.__init__(self, attr)
		self.tag = tag
		
	def begin_html(self):
		return "<%s%s>" % (self.tag, self.get_attributes())
		
	def end_html(self):
		return "</%s>" % self.tag
	
class xfree(xnode):
	
	def __init__(self, text):
		xnode.__init__(self)
		self.text = text
		
	def begin_html(self):
		return self.text

class xhr(xtag):
	def __init__(self):
		xtag.__init__(self, "hr")
		
class xpar(xtag):
	
	def __init__(self, text=None, attr={}):
		xtag.__init__(self, "p", attr)
		if text != None:
			if type(text) is str:
				self.add(xfree(text))
			else:
				self.add(text)
	
class xdiv(xtag):
	
	def __init__(self, class_attr, id_attr=None):
		attr = {}
		if class_attr:
			attr["class"] = class_attr
		if id_attr:
			attr["id"] = id_attr
		xtag.__init__(self, "div", attr)
		
	
class xh1(xtag):
	
	def __init__(self, heading):
		xtag.__init__(self, "h1")
		self.add(xfree(heading))

class xh2(xtag):
	
	def __init__(self, heading):
		xtag.__init__(self, "h2")
		self.add(xfree(heading))


class xh3(xtag):
	
	def __init__(self, heading):
		xtag.__init__(self, "h3")
		self.add(xfree(heading))

			
	
class xcell(xtag):
	
	def __init__(self, child, attr={}):
		xtag.__init__(self, "td", attr)
		self.add(child)
	
class xrow(xtag):
	
	def __init__(self, attr={}):
		xtag.__init__(self, "tr", attr)
	
	def add(self, node):
		if type(node) is str:
			self.nodes.append(xcell(node))
		else:
			self.nodes.append(node)
	
		
class xtable(xtag):
	
	def __init__(self, attr={}):
		xtag.__init__(self, "table", attr)
		self.tbody = xtag("tbody")
		self.add(self.tbody)
		
	def addrow(self, *arg):
		row = xrow()
		for item in arg:
			if type(item) is str:
				row.add(xcell(item))
			else:
				row.add(item)
		self.tbody.add(row)
		

class xhead(xtag):
	
	def __init__(self):
		xtag.__init__(self, "head")
		self.title   = ""
		self.css     = ["css/default.css"]
		self.scripts = []
		
	def begin_html(self):
		html = []
		html.append("<head>")
		if self.title:
			html.append("  <title>%s</title>" % self.title)
		html.append("""  <meta http-equiv="Content-Type" content="text/html; charset=utf-8"></meta>""")
		for style in self.css:
			html.append("""  <link rel="stylesheet" href="%s" type="text/css"></link>""" % style)
		for java in self.scripts:
			html.append("""  <script type="text/javascript" src="%s"></script>""" % java)
		return "\r\n".join(html)


class xbody(xtag):
	
	def __init__(self):
		xtag.__init__(self, "body")


class xsection(xdiv):
	
	def __init__(self, title, text):
		xdiv.__init__(self, "section")
		par = xpar()
		par.add(xh2(title))
		par.add(xhr())
		if type(text) is str:
			par.add(xfree(text))
		else:
			par.add(text)
		self.add(par)
		
class xpage(xtag):
	
	class xpagetable(xtable):
		
		def __init__(self, title):
			xtable.__init__(self, {"class":"page-outer-table"})

			row = xrow()
			row.add(xcell("&nbsp", {"class":"page-header-left"}))
			row.add(xcell(xh1(title), {"class":"page-header-right"}))
			self.tbody.add(row)
			
			self.sidebar = xdiv("sidebar")
			self.content = xdiv("content")
			
			row = xrow()
			row.add(xcell(self.sidebar, {"class" : "sidebar-cell"}))
			row.add(xcell(self.content))
			self.tbody.add(row)
	
	def __init__(self):
		xtag.__init__(self, "html")
		self.head = xhead()
		self.add(self.head)
		self.body = xbody()
		self.add(self.body)
		
	def begin_html(self):
		html = []
		html.append("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">""")
		html.append(xtag.begin_html(self))
		return "\r\n".join(html)
	


