#!/usr/bin/env python

import pg
import xml.etree.ElementTree as etree
import datetime
import html

class xtextmining(html.XNode):
	
	def __init__(self, parent, type, id):
		html.XNode.__init__(self, parent)
		self.type = type
		self.id = id
		
	def begin_html(self):
		q = executeSQL("SELECT document FROM matches WHERE type=%i AND id='%s' ORDER BY document DESC LIMIT 30;" % (self.type, self.id))
		q = getArticles(q.getresult())
		return GetArticleAsHTML(q, False);

	
def getConnection():
	conn_string = ['localhost','5432','ljj','textmining']
	return pg.connect(host = conn_string[0], port = int(conn_string[1]), user = conn_string[2], passwd = '', dbname = conn_string[3])

def executeSQL(cmd):
	conn = getConnection()
	q = conn.query(cmd)
	conn.close()
	return q

def getArticles(pmidlist):
	pmidlist = ",".join(map(lambda a: str(a[0]), pmidlist))
	cmd = 'SELECT * FROM documents WHERE document IN ({0});'.format(pmidlist)
	q = executeSQL(cmd)
	return q.dictresult()
	
def UTF_Encode(uni):
	return unicode(uni, 'utf-8')

def CDATAWrap(value):
	return '{0}{1}{2}'.format("<![CDATA[", value, "]]>")

def dateparser(value):
	if value.isdigit():
		return int(value)
	else :
		return 1

def str_to_set(str):
	return Set(str_to_array(str))

def str_to_array(str):
	arr = []
	str = str.strip()
	if len(str) > 0 :
		arr = [int(x) for x in str.split(',')]
	return arr
	

def GetArticleAsHTML(ranked_dictresult, CDATAWRAP):
	parsed_result = ParseDBResult(ranked_dictresult, CDATAWRAP)
	results = parsed_result['results']
	articles = {}
	for article in ranked_dictresult :
		PMID = str(article['document'])
		articles[PMID] = results[PMID]
			
	root = etree.Element('Response')
	articlehtml = etree.SubElement(root, 'ArticleHTML')    
	return HTMLWrapArticles(articles, CDATAWRAP)

def ParseDBResult( pygresql_dictresult, CDATAWRAP ):
	results = {}
	PMID = None
	for result in pygresql_dictresult :
		PMID = str(result['document'])
		doc_text = result['text'].split('\t', 1)
		
		data = {}
		data['journal'] = result['publication']
		data['authors'] = result['authors'].split(',')
		data['year'] = result['year']
		data['title'] = UTF_Encode(doc_text[0])
		
		if len(doc_text) > 1 :
			data['abstract'] = doc_text[1]
		else :
			data['abstract'] = ''
		results[PMID] = data
	return_val = {}
	return_val['results'] = results
	return return_val

def HTMLWrapArticles(articles, CDATAWRAP):
	
	tagname = "ArticleHTML"
	articlehtml = etree.Element(tagname)
	
	date_sorting = {}
	journal_sorting = {}
	title_sorting = {}
	ranked_sorting = []
	
	t_start = datetime.datetime.now()
	for pmid, values in articles.iteritems():
		PMID = pmid
		article_wrapper = etree.SubElement(articlehtml,'div', {'class': 'article_wrapper', 'id': PMID})
		title_wrapper = etree.SubElement(article_wrapper, 'div', {'class': 'article_title'})
		title_wrapper.text = values['title']
		
		author_wrapper = etree.SubElement(article_wrapper, 'span', {'class': 'article_authors'})
		for idx, el_author in enumerate(values['authors'][:3]):
			a = etree.SubElement(author_wrapper, 'a', {'href': 'http://www.ncbi.nlm.nih.gov/pubmed?term={0}[author]'.format(el_author), 'target': '_blank'})
			a.text = UTF_Encode( el_author )
			if idx == 2 :
				a.text += " ..."
				
		journal_wrapper = etree.SubElement(author_wrapper, 'span', {'class': 'article_journal'})
		journal = values['journal']
		link = 'http://www.ncbi.nlm.nih.gov/pubmed?term={0}[journal]'.format(journal.split('.')[0])
		a = etree.SubElement(journal_wrapper, 'a', {'href': link, 'target': '_blank'})
		a.text = journal
		label_year = etree.SubElement(journal_wrapper, 'label', {'class': 'article_year'})
		label_year.text = "(" + values['year'] + ')'
		
		doc = values['abstract']
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
		title_sorting[PMID] = values['title'][:10]
		pubdate = date(dateparser(str(values['year'])), 1, 1)
		date_sorting[PMID] = pubdate
		journal_sorting[PMID] = values['journal']
	
	
	html = etree.tostring(articlehtml) 
	html = html[html.find('<' + tagname + '>')+len(tagname)+2:html.find('</' + tagname+ '>')]
	return_val = {}
	
	if CDATAWRAP:
		return_val[tagname] = CDATAWrap( html )
	else :
		return_val[tagname] = html
	
	return_val['ranked_sorting'] = ranked_sorting
	return_val['title_sorting'] = title_sorting
	return_val['journal_sorting'] = journal_sorting
	return_val['date_sorting'] = date_sorting
	return html 
