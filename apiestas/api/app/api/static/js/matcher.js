var bookmakers = []
var action = "new"



// Example POST method implementation:
async function postCompetitor(url = '', data = {}) {
    // Default options are marked with *
    const response = await fetch(url, {
      method: 'POST', // *GET, POST, PUT, DELETE, etc.
      cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data) // body data type must match "Content-Type" header
    });
    console.log(response.status)
    if (response.status == 200){
        $( "div.success" ).fadeIn( 300 ).delay( 1500 ).fadeOut( 400 );
    } else{
        $( "div.failure" ).fadeIn( 300 ).delay( 1500 ).fadeOut( 400 );
    }
    return response.json()
  }


function submit_competitor(event){
    var form = event.parentElement.parentElement
    var sport = form.getElementsByClassName("bookmaker-sport-input")[0].value
    var bookmakers_els = form.getElementsByClassName("bookmaker-bookmaker-input")
    var tournaments_els = form.getElementsByClassName("bookmaker-tournament-input")
    var competitors_els = form.getElementsByClassName("bookmaker-competitor-input")
    var tournament_id = document.getElementById("tournament-id").value
    var competitor_id = document.getElementById("competitor-id").value
    var final_obj = {}
    final_obj["sport"] = sport
    final_obj["action_type"] = action
    final_obj["tournament_slug_id"] = tournament_id
    final_obj["competitor_slug_id"] = competitor_id
    final_obj["bookmaker_different_event_names"] = {}
    for (let i = 0; i < bookmakers_els.length; i++) {
        if (bookmakers_els[i].value && tournaments_els[i].value && competitors_els[i].value) {
            final_obj["bookmaker_different_event_names"][bookmakers_els[i].value] = {}
            final_obj["bookmaker_different_event_names"][bookmakers_els[i].value]["tournament"] = [tournaments_els[i].value]
            final_obj["bookmaker_different_event_names"][bookmakers_els[i].value]["competitor"] = [competitors_els[i].value]
        }
    }
    console.log(JSON.stringify(final_obj))
    // TODO: send request to add the competitor
    // if success
    postCompetitor('../api/linker/matched', final_obj)
    .then((response) => {
        console.log("response")
        console.log(response)
    })
    
    document.getElementById("tournament-id").value = ""
    document.getElementById("competitor-id").value = ""

    // update the matched competitors
    highlight_matched_competitors()
}


function insert_create_competitor(bookmaker, tournament, competitor, sport){
    var competitor_el = document.getElementsByClassName(bookmaker)[0]
    competitor_el.getElementsByClassName("bookmaker-bookmaker-input")[0].value = bookmaker
    competitor_el.getElementsByClassName("bookmaker-tournament-input")[0].value = tournament
    competitor_el.getElementsByClassName("bookmaker-competitor-input")[0].value = competitor
    form = competitor_el.parentElement.parentElement
    form.getElementsByClassName("bookmaker-sport-input")[0].value = sport
}

function automatically_insert_ids(){
    var tournaments = [...document.getElementsByClassName("bookmaker-tournament-input")].map(x=>x.value)
    var tournament_id = tournaments.sort(function (a, b) { return b.length - a.length })[0];
    document.getElementById("tournament-id").value = tournament_id

    var competitors = [...document.getElementsByClassName("bookmaker-competitor-input")].map(x=>x.value)
    var competitor_id = competitors.sort(function (a, b) { return b.length - a.length })[0];
    document.getElementById("competitor-id").value = competitor_id

}


function insert_add_competitor(bookmaker, tournament, competitor, sport){
    var competitor_el = document.getElementsByClassName("bookmaker-set-up-container")[0]
    document.getElementsByClassName("bookmaker-set-up-element")[0].innerText = bookmaker
    competitor_el.getElementsByClassName("bookmaker-bookmaker-input")[0].value = bookmaker
    competitor_el.getElementsByClassName("bookmaker-tournament-input")[0].value = tournament
    competitor_el.getElementsByClassName("bookmaker-competitor-input")[0].value = competitor
    form = competitor_el.parentElement.parentElement
    form.getElementsByClassName("bookmaker-sport-input")[0].value = sport
}

function set_up_create_competitors(){
    var container = document.getElementsByClassName("bookmaker-variable-content")[0]
    var string = ""
    for (const bookmaker of bookmakers){
        string += '<div class="bookmaker-set-up-container '+ bookmaker +'">'
        string += '<div class="bookmaker-set-up-element">'+ bookmaker +'</div>'
        string += '<div class="bookmaker-tournament bookmaker-set-up-element">'
        string += '<input type="text" placeholder="bookmakers tournament" class="bookmaker-tournament-input">'
        string += '</div>'
        string += '<div class="bookmaker-competitor bookmaker-set-up-element">'
        string += '<input type="text" placeholder="bookmakers competitor" class="bookmaker-competitor-input">'
        string += '</div>'
        string += '<input type="hidden" class="bookmaker-bookmaker-input" value="'+ bookmaker +'">'
        string += '</div>'
    }
    container.innerHTML = string
}

function set_up_add_competitors(){
    var container = document.getElementsByClassName("bookmaker-variable-content")[0]
    var string = ""
    string += '<div class="bookmaker-set-up-container">'
    string += '<div class="bookmaker-set-up-element"></div>'
    string += '<div class="bookmaker-tournament bookmaker-set-up-element">'
    string += '<input type="text" placeholder="bookmakers tournament" class="bookmaker-tournament-input">'
    string += '</div>'
    string += '<div class="bookmaker-competitor bookmaker-set-up-element">'
    string += '<input type="text" placeholder="bookmakers competitor" class="bookmaker-competitor-input">'
    string += '</div>'
    string += '<input type="hidden" class="bookmaker-bookmaker-input" value="">'
    string += '</div>'
    container.innerHTML = string
}

function add_competitor(event){
    var td_el = event.parentElement
    var bookmaker = td_el.getElementsByClassName("matcher-bookmaker-value")[0].value
    var tournament = td_el.getElementsByClassName("matcher-tournament-value")[0].value
    var competitor = td_el.getElementsByClassName("matcher-competitor-value")[0].value
    var sport = td_el.getElementsByClassName("matcher-sport-value")[0].value
    // todo insert the values into the relevant inputs
    if (action == "new"){
        insert_create_competitor(bookmaker, tournament, competitor, sport)
        automatically_insert_ids()
    } else if (action == "add"){
        insert_add_competitor(bookmaker, tournament, competitor, sport)
    }
    
}


function change_action(event){
    action = event.value
    if (action == "new"){
        set_up_create_competitors()
    } else if (action == "add"){
        set_up_add_competitors()
    }
}


function set_headers(table, bookmakers){
    var string = "<tr>"
    for (const bookmaker of bookmakers){
        string += "<th>" + bookmaker + "</th>"
    }
    string += "</tr>"
    table.innerHTML += string
}

function set_collumns(table, max_length, events, bookmakers){
    // TODO: order it by the tournaments, it will be better to create a matched events then
    string = ""
    for (let i = 0; i < max_length; i++) {
        string += "<tr>"
        for (const bookmaker of bookmakers){
            string += "<td>"
            if (events[bookmaker][i]){
                string += "<label class='unmatched-unit-name'>" + events[bookmaker][i].competitor + "</label><br>"
                string += "<label class='unmatched-unit-slugified-name'>" + events[bookmaker][i].tournament + "</label><br>"
                string += "<label class='unmatched-unit-slugified-name'>" + events[bookmaker][i].competitorNice + "</label><br>"
                string += "<label class='unmatched-unit-slugified-name'>" + events[bookmaker][i].label + "</label><br>"
                string += "<input type='hidden' class='matcher-bookmaker-value' value='" + bookmaker + "'>"
                string += "<input type='hidden' class='matcher-tournament-value' value='" + events[bookmaker][i].tournament + "'>"
                string += "<input type='hidden' class='matcher-competitor-value' value='" + events[bookmaker][i].competitor + "'>"
                string += "<input type='hidden' class='matcher-sport-value' value='" + events[bookmaker][i].sport + "'>"
                string += "<button type='button' onclick='add_competitor(this)'>Add competitor</button>"
            } else {
                string += undefined
            }
            string += "</td>"
        }
        string += "</tr>"
    }
    table.innerHTML += string
    console.log(events)
}

function highlight_matched_competitors(){
    fetch('../api/linker/matched?sport=soccer')
    .then((response) => response.json())
    .then((data) => {
        var events = data["events"];
        var tds = document.getElementsByTagName("td");
        for (const td of tds){
            var td_bookmakers = td.getElementsByClassName("matcher-bookmaker-value")
            if (td_bookmakers.length) {
                var td_bookmaker = td.getElementsByClassName("matcher-bookmaker-value")[0].value
                var td_tournament = td.getElementsByClassName("matcher-tournament-value")[0].value
                var td_competitor = td.getElementsByClassName("matcher-competitor-value")[0].value
                for (const event of events){
                    var competitor_obj = event["bookmakerDifferentEventNames"][td_bookmaker]
                    if (competitor_obj){
                        var tournaments = competitor_obj["tournament"]
                        var competitors = competitor_obj["competitor"]
                        if (tournaments.includes(td_tournament) && competitors.includes(td_competitor)) {
                            td.style.backgroundColor = "#afafaf"
                        } else {
                            td.style.backgroundColor = "transparent"
                        }
                    }
                }
            }
        }

        var data_blobs = document.getElementsByTagName("td")
        for (const data_blob of data_blobs){
            var bookmaker = data_blob.getElementsByClassName("matcher-bookmaker-value")
            if (bookmaker.length > 0){

            }
        }
        console.log(events)
    })
}

function get_unmatched_tournaments() {
    //fetch('../api/linker/unmatched/tournaments?sport=soccer')
    fetch('../api/linker/unmatched?sport=soccer')
    .then((response) => response.json())
    .then((data) => {
        let events = data["events"]
        // from all events get the bookmaker parameter
        let unfiltered_bookmakers = events.map(function (event){
            return event.bookmaker
        })
        // get only unique bookmakers
        bookmakers = [...new Set(unfiltered_bookmakers)]
        // for every bookmar initialize all the leagues that are in dataset
        let organized_events = []
        for (var bookmaker of bookmakers){
            organized_events[bookmaker] = {}
            var bookmakers_leagues = events.filter( event => bookmaker == event.bookmaker)
            var unfiltered_leagues = bookmakers_leagues.map(function (event){
                    return event.tournament
            })
            var leagues = [...new Set(unfiltered_leagues)]
            for (var league of leagues){
                organized_events[bookmaker][league] = []
            }
        }
        // organize all the data into specific bookmaker and league objects
        for (const event of events){
            organized_events[event.bookmaker][event.tournament].push(event)
        }

        let table = document.getElementById("unmatched-content")
        set_headers(table, bookmakers)

        let bookmaker_length_content = []
        let ordered_events = {}
        // since data is organized I can throw it into one array for specific bookmaker and it will still be ordered
        // + I find out what bookmaker has the most events
        for (var bookmaker of bookmakers){
            ordered_events[bookmaker] = Object.values(organized_events[bookmaker]).flat()
            bookmaker_length_content.push(ordered_events[bookmaker].length)
        }
        max_bookmaker_length = Math.max(...bookmaker_length_content)
        set_collumns(table, max_bookmaker_length, ordered_events, bookmakers)
        highlight_matched_competitors()
        set_up_create_competitors()
    });
}

(async ()=> {
    get_unmatched_tournaments()
})()