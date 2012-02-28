#!/usr/bin/env python

import html
import datetime
import xml.etree.ElementTree as etree


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
	
	def __init__(self, parent, database, type, id):
		html.XNode.__init__(self, parent)
		self.database = database
		self.type = type
		self.id   = id
		
	def begin_html(self):
		articles = {}
		cmd = "SELECT document FROM matches WHERE type=%i AND id='%s' ORDER BY document DESC LIMIT 5;" % (self.type, self.id)
		for pmid in self.database.query(cmd).getresult():
			PMID = str(pmid[0])
			document = self.database.query("SELECT * FROM documents WHERE document=%i;" % pmid).dictresult()[0]
			doc_text = document['text'].split('\t', 1)
			data = {}
			data['journal'] = document['publication']
			data['authors'] = document['authors'].split(',')
			data['year']  = document['year']
			data['title'] = unicode(doc_text[0], 'utf-8')
			if len(doc_text) > 1 :
				data['abstract'] = doc_text[1]
			else :
				data['abstract'] = ''
			articles[PMID] = data

		root = etree.Element('Response')
		articlehtml = etree.SubElement(root, 'ArticleHTML')    
		
		tagname = "ArticleHTML"
		articlehtml = etree.Element(tagname)
		
		date_sorting = {}
		journal_sorting = {}
		title_sorting = {}
		ranked_sorting = []
		
		t_start = datetime.datetime.now()
		for PMID in articles:
			document = articles[PMID]
			article_wrapper = etree.SubElement(articlehtml,'div', {'class': 'article_wrapper', 'id': PMID})
			title_wrapper = etree.SubElement(article_wrapper, 'div', {'class': 'article_title'})
			title_wrapper.text = document['title']
			
			author_wrapper = etree.SubElement(article_wrapper, 'span', {'class': 'article_authors'})
			for idx, el_author in enumerate(document['authors'][:3]):
				a = etree.SubElement(author_wrapper, 'a', {'href': 'http://www.ncbi.nlm.nih.gov/pubmed?term={0}[author]'.format(el_author), 'target': '_blank'})
				a.text = unicode(el_author, 'utf-8')
				if idx == 2 :
					a.text += " ..."
					
			journal_wrapper = etree.SubElement(author_wrapper, 'span', {'class': 'article_journal'})
			journal = document['journal']
			link = 'http://www.ncbi.nlm.nih.gov/pubmed?term={0}[journal]'.format(journal.split('.')[0])
			a = etree.SubElement(journal_wrapper, 'a', {'href': link, 'target': '_blank'})
			a.text = journal
			label_year = etree.SubElement(journal_wrapper, 'label', {'class': 'article_year'})
			label_year.text = "(" + document['year'] + ')'
			
			doc = document['abstract']
			if len(doc) == 0:
				abstract_wrapper = etree.SubElement(article_wrapper, 'div', {'class': 'article_abstract abstract_expand'})
				abstract_wrapper.text = "[No abstract text.]"
			elif len(doc) < 170:
				abstract_wrapper = etree.SubElement(article_wrapper, 'div', {'class': 'article_abstract abstract_expand'})
				abstract_wrapper.text = doc
			else:
				abstract_teaser = etree.SubElement(article_wrapper, 'div', {'class': 'article_abstract', 'style':'display:inline'})
				abstract_teaser.text = doc[:170]
				abstract_wrapper = etree.SubElement(article_wrapper, 'div', {'class': 'article_abstract abstract_expand', 'style':'display:none;'})
				abstract_wrapper.text = doc
				expand_link = etree.SubElement(article_wrapper, 'span', {'style':'float:right;', 'onclick' : "toggle_abstract('%s')" % PMID})
				expand_link.text = '(more)'
			
			h_spacer = etree.SubElement(articlehtml, 'div', {'class': 'h_spacer'})
			h_spacer.text = ' '
			
			ranked_sorting.append(PMID)
			title_sorting[PMID] = document['title'][:10]
			if document['year'].isdigit():
				date_sorting[PMID] = datetime.date(int(document['year']), 1, 1)
			else:
				date_sorting[PMID] = datetime.date(1, 1, 1)
			journal_sorting[PMID] = document['journal']
		
		html = etree.tostring(articlehtml) 
		html = html[html.find('<' + tagname + '>')+len(tagname)+2:html.find('</' + tagname+ '>')]
		return html 
