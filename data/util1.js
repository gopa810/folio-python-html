function doSearch() {
    var e = document.getElementById('search_box')
    var text = e.value
    var url = "x/search"

    if (text.length > 0) {
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                showSearchResults(this.responseText)
            }
        };
        xmlhttp.open("POST", url, true);
        xmlhttp.send(text);
    } else {
        var e = document.getElementById("search_result")
        if (e) {
            e.style.display = 'block'
        }
        //resizeElements()
    }

    e.value = ''
}

function goExSearch(url) {

    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            showSearchResults(this.responseText)
        }
    };
    xmlhttp.open("POST", url, true);
    xmlhttp.send();
}




function showFoundFile(file) {
    var titleE = document.getElementById('titleDoc')
    titleE.innerHTML = file

    var e = document.getElementById('frm1')
    e.src = file
    //window.location.href = file
}

var sfl_temp = {
    'lastFile': ''
}

function showFoundLoc(file,tag,num) {
    var titleE = document.getElementById('titleDoc')
    titleE.innerHTML = file

    var e = document.getElementById('frm1')
    tout = 1

    if (sfl_temp['last']!=file) {
        e.src = file
        sfl_temp['last'] = file
        tout = 200
    }

    setTimeout(function() {
        if (tag!='body') {
            efunc = 'var els = document.getElementsByTagName(\"' + tag + '\"); ' +
                'if (els.length > ' + num + ') { ce = els[' + num + ']; ' +
                'var coff = 0; ' +
                'var cel = ce; ' +
                'while (cel) { coff += cel.offsetTop; cel = cel.offsetParent;  } ' +
                'var topx = coff - (window.innerHeight / 2); ' +
                'window.scrollTo(0, topx);' +
                'ce.setAttribute(\'data-old-border\',ce.style.border); ' +
                'ce.setAttribute(\'data-old-borderRadius\',ce.style.borderRadius); ' +
                'ce.setAttribute(\'data-old-backgroundColor\',ce.style.backgroundColor); ' +
                'ce.setAttribute(\'data-old-margin\',ce.style.margin); ' +
                'ce.style.border = \'1px solid black\';' +
                'ce.style.borderRadius = \'4px\';' +
                'ce.style.backgroundColor = \'yellow\';' +
                '}'
            e.contentWindow.eval(efunc)
            //alert(e.contentWindow.scrollToEN.toString())
            //e.contentWindow.scrollToEN()
            setTimeout(function(){
                efunc2 = 'var els = document.getElementsByTagName(\"' + tag + '\"); ' +
                    'if (els.length > ' + num + ') { ce = els[' + num + ']; ' +
                    'ce.style.border = ce.getAttribute(\'data-old-border\'); ' +
                    'ce.style.borderRadius = ce.getAttribute(\'data-old-borderRadius\');' +
                    'ce.style.backgroundColor = ce.getAttribute(\'data-old-backgroundColor\');' +
                    '}'
                e.contentWindow.eval(efunc2)
            }, 1000)
        }
    },tout)
}



function resizeElements() {
    return;
    width = window.innerWidth
    height = window.innerHeight
    sbwidth = parseInt(width / 3)

    tb = document.getElementById('topbar')
    tbbottom = 52

    sp = document.getElementById('search_result')
    frm = document.getElementById('frm1')
    sp.style.left = 0
    if (sp.style.display != 'block') {
        frm.style.left = 0
        frm.style.width = width
    } else {
        sp.style.width = sbwidth

        frm.style.left = sbwidth + 20
        frm.style.width = width - frm.style.left
    }

    sp.style.top = tbbottom
    sp.style.height = height - tbbottom
    frm.style.top = tbbottom
    frm.style.height = height - tbbottom
    sp.style.top = frm.style.top
    sp.style.height = frm.style.height
}

function showSearchResults(text) {
    //alert(text)
    var data = JSON.parse(text)
    //
    // display search panel
    //
    var e = document.getElementById("search_result")
    if (e) {
        e.style.display = 'block'
    }
    //resizeElements()

    //
    // display navigation bar
    //
    txt = ''
    if (data.canGoBack) {
        txt += '<span class=\'pad8 cpoi\' onclick=\'goExSearch(\"x/search-back\");\'>&lt;</span>'
    } else {
        txt += '<span class=\'pad8\'>&nbsp;</span>'
    }
    if (data.currentPage < 0) {
        txt += 'No Results'
    } else {
        txt += '<span class=\'pad8\'>Page ' + data.currentPage + '/' + data.pages + ' </span>'
    }
    if (data.canGoForward) {
        txt += '<span class=\'pad8 cpoi\' onclick=\'goExSearch(\"x/search-forward\");\'>&gt;</span>'
    } else {
        txt += '<span class=\'pad8\'>&nbsp;</span>'
    }
    txt += '\n'

    var e_sn = document.getElementById("pageNavigation")
    e_sn.innerHTML = txt

    //
    // display search results
    //
    e = document.getElementById("search_result_text")
    if (data.currentPage >= 0) {
        if (!e) {
            return
        }
        txt = ''
        data.texts.forEach((e) => {
            txt += '<div class=\'sr_hdr\' onclick=\'showFoundFile(\"' + e.file + '\")\'>'
            txt += e.title
            txt += '</div>'
            e.text.forEach((h) => {
                txt += '<p class=\'sr_txt cpoi\' onclick=\'showFoundLoc(\"' + e.file + '\",\"' + h.tag + '\",' + h.num + ')\'>' + h.text
            })
        })
    } else {
        txt += '<div>Results for <b>\"' + data.query + '\"</b> not found</div>'
    }
    e.innerHTML = txt
}

function PutRequest(url, func) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var myArr = JSON.parse(this.responseText);
            func(myArr);
        }
    };
    xmlhttp.open("PUT", url, true);
    xmlhttp.send();
}

function getElementValue(elemId) {
    var e = document.getElementById(elemId)
    if (e) {
        return e.value
    }
    return ""
}
