jQuery(function(){
    var elements = {
        form_nominate_speaker: jQuery('#form_nominate_speaker')
    };

    elements.form_nominate_speaker.find('input[name="presentation"]').change(function(event){
        elements.form_nominate_speaker.find('input[name="presentation_filename"]').val(jQuery(this).val());
    });
});

