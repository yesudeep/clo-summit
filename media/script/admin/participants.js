// common.js should be included before this file.

/*
function itemActions(item){
    return defaultActions('participants', item) + '<a class="awesome-button" rel="email-message" href="mailto:' + item.email + '"><span class="symbol">&rArr;</span> Send message</a>';
}
*/
function createItemHTML(participant){
    return dataListEntry(participant, participant.full_name, defaultActions('participants', participant)/*itemActions(participant)*/, defaultTags());
}

function editItem(){

}

jQuery(function(){
    jQuery.getJSON('/api/participants/list', {}, function(participants){
        var participant, html = [];
        for (var i = 0, len = participants.length; i < len; ++i){
            participant = participants[i];
            html.push(createItemHTML(participant));
        }
        jQuery('#data-list').html(html.join(''));
    });
});

