import mamba.task
from html import *
import datamining

class xprotlocpage(xpage):		
			
	
	def __init__(self, type, id):
		xpage.__init__(self)
		self.head.title = "Demo page"		
		self.page = xpage.xpagetable("Compendium of Disease Genes")
		
		wrapper = xdiv("wrapper")
		wrapper.add(self.page)
		self.body.add(wrapper)
		
		self.page.sidebar.add(xpar(datetime.datetime.now().strftime('%a-%d-%b-%Y %H:%M:%S %Z')))
		tbl = xtable({"width":"100%"})
		tbl.addrow("&nbsp")
		tbl.addrow("Disease", "8,553")
		tbl.addrow("Proteins", "2,714")
		self.page.sidebar.add(tbl)
				
		self.page.content.add(xsection("Disease gene association", '<img src="figure2.png" width="60%"></img>Using an andvanced textmining pipeline against the full body of indexed medical literatur and a ontology-derived, ontology-self-curated dictionary consisting of proteins, disease, chemicals etc. we have created the worlds first resource linking genes to diseases on a scale never seen before.'))
		self.page.content.add(xsection("Alzheimer's disease", "A dementia that results in progressive memory loss, impaired thinking, disorientation, and changes in personality and mood starting in late middle age and leads in advanced cases to a profound decline in cognitive and physical functioning and is marked histologically by the degeneration of brain neurons especially in the cerebral cortex and by the presence of neurofibrillary tangles and plaques containing beta-amyloid."))
		
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
		
		page = xprotlocpage(type, id)
		reply = mamba.http.HTMLResponse(self, str(page))
		reply.send()
		