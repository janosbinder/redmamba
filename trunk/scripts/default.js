var http;
if (window.XMLHttpRequest) { 
	http = new XMLHttpRequest();

} else if (window.ActiveXObject) { 
	http = new ActiveXObject("Microsoft.XMLHTTP");
}

function makeDocumentsRequest(type1, id1, type2, offset) {
	http.open('get', 'GetDocuments?type1=" + type1 + "&id1=' + id1 + "&type2=" + type2 + "&offset=" + offset);
    http.onreadystatechange = processDocumentsResponse;
    http.send(null);
}

function processDocumentsResponse() {
    if(http.readyState == 4){
        document.getElementById('documentsBox').innerHTML = http.responseText;
    }
}
