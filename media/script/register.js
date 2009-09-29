jQuery(function(){
    var elements = {
        organization_1: jQuery('#form_register_participants input[name="organization_1"]'),
        address_1: jQuery('#form_register_participants textarea[name="address_1"]'),
        other_address_fields: jQuery('#form_register_participants textarea.address'),
        other_organization_fields: jQuery('#form_register_participants input.organization')
    };

    jQuery('form.decorated-fields').validate({
        rules: {
            mobile_number: {
                mobile: true
            },
            phone_number: {
                phone: true
            }
        }
    });

    function updateOrganizations(event){
        elements.other_organization_fields.val(jQuery(this).val());
    }
    function updateAddresses(event){
        elements.other_address_fields.val(jQuery(this).val());
    }
    elements.organization_1.keyup(jQuery.defer(100, updateOrganizations));
    elements.address_1.keyup(jQuery.defer(100, updateAddresses));
});

