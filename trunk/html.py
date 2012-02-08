import os
import sys
import datetime
import mamba.task
import mamba.http


class xnode:
	
	def __init__(self, attributes={}):
		self.attributes = {}
		for name in attributes:
			self.attributes[name] = attributes[name]
		self.nodes = []
		
	def add(self, node):
		if node == self:
			raise Exception, "HTML node %s is a child of itself" % str(node)
		self.nodes.append(node)
	
	def begin_html(self):
		return ""
	
	def end_html(self):
		return ""

	def __setitem__(self, name, value):
		print 
		self.attributes[name] = value
		
	def __getitem__(self, name):
		return self.attributes[name]
		
	def tohtml(self):
		html = []
		html.append(self.begin_html())
		for node in self.nodes:
			s = node.tohtml()
			s = "\r\n".join(map(lambda a: "  " + a, s.split("\r\n")))
			html.append(s)
		html.append(self.end_html())
		return "\r\n".join(html).rstrip()
		
	
class xtag(xnode):
	
	def __init__(self, tag, attributes={}):
		xnode.__init__(self, attributes)
		self.tag = tag
		
	def begin_html(self):
		att = [""]
		for name in self.attributes:
			value = self.attributes[name].replace('"', '\\"')
			att.append("%s=\"%s\"" % (name, value))
		if len(att):
			att = " ".join(att)
		else:
			att = ""
		return "<%s%s>" % (self.tag, att)
		
	def end_html(self):
		return "</%s>" % self.tag
	
	
class xfree(xtag):
	
	def __init__(self, text):
		xnode.__init__(self)
		self.text = text
		
	def begin_html(self):
		return self.text
	
	def end_html(self):
		return ""

class xhr(xtag):
	
	def __init__(self):
		xtag.__init__(self, "hr")
		
class xpar(xtag):
	
	def __init__(self, text=None, attributes={}):
		xtag.__init__(self, "p", attributes)
		if text != None:
			if type(text) is str:
				self.add(xfree(text))
			else:
				self.add(text)
	
class xdiv(xtag):
	
	def __init__(self, class_attributes, id_attributes=None):
		xtag.__init__(self, "div")
		if class_attributes:
			self["class"] = class_attributes
		if id_attributes:
			self["id"] = id_attributes
		
	
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
	
	def __init__(self, child, attributes={}):
		xtag.__init__(self, "td", attributes)
		self.add(child)
		
	def add(self, node):
		if isinstance(node, str):
			self.nodes.append(xfree(node))
		else:
			self.nodes.append(node)
	
class xrow(xtag):
	
	def __init__(self, attributes={}):
		xtag.__init__(self, "tr", attributes)
	
	def add(self, node):
		if isinstance(node, str):
			self.nodes.append(xcell(node))
		else:
			self.nodes.append(node)
	
		
class xtable(xtag):
	
	def __init__(self, attributes={}):
		xtag.__init__(self, "table", attributes)
		self.tbody = xtag("tbody")
		self.add(self.tbody)
		
	def addrow(self, *arg):
		row = xrow()
		for item in arg:
			if isinstance(item, str):
				row.add(xcell(item))
			else:
				row.add(item)
		self.tbody.add(row)
		

class xhead(xtag):
	
	def __init__(self):
		xtag.__init__(self, "head")
		self.title   = ""
		self.css     = ["css/default.css"]
		self.scripts = []#["scripts/default.js"]
		
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
		
class xform(xtag):
	
	def __init__(self, action, method="POST"):
		xtag.__init__(self, "form")
		self.action = action
		self.method = method
		self["action"] = action
		self["method"] = method
		self.par = xpar()
		self.nodes.append(self.par)
		
	def add(self, node):
		self.par.add(node)
		
		
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
	
	def __init__(self, title):
		xtag.__init__(self, "html")

		self.head = xhead()
		self.add(self.head)

		self.body = xbody()
		self.add(self.body)

		self.main_table = xpage.xpagetable(title)
		self.body.add(self.main_table)
	
	def get_sidebar(self):
		return self.main_table.sidebar
		
	def get_content(self):
		return self.main_table.content
		
	def begin_html(self):
		html = []
		html.append("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">""")
		html.append(xtag.begin_html(self))
		return "\r\n".join(html)
	


