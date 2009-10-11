jQuery(function(){
    var elements = {
        participant_count: jQuery('#form_register_participants input[name="count"]'),
        organization_1: jQuery('#form_register_participants input[name="organization_1"]'),
        address_1: jQuery('#form_register_participants textarea[name="address_1"]'),
        city_1: jQuery('#form_register_participants input[name="city_1"]'),
        country_code_1: jQuery('#form_register_participants select[name="country_code_1"]'),
        state_province_1: jQuery('#form_register_participants input[name="state_province_1"]'),
        zip_code_1: jQuery('#form_register_participants input[name="zip_code_1"]'),
        phone_number_1: jQuery('#form_register_participants input[name="phone_number_1"]'),
        other_address_fields: jQuery('#form_register_participants textarea.address'),
        other_organization_fields: jQuery('#form_register_participants input.organization'),
        other_country_code_fields: jQuery('#form_register_participants select.country_code'),
        other_state_province_fields: jQuery('#form_register_participants input.state_province'),
        other_city_fields: jQuery('#form_register_participants input.city'),
        other_zip_code_fields: jQuery('#form_register_participants input.zip_code'),
        other_phone_number_fields: jQuery('#form_register_participants input.phone_number'),
        link_remove_registrant: jQuery('#form_register_participants a[href="#remove"]')
    };


    function updateOrganizations(event){
        elements.other_organization_fields.val(jQuery(this).val().lowerSanitizeCapitalization());
    }
    function updateAddresses(event){
        elements.other_address_fields.val(jQuery(this).val());
    }
    function updateStateProvince(event){
        elements.other_state_province_fields.val(jQuery(this).val().sanitizeCapitalization());
    }
    function updateCountryCode(event){
        elements.other_country_code_fields.val(jQuery(this).val());
    }
    function updateZipCode(event){
        elements.other_zip_code_fields.val(jQuery(this).val());
    }
    function updateCity(event){
        elements.other_city_fields.val(jQuery(this).val().sanitizeCapitalization());
    }
    function updatePhoneNumber(event){
        elements.other_phone_number_fields.val(jQuery(this).val());
    }

    elements.organization_1.keyup(jQuery.defer(100, updateOrganizations));
    elements.address_1.keyup(jQuery.defer(100, updateAddresses));
    elements.zip_code_1.keyup(jQuery.defer(100, updateZipCode));
    elements.country_code_1.change(updateCountryCode);
    elements.state_province_1.keyup(jQuery.defer(100, updateStateProvince));
    elements.city_1.keyup(jQuery.defer(100, updateCity));
    elements.phone_number_1.keyup(jQuery.defer(100, updatePhoneNumber));

    elements.link_remove_registrant.click(function(event){
        event.preventDefault();
        event.stopPropagation();

        jQuery(this).parents('fieldset').remove();
        var value = elements.participant_count.val();
        elements.participant_count.val(value - 1);

        return false;
    });
});

