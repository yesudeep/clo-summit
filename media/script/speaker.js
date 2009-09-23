jQuery(function(){
    jQuery('form.decorated-fields').validate({
        rules:{
            presentation: {
              required: true,
              accept: "ppt|doc|pdf"
            }
        },
        messages: {
            presentation: {
                accept: "Please upload a PowerPoint presentation, a Word document, or a PDF document only."
            }
        }
    });
});

