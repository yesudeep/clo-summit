jQuery(function(){
    jQuery('form.decorated-fields').validate({
        rules: {
            mobile_number: {
                mobile: true
            },
            phone_number: {
                mobile: true
            }
        }
    });
});

