#!/usr/bin/env python

import pg
import types
import xml.sax.saxutils as saxutils
import xml.etree.ElementTree as etree
import time, datetime
from datetime import date
from time import gmtime, strftime, strptime
from operator import itemgetter
import math

DB_CONN = ['localhost',8081,'andbok','OpenMed']

#TODO : FIXME: sdsdfds  

def get_html(type, id) :
    """
        : param type : type of ?
        : param id : id of protein
    """
    
    pmidlist = '21779458 ,22002450'
    q = getArticles(pmidlist)
    
    html = GetArticleAsHTML(q, False);
    # Get the matching documentids
    # call getArticles
    # call GetArticleAsHTML2
    # return html fragment 
    return html

def getConnection() :
    #conn_string = mamba.setup.config().globals['conn_string'].split(";")
    conn_string = DB_CONN
    return pg.connect(host = conn_string[0], port = int(conn_string[1]), user = conn_string[2], passwd = '', dbname = conn_string[3])

def executeSQL(cmd) :
    conn = getConnection()
    q = conn.query(cmd)
    conn.close()
    return q

def getArticles(pmidlist) :    
    """
        get articles from database
        :param pmidlist : list of pmids to retrieve
    """    
        
    print 'pmidlist'
    print pmidlist
    
    cmd = 'SELECT * FROM documents WHERE PMID in ({0})'.format(pmidlist)
    q = executeSQL(cmd)
    return q.dictresult()
    
def UTF_Encode(uni) :
    #uni = uni.encode('iso-8859-1')
    return unicode(uni, 'utf-8')

def CDATAWrap(value) :
    return '{0}{1}{2}'.format("<![CDATA[", value, "]]>")

def dateparser(value) :
    if value.isdigit() :
        return int(value)
    else :
        return 1

def str_to_set(str) :
    return Set(str_to_array(str))

def str_to_array(str) :
    arr = []
    str = str.strip()
    if len(str) > 0 :
        arr = [int(x) for x in str.split(',')]
    return arr
    

def GetArticleAsHTML(ranked_dictresult, CDATAWRAP) :
    
    parsed_result = ParseDBResult(ranked_dictresult, CDATAWRAP)
    
    results = parsed_result['results']
    
    
    articles = {}
    
    for article in ranked_dictresult :
        PMID = str(article['pmid'])
        articles[PMID] = results[PMID]
            
    root = etree.Element('Response')
    
    
    articlehtml = etree.SubElement(root, 'ArticleHTML')
    
    wrapped = HTMLWrapArticles(articles, "ArticleHTML", CDATAWRAP)
    
    articlehtml.text = wrapped['ArticleHTML']
    
    date_sorting = wrapped['date_sorting']
    journal_sorting = wrapped['journal_sorting']
    title_sorting = wrapped['title_sorting']
    ranked_sorting = wrapped['ranked_sorting']
    
    custom_tags = etree.SubElement(root, 'CUSTOM_TAGS')
    
    date_sorting = sorted(date_sorting.iteritems(), key=itemgetter(1), reverse=True)
    sorted_values = map(lambda x: x[0],date_sorting)
    el = etree.SubElement(custom_tags, 'Date_sorting')
    el.text = ','.join(map(str, sorted_values))
    
    journal_sorting = sorted(journal_sorting.iteritems(), key=itemgetter(1))
    sorted_values = map(lambda x: x[0], journal_sorting)
    el = etree.SubElement(custom_tags, 'Journal_sorting')
    el.text = ','.join(map(str, sorted_values))

    title_sorting = sorted(title_sorting.iteritems(), key=itemgetter(1))
    sorted_values = map(lambda x: x[0], title_sorting)
    el = etree.SubElement(custom_tags,'Title_sorting')
    el.text = ','.join(map(str, sorted_values))
    
    el = etree.SubElement(custom_tags,'Ranked_sorting')
    el.text = ','.join(map(str, sorted_values))
    
#    for key, value in extra_tags.iteritems() :
#        el = etree.Element(key)
#        el.text = str(value) + ' '
#        custom_tags.append(el)
    
    if CDATAWRAP :
        html = etree.tostring(custom_tags)
        html = html[html.find('<CUSTOM_TAGS>')+13:html.find('</CUSTOM_TAGS>')]
        custom_tags.text = CDATAWrap( html )
    
    
#    pages = math.ceil(float(extra_tags['QuerySize'])/float(extra_tags['PageSize']))
#    prev_next_page_wrapper = etree.SubElement(root, 'PREV_NEXT_PAGE_HTML')
#    if extra_tags['PageNumber'] > 0 : 
#        a = etree.SubElement(prev_next_page_wrapper, 'a', {'href': "javascript:onChangePage('prev');"})
#        a.text = 'prev'
    
#    for i in range(min(5, int(pages))) :
#        attribs = {}
#        attribs['href'] = "javascript:onChangePage('{0}');".format(i)
#        if (i == extra_tags['PageNumber']) :
#            attribs['class'] = 'selected'
#        a = etree.SubElement(prev_next_page_wrapper, 'a', attribs)
#        a.text = str(i+1)
#    if extra_tags['PageNumber'] < pages-1 : 
#        a = etree.SubElement(prev_next_page_wrapper, 'a', {'href': "javascript:onChangePage('next');"})
#        a.text = 'next'
    
    if CDATAWRAP :
        html = etree.tostring(prev_next_page_wrapper)
        html = html[html.find('<PREV_NEXT_PAGE_HTML>')+21:html.find('</PREV_NEXT_PAGE_HTML>')]
        prev_next_page_wrapper.text = CDATAWrap( html )
    
    HTML = etree.SubElement(root, 'ReflectHTML')
#    HTML.text = reflected.findtext('HTML')
    
    #Debug
    #output = open('output.txt', 'w')
    #output.write(etree.tostring(root))
    #output.close();
    
    return articlehtml

def ParseDBResult( pygresql_dictresult, CDATAWRAP ) :
#    reflected = etree.Element('Response')
    results = {}
    
    PMID = None
    for result in pygresql_dictresult :
        PMID = str(result['pmid'])
        doc_text = result['document'].split('\\t', 1)
        data = {}
        
        data['journal'] = result['publication']
        data['authors'] = result['author'].split(',')
        data['year'] = result['year']
        data['title'] = UTF_Encode(doc_text[0])
        
#        r_pmid = etree.SubElement(reflected, 'Article', {'pmid': PMID})
        
#        r_title = etree.SubElement(r_pmid, 'title')
#        r_title.text = UTF_Encode( doc_text[0] )
        
#        r_abstract_txt = etree.SubElement(r_pmid, 'abstract_txt')
        if len(doc_text) > 1 :
            #r_abstract_txt.text = doc_text[1] 
            data['abstract'] = doc_text[1]
        else :
            #r_abstract_txt.text = ''
            data['abstract'] = ''
        
        results[PMID] = data
    
    
    return_val = {}
    return_val['results'] = results
    return return_val

def HTMLWrapArticles(articles, tagname, CDATAWRAP) :
    articlehtml = etree.Element(tagname)    
    
    date_sorting = {}
    journal_sorting = {}
    title_sorting = {}
    ranked_sorting = []
    
    t_start = datetime.datetime.now()
    for pmid, values in articles.iteritems() :
        PMID = pmid
        print PMID
        article_wrapper = etree.SubElement(articlehtml,'div', {'class': 'article_wrapper article_neutral', 'id': PMID})
        feedback_wrapper = etree.SubElement(article_wrapper, 'div', {'class': 'article_feedback'})
        
        icon_titles = {'positive':'add article to positives', 'negative':'remove article from search result'}
        icons = {'positive':'yes.png', 'negative':'no.png'}
        # Debug
        #icons = {}  
        for key, value in icons.iteritems() :
            cmd = "javascript:handleFeedback('{0}', '{1}')".format(PMID, key)
            a = etree.SubElement(feedback_wrapper, 'a', {'href': cmd, 'class': 'feedback_' + key, 'title': icon_titles[key]})
            img = etree.SubElement(a, 'img', {'src': 'css/images/{0}'.format(value)})
        
        title_wrapper = etree.SubElement(article_wrapper, 'div', {'class': 'article_title'})
        title_wrapper.text = values['title']
        
        author_wrapper = etree.SubElement(article_wrapper, 'span', {'class': 'article_authors'})
        
        #for el_author in values['authors'] :
        for idx, el_author in enumerate(values['authors'][:3]) :
            a = etree.SubElement(author_wrapper, 'a', {'href': 'http://www.ncbi.nlm.nih.gov/pubmed?term={0}[author]'.format(el_author), 'target': '_blank'})
            a.text = UTF_Encode( el_author )
            if idx == 2 :
                a.text += " ..."
                
        journal_wrapper = etree.SubElement(article_wrapper, 'span', {'class': 'article_journal'})
        journal = values['journal']
        link = 'http://www.ncbi.nlm.nih.gov/pubmed?term={0}[journal]'.format(journal.split('.')[0])
        a = etree.SubElement(journal_wrapper, 'a', {'href': link, 'target': '_blank'})
        a.text = journal
        label_year = etree.SubElement(journal_wrapper, 'label', {'class': 'article_year'})
        label_year.text = "(" + values['year'] + ')'
        
        abstract_wrapper = etree.SubElement(article_wrapper, 'div', {'class': 'article_abstract'})
        abstract_wrapper.text = values['abstract'] + '&nbsp;'
        
        h_spacer = etree.SubElement(articlehtml, 'div', {'class': 'h_spacer'})
        h_spacer.text = '&nbsp;'
        
        ranked_sorting.append(PMID)
        title_sorting[PMID] = values['title'][:10]
        pubdate = date(dateparser(str(values['year'])), 1, 1)
        date_sorting[PMID] = pubdate
        journal_sorting[PMID] = values['journal']
    
    
    print etree.tostring(articlehtml)
    html = saxutils.unescape( etree.tostring(articlehtml) )
    print "\n\n\n\n\n"
    print articlehtml
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

    return return_val

html = get_html(1, 1);
