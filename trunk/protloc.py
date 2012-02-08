import mamba.task
from   html import *
import datamining


class HtmlBasePage(xpage):
	
	def __init__(self):
		xpage.__init__(self, "Compendium of Liteature Listed Disease Gene Associations (Collide&#0153;)")
		self.get_sidebar().add(xpar(datetime.datetime.now().strftime('%a-%d-%b-%Y %H:%M:%S %Z')))
		tbl = xtable({"width":"100%"})
		tbl.addrow("&nbsp")
		tbl.addrow("Disease",  "8,553")
		tbl.addrow("Proteins", "2,714")
		self.get_sidebar().add(tbl)


class HtmlSearchPage(HtmlBasePage):		
	
	def __init__(self):
		HtmlBasePage.__init__(self)
		self.head.title = "Search diseases and genes"
		form = xform("Search")
		form.add(xfree('Search database: <input type="text" size="100"></input><br></br>'))
		center = xtag("center")
		center.add(xfree('Filter: <input type="radio" name="filter" value="on">Any</input>'))
		center.add(xfree('<input type="radio" name="filter">Disease</input>'))
		center.add(xfree('<input type="radio" name="filter">Gene</input><br></br>'))
		form.add(center)
		self.get_content().add(form)
		

class HtmlProteinPage(HtmlBasePage):
	
	def __init__(self, type, id):
		HtmlBasePage.__init__(self)
		self.head.title = "Protein %s" % id
		self.get_content().add(datamining.xtextmining(9606, "ENSP00000335657"))


class HtmlDiseasePage(HtmlBasePage):
	
	def __init__(self, disease):
		HtmlBasePage.__init__(self)
		self.head.title = disease
		self.get_content().add(xsection("Disease gene association", '<img src="figure2.png" width="250px"></img>Using an andvanced textmining pipeline against the full body of indexed medical literatur and a ontology-derived, ontology-self-curated dictionary consisting of proteins, disease, chemicals etc. we have created the worlds first resource linking genes to diseases on a scale never seen before.'))
		self.get_content().add(xsection("Alzheimer's disease", "A dementia that results in progressive memory loss, impaired thinking, disorientation, and changes in personality and mood starting in late middle age and leads in advanced cases to a profound decline in cognitive and physical functioning and is marked histologically by the degeneration of brain neurons especially in the cerebral cortex and by the presence of neurofibrillary tangles and plaques containing beta-amyloid."))
		self.get_content().add(datamining.xtextmining(9606, "ENSP00000335657"))


class Search(mamba.task.Request):
	
	def main(self):
		rest = mamba.task.RestDecoder(self)
		page = HtmlSearchPage()
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
