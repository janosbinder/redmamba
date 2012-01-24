#!/usr/bin/env python

import pg
import types

DB_CONN = 'localhost;8081;andbok;;OpenMed'

# TODO : sfsdf

def get_html(self, type, id) :
    """
        : param type : type of ?
        : param id : id of protein
    """
    print 'peace'

def doSearch(id) :
    """
        Search document database for matching articles 
    """
    # call getArticles
    # call GetArticleAsHTML2
    # return html fragment

def getConnection(self) :
    conn_string = mamba.setup.config().globals['conn_string'].split(";")
    return pg.connect(host = conn_string[0], port = int(conn_string[1]), user = conn_string[2], passwd = conn_string[3], dbname = conn_string[4])

def getArticles(self, pmidlist) :
    
    """
        get articles from database
        :param pmidlist : list of pmids to retrieve
    """
    print 'pmidlist'
    print pmidlist
    cmd = 'SELECT * FROM documents WHERE PMID in ({0})'.format(pmidlist)
    q = executeSQL(cmd)
    return q.dictresult()
    
def UTF_Encode(self, uni) :
    #uni = uni.encode('iso-8859-1')
    return unicode(uni, 'utf-8')
    

def GetArticleAsHTML(ranked_dictresult, reflect, CDATAWRAP) :
    
    merged = list(ranked_dictresult)
    for result in positives_dictresult :
        merged.append(result)
    print 'merged'
    print merged
    parsed_result = ParseDBResult(merged, reflect, CDATAWRAP)
    
    reflected = parsed_result['reflected']
    print (reflected)
    results = parsed_result['results']
    
    articles = {}
    positives = {}
    
    for article in ranked_dictresult :
        PMID = str(article['pmid'])
        articles[PMID] = results[PMID]
    
    for article in positives_dictresult :
        PMID = str(article['pmid'])
        positives[PMID] = results[PMID]
    
    root = etree.Element('Response')
    
    if len(positives_dictresult) > 0 :
        positiveshtml = etree.SubElement(root, 'PositivesHTML')
        wrapped = HTMLWrapArticles(positives, "PositivesHTML", CDATAWRAP)
        positiveshtml.text = wrapped['PositivesHTML']
    
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
    
    for key, value in extra_tags.iteritems() :
        el = etree.Element(key)
        el.text = str(value) + ' '
        custom_tags.append(el)
    
    if CDATAWRAP :
        html = etree.tostring(custom_tags)
        html = html[html.find('<CUSTOM_TAGS>')+13:html.find('</CUSTOM_TAGS>')]
        custom_tags.text = CDATAWrap( html )
    
    
    pages = math.ceil(float(extra_tags['QuerySize'])/float(extra_tags['PageSize']))
    prev_next_page_wrapper = etree.SubElement(root, 'PREV_NEXT_PAGE_HTML')
    if extra_tags['PageNumber'] > 0 : 
        a = etree.SubElement(prev_next_page_wrapper, 'a', {'href': "javascript:onChangePage('prev');"})
        a.text = 'prev'
    
    for i in range(min(5, int(pages))) :
        attribs = {}
        attribs['href'] = "javascript:onChangePage('{0}');".format(i)
        if (i == extra_tags['PageNumber']) :
            attribs['class'] = 'selected'
        a = etree.SubElement(prev_next_page_wrapper, 'a', attribs)
        a.text = str(i+1)
    if extra_tags['PageNumber'] < pages-1 : 
        a = etree.SubElement(prev_next_page_wrapper, 'a', {'href': "javascript:onChangePage('next');"})
        a.text = 'next'
    
    if CDATAWRAP :
        html = etree.tostring(prev_next_page_wrapper)
        html = html[html.find('<PREV_NEXT_PAGE_HTML>')+21:html.find('</PREV_NEXT_PAGE_HTML>')]
        prev_next_page_wrapper.text = CDATAWrap( html )
    
    HTML = etree.SubElement(root, 'ReflectHTML')
    HTML.text = reflected.findtext('HTML')
    
    #output = open('output.txt', 'w')
    #output.write(etree.tostring(root))
    #output.close();
    
    return root

def ParseDBResult( pygresql_dictresult, REFLECT, CDATAWRAP ) :
    reflected = etree.Element('Response')
    results = {}
    
    PMID = None
    for result in pygresql_dictresult :
        PMID = str(result['pmid'])
        doc_text = result['document'].split('\\t', 1)
        data = {}
        
        data['journal'] = result['publication']
        data['authors'] = result['author'].split(',')
        data['year'] = result['year']
        data['title'] = doc_text[0]
        
        r_pmid = etree.SubElement(reflected, 'Article', {'pmid': PMID})
        
        r_title = etree.SubElement(r_pmid, 'title')
        r_title.text = UTF_Encode( doc_text[0] )
        
        r_abstract_txt = etree.SubElement(r_pmid, 'abstract_txt')
        if len(doc_text) > 1 :
            r_abstract_txt.text = doc_text[1] 
            data['abstract'] = doc_text[1]
        else :
            r_abstract_txt.text = ''
            data['abstract'] = ''
        
        results[PMID] = data
    
    if REFLECT == True :
        t_start = datetime.datetime.now()
        reflected = Reflect(reflected, CDATAWRAP)
        print ('reflected')
        print (datetime.datetime.now()-t_start)
        for article in reflected.findall('Article') :
            PMID = article.get('pmid')
            
            title = etree.tostring(article.find('title'), 'UTF-8')
            results[PMID]['title'] = title[title.find('<title>')+7:title.find('</title>')]
            
            abstract = article.find('abstract_txt')
            
            if abstract.text == None :
                results[PMID]['abstract'] = ''
            else :
                abstract = etree.tostring(abstract, 'UTF-8')
                results[PMID]['abstract'] = abstract[abstract.find('<abstract_txt>')+14:abstract.find('</abstract_txt>')]
    
    return_val = {}
    return_val['reflected'] = reflected
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
    
    html = saxutils.unescape( etree.tostring(articlehtml) )
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


def Reflect(doc, CDATAWRAP):
    doc = etree.tostring(doc)
    tagdoc = mamba.setup.config().tagger.GetHTML(doc, None, [-1, -11, 9606])
    reflect_response = etree.fromstring(tagdoc[:tagdoc.find('</Response>')+11]);
    HTML = etree.SubElement(reflect_response, 'HTML')
    if CDATAWRAP: 
        HTML.text = CDATAWrap(tagdoc[tagdoc.find('</Response>')+11:tagdoc.find('</body>')])
    else :
        HTML.text = tagdoc[tagdoc.find('</Response>')+11:tagdoc.find('</body>')]
    
    return reflect_response