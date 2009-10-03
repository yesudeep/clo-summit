// common.js should be included before this file.

function createItemHTML(participant){
    return dataListEntry(participant, participant.full_name, defaultActions('participants', participant), defaultTags());
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

