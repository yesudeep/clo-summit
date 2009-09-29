jQuery(function(){
    var elements = {
        form_nominate_speaker: jQuery('#form_nominate_speaker')
    };

    jQuery('form.decorated-fields').validate({
        rules:{
            presentation: {
              required: true,
              accept: "ppt|doc|pdf"
            },
            mobile_number: {
              mobile: true
            }
        },
        messages: {
            presentation: {
                accept: "Please upload a PowerPoint presentation, a Word document, or a PDF document only."
            }
        }
    });


    elements.form_nominate_speaker.find('input[name="presentation"]').change(function(event){
        elements.form_nominate_speaker.find('input[name="presentation_filename"]').val(jQuery(this).val());
    });
});

