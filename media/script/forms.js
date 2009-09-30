jQuery(function(){
    var elements = {
        mobile_or_phone_fields: jQuery('form input.mobile, form input.phone'),
        form_decorated_fields: jQuery('form.decorated-fields'),
        url_fields: jQuery('form input.url')
    };

    elements.mobile_or_phone_fields.numeric({allow: '+-() '});
    elements.url_fields.focus(function(event){
        var elem = jQuery(this), value = elem.val();
        if (!jQuery.trim(value)){
            elem.val("http://");
        }
    });

    elements.form_decorated_fields.validate({
        rules: {
            presentation: {
              required: true,
              accept: "ppt|doc|pdf"
            },
            mobile_number: {
                mobile: true
            },
            phone_number: {
                phone: true
            }
        },
        messages: {
            presentation: {
                accept: "Please upload a PowerPoint presentation, a Word document, or a PDF document only."
            }
        }
    });
});

