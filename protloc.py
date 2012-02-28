import pg
import math
import datetime

from html import *
import datapage
import obo

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
	def get_pairs(type1, id1, type2, textmining):
		return textmining.query("SELECT * FROM pairs WHERE type1=%i AND id1='%s' AND type2=%i ORDER BY evidence DESC LIMIT 50;" % (type1, id1, type2))
		
	@staticmethod
	def get_stars(score):
		score = min(5, float(score))
		stars = "".join(["&#9733;"]*int(score))
		if round(score) - int(score) >= 0.5:
			stars += "&#9734;"
		if score >= 4:
			stars = '<font color="green">%s</font>' % stars
		elif score >= 3:
			stars = '<font color="blue">%s</font>' % stars
		else:
			stars = '<font color="MidnightBlue">%s</font>' % stars
		return stars
	

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
		

class HTMLPageCollide(XPage):
	
	def __init__(self):
		XPage.__init__(self, "<table><tr><td>Compendium of Liteature Listed</td></tr><tr><td>Disease Gene Associations (Collide&#0153;)</td></tr></table>")
		XP(self.frame.sidebar, datetime.datetime.now().strftime('%a-%d-%b-%Y %H:%M:%S %Z'))
		tbl = XTable(self.frame.sidebar, {"width":"100%"})
		tbl.addrow("Disease",  "8,553")
		tbl.addrow("Proteins", "2,714")
		

class TextminingPairsTable(XDataTable):
	
	def __init__(self, parent, type1, id1, type2, textmining, dictionary):
		XDataTable.__init__(self, parent)
		self["width"] = "100%"
		
		if type2 > 0:
			self.addhead("#", "Gene name", "Ensembl ID", "Z-score", "Evidence")
		elif type2 == -1:
			self.addhead("#", "Drug", "PubChem ID", "Z-score", "Evidence")
		elif type2 <= -21 and type2 >= -24:
			self.addhead("#", "Gene Ontology", "GO ID", "Z-score", "Evidence")
		else:
			self.addhead("#", "Name", str(type2), "Z-score", "Evidence")
			
		i = 1
		for row in TalkDB.get_pairs(type1, id1, type2, textmining).getresult():
			ty1, idx1, ty2, idx2, evidence, score = ensp = row
			if score < 2.4:
				break
			bestname = TalkDB.get_best_name(ty2, idx2, dictionary)
			ensembl = '<a href="http://www.ensembl.org/Homo_sapiens/Gene/Summary?g=%s" target="_blank">%s</a>' % (idx2, idx2)
			row = self.addrow(i, "<strong>%s</strong>" % bestname, ensembl, "%.2f" % evidence, TalkDB.get_stars(score))
			row.nodes[4]["fgcolor"] = "red"
			i += 1
		


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
			XH3(p1, "Definition (DOID)")
			XFree(p1, term.definition)
		
		if len(term.wikitext):
			XH3(p1, "Description (Wikipedia)")
			XFree(p1, term.wikitext)
		
		if term.wiki:
			XFree(p1, '<br></br><a href="%s" target="wikipedia_tab">Wikipedia</a>' % term.wiki)
		
		p2 = XP(section.body)
		XH3(p2, "Synonyms")
		ul = XTag(p2, "ul")
		for synonym in term.synonyms:
			XFree(XTag(ul, "li"), synonym.capitalize())	
			
		if len(term.parents):
			p3 = XP(section.body)
			XH3(p3, "Derives from")
			ul = XTag(p3, "ul")
			for parent in term.parents:
				XFree(ul, '<li><a href="/Browse?doid=%s">%s</a></li>' % (parent.id, parent.name.capitalize()))
		
		if len(term.children):
			p5 = XP(section.body)
			XH3(p5, "Relates to")
			ul = XTag(p5, "ul")
			for child in term.children:
				XFree(ul, '<li><a href="/Browse?doid=%s">%s</a></li>' % (child.id, child.name.capitalize()))
		
		textmining = pg.connect(host='localhost', user='ljj', dbname='textmining')
		dictionary = pg.connect(host='localhost', user='ljj', dbname='dictionary')
		
		XH3(section.body, "Literature")
		datapage.XTextMiningResult(section.body, textmining, -26, term.id)
		
		XHr(section.body)
			
		p6 = XP(section.body)
		XH3(p6, "Sub-cellular localization")
		tbl = XDataTable(p6)
		tbl["width"] = "100%"
		tbl.addhead("#", "Term", "GO", "Z-score", "Evidence")
		i = 1
		for score, go in term.gocc:
			if i > 10:
				break
			best   = TalkDB.get_best_name(-22, go, dictionary).capitalize()
			golink = '<a href="http://www.ebi.ac.uk/QuickGO/GTerm?id=%s" target="gene_ontology_tab">%s</a>' % (go, go)
			zscore = "%.2f" % score
			stars  = TalkDB.get_stars(score)
			row = tbl.addrow(i, "<strong>%s</strong>" % best, golink, zscore, stars)
			i += 1
		
		p7 = XP(section.body)
		XH3(p7, "Genes")
		TextminingPairsTable(p7, -26, term.id, 9606, textmining, dictionary)
			
		XH3(p7, "Drugs and Compounds")
		tbl = XDataTable(p7)
		TextminingPairsTable(p7, -26, term.id, -1, textmining, dictionary)
		


class HTMLPageSearch(HTMLPageCollide):
	
	def __init__(self, rest):
		HTMLPageCollide.__init__(self)
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
			

class HTMLPageProtein(HTMLPageCollide):
	
	def __init__(self, type, id):
		HTMLPageCollide.__init__(self)
		self.head.title = "Protein %s" % id
		box = XBox(self.frame.content)
		textmining = pg.connect(host='localhost', user='ljj', dbname='textmining')
		datapage.XTextMiningResult(box.content, textmining, 9606, "ENSP00000332369")


class HTMLPageDiseaseInfo(HTMLPageCollide):
	
	def __init__(self, disease):
		HTMLPageCollide.__init__(self)
		self.head.title = "Diseases"

		group1 = XGroup(self.frame.content, "Diseases")
		XSection(group1.body, "Disease gene associations", '<img src="figure2.png" width="250px"></img>Using an andvanced textmining pipeline against the full body of indexed medical literatur and a ontology-derived, ontology-self-curated dictionary consisting of proteins, disease, chemicals etc. we have created the worlds first resource linking genes to diseases on a scale never seen before.')
		XSection(group1.body, "Alzheimer's disease", "A dementia that results in progressive memory loss, impaired thinking, disorientation, and changes in personality and mood starting in late middle age and leads in advanced cases to a profound decline in cognitive and physical functioning and is marked histologically by the degeneration of brain neurons especially in the cerebral cortex and by the presence of neurofibrillary tangles and plaques containing beta-amyloid.")
		
		group2 = XGroup(self.frame.content, "Text-mining")
		textmining = pg.connect(host='localhost', user='ljj', dbname='textmining')
		datapage.XTextMiningResult(group2.body, textmining, 9606, "ENSP00000332369")



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
