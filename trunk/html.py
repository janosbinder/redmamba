import os
import sys
import mamba.task
import mamba.http


class xnode:
	
	def __init__(self, attr={}):
		self.attr  = attr
		self.nodes = []
		#self.parent = None
		
	def add(self, node):
		if node == self:
			raise Exception, "HTML node %s is a child of itself" % str(node)
		self.nodes.append(node)
		#node.parent = self
		
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
	
	def get_html(self):
		html = []
		html.append(self.begin_html())
		for node in self.nodes:
			#print " ", self, node
			html.append(node.get_html())
		html.append(self.end_html())
		return "\r\n".join(html)		
		
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
			self.add(xfree(text))
	
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


class xh2(xtag):
	
	def __init__(self, heading):
		xtag.__init__(self, "h3")
		self.add(xfree(heading))

			
	
class xcell(xtag):
	
	def __init__(self, child, attr={}):
		xtag.__init__(self, "td", attr)
		self.add(child)

class xleftcell(xcell):
	
	def __init__(self, child):
		attr = {"class" : "left-cell"}
		xcell.__init__(self, child, attr)
	
	
class xrow(xtag):
	
	def __init__(self, attr={}):
		xtag.__init__(self, "tr", attr)
	
	def add(self, node):
		if len(self.nodes) == 0:
			self.nodes.append(xleftcell(node))
		else:
			self.nodes.append(xcell(node))
	
		
class xtable(xtag):
	
	def __init__(self, attr={}):
		xtag.__init__(self, "table", attr)
		

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


class xsesction(xdiv):
	
	def __init__(self, title, text):
		xdiv.__init__(self, "section")
		par = xpar()
		par.add(xh1(title))
		par.add(xhr())
		par.add(xfree(text))
		self.add(par)
		#self.add(xh1(title))
		#self.add(xtag("hr"))
		#self.add(xpar(text))

		
class xpage(xtag):
	
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
	

class xdemopage(xpage):
	
	def __init__(self):
		xpage.__init__(self)

		self.head.title = "Demo page"
		
		wrapper = xdiv("wrapper")
		title = xdiv(None, "title")
		title.add(xfree("<h1>Compendium of Disease Genes</h1>"))
		wrapper.add(title)
		
		sidebar = xdiv("sidebar")
		sidebar.add(xfree("<p>Genes: 2,714<br>Disease: 8,559</p>&nbsp;"))
		content = xdiv("content")
		
		table = xtable()

		row = xrow()
		row.add(sidebar)
		row.add(content)

		table.add(row)
		
		wrapper.add(table)
		
		content.add(xsesction("Alzheimer's disease", "A dementia that results in progressive memory loss, impaired thinking, disorientation, and changes in personality and mood starting in late middle age and leads in advanced cases to a profound decline in cognitive and physical functioning and is marked histologically by the degeneration of brain neurons especially in the cerebral cortex and by the presence of neurofibrillary tangles and plaques containing beta-amyloid."))
		content.add(xsesction("Diabetes mellitus", "Diabetes mellitus, often simply referred to as diabetes, is a group of metabolic diseases in which a person has high blood sugar, either because the body does not produce enough insulin, or because cells do not respond to the insulin that is produced."))
		content.add(xsesction("Shigellosis", "A primary bacterial infectious disease that results in infection located in epithelium of colon, has material basis in Shigella boydii, has material basis in Shigella dysenteriae, has material basis in Shigella flexneri, or has material basis in Shigella sonnei, which produce toxins that can attack the lining of the large intestine, causing swelling, ulcers on the intestinal wall, and bloody diarrhea."))
		
		import datamining
		content.add(xfree(datamining.get_html(9606, "ENSP00000335657")))
		
		self.body.add(wrapper)
		

class MyPage(mamba.task.Request):
	
	def main(self):
		rest = mamba.task.RestDecoder(self)
		type = rest["type"]
		id   = rest["identifier"]
		
		page = xdemopage()
		reply = mamba.http.HTMLResponse(self, page.get_html())
		reply.send()
		