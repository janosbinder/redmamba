import os
import sys
import datetime
import datamining
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
			try:
				s = str(node)
				s = "\r\n".join(map(lambda a: "  " + a, s.split("\r\n")))
				html.append(s)
			except Exception, e:
				html.append('<span style="color: red">%s</span>' % str(e))
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
	
	class xpagetable(xtable):
		
		def __init__(self, title):
			xtable.__init__(self, {"class":"page-outer-table"})

			row = xrow()
			row.add(xcell("&nbsp", {"class":"page-header-left"}))
			row.add(xcell(xh1(title), {"class":"page-header-right"}))
			self.tbody.add(row)
			
			row = xrow()
			row.add(xcell("&nbsp", {"class" : "top-separator"}))
			row.add(xcell("&nbsp", {"class" : "top-separator"}))
			self.tbody.add(row)
			
			self.sidebar = xdiv("sidebar")
			self.content = xdiv("content")
			
			row = xrow()
			row.add(xcell(self.sidebar, {"class" : "sidebar-cell"}))
			row.add(xcell(self.content))
			self.tbody.add(row)
			
			
	
	def __init__(self, type, id):
		xpage.__init__(self)
		self.head.title = "Demo page"		
		self.page = xdemopage.xpagetable("Compendium of Disease Genes")
		
		wrapper = xdiv("wrapper")
		wrapper.add(self.page)
		self.body.add(wrapper)
		
		tbl = xtable({"width":"100%"})
		tbl.addrow("&nbsp", "&nbsp")
		tbl.addrow("Last updated:", datetime.datetime.now().strftime('%a-%d-%b-%Y %H:%M:%S %Z'))
		tbl.addrow("Disease", "8,553")
		tbl.addrow("Genes and proteins", "2,714")
		self.page.sidebar.add(tbl)
		
		
		sec0 = xsection("Disease gene association", '<img src="figure2.png" width="60%"></img>Using an andvanced textmining pipeline against the full body of indexed medical literatur and a ontology-derived, ontology-self-curated dictionary consisting of proteins, disease, chemicals etc. we have created the worlds first resource linking genes to diseases on a scale never seen before.')
		sec1 = xsection("Alzheimer's disease", "A dementia that results in progressive memory loss, impaired thinking, disorientation, and changes in personality and mood starting in late middle age and leads in advanced cases to a profound decline in cognitive and physical functioning and is marked histologically by the degeneration of brain neurons especially in the cerebral cortex and by the presence of neurofibrillary tangles and plaques containing beta-amyloid.")
		sec2 = xsection("Diabetes mellitus", "Diabetes mellitus, often simply referred to as diabetes, is a group of metabolic diseases in which a person has high blood sugar, either because the body does not produce enough insulin, or because cells do not respond to the insulin that is produced.")
		sec3 = xsection("Shigellosis", "A primary bacterial infectious disease that results in infection located in epithelium of colon, has material basis in Shigella boydii, has material basis in Shigella dysenteriae, has material basis in Shigella flexneri, or has material basis in Shigella sonnei, which produce toxins that can attack the lining of the large intestine, causing swelling, ulcers on the intestinal wall, and bloody diarrhea.")
		self.page.content.add(sec0)
		self.page.content.add(sec1)
		self.page.content.add(sec2)
		self.page.content.add(sec3)
		
		
		par = xpar()
		par.add(xfree("This is just a test of a customized section we might have. Here is an ugly table:"))
		tbl = xtable({"frame":"hsides", "width":"100%", "style":"background: #F7FCE4"})
		tbl.add(xfree("<caption><em>Table 1:</em> Monthly savings.</caption>"))
		tbl.addrow("Happy", "Go", "Lucky")
		tbl.addrow("What can I", "come up with")
		tbl.addrow("for this row?")
		par.add(tbl)
		
		self.page.content.add(xsection("Test", par))
		
		self.page.content.add(datamining.xtextmining(9606, "ENSP00000335657"))
		
		
		

class MyPage(mamba.task.Request):
	
	def main(self):
		rest = mamba.task.RestDecoder(self)
		type = rest["type"]
		id   = rest["identifier"]
		
		page = xdemopage(type, id)
		reply = mamba.http.HTMLResponse(self, str(page))
		reply.send()
		