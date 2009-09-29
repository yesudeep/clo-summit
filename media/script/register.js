jQuery(function(){
    var elements = {
        participant_count: jQuery('#form_register_participants input[name="count"]'),
        organization_1: jQuery('#form_register_participants input[name="organization_1"]'),
        address_1: jQuery('#form_register_participants textarea[name="address_1"]'),
        other_address_fields: jQuery('#form_register_participants textarea.address'),
        other_organization_fields: jQuery('#form_register_participants input.organization'),
        link_remove_registrant: jQuery('#form_register_participants a[href="#remove"]')
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

    elements.link_remove_registrant.click(function(event){
        event.preventDefault();
        event.stopPropagation();

        jQuery(this).parents('fieldset').remove();
        var value = elements.participant_count.val();
        elements.participant_count.val(value - 1);

        return false;
    });
});

