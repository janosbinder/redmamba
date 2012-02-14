import pg
import datetime
import datamining
import html

import mamba.task


class xsearchfield(html.xtag):
	
	def __init__(self, action="Search"):
		html.xtag.__init__(self, "form")
		self["action"] = action
		self["method"] = "post"
		
		center = html.xtag("center")
		par1 = html.xpar()
		par1.add(html.xh3("Search for diseases, genes and identifiers"))
		par1.add(html.xtag("input", {"type":"text", "name":"query", "size":"100%"}))
		center.add(par1)
		
		par2 = html.xpar()
		radio1 = html.xtag("input", {"type":"radio", "name":"filter", "value":"any", "checked":"1"})
		radio1.add("Any")
		
		radio2 = html.xtag("input", {"type":"radio", "name":"filter", "value":"disease"})
		radio2.add("Diseases")
		space2 = html.xfree("&nbsp;")
		space2.add(radio2)
		
		radio3 = html.xtag("input", {"type":"radio", "name":"filter", "value":"gene"})
		radio3.add("Genes")
		space3 = html.xfree("&nbsp;")
		space3.add(radio3)
		
		submit = html.xtag("input", {"type":"submit", "value":"submit"})
		par2.add(radio1)
		par2.add(space2)
		par2.add(space3)
		par3 = html.xpar()
		par3.add(submit)
		par2.add(par3)
		
		center.add(par2)
		self.add(center)


class HtmlBasePage(html.xpage):
	
	def __init__(self):
		html.xpage.__init__(self, "<table><tr><td>Compendium of Liteature Listed</td></tr><tr><td>Disease Gene Associations (Collide&#0153;)</td></tr></table>")
		self.get_sidebar().add(html.xpar(datetime.datetime.now().strftime('%a-%d-%b-%Y %H:%M:%S %Z')))
		tbl = html.xtable({"width":"100%"})
		tbl.addrow("&nbsp")
		tbl.addrow("Disease",  "8,553")
		tbl.addrow("Proteins", "2,714")
		self.get_sidebar().add(tbl)


class HtmlSearchPage(HtmlBasePage):
	
	def __init__(self, rest):
		HtmlBasePage.__init__(self)
		if "filter" in rest and "query" in rest:
			if filter == "any":
				pass
			elif filter == "disease":
				pass
			elif filter == "gene":
				pass
			self.add_content(html.xh2("Result for: %s" % rest["query"]))
			tbl = html.xtable()
			conn = pg.connect(host='localhost', user='ljj', dbname='knowledge')
			q = conn.query("SELECT * FROM knowledge WHERE type1=9606 and id1='ENSP00000000233' AND type2=-23 LIMIT 30;")
			for x in q.getresult():
				r = html.xrow()
				r.add(x[0])
				r.add(x[1])
				r.add(x[3])
				r.add('<a href="%s">%s</a>' % (x[-1], x[-1]))
				tbl.addrow(r)
			self.add_content(html.xshadowbox(tbl))
		else:
			self.head.title = "Search diseases and genes"
			self.add_content(html.xshadowbox(xsearchfield()))
			

class HtmlProteinPage(HtmlBasePage):
	
	def __init__(self, type, id):
		HtmlBasePage.__init__(self)
		self.head.title = "Protein %s" % id
		self.add_content(html.xshadowbox(datamining.xtextmining(9606, "ENSP00000332369")))


class HtmlDiseasePage(HtmlBasePage):
	
	def __init__(self, disease):
		HtmlBasePage.__init__(self)
		self.head.title = disease
		self.add_content(html.xsection("Disease gene association", '<img src="figure2.png" width="250px"></img>Using an andvanced textmining pipeline against the full body of indexed medical literatur and a ontology-derived, ontology-self-curated dictionary consisting of proteins, disease, chemicals etc. we have created the worlds first resource linking genes to diseases on a scale never seen before.'))
		self.add_content(html.xsection("Alzheimer's disease", "A dementia that results in progressive memory loss, impaired thinking, disorientation, and changes in personality and mood starting in late middle age and leads in advanced cases to a profound decline in cognitive and physical functioning and is marked histologically by the degeneration of brain neurons especially in the cerebral cortex and by the presence of neurofibrillary tangles and plaques containing beta-amyloid."))
		self.add_content(datamining.xtextmining(9606, "ENSP00000335657"))



# ==============================================================================


class Search(mamba.task.Request):
	
	def main(self):
		rest = mamba.task.RestDecoder(self)
		page = HtmlSearchPage(rest)
		reply = mamba.http.HTMLResponse(self, page.tohtml())
		reply.send()
		

class Protein(mamba.task.Request):
	
	def main(self):
		rest = mamba.task.RestDecoder(self)
		page = HtmlProteinPage(rest["type"], rest["identifier"])
		reply = mamba.http.HTMLResponse(self, page.tohtml())
		reply.send()
		
		
class Disease(mamba.task.Request):
	
	def main(self):
		rest = mamba.task.RestDecoder(self)
		page = HtmlDiseasePage(rest["disease"])
		reply = mamba.http.HTMLResponse(self, page.tohtml())
		reply.send()
