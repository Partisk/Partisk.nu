// Construct html based on matching text and search term
var splitText = function (text, term) {
    var pos = text.toLowerCase().indexOf(term);

    if (pos === 0) {
        var rem = text.slice(term.length);
        return '<span class="term">' + term + '</span><span>' + rem + '</span>';
    } else if (pos === text.length - term.length) {
        var rem = text.slice(0, text.length - term.length);
        return '<span>' + rem + '</span><span class="term">' + term + '</span>';
    } else if (pos === -1) {
        return '<span>' + text + '</span>';
    } else {
        var start = text.slice(0, pos);
        var end = text.slice(pos + term.length);
        return '<span>' + start + '</span><span class="term">' + term + '</span><span>' + end + '</span>';
    }
}

var partiesSettingsHash;

var showParty = function (party) {
    if (partiesSettingsHash === undefined) {
        return party.x;
    } else {
        return partiesSettingsHash[party.i];
    }
}

function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function updateCookie(cname, value) {
    var myDate = new Date();
    myDate.setMonth(myDate.getMonth() + 12);

    document.cookie = cname + '=' + value + ';expires=' + myDate + ';';
    console.log(cname + '=' + value + ';');
}

var loadSettings = function () {
    var settingsCookie = getCookie('settings');

    if (settingsCookie) {
        var settings = settingsCookie.split(',');
    
        partiesSettingsHash = {};
        for (var i = 0; i < settings.length; i++) {
            partiesSettingsHash[settings[i]] = true;
        }
    
        console.log(partiesSettingsHash);
    }
}

var updateSettings = function () {
    var newSettings = [];

    var inputs = document.querySelectorAll('#qa-table .settings input')

    for (var i = 0; i < inputs.length; i++) {
        var name = inputs[i].name;
        var checked = inputs[i].checked;

        if (checked) {
            newSettings.push(name);
        }
    }

    console.log(newSettings);

    updateCookie('settings', newSettings.join(','));
}

// Onload
document.addEventListener("DOMContentLoaded", function(event) {
    var mainFont = new FontFaceObserver('Lato', {
        weight: 400
    });

    // Lazy load fonts for quicker initial render
    mainFont.load().then(function () {
        document.documentElement.className += "fonts-ready";
    }, function () {
    });

    var input = document.getElementById("search").getElementsByTagName('input')[0];
    input.focus();

    var partiskComplete = new autoComplete({
        selector: input,
        minChars: 3,
        source: function (term, suggest) {
            var request = new XMLHttpRequest();

            request.onreadystatechange = function() {
                console.log(request.responseText);
                if(request.readyState === 4 && request.status === 200) {
                    var data = JSON.parse(request.responseText);
                    var result = [];

                    suggest(data.suggestions);
                }
            }

            request.open('GET', serviceUrl + "?query=" + term, true);
            request.send();
        },
        renderItem: function (s, c) {
            switch (s.data.type) {
                case 'q': return '<li class="autocomplete-suggestion" data-type="' + s.data.type + '" data-value="' + s.value + '"><i class="fa fa-question-circle-o"></i>' + splitText(s.value, c) + '</li>';
                case 't': return '<li class="autocomplete-suggestion" data-type="' + s.data.type + '" data-value="' + s.value + '"><i class="fa fa-tag"></i>' + splitText(s.value, c) + '</li>';
                case 'p': return '<li class="autocomplete-suggestion" data-type="' + s.data.type + '" data-value="' + s.value + '"><i class="fa fa-black-tie"></i>' + splitText(s.value, c) + '</li>';
                case 'z': return '<li class="autocomplete-suggestion" data-type="' + s.data.type + '" data-value="' + s.value + '"><i class="fa fa-check-square"></i>' + splitText(s.value, c) + '</li>';
            }
        },
        onSelect: function (e, c, item) {
            var t = item.dataset.type;
            var v = item.dataset.value;
            switch(t) {
                case "q": window.location.replace(questionsUrl + v.replace(/ /g, "_").toLowerCase()); break;
                case "t": window.location.replace(tagsUrl + v.replace(/ /g, "_").toLowerCase()); break;
                case "p": window.location.replace(partiesUrl + v.replace(/ /g, "_").toLowerCase()); break;
                case "z": window.location.replace(quizzesUrl + v.replace(/ /g, "_").toLowerCase()); break;
            }
        }
    });
});

var indexPartyHash = {};
var items = {};
var indexRendered = {};
var questionHeight = 64;
var question_answers = {};
var questions = [];
var noQuestions;
var content;
var no_parties;
var initial_chunk_size = 20;
var chunk_size = 50;
var scrollIndexMargin = 5;

var drawQuestion = function (question) {
    var trow = document.createElement('div');
    trow.setAttribute('class', 'trow');
    var tcol = document.createElement('div');
    tcol.setAttribute('class', 'tcol name');
    var a = document.createElement('a');
    a.setAttribute('href', questionsUrl + question.s);
    a.innerHTML = question.t;

    trow.appendChild(tcol);
    tcol.appendChild(a);

    for (var k = 0; k < no_parties; k++) {
        var answer = question_answers[question.i] && question_answers[question.i][k];
        var party = indexPartyHash[k];

        if (showParty(party)) {
            if (answer) {
                var item = document.createElement('div');
                item.setAttribute('class', "tcol answer answer-type-" + answer);
                var itemA = document.createElement('a');
                itemA.setAttribute('href', answersUrl + question.s + '/' + party.s);
                itemA.innerHTML = answer === 1 ? 'ja' : 'nej';
                item.appendChild(itemA);
                trow.appendChild(item);
            } else {
                var item = document.createElement('div');
                item.setAttribute('class', "tcol answer empty");
                var itemI = document.createElement('i');
                itemI.setAttribute('class', 'fa fa-times');
                item.appendChild(itemI);
                trow.appendChild(item);
            }
        }
    }

    return trow;
}

var drawQuestions = function (scrollTop, offsetTop, windowHeight) {
    var topIndex = Math.round((scrollTop - offsetTop) / questionHeight) - scrollIndexMargin;
    var bottomIndex = Math.round((scrollTop - offsetTop + windowHeight) / questionHeight) + scrollIndexMargin;

    for (var i = topIndex; i <= bottomIndex; i++) {
        if (i >= 0 && i < noQuestions && !indexRendered[i]) {
            items[i].replaceWith(drawQuestion(questions[i]));
            indexRendered[i] = true;
        }
    }
}

// Draw questions table
document.addEventListener("DOMContentLoaded", function(event) {
    if (typeof data !== 'undefined') {
        questions = data.questions.sort((a,b) => {
            if (a.t > b.t) {
                return 1;
            }
            if (a.t < b.t) {
                return -1;
            }

            return 0;
        });

        var question_index_map = {}
        no_parties = data.parties.length;

        for (var i = 0; i < data.parties.length; i++) {
            var party = data.parties[i];
            question_index_map[party.i] = i;
            indexPartyHash[i] = party;
        }

        for (var i = 0; i < data.answers.length; i++) {
            var answer = data.answers[i];
            if (question_answers[answer.q] === undefined) {
                question_answers[answer.q] = {}
            }

            if (question_index_map[answer.p] !== undefined) {
                question_answers[answer.q][question_index_map[answer.p]] = answer.a;
            }
        }

        var qaTable = document.getElementById('qa-table');

        loadSettings();

        var settings = document.createElement('ul');
        settings.setAttribute('class', 'settings');
        
        for (var i = 0; i < data.parties.length; i++) {
            var party = data.parties[i];
            var li = document.createElement('li');
            var input = document.createElement('input');
            input.setAttribute('type', 'checkbox');
            input.setAttribute('name', party.i);

            input.checked = showParty(party);
            input.addEventListener('click', function () {
                updateSettings();
            });

            li.appendChild(input);

            var text = document.createElement('span');
            text.innerText = party.n;

            li.appendChild(text);
            
            settings.appendChild(li);
        }

        qaTable.appendChild(settings);

        var table = document.createElement(`div`);
        table.setAttribute('class', 'table');
        qaTable.appendChild(table);

        if (data.parties.length > 1) {
            var trowFiller = document.createElement('div');
            var tcolFiller = document.createElement('div');
            trowFiller.setAttribute('class', 'head trow');
            tcolFiller.setAttribute('class', 'tcol filler');
            trowFiller.appendChild(tcolFiller);

            qaTable.getElementsByClassName('table')[0].appendChild(trowFiller);

            for (var i = 0; i < data.parties.length; i++) {
                var party = data.parties[i];

                var tcol = document.createElement('div');
                var tcolA = document.createElement('a');
                var tcolPartyLogo = document.createElement('div');
                var tcolPartyLogoSmall = document.createElement('div');
                tcol.setAttribute('class', 'tcol table-logo');

                if (!showParty(party)) {
                    tcol.setAttribute('style', 'display: none');
                }

                tcolA.setAttribute('href', partiesUrl + party.s);
                tcolPartyLogo.setAttribute('class', 'party-logo party-logo-' + party.i);
                tcolPartyLogoSmall.setAttribute('class', 'party-logo-small party-logo-small-' + party.i);

                tcol.appendChild(tcolA);
                tcolA.appendChild(tcolPartyLogo);
                tcolA.appendChild(tcolPartyLogoSmall);

                trowFiller.appendChild(tcol);
            }
        }

        noQuestions = questions.length;

        var content = document.createElement('div');
        content.setAttribute('class', 'content');
        qaTable.getElementsByClassName("table")[0].appendChild(content);

        content.setAttribute('style', 'overflow: hidden; height: ' + noQuestions * questionHeight + ';');

        var doc = document.documentElement;
        var scrollTop = doc.scrollTop;
        var offsetTop = content.offsetTop;
        var windowHeight = document.body.clientHeight;

        for (var i = 0; i < noQuestions; i++) {
            var trow = document.createElement('div');
            trow.setAttribute('class', 'trow');
            trow.setAttribute('style', "height:" + questionHeight + "px");
            items[i] = trow
            content.appendChild(items[i]);
        }

        document.addEventListener("scroll", function (e) {
            var scrollTop = doc.scrollTop;
            drawQuestions(scrollTop, offsetTop, windowHeight);
        });

        drawQuestions(scrollTop, offsetTop, windowHeight);
    }
});
