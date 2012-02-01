import os
import mamba.task
import mamba.http


class HtmlNode:
	
	def __init__(self):
		self.nodes = []
		
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
			html.append(node.get_html())
		html.append(self.end_html())
		return "\r\n".join(html)
		
		
class HtmlText(HtmlNode):
	
	def __init__(self, text):
		HtmlNode.__init__(self)
		self.text = text
	
	def begin_html(self):
		return self.text


class HtmlPar(HtmlText):
	
	def begin_html(self):
		return "".join(["<p>", self.text, "</p>"])


class HtmlBody(HtmlNode):
	
	def begin_html(self):
		return "<body>"

	def end_html(self):
		return "</body>"


class HtmlHead(HtmlNode):
	
	def __init__(self):
		HtmlNode.__init__(self)
		self.css = []
		self.scripts = []
		
	def begin_html(self):
		html = []
		html.append("<head>")
		html.append("""  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />""")
		for style in self.css:
			html.append("""  <link rel="stylesheet" href="%s" type="text/css" />""" % style)
		for java in self.scripts:
			if not os.path.exists(java):
				html.append("""  <script language="javascript" type="text/javascript" src="%s" />""" % java)
			else:
				html.append("""<script language="javascript" type="text/javascript">""")
				html.append(open(java).read())
				html.append("""</script>""")
		return "\r\n".join(html)
	
	def end_html(self):
		return "</head>"
	
		
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
		return "\r\n".join(html)
	
	def end_html(self):
		return "</html>"
		

class HtmlDemoPage(HtmlPage):
	
	def __init__(self):
		HtmlPage.__init__(self)
		self.body.add(HtmlPar("<H1>This is the header.</H1>"))
		self.body.add(HtmlPar("This is the body."))
		self.body.add(HtmlPar("<H1>This is the footer.</H1>"))
		

class MyPage(mamba.task.Request):
	
	def main(self):
		rest = mamba.task.RestDecoder(self)
		type = rest["type"]
		id = rest["identifier"]
		
		page = HtmlDemoPage()
		
		reply = mamba.http.HTMLResponse(self, page.get_html())
		reply.send()
