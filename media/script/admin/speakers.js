// common.js should be included before this file.

function createItemHTML(speaker){
    return dataListEntry(speaker, speaker.full_name, defaultActions('speakers', speaker), defaultTags());
}

function editItem(){

}

jQuery(function(){
    jQuery.getJSON('/api/speakers/list', {}, function(speakers){
        var speaker, html = [];
        for (var i = 0, len = speakers.length; i < len; ++i){
            speaker = speakers[i];
            html.push(createItemHTML(speaker));
        }
        jQuery('#data-list').html(html.join(''));
    });
});

