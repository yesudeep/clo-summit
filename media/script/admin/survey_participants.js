// common.js should be included before this file.

function createItemHTML(survey_participant){
    return dataListEntry(survey_participant, survey_participant.full_name, defaultActions('survey_participants', survey_participant), defaultTags());
}

function editItem(){

}

jQuery(function(){
    jQuery.getJSON('/api/survey_participants/list', {}, function(survey_participants){
        var survey_participant, html = [];
        for (var i = 0, len = survey_participants.length; i < len; ++i){
            survey_participant = survey_participants[i];
            html.push(createItemHTML(survey_participant));
        }
        jQuery('#data-list').html(html.join(''));
    });
});

