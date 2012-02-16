import pg
import datetime
import datamining
from html import *

import mamba.task


class xsearchfield(XTag):
	
	def __init__(self, parent, action="Search"):
		XTag.__init__(self, parent, "form")
		self["action"] = action
		self["method"] = "post"
		
		center = XTag(self, "center")
		p1 = XP(center)
		XH3(p1, "Search for diseases, genes and identifiers")
		XTag(p1, "input", {"type":"text", "name":"query", "size":"100%", "value":"ENSP00000321537"})
		
		p2 = XP(center)
		ra1 = XTag(p2, "input", {"type":"radio", "name":"filter", "value":"any", "checked":"1"})
		XFree(ra1, "Any")
		
		sp1 = XFree(p2, "&nbsp;")	
		ra2 = XTag(sp1, "input", {"type":"radio", "name":"filter", "value":"disease"})
		XFree(ra2, "Diseases")
		
		sp2 = XFree(p2, "&nbsp;")	
		ra3 = XTag(sp2, "input", {"type":"radio", "name":"filter", "value":"gene"})
		XFree(ra3, "Genes")
		
		p3 = XP(p2)
		submit = XTag(p3, "input", {"type":"submit", "value":"submit"})
		

class HtmlBasePage(XPage):
	
	def __init__(self):
		XPage.__init__(self, "<table><tr><td>Compendium of Liteature Listed</td></tr><tr><td>Disease Gene Associations (Collide&#0153;)</td></tr></table>")

		XP(self.frame.sidebar, datetime.datetime.now().strftime('%a-%d-%b-%Y %H:%M:%S %Z'))
		tbl = XTable(self.frame.sidebar, {"width":"100%"})
		tbl.addrow("Disease",  "8,553")
		tbl.addrow("Proteins", "2,714")
		


class HtmlSearchPage(HtmlBasePage):
	
	def __init__(self, rest):
		HtmlBasePage.__init__(self)
		if "filter" in rest and "query" in rest:
			self.head.title = "Search result"
			if filter == "any":
				pass
			elif filter == "disease":
				pass
			elif filter == "gene":
				pass
			XH1(self.frame.content, "Result for: '%s' (%s)" % (rest["query"], rest["filter"]))
			
			groups = XTable(self.frame.content)
			group1 = XTd(XTr(groups))
			group2 = XTd(XTr(groups))
			group3 = XTd(XTr(groups))
			
			XH2(group1, "Text-mining:")
			tbl0 = XDataTable(XBox(group1).content)
			tbl0.addhead("Disease (DOID)", "Score")
			
			dictionary = pg.connect(host='localhost', user='ljj', dbname='dictionary')
			#### TODO: Get preferred names from the dictionary database.
			
			knowledge = pg.connect(host='localhost', user='ljj', dbname='textmining')
			q = knowledge.query("SELECT * FROM pairs WHERE type1=9606 and id1='%s' AND type2=-26 ORDER BY Score DESC LIMIT 30;" % rest["query"])
			for x in q.getresult():
				tbl0.addrow(x[3], x[4])
			
			XH2(group2, "Valid:")
			tbl1 = XDataTable(XBox(group2).content)
			tbl1.addhead("Disease ID", "Evidence", "Stars", "Source")
			
			XH2(group3, "Non-valid:")
			tbl2 = XDataTable(XBox(group3).content)
			tbl2.addhead("Disease ID", "Evidence", "Stars", "Source")
			
			knowledge = pg.connect(host='localhost', user='ljj', dbname='knowledge')
			q = knowledge.query("SELECT * FROM knowledge WHERE type1=9606 and id1='%s' AND type2=-26 LIMIT 30;" % rest["query"])
			for x in q.getresult():
				if x[7] == 't':
					tbl1.addrow(x[3], x[5], str(x[6]), '<a href="%s">%s</a>' % (x[8], x[4]))
				else:
					tbl2.addrow(x[3], x[5], str(x[6]), '<a href="%s">%s</a>' % (x[8], x[4]))
		else:
			self.head.title = "Search diseases and genes"
			xsearchfield(self.frame.content)
			

class HtmlProteinPage(HtmlBasePage):
	
	def __init__(self, type, id):
		HtmlBasePage.__init__(self)
		self.head.title = "Protein %s" % id
		box = XBox(self.frame.content)
		datamining.xtextmining(box.content, 9606, "ENSP00000332369")


class HtmlDiseasePage(HtmlBasePage):
	
	def __init__(self, disease):
		HtmlBasePage.__init__(self)
		self.head.title = disease
		self.add_content(XSection("Disease gene association", '<img src="figure2.png" width="250px"></img>Using an andvanced textmining pipeline against the full body of indexed medical literatur and a ontology-derived, ontology-self-curated dictionary consisting of proteins, disease, chemicals etc. we have created the worlds first resource linking genes to diseases on a scale never seen before.'))
		self.add_content(XSection("Alzheimer's disease", "A dementia that results in progressive memory loss, impaired thinking, disorientation, and changes in personality and mood starting in late middle age and leads in advanced cases to a profound decline in cognitive and physical functioning and is marked histologically by the degeneration of brain neurons especially in the cerebral cortex and by the presence of neurofibrillary tangles and plaques containing beta-amyloid."))
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
