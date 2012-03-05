// =============================================================================
//
// Unfinished functions for retrieving "pages" of documents for textmining.
//
// =============================================================================
//var http;
//if (window.XMLHttpRequest) { 
//	http = new XMLHttpRequest();
//
//} else if (window.ActiveXObject) { 
//	http = new ActiveXObject("Microsoft.XMLHTTP");
//}
//
//function makeDocumentsRequest(type1, id1, type2, offset) {
//	http.open('get', 'GetDocuments?type1=" + type1 + "&id1=' + id1 + "&type2=" + type2 + "&offset=" + offset);
//    http.onreadystatechange = processDocumentsResponse;
//    http.send(null);
//}
//
//function processDocumentsResponse() {
//    if(http.readyState == 4){
//        document.getElementById('documentsBox').innerHTML = http.responseText;
//    }
//}


// =============================================================================
//
// Textmining-table: Expnad, collapse teaser vs. whole abstract text.
//
// =============================================================================

function toggle_abstract(article_id, action)
{
	divs = $("#" + article_id + " .article_abstract div");
	el1 = divs[0];
	el2 = divs[1];
	if (action == "expand") {
		$(el1).addClass("hidden");
		$(el2).removeClass("hidden");
	}
	else {
		$(el1).removeClass("hidden");
		$(el2).addClass("hidden");
	}
}