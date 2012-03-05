#!/usr/bin/env python

import html
import datetime


class PairsHTML(html.XDataTable):
	
	def __init__(self, parent, type1, id1, type2, textmining, dictionary):
		html.XDataTable.__init__(self, parent)
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
		for row in self.select_pairs(type1, id1, type2, textmining).getresult():
			ty1, idx1, ty2, idx2, evidence, score = ensp = row
			if score < 2.4:
				break
			bestname = self.select_best_name(ty2, idx2, dictionary)
			ensembl = '<a href="http://www.ensembl.org/Homo_sapiens/Gene/Summary?g=%s" target="_blank">%s</a>' % (idx2, idx2)
			row = self.addrow(i, "<strong>%s</strong>" % bestname, ensembl, "%.2f" % evidence, self.give_stars(score))
			i += 1
		
	def __str__(self):
		return self.tohtml()
		
	def select_best_name(self, typex, idx, dictionary):
		bestname = idx
		names = dictionary.query("SELECT name FROM preferred WHERE type=%i AND id='%s';" % (typex, idx)).getresult()
		if len(names):
			bestname = names[0][0]
		return bestname
	
	def select_pairs(self, type1, id1, type2, textmining):
		return textmining.query("SELECT * FROM pairs WHERE type1=%i AND id1='%s' AND type2=%i ORDER BY evidence DESC LIMIT 50;" % (type1, id1, type2))
		
	def give_stars(self, score):
		stars = int(min(5, float(score)))
		return '<span class="stars">%s</span>' % "".join(["&#9733;"]*stars + ["&#9734;"]*(5-stars))


class DocumentsHTML(html.XNode):
	
	def __init__(self, parent, database, qtype, qid):
		html.XNode.__init__(self, parent)
		
		self.database = database
		self.qtype = qtype
		self.qid   = qid
		
		cmd = "SELECT DISTINCT document FROM matches WHERE type=%i AND id='%s' ORDER BY document DESC LIMIT 10;" % (self.qtype, self.qid)
		n = 0
		for pmid in self.database.query(cmd).getresult():
			PMID = str(pmid[0])
			document = self.database.query("SELECT * FROM documents WHERE document=%i;" % pmid).dictresult()[0]
			doc_text = html.string2bytes(document["text"]).split("\t", 1)
			title    = doc_text[0]
			if len(doc_text) > 1 :
				abstract = doc_text[1]
			else :
				abstract = ""
			journal  = html.string2bytes(document["publication"])
			authors  = html.string2bytes(document["authors"]).split(",")
			year     = html.string2bytes(document["year"])
			
			n += 1
			article_wrapper = html.XDiv(self, "article_wrapper", PMID)
			if n % 2 == 0:
				article_wrapper["style"] = "border: solid 2px #CCCCAA; background: #EEEEDD;"
			
			title_wrapper = html.XDiv(article_wrapper, "article_title")
			html.XFree(title_wrapper, title)
			author_wrapper = html.XSpan(article_wrapper, {"class": "article_authors"})
			for idx, el_author in enumerate(authors[:3]):
				text = el_author
				if idx == 2:
					text += " ..."
				addr = "http://www.ncbi.nlm.nih.gov/pubmed?term=%s[author]" % el_author
				a = html.XLink(author_wrapper, addr, text)
				a["style"] = "text-decoration: none"
					
			journal_wrapper = html.XSpan(author_wrapper, {'class': 'article_journal'})
			a = html.XLink(journal_wrapper, "http://www.ncbi.nlm.nih.gov/pubmed?term=%s[journal]" % journal.split(".")[0], journal)
			a["style"] = "text-decoration: none"
			label = html.XTag(journal_wrapper, "label", {'class': 'article_year'})
			html.XFree(label, "(%s)" % year)
			
			article_abstract = html.XDiv(article_wrapper, "article_abstract")
			if len(abstract) == 0:
				html.XFree(article_abstract, "[No abstract text.]")
			elif len(abstract) < 270:
				abstract_text = html.XDiv(article_abstract)
				abstract_text["style"] = "display:block"
				html.XFree(abstract_text, abstract)
			else:
				abstract_teaser = html.XDiv(article_abstract)
				abstract_teaser["onclick"] = "javascript:toggle_abstract('%s', 'expand')" % PMID
				html.XFree(abstract_teaser, " ".join([abstract[:270], " ...", '<span style="color: steelblue;">(more)</span>']))
				
				abstract_full = html.XDiv(article_abstract)
				abstract_full["onclick"] = "javascript:toggle_abstract('%s', 'collapse')" % PMID
				abstract_full["class"] = "hidden"
				html.XFree(abstract_full, abstract)
		