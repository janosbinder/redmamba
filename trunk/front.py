import os
import mamba.task
import mamba.http


class HtmlNode:
	
	def __init__(self):
		self.nodes = []
		
	def _list2html(self, html):
		return "\r\n".join(html)
	
	def add(self, node):
		self.nodes.append(node)
	
	def begin_html(self):
		return ""
		
	def end_html(self):
		return ""
	
	def get_html(self):
		html = []
		html.append(self.begin_html())
		for node in self.nodes:
			html.append(node.get_html().rstrip())
		html.append(self.end_html())
		return self._list2html(html)		
		
		
class HtmlText(HtmlNode):
	
	def __init__(self, text):
		HtmlNode.__init__(self)
		self.text = text
	
	def begin_html(self):
		return self.text


class HtmlPar(HtmlText):
	
	def begin_html(self):
		return "".join(["<p>", self.text, "</p>"])


class HtmlHead(HtmlNode):
	
	def __init__(self):
		HtmlNode.__init__(self)
		self.title   = ""
		self.css     = []
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
		return self._list2html(html)
	
	def end_html(self):
		return "</head>"


class HtmlBody(HtmlNode):
	
	def begin_html(self):
		return "<body>"

	def end_html(self):
		return "</body>"


class HtmlDiv(HtmlNode):
	
	def __init__(self, div_id, div_class=None):
		HtmlNode.__init__(self)
		self.div_id    = div_id
		self.div_class = div_class
		
	def begin_html(self):
		html = []
		attr = []
		if self.div_id:
			attr.append('id="%s"' % self.div_id)
		if self.div_class:
			attr.append('class="%s"' % self.div_class)
		attr = " ".join(attr)
		if len(attr):
			html.append("<div %s>" % attr)
		else:
			html.append("<div>")
		return self._list2html(html)
			
	def end_html(self):
		return "</div>"


class HtmlSection(HtmlDiv):
	
	def __init__(self, title, text):
		HtmlDiv.__init__(self, None, "section")
		self.nodes.append(HtmlText("<h2>%s</h2>" % title))
		self.nodes.append(HtmlPar(text))
		

class HtmlCell(HtmlNode):
	
	def __init__(self, node):
		HtmlNode.__init__(self)
		self.add(node)
	
	def begin_html(self):
		return "<td>"

	def end_html(self):
		return "</td>"


class HtmlLeftCell(HtmlCell):
	
	def begin_html(self):
		return "<td class=\"left-cell\">"

		
class HtmlRow(HtmlNode):
	
	def add(self, node):
		if len(self.nodes) == 0:
			HtmlNode.add(self, HtmlLeftCell(node))
		else:
			HtmlNode.add(self, HtmlCell(node))
	
	def begin_html(self):
		return "<tr>"
	
	def end_html(self):
		return "</tr>"
		
		
class HtmlTable(HtmlNode):
	
	def begin_html(self):
		return "<table valign=\"top\">"
	
	def end_html(self):
		return "</table>"
		
		
class HtmlPage(HtmlNode):
	
	def __init__(self):	
		HtmlNode.__init__(self)
		
		self.head = HtmlHead()
		self.head.css.append("css/default.css")
		#self.head.scripts.append("scripts/default.js")
		
		self.body = HtmlBody()

		self.add(self.head)
		self.add(self.body)
		
	def begin_html(self):
		html = []
		html.append("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">""")
		html.append("<html>")
		return self._list2html(html)
	
	def end_html(self):
		return "</html>"
		

class HtmlDemoPage(HtmlPage):
	
	def __init__(self):
		HtmlPage.__init__(self)

		self.head.title = "Demo page"

		wrapper = HtmlDiv("wrapper")
		
		title   = HtmlDiv("title")
		wrapper.add(title)
		
		sidebar = HtmlDiv("sidebar")
		content = HtmlDiv("content")
		
		table = HtmlTable()
		row = HtmlRow()
		row.add(sidebar)
		row.add(content)
		table.add(row)
		
		wrapper.add(table)

		title.add(HtmlText("<h1>Compendium of Disease Genes</h1>"))
		sidebar.add(HtmlText("The sidebar"))
		content.add(HtmlSection("Alzheimer's disease", "A dementia that results in progressive memory loss, impaired thinking, disorientation, and changes in personality and mood starting in late middle age and leads in advanced cases to a profound decline in cognitive and physical functioning and is marked histologically by the degeneration of brain neurons especially in the cerebral cortex and by the presence of neurofibrillary tangles and plaques containing beta-amyloid."))
		content.add(HtmlSection("Diabetes mellitus", "Diabetes mellitus, often simply referred to as diabetes, is a group of metabolic diseases in which a person has high blood sugar, either because the body does not produce enough insulin, or because cells do not respond to the insulin that is produced."))
		content.add(HtmlSection("Shigellosis", "A primary bacterial infectious disease that results in infection located in epithelium of colon, has material basis in Shigella boydii, has material basis in Shigella dysenteriae, has material basis in Shigella flexneri, or has material basis in Shigella sonnei, which produce toxins that can attack the lining of the large intestine, causing swelling, ulcers on the intestinal wall, and bloody diarrhea."))
		self.body.add(wrapper)
		

class MyPage(mamba.task.Request):
	
	def main(self):
		rest = mamba.task.RestDecoder(self)
		type = rest["type"]
		id   = rest["identifier"]
		
		page = HtmlDemoPage()
		
		reply = mamba.http.HTMLResponse(self, page.get_html())
		reply.send()
