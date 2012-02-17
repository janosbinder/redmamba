import os
import sys
import types
import datetime


class XNode:
	
	def __init__(self, parent, attr={}):
		self.parent = None
		if parent != None:
			#if not isinstance(type, types.ClassType):
			#	raise Exception, "XNode.__init__() failed because 'parent' is not a class but %s" % type(parent)
			#if not isinstance(parent, XNode):
			#	raise Exception, "XNode.__init__() failed because 'parent' is not an XNode but %s" % parent
			parent.add(self)
		self.attr = {}
		for name in attr:
			self.attr[name] = attr[name]
		self.nodes = []

	def remove(self):
		if self.parent != None and isinstance(self.parent, XNode):
			i = 0
			for node in self.parent.nodes:
				if node == self:
					del self.parent.nodes[i]
				else:
					i += 1
		self.nodes = []
		self.parent = None
		
	def add(self, node):
		if node == self:
			raise Exception, "HTML node %s is a child of itself" % str(node)
		self.nodes.append(node)
		if node.parent != None and node.parent != self:
			raise Exception, "Cannot add node due to parent mismatch: %s has parent %s which is not %s." % (node, node.parent, self)
		node.parent = self
	
	def begin_html(self):
		return ""
	
	def end_html(self):
		return ""

	def __setitem__(self, name, value):
		self.attr[name] = value
		
	def __getitem__(self, name):
		return self.attr[name]
		
	def tohtml(self):
		html = []
		text = self.begin_html()
		if text != None:
			html.append(text)
		for node in self.nodes:
			text = None
			if isinstance(node, XNode):
				text = node.tohtml()
			elif isinstance(node, str):
				text = node
			elif isinstance(node, unicode):
				text = node.encode("UTF-8")
			else:
				raise Exception, "%s has child node which is of unsuported: %s" % (type(self), type(node))
			if text != None:
				text = "\r\n".join(map(lambda a: "  " + a, text.split("\r\n")))
				html.append(text)
		text = self.end_html()
		if text != None:
			html.append(text)
		if len(html):
			return "\r\n".join(html).rstrip()
		return None
		
	
class XTag(XNode):
	
	def __init__(self, parent, tag, attr={}):
		XNode.__init__(self, parent, attr)
		self.tag = tag
		
	def begin_html(self):
		att = [""]
		for name in self.attr:
			try:
				value = self.attr[name].replace('"', '\\"')
			except AttributeError:
				print self, self.attr[name]
			att.append("%s=\"%s\"" % (name, value))
		if len(att):
			att = " ".join(att)
		else:
			att = ""
		return "<%s%s>" % (self.tag, att)
		
	def end_html(self):
		return "</%s>" % self.tag
	

class XOuterTag(XTag):
	
	def begin_html(self):
		if len(self.nodes):
			return XTag.begin_html(self)
		return None
	
	def end_html(self):
		if len(self.nodes):
			return XTag.end_html(self)
		return None
	
	
class XFree(XTag):
	
	def __init__(self, parent, text):
		XNode.__init__(self, parent)
		self.text = text
		
	def begin_html(self):
		return self.text
	
	def end_html(self):
		return ""

class XHr(XTag):
	
	def __init__(self, parent):
		XTag.__init__(self, parent, "hr")
		
class XP(XTag):
	
	def __init__(self, parent, text=None, attr={}):
		XTag.__init__(self, parent, "p", attr)
		if text != None:
			if type(text) is str:
				XFree(self, text)
			else:
				#self.add(text)
				self.nodes.append(text)
				text.parent = self
	
class XDiv(XTag):
	
	def __init__(self, parent, class_attributes=None, id_attributes=None):
		XTag.__init__(self, parent, "div")
		if class_attributes:
			self["class"] = class_attributes
		if id_attributes:
			self["id"] = id_attributes
		
	
class XH1(XTag):
	
	def __init__(self, parent, heading):
		XTag.__init__(self, parent, "h1")
		XFree(self, heading)

class XH2(XTag):
	
	def __init__(self,parent,  heading):
		XTag.__init__(self, parent, "h2")
		XFree(self, heading)


class XH3(XTag):
	
	def __init__(self, parent, heading):
		XTag.__init__(self, parent, "h3")
		XFree(self, heading)
			
	
class XTd(XTag):
	
	def __init__(self, parent, attr={}):
		XTag.__init__(self, parent, "td", attr)
	
class XTr(XTag):
	
	def __init__(self, parent, attr={}):
		if isinstance(parent, XTable):
			parent = parent.tbody
		XTag.__init__(self, parent, "tr", attr)

	
class XCaption(XTag):
	
	def __init__(self, parent, text=None, attr={}):
		XTag.__init__(self, parent, "caption", attr)
		self.text = text
		
	def begin_html(self):
		if self.text:
			return XTag.begin_html(self)
			
	def end_html(self):
		if self.text:
			return XTag.end_html(self)
		

class XTable(XTag):
	
	def __init__(self, parent, attr={}):
		XTag.__init__(self, parent, "table", attr)
		#self.caption = XCaption(self, "caption")
		self.thead   = XOuterTag(self, "thead")
		self.tfoot   = XOuterTag(self, "tfoot")
		self.tbody   = XOuterTag(self, "tbody")
		
	def _new_row(self):
		return XTr(self.tbody)
		
	def addrow(self, *args):
		row = self._new_row()
		for arg in args:
			if not isinstance(arg, XNode):
				XFree(XTd(row), str(arg))
			else:
				row.add(str(arg))
				
	def addhead(self, *args):
		row = XTr(self.thead)
		row["style"] = "font-family: helvetica; font-weight: bold;"
		for arg in args:
			if not isinstance(arg, XNode):
				XFree(XTd(row), str(arg))
			else:
				row.add(str(arg))
			
				
				
class XDataTable(XTable):
	
	def __init__(self, parent):
		XTable.__init__(self, parent)
		self["class"] = "data"
		
	def _new_row(self):
		row = XTable._new_row(self)
		if len(self.tbody.nodes) % 2 == 1:
			row["class"] = "odd"
		return row
	

class XHead(XTag):
	
	def __init__(self, parent):
		XTag.__init__(self, parent, "head")
		self.title   = ""
		self.css     = ["css/default.css"]
		self.scripts = ["scripts/default.js"]
		
	def begin_html(self):
		html = []
		html.append("<head>")
		if self.title:
			html.append("  <title>%s</title>" % self.title)
		html.append("""  <meta http-equiv="Content-Type" content="text/html; charset=utf-8"></meta>""")
		html.append("""  <meta http-equiv="X-UA-Compatible" content="IE=9"></meta>""")
		for style in self.css:
			html.append("""  <link rel="stylesheet" href="%s" type="text/css"></link>""" % style)
		for java in self.scripts:
			html.append("""  <script type="text/javascript" src="%s"></script>""" % java)
		return "\r\n".join(html)


class XBody(XTag):
	
	def __init__(self, page):
		XTag.__init__(self, page, "body")
		

class XBox(XDiv):
	
	def __init__(self, parent, content=None):
		XDiv.__init__(self, parent, "shadowbox-top-right")
		d1 = XDiv(self, "shadowbox-top-left")
		d2 = XDiv(d1, "shadowbox-bottom-right")
		d3 = XDiv(d2, "shadowbox-bottom-left")
		d4 = XDiv(d3, "shadowbox-content")
		d5 = XDiv(d4)
		d5["style"] = "padding: 15px 7px 10px"
		self.content = d5
		if content != None:
			self.content.add(content)
		

class XSection(XDiv):
	
	def __init__(self, parent, title, text):
		XDiv.__init__(self, parent, "section")
		p = XP(self)
		XH2(p, title)
		XHr(p)
		if type(text) is str:
			XFree(p, text)
		else:
			par.add(text)
			
		
class XPage(XTag):
	
	class XFrame(XTable):
		
		def __init__(self, parent, title):
			XTable.__init__(self, parent, {"class":"page-outer-table"})
			row = XTr(self)
			c1 = XTd(row, {"class":"page-header-left"})
			XFree(c1, "&nbsp")
			c2 = XTd(row, {"class":"page-header-right"})
			XH1(c2, title)
			row = XTr(self)
			c3 = XTd(row, {"class":"sidebar-cell"})
			self.sidebar = XDiv(c3, "sidebar")
			c4 = XTd(row)
			self.content = XDiv(c4, "content")
			
	def __init__(self, title):
		XTag.__init__(self, None, "html")
		self.head = XHead(self)
		self.body = XBody(self)
		self.frame = XPage.XFrame(self.body, title)
	
	def add_content(self, node):
		self.frame.content.add(node)
		
	def add_sidebar(self, node):
		self.frame.sidebar.add(node)
		
	def begin_html(self):
		html = []
		html.append("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">""")
		html.append(XTag.begin_html(self))
		return "\r\n".join(html)
	


