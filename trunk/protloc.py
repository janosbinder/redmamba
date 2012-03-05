import pg
import math
import datetime

from html import *
import obo
import textmining

import mamba.setup
import mamba.task


class MyConfig(mamba.setup.Configuration):
	
	def __init__(self, ini_filename):
		mamba.setup.Configuration.__init__(self, ini_filename)
		
		self.doid = obo.Ontology("/home/purple1/dictionary/doid.obo")
		
		for id in self.doid.terms:
			term = self.doid.terms[id]
			term.wiki = None
			term.gocc = {}
			term.gomf = {}
			term.gobp = {}
			if term.definition == None:
				term.definition = ""
			term.wikitext = ""
			
		for line in open("/home/green1/frankild/ModernDiseaseDB/wikipedia/wikitext_doid_log.tsv"):
			id, sentence, name, rname, wiki_url = line[:-1].split("\t")
			if id in self.doid.terms:
				term = self.doid.terms[id]
				if wiki_url.startswith("http://en.wikipedia.org") and term.wiki == None:
					term.wiki = wiki_url
		
		for line in open("/home/green1/frankild/ModernDiseaseDB/wikipedia/wikitext_doid_par.tsv"):
			serial, id, text = line[:-1].split("\t")
			if id in self.doid.terms:
				self.doid.terms[id].wikitext = text
				
		
		for line in open("/home/green1/frankild/ModernDiseaseDB/GO/gocc_pairs.tsv"):
			type1, doid, type2, go, score = line[:-1].split("\t")
			score = float(score)
			if score > 2.4 and doid in self.doid.terms:
				term = self.doid.terms[doid]
				term.gocc[go] = score
		
		for id in self.doid.terms:
			term = self.doid.terms[id]
			term.gocc = sorted(map(lambda a: (a[1],a[0]), term.gocc.items()), reverse=True)
		
		for line in open("/home/green1/frankild/ModernDiseaseDB/GO/gomf_pairs.tsv"):
			type1, doid, type2, go, score = line[:-1].split("\t")
			score = float(score)
			if score > 2.4 and doid in self.doid.terms:
				term = self.doid.terms[doid]
				term.gomf[go] = score
		
		for line in open("/home/green1/frankild/ModernDiseaseDB/GO/gobp_pairs.tsv"):
			type1, doid, type2, go, score = line[:-1].split("\t")
			score = float(score)
			if score > 2.4 and doid in self.doid.terms:
				term = self.doid.terms[doid]
				term.gobp[go] = score
		
	

class TalkDB:
	
	@staticmethod
	def get_best_name(typex, idx, dictionary):
		bestname = idx
		names = dictionary.query("SELECT name FROM preferred WHERE type=%i AND id='%s';" % (typex, idx)).getresult()
		if len(names):
			bestname = names[0][0]
		return bestname
	
	@staticmethod
	def get_stars(score):
		stars = int(min(5, float(score)))
		return '<span class="stars">%s</span>' % "".join(["&#9733;"]*stars + ["&#9734;"]*(5-stars))
	


class HTMLPageCollide(XPage):
	
	def __init__(self):
		XPage.__init__(self, "<table><tr><td>Compendium of Liteature Listed</td></tr><tr><td>Disease Gene Associations (Collide&#0153;)</td></tr></table>")
		XP(self.frame.sidebar, datetime.datetime.now().strftime('%a-%d-%b-%Y %H:%M:%S %Z'))
		tbl = XTable(self.frame.sidebar, {"width":"100%"})
		tbl.addrow("Disease",  "8,553")
		tbl.addrow("Proteins", "2,714")
		


class HTMLPageBrowseDisease(HTMLPageCollide):
	
	def __init__(self, rest):
		HTMLPageCollide.__init__(self)
		
		if "doid" not in rest:
			id = "DOID:4"
		else:
			id = rest["doid"].encode("utf8")
			
		term = mamba.setup.config().doid.terms[id]
		
		title = '<a href="/Browse" style="link:inherit; text-decoration:none; visited:inherit;">Browse the disease ontology</a>'
		group = XGroup(self.frame.content, title)
		section = XSection(group.body, '%s &nbsp &nbsp; (%s)' % (term.name.capitalize(), term.id))

		p1 = XP(section.body)
		if len(term.definition):
			XH4(p1, "Definition (DOID)")
			XFree(p1, term.definition)
		
		if len(term.wikitext):
			XH4(p1, "Description (Wikipedia)")
			XFree(p1, term.wikitext)
		
		if term.wiki:
			XFree(p1, '<br></br><a href="%s" target="wikipedia_tab">Wikipedia</a>' % term.wiki)
		
		p2 = XP(section.body)
		XH4(p2, "Synonyms")
		ul = XTag(p2, "ul")
		for synonym in term.synonyms:
			XFree(XTag(ul, "li"), synonym.capitalize())	
			
		if len(term.parents):
			p3 = XP(section.body)
			XH4(p3, "Derives from")
			ul = XTag(p3, "ul")
			for parent in term.parents:
				XFree(ul, '<li><a href="/Browse?doid=%s">%s</a></li>' % (parent.id, parent.name.capitalize()))
		
		if len(term.children):
			p5 = XP(section.body)
			XH4(p5, "Relates to")
			ul = XTag(p5, "ul")
			for child in term.children:
				XFree(ul, '<li><a href="/Browse?doid=%s">%s</a></li>' % (child.id, child.name.capitalize()))
		
		conn_text = pg.connect(host='localhost', user='ljj', dbname='textmining')
		conn_dict = pg.connect(host='localhost', user='ljj', dbname='dictionary')
		
		XH4(section.body, "Literature")
		textmining.DocumentsHTML(section.body, conn_text, -26, term.id)
		
		XHr(section.body)
			
		p6 = XP(section.body)
		XH4(p6, "Sub-cellular localization")
		tbl = XDataTable(p6)
		tbl["width"] = "100%"
		tbl.addhead("#", "Term", "GO", "Z-score", "Evidence")
		i = 1
		for score, go in term.gocc:
			if i > 10:
				break
			best   = TalkDB.get_best_name(-22, go, conn_dict).capitalize()
			golink = '<a href="http://www.ebi.ac.uk/QuickGO/GTerm?id=%s" target="gene_ontology_tab">%s</a>' % (go, go)
			zscore = "%.2f" % score
			stars  = TalkDB.get_stars(score)
			row = tbl.addrow(i, "<strong>%s</strong>" % best, golink, zscore, stars)
			i += 1
		
		p7 = XP(section.body)
		XH4(p7, "Genes")
		textmining.PairsHTML(p7, -26, term.id, 9606, conn_text, conn_dict)
			
		XH4(p7, "Drugs and Compounds")
		tbl = XDataTable(p7)
		textmining.PairsHTML(p7, -26, term.id, -1, conn_text, conn_dict)
		


class HTMLPageSearch(HTMLPageCollide):
	
	def __init__(self, rest):
		HTMLPageCollide.__init__(self)
			
		if "query" in rest:
			self.head.title = "Search result"
			dictionary = pg.connect(host='localhost', user='ljj', dbname='dictionary')
			search = pg.escape_string(rest["query"])
			names = dictionary.query("SELECT type, id, name FROM preferred WHERE name ILIKE '%s%%' AND type<>-11;" % search).getresult()
			if len(names):
				XH1(self.frame.content, "Result for '%s'" % (rest["query"]))
				table = XTable(self.frame.content)
				for type, id, name in names:
					table.addrow(type, id, name)
			else:
				XH1(self.frame.content, "Nothing found for '%s' (%s)" % (rest["query"], rest["filter"]))

		else:
			self.head.title = "Search diseases and genes"
			
			form = XTag(self.frame.content, "form")
			form["action"] = "Search"
			form["method"] = "post"		
			center = XTag(form, "center")
			p1 = XP(center)
			XH3(p1, "Search for diseases, genes and identifiers")
			XTag(p1, "input", {"type":"text", "name":"query", "size":"100%", "value":"ABCA17P"})
			submit = XTag(XP(p1), "input", {"type":"submit", "value":"submit"})


class HTMLPageProtein(HTMLPageCollide):
	
	def __init__(self, type, id):
		HTMLPageCollide.__init__(self)
		self.head.title = "Protein %s" % id
		box = XBox(self.frame.content)
		conn_text = pg.connect(host="localhost", user="ljj", dbname="textmining")
		textmining.DocumentsHTML(group2.body, conn_text, 9606, "ENSP00000332369")


class HTMLPageDiseaseInfo(HTMLPageCollide):
	
	def __init__(self, disease):
		HTMLPageCollide.__init__(self)
		self.head.title = "Diseases"

		group1 = XGroup(self.frame.content, "Diseases")
		XSection(group1.body, "Disease gene associations", '<img src="figure2.png" width="250px"></img>Using an andvanced textmining pipeline against the full body of indexed medical literatur and a ontology-derived, ontology-self-curated dictionary consisting of proteins, disease, chemicals etc. we have created the worlds first resource linking genes to diseases on a scale never seen before.')
		XSection(group1.body, "Alzheimer's disease", "A dementia that results in progressive memory loss, impaired thinking, disorientation, and changes in personality and mood starting in late middle age and leads in advanced cases to a profound decline in cognitive and physical functioning and is marked histologically by the degeneration of brain neurons especially in the cerebral cortex and by the presence of neurofibrillary tangles and plaques containing beta-amyloid.")
		
		group2 = XGroup(self.frame.content, "Text-mining")
		conn_text = pg.connect(host="localhost", user="ljj", dbname="textmining")
		textmining.DocumentsHTML(group2.body, conn_text, 9606, "ENSP00000332369")


class HTMLTestPage(HTMLPageCollide):
	
	def __init__(self):
		HTMLPageCollide.__init__(self)
		XFree(self.frame.content, open("test.html").read())

# ==============================================================================


class Search(mamba.task.Request):	
	def main(self):
		rest = mamba.task.RestDecoder(self)
		page = HTMLPageSearch(rest)
		reply = mamba.http.HTMLResponse(self, page.tohtml())
		reply.send()
		

class Protein(mamba.task.Request):
	def main(self):
		rest = mamba.task.RestDecoder(self)
		page = HTMLPageProtein(rest["type"], rest["identifier"])
		reply = mamba.http.HTMLResponse(self, page.tohtml())
		reply.send()
		
		
class Disease(mamba.task.Request):
	def main(self):
		rest = mamba.task.RestDecoder(self)
		page = HTMLPageDiseaseInfo(rest["disease"])
		reply = mamba.http.HTMLResponse(self, page.tohtml())
		reply.send()


class Browse(mamba.task.Request):
	def main(self):
		rest = mamba.task.RestDecoder(self)
		page = HTMLPageBrowseDisease(rest)
		reply = mamba.http.HTMLResponse(self, page.tohtml())
		reply.send()

class Test(mamba.task.Request):
	def main(self):
		page = HTMLTestPage()
		reply = mamba.http.HTMLResponse(self, page.tohtml())
		reply.send()
